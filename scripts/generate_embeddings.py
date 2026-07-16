#!/usr/bin/env python3
"""
Generate embeddings for OKF chunks with inherited metadata (Phase 7).

Uses Ollama embeddings (nomic-embed-text) by default, configurable via env vars.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml
from langchain_ollama import OllamaEmbeddings
from tqdm import tqdm


# Configuration from environment
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
CHUNKS_DIR = Path(os.getenv("CHUNKS_DIR", "docs/okfs/chunks"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "docs/okfs/embeddings"))


def load_chunks(chunks_dir: Path) -> list[dict[str, Any]]:
    """Load all chunk JSONL files from the chunks directory."""
    chunks = []
    jsonl_files = list(chunks_dir.rglob("*_chunks.jsonl"))
    
    if not jsonl_files:
        # Fallback: look for any .jsonl files
        jsonl_files = list(chunks_dir.rglob("*.jsonl"))
    
    print(f"Found {len(jsonl_files)} chunk files")
    
    for file_path in jsonl_files:
        print(f"  Loading {file_path.relative_to(chunks_dir)}")
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    chunks.append(json.loads(line))
    
    print(f"Total chunks loaded: {len(chunks)}")
    return chunks


def prepare_embedding_text(chunk: dict[str, Any]) -> str:
    """Prepare text for embedding: combine title, type, description, and content."""
    parts = []
    
    # Title and type
    if chunk.get("title"):
        parts.append(f"Title: {chunk['title']}")
    if chunk.get("type"):
        parts.append(f"Type: {chunk['type']}")
    
    # Description from metadata
    meta = chunk.get("metadata", {})
    if meta.get("description"):
        parts.append(f"Description: {meta['description']}")
    
    # Tags for context
    tags = chunk.get("tags", [])
    if tags:
        parts.append(f"Tags: {', '.join(tags)}")
    
    # Main content
    content = chunk.get("content", "")
    if content:
        parts.append(f"Content: {content}")
    
    return "\n\n".join(parts)


def generate_embeddings(chunks: list[dict], model: str, base_url: str) -> list[dict]:
    """Generate embeddings for all chunks."""
    print(f"Initializing embeddings model: {model} @ {base_url}")
    embeddings = OllamaEmbeddings(model=model, base_url=base_url)
    
    print("Generating embeddings...")
    results = []
    
    for chunk in tqdm(chunks, desc="Embedding"):
        text = prepare_embedding_text(chunk)
        
        try:
            vector = embeddings.embed_query(text)
            
            # Store embedding in chunk
            chunk_with_embedding = chunk.copy()
            chunk_with_embedding["embedding"] = vector
            chunk_with_embedding["embedding_model"] = model
            chunk_with_embedding["embedding_dim"] = len(vector)
            results.append(chunk_with_embedding)
            
        except Exception as e:
            print(f"Error embedding chunk {chunk.get('chunk_id', 'unknown')}: {e}")
            # Store chunk without embedding
            chunk_with_embedding = chunk.copy()
            chunk_with_embedding["embedding"] = None
            chunk_with_embedding["embedding_error"] = str(e)
            results.append(chunk_with_embedding)
    
    return results


def save_embeddings(chunks_with_embeddings: list[dict], output_dir: Path):
    """Save chunks with embeddings to JSONL files by bundle."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Group by bundle (from concept_id prefix)
    by_bundle: dict[str, list[dict]] = {}
    for chunk in chunks_with_embeddings:
        concept_id = chunk.get("concept_id", "")
        bundle = concept_id.split("/")[0] if "/" in concept_id else concept_id.split("#")[0]
        by_bundle.setdefault(bundle, []).append(chunk)
    
    for bundle, bundle_chunks in by_bundle.items():
        output_file = output_dir / f"{bundle}_embeddings.jsonl"
        with open(output_file, "w") as f:
            for chunk in bundle_chunks:
                # Remove embedding from main JSON to save space in preview
                # but keep it for indexing
                f.write(json.dumps(chunk) + "\n")
        print(f"  Saved {len(bundle_chunks)} embeddings to {output_file}")


def save_metadata_summary(chunks_with_embeddings: list[dict], output_dir: Path):
    """Save a metadata summary for verification."""
    summary = {
        "total_chunks": len(chunks_with_embeddings),
        "chunks_with_embeddings": sum(1 for c in chunks_with_embeddings if c.get("embedding") is not None),
        "chunks_with_errors": sum(1 for c in chunks_with_embeddings if c.get("embedding_error")),
        "embedding_model": chunks_with_embeddings[0].get("embedding_model") if chunks_with_embeddings else "unknown",
        "embedding_dim": chunks_with_embeddings[0].get("embedding_dim") if chunks_with_embeddings else 0,
        "by_type": {},
        "by_bundle": {},
    }
    
    for chunk in chunks_with_embeddings:
        ctype = chunk.get("type", "Unknown")
        summary["by_type"][ctype] = summary["by_type"].get(ctype, 0) + 1
        
        concept_id = chunk.get("concept_id", "")
        bundle = concept_id.split("/")[0] if "/" in concept_id else concept_id.split("#")[0]
        summary["by_bundle"][bundle] = summary["by_bundle"].get(bundle, 0) + 1
    
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "embedding_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nEmbedding Summary:")
    print(f"  Total chunks: {summary['total_chunks']}")
    print(f"  With embeddings: {summary['chunks_with_embeddings']}")
    print(f"  Errors: {summary['chunks_with_errors']}")
    print(f"  Model: {summary['embedding_model']}")
    print(f"  Dimension: {summary['embedding_dim']}")
    print(f"  By type: {summary['by_type']}")
    print(f"  By bundle: {summary['by_bundle']}")


def main():
    print("=== Phase 7: Generate Embeddings for OKF Chunks ===")
    print(f"Chunks dir: {CHUNKS_DIR}")
    print(f"Output dir: {OUTPUT_DIR}")
    print(f"Model: {EMBEDDING_MODEL} @ {OLLAMA_BASE_URL}")
    
    if not CHUNKS_DIR.exists():
        print(f"ERROR: Chunks directory not found: {CHUNKS_DIR}")
        sys.exit(1)
    
    # Load chunks
    chunks = load_chunks(CHUNKS_DIR)
    if not chunks:
        print("No chunks found!")
        sys.exit(1)
    
    # Generate embeddings
    chunks_with_embeddings = generate_embeddings(chunks, EMBEDDING_MODEL, OLLAMA_BASE_URL)
    
    # Save results
    save_embeddings(chunks_with_embeddings, OUTPUT_DIR)
    save_metadata_summary(chunks_with_embeddings, OUTPUT_DIR)
    
    print(f"\n✅ Embeddings saved to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()