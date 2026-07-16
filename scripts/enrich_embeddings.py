#!/usr/bin/env python3
"""
Enrich embedding chunks with Q&A metadata (category, importance, concepts, confidence).
Matches Q&A entries to chunks by concept_id and source.
"""

import json
import os
from pathlib import Path
from typing import Any
from collections import defaultdict


EMBEDDINGS_DIR = Path(os.getenv("EMBEDDINGS_DIR", "docs/okfs/embeddings"))
QA_FILE = Path(os.getenv("QA_FILE", "qa_pairs.jsonl"))


def load_qa(qa_file: Path) -> dict[str, list[dict]]:
    """Load Q&A pairs and index by concept_id."""
    qa_by_concept = defaultdict(list)
    with open(qa_file) as f:
        for line in f:
            line = line.strip()
            if line:
                qa = json.loads(line)
                # Index by concept_id from concepts or by source
                for concept in qa.get("concepts", []):
                    qa_by_concept[concept.lower()].append(qa)
                # Also index by source filename
                source = qa.get("source", "")
                if source:
                    qa_by_concept[source.lower()].append(qa)
    return qa_by_concept


def enrich_embeddings():
    """Enrich all embedding files with Q&A metadata."""
    qa_by_concept = load_qa(QA_FILE)
    print(f"Loaded {len(qa_by_concept)} Q&A concept mappings")
    
    jsonl_files = list(EMBEDDINGS_DIR.rglob("*_embeddings.jsonl"))
    print(f"Found {len(jsonl_files)} embedding files")
    
    total_enriched = 0
    
    for file_path in jsonl_files:
        bundle_name = file_path.stem.replace("_embeddings", "")
        print(f"\nProcessing {file_path.name} (bundle: {bundle_name})...")
        
        # Load chunks
        chunks = []
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    chunks.append(json.loads(line))
        
        # Enrich each chunk
        enriched = 0
        for chunk in chunks:
            concept_id = chunk.get("concept_id", "").lower()
            source_file = chunk.get("metadata", {}).get("source_file", "").lower()
            title = chunk.get("metadata", {}).get("title", "").lower()
            tags = [t.lower() for t in chunk.get("metadata", {}).get("tags", [])]
            
            # Find matching Q&A
            matching_qa = []
            for key in [concept_id, source_file, title] + tags:
                if key in qa_by_concept:
                    matching_qa.extend(qa_by_concept[key])
            
            if matching_qa:
                # Merge Q&A metadata (take highest confidence)
                best_qa = max(matching_qa, key=lambda x: x.get("confidence", 0))
                
                # Add Q&A enrichment to chunk metadata
                if "metadata" not in chunk:
                    chunk["metadata"] = {}
                
                chunk["metadata"]["qa_category"] = best_qa.get("category", "")
                chunk["metadata"]["qa_importance"] = best_qa.get("importance", "")
                chunk["metadata"]["qa_concepts"] = best_qa.get("concepts", [])
                chunk["metadata"]["qa_confidence"] = best_qa.get("confidence", 0.0)
                chunk["metadata"]["qa_question"] = best_qa.get("question", "")
                enriched += 1
                total_enriched += 1
        
        # Write back enriched chunks
        with open(file_path, "w") as f:
            for chunk in chunks:
                f.write(json.dumps(chunk, ensure_ascii=False) + "\n")
        
        print(f"  Enriched {enriched}/{len(chunks)} chunks")
    
    print(f"\n✅ Total enriched: {total_enriched} chunks")


if __name__ == "__main__":
    enrich_embeddings()