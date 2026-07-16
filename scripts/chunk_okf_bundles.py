#!/usr/bin/env python3
"""
Semantic chunking pipeline for OKF bundles (Phase 6).

Loads OKF bundles, splits large concepts by semantic boundaries (headings, code blocks),
preserves parent-child relationships, and outputs chunks ready for embedding.
"""

import argparse
import json
import re
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from tqdm import tqdm


@dataclass
class OKFChunk:
    """A semantic chunk derived from an OKF concept."""
    chunk_id: str
    concept_id: str
    parent_concept_id: str
    chunk_number: int
    title: str
    type: str
    tags: list[str]
    content: str
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class OKFConcept:
    """Parsed OKF concept from bundle."""
    concept_id: str
    type: str
    title: str
    description: str
    resource: str
    tags: list[str]
    timestamp: str
    content: str
    frontmatter: dict
    file_path: Path


class OKFBundleLoader:
    """Loads and parses OKF bundles from disk."""
    
    def __init__(self, bundle_dir: Path):
        self.bundle_dir = bundle_dir.resolve()
    
    def load_concepts(self) -> list[OKFConcept]:
        """Load all concepts from bundle, excluding index.md and log.md."""
        concepts = []
        
        for md_file in self.bundle_dir.rglob("*.md"):
            if md_file.name in ("index.md", "log.md"):
                continue
            
            try:
                concept = self._parse_concept(md_file)
                if concept:
                    concepts.append(concept)
            except Exception as e:
                print(f"Warning: Failed to parse {md_file}: {e}")
        
        return concepts
    
    def _parse_concept(self, file_path: Path) -> Optional[OKFConcept]:
        content = file_path.read_text(encoding="utf-8")
        
        if not content.startswith("---\n"):
            return None
        
        parts = content.split("---\n", 2)
        if len(parts) < 3:
            return None
        
        try:
            fm = yaml.safe_load(parts[1]) or {}
        except yaml.YAMLError:
            return None
        
        body = parts[2].lstrip()
        
        concept_id = fm.get("concept_id", "")
        if not concept_id:
            # Derive from relative path
            concept_id = str(file_path.relative_to(self.bundle_dir).with_suffix(""))
        
        return OKFConcept(
            concept_id=concept_id,
            type=fm.get("type", "Unknown"),
            title=fm.get("title", file_path.stem),
            description=fm.get("description", ""),
            resource=fm.get("resource", ""),
            tags=fm.get("tags", []),
            timestamp=fm.get("timestamp", datetime.now().isoformat()),
            content=body,
            frontmatter=fm,
            file_path=file_path,
        )


class SemanticChunker:
    """
    Splits OKF concepts into semantic chunks.
    
    Strategy:
    1. If concept is small (< 2000 chars), keep as single chunk
    2. Split by markdown headings (##, ###)
    3. Keep code blocks intact
    4. Preserve tables as single chunks
    5. Maintain parent-child hierarchy via chunk_number
    """
    
    MAX_CHUNK_CHARS = 2000
    MIN_CHUNK_CHARS = 100
    
    def __init__(self, max_chars: int = 2000):
        self.max_chars = max_chars
    
    def chunk_concept(self, concept: OKFConcept) -> list[OKFChunk]:
        """Split a concept into semantic chunks."""
        # Small concepts: single chunk
        if len(concept.content) <= self.max_chars:
            return [self._make_chunk(concept, 0, concept.title, concept.content)]
        
        # Large concepts: split by semantic structure
        return self._split_by_headings(concept)
    
    def _make_chunk(
        self, 
        concept: OKFConcept, 
        chunk_num: int, 
        title: str, 
        content: str
    ) -> OKFChunk:
        """Create a chunk with inherited metadata."""
        chunk_id = f"{concept.concept_id}#chunk-{chunk_num}"
        
        # Inherit and extend metadata
        metadata = {
            **concept.frontmatter,
            "chunk_number": chunk_num,
            "parent_concept_id": concept.concept_id,
            "chunk_title": title,
            "source_file": concept.resource,
            "concept_type": concept.type,
        }
        
        # Add section heading as tag if it's a method/function
        if concept.type in ("Function", "Method", "Class"):
            metadata["section"] = title
        
        return OKFChunk(
            chunk_id=chunk_id,
            concept_id=concept.concept_id,
            parent_concept_id=concept.concept_id,
            chunk_number=chunk_num,
            title=title,
            type=concept.type,
            tags=concept.tags,
            content=content.strip(),
            metadata=metadata,
        )
    
    def _split_by_headings(self, concept: OKFConcept) -> list[OKFChunk]:
        """Split concept by markdown headings, preserving code blocks."""
        content = concept.content
        chunks = []
        
        # Find all headings with their positions
        heading_pattern = re.compile(r"^(#{2,4})\s+(.+)$", re.MULTILINE)
        headings = [(m.start(), m.group(1).count("#"), m.group(2).strip()) 
                    for m in heading_pattern.finditer(content)]
        
        if not headings:
            # No headings - split by paragraphs
            return self._split_by_paragraphs(concept)
        
        # Add virtual heading at start for content before first heading
        sections = []
        if headings[0][0] > 0:
            sections.append((0, 0, concept.title, content[:headings[0][0]]))
        
        # Process each heading section
        for i, (start, level, title) in enumerate(headings):
            end = headings[i + 1][0] if i + 1 < len(headings) else len(content)
            section_content = content[start:end]
            sections.append((start, level, title, section_content))
        
        # Merge small sections, split large ones
        for start, level, title, section_content in sections:
            if len(section_content) <= self.max_chars:
                chunks.append(self._make_chunk(concept, len(chunks), title, section_content))
            else:
                # Recursively split large section
                sub_chunks = self._split_large_section(concept, len(chunks), title, section_content)
                chunks.extend(sub_chunks)
        
        return chunks if chunks else [self._make_chunk(concept, 0, concept.title, content)]
    
    def _split_large_section(
        self, 
        concept: OKFConcept, 
        base_num: int, 
        title: str, 
        content: str
    ) -> list[OKFChunk]:
        """Split a large section by code blocks, then paragraphs."""
        chunks = []
        
        # Split by code blocks first
        code_block_pattern = re.compile(r"(```[\s\S]*?```)", re.MULTILINE)
        parts = code_block_pattern.split(content)
        
        current_text = ""
        chunk_num = base_num
        
        for part in parts:
            if code_block_pattern.match(part):
                # Code block - keep intact
                if current_text.strip():
                    chunks.append(self._make_chunk(
                        concept, chunk_num, f"{title} (part {chunk_num - base_num + 1})", 
                        current_text
                    ))
                    chunk_num += 1
                    current_text = ""
                chunks.append(self._make_chunk(
                    concept, chunk_num, f"{title} — code", part
                ))
                chunk_num += 1
            else:
                current_text += part
        
        if current_text.strip():
            chunks.append(self._make_chunk(
                concept, chunk_num, f"{title} (part {chunk_num - base_num + 1})", 
                current_text
            ))
        
        return chunks
    
    def _split_by_paragraphs(self, concept: OKFConcept) -> list[OKFChunk]:
        """Fallback: split by double newlines."""
        paragraphs = [p.strip() for p in concept.content.split("\n\n") if p.strip()]
        chunks = []
        current = ""
        chunk_num = 0
        
        for p in paragraphs:
            if len(current) + len(p) + 2 <= self.max_chars:
                current += ("\n\n" + current) if current else p
            else:
                if current:
                    chunks.append(self._make_chunk(concept, chunk_num, 
                        f"{concept.title} (part {chunk_num + 1})", current))
                    chunk_num += 1
                current = p
        
        if current:
            chunks.append(self._make_chunk(concept, chunk_num, 
                f"{concept.title} (part {chunk_num + 1})", current))
        
        return chunks if chunks else [self._make_chunk(concept, 0, concept.title, concept.content)]


class ChunkingPipeline:
    """Orchestrates the chunking pipeline across bundles."""
    
    def __init__(self, max_chunk_chars: int = 2000):
        self.chunker = SemanticChunker(max_chunk_chars)
    
    def process_bundle(self, bundle_dir: Path) -> list[OKFChunk]:
        """Process a single bundle directory."""
        loader = OKFBundleLoader(bundle_dir)
        concepts = loader.load_concepts()
        
        all_chunks = []
        for concept in tqdm(concepts, desc=f"Chunking {bundle_dir.name}"):
            chunks = self.chunker.chunk_concept(concept)
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def process_multiple_bundles(self, bundle_dirs: list[Path]) -> dict[str, list[OKFChunk]]:
        """Process multiple bundles, returning chunks per bundle."""
        results = {}
        for bundle_dir in bundle_dirs:
            results[bundle_dir.name] = self.process_bundle(bundle_dir)
        return results
    
    def save_chunks(self, chunks: list[OKFChunk], output_path: Path):
        """Save chunks as JSONL for embedding pipeline."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with output_path.open("w") as f:
            for chunk in chunks:
                f.write(json.dumps(chunk.to_dict()) + "\n")
        
        print(f"Saved {len(chunks)} chunks to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Semantic chunking for OKF bundles (Phase 6)")
    parser.add_argument("--bundle", action="append", required=True, 
                       help="Bundle directory (can specify multiple)")
    parser.add_argument("--output", default="okf_chunks", 
                       help="Output directory for chunk JSONL files")
    parser.add_argument("--max-chars", type=int, default=2000,
                       help="Maximum characters per chunk")
    args = parser.parse_args()
    
    bundle_dirs = [Path(b).resolve() for b in args.bundle]
    
    for d in bundle_dirs:
        if not d.exists():
            print(f"Error: Bundle not found: {d}")
            return 1
    
    pipeline = ChunkingPipeline(max_chunk_chars=args.max_chars)
    results = pipeline.process_multiple_bundles(bundle_dirs)
    
    output_dir = Path(args.output).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    total_chunks = 0
    for bundle_name, chunks in results.items():
        output_file = output_dir / f"{bundle_name}_chunks.jsonl"
        pipeline.save_chunks(chunks, output_file)
        total_chunks += len(chunks)
        
        # Print stats
        by_type = {}
        for c in chunks:
            by_type[c.type] = by_type.get(c.type, 0) + 1
        print(f"  {bundle_name}: {len(chunks)} chunks ({by_type})")
    
    print(f"\nTotal: {total_chunks} chunks across {len(results)} bundles")
    print(f"Output: {output_dir}")
    return 0


if __name__ == "__main__":
    exit(main())