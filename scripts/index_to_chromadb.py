#!/usr/bin/env python3
"""
Index OKF chunks with embeddings into ChromaDB (Phase 8).

Creates a persistent vector store with full metadata filtering support.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_openai import OpenAIEmbeddings
from pydantic import SecretStr
from tqdm import tqdm


# ─── NVIDIA Embeddings (raw string, no tokenization) ──────────────────────
class NVIDIAEmbeddings(OpenAIEmbeddings):
    """NVIDIA embeddings API - sends raw strings, not tokenized input."""
    
    def embed_documents(self, texts: list[str], chunk_size: int | None = None, **kwargs) -> list[list[float]]:
        """Override to send raw strings without tokenization."""
        return self._embed(texts)
    
    def embed_query(self, text: str, **kwargs) -> list[float]:
        """Override to send raw string without tokenization."""
        return self._embed([text])[0]
    
    def _embed(self, texts: list[str]) -> list[list[float]]:
        """Send raw strings to NVIDIA embeddings endpoint."""
        # Ensure client is initialized
        if self.client is None:
            from openai import OpenAI
            self.client = OpenAI(
                base_url=self.openai_api_base,
                api_key=self.openai_api_key,
            )
        response = self.client.embeddings.create(
            input=texts,
            model=self.model,
        )
        return [d.embedding for d in response.data]
        return [d.embedding for d in response.data]


# Configuration
EMBEDDINGS_DIR = Path(os.getenv("EMBEDDINGS_DIR", "docs/okfs/embeddings"))
CHROMA_BASE_DIR = Path(os.getenv("CHROMA_BASE_DIR", "docs/okfs/chromadb"))
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")

# Provider-specific configuration
PROVIDER_CONFIG = {
    "local": {
        "collection": "okf_knowledge_local",
        "embedding_model": "nomic-embed-text",
        "chroma_dir": Path(os.getenv("CHROMA_BASE_DIR", "docs/okfs/chromadb")) / "local",
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    },
    "nvidia": {
        "collection": "okf_knowledge_nvidia",
        "embedding_model": "nvidia/nv-embed-v1",
        "chroma_dir": Path(os.getenv("CHROMA_BASE_DIR", "docs/okfs/chromadb")) / "nvidia",
        "base_url": os.getenv("LLM_BASE_URL", "https://integrate.api.nvidia.com/v1"),
    },
    "cloud": {
        "collection": "okf_knowledge_cloud",
        "embedding_model": "text-embedding-3-small",
        "chroma_dir": Path(os.getenv("CHROMA_BASE_DIR", "docs/okfs/chromadb")) / "cloud",
        "base_url": os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"),
    },
}

CONFIG = PROVIDER_CONFIG.get(LLM_PROVIDER, PROVIDER_CONFIG["local"])
CHROMA_DIR = CONFIG["chroma_dir"]
COLLECTION_NAME = CONFIG["collection"]
EMBEDDING_MODEL = CONFIG["embedding_model"]
BASE_URL = CONFIG["base_url"]
API_KEY = CONFIG.get("api_key", "")


def load_embeddings(embeddings_dir: Path) -> list[dict[str, Any]]:
    """Load all embedding JSONL files."""
    chunks = []
    jsonl_files = list(embeddings_dir.rglob("*_embeddings.jsonl"))
    
    print(f"Found {len(jsonl_files)} embedding files")
    
    for file_path in jsonl_files:
        # Extract bundle name from filename (e.g., "strategies_embeddings.jsonl" -> "strategies")
        bundle_name = file_path.stem.replace("_embeddings", "")
        print(f"  Loading {file_path.relative_to(embeddings_dir)} (bundle: {bundle_name})")
        with open(file_path) as f:
            for line in f:
                line = line.strip()
                if line:
                    chunk = json.loads(line)
                    chunk["_bundle"] = bundle_name  # Track bundle origin
                    chunks.append(chunk)
    
    print(f"Total chunks loaded: {len(chunks)}")
    return chunks


def chunk_to_document(chunk: dict[str, Any], chunk_index: int) -> Document:
    """Convert a chunk dict to a LangChain Document with metadata."""
    metadata = chunk.get("metadata", {}).copy()
    
    # Add top-level fields to metadata for filtering
    for key in ["chunk_id", "concept_id", "parent_concept_id", "chunk_number", 
                "title", "type", "tags", "embedding_model", "embedding_dim"]:
        if key in chunk:
            metadata[key] = chunk[key]
    
    # Add bundle to metadata
    bundle = chunk.get("_bundle", "")
    if bundle:
        metadata["bundle"] = bundle
    
    # Ensure metadata values are simple types (Chroma requirement)
    for k, v in list(metadata.items()):
        if isinstance(v, (list, dict)):
            metadata[k] = json.dumps(v)
        elif v is None:
            metadata[k] = ""
    
    # Create globally unique ID from bundle + concept_id + global chunk index
    concept_id = chunk.get("concept_id", "")
    chunk_number = chunk.get("chunk_number", 0)
    bundle = chunk.get("_bundle", "")
    
    # Use bundle + concept_id + global index as unique ID (guaranteed unique)
    if concept_id:
        if bundle:
            unique_id = f"{bundle}/{concept_id}#chunk-{chunk_index}"
        else:
            unique_id = f"{concept_id}#chunk-{chunk_index}"
    else:
        chunk_id = chunk.get("chunk_id", "")
        if bundle:
            unique_id = f"{bundle}/{chunk_id}#chunk-{chunk_index}"
        else:
            unique_id = f"{chunk_id}#chunk-{chunk_index}" or f"unknown#chunk-{chunk_index}"
    
    # Update metadata with the unique ID
    metadata["chunk_id"] = unique_id
    
    # Create Document with explicit ID
    doc = Document(
        page_content=chunk.get("content", ""),
        metadata=metadata,
        id=unique_id
    )
    
    return doc

def index_to_chromadb(chunks: list[dict], chroma_dir: Path, collection_name: str):
    """Index chunks into ChromaDB."""
    print(f"Initializing ChromaDB at {chroma_dir}")
    print(f"Collection: {collection_name}")
    print(f"Embedding model: {EMBEDDING_MODEL} @ {BASE_URL}")
    
    # Initialize embeddings (for query-time embedding) - use provider-specific
    if LLM_PROVIDER == "nvidia":
        embeddings = NVIDIAEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=BASE_URL,
            api_key=SecretStr(API_KEY) if API_KEY else None,
        )
    elif LLM_PROVIDER == "cloud":
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
    else:
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=BASE_URL)
    
    # Create or load vector store
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(chroma_dir),
    )
    
    # Convert chunks to documents
    print("Converting chunks to documents...")
    documents = [chunk_to_document(chunk, i) for i, chunk in enumerate(tqdm(chunks, desc="Converting"))]
    
    # Extract pre-computed embeddings
    embeddings_list = [chunk.get("embedding") for chunk in chunks]
    
    # Filter out any None embeddings
    valid_docs = []
    valid_embeddings = []
    for doc, emb in zip(documents, embeddings_list):
        if emb is not None:
            valid_docs.append(doc)
            valid_embeddings.append(emb)
        else:
            print(f"  Skipping chunk without embedding: {doc.id}")
    
    print(f"Indexing {len(valid_docs)} documents with pre-computed embeddings...")
    
    # Add to vector store with pre-computed embeddings
    vector_store._collection.add(
        documents=[d.page_content for d in valid_docs],
        metadatas=[d.metadata for d in valid_docs],
        embeddings=valid_embeddings,
        ids=[d.id for d in valid_docs],  # Use the unique Document ID
    )
    
    # Persist (automatic in newer versions)
    try:
        vector_store.persist()
    except AttributeError:
        pass  # Auto-persist in newer versions
    
    print(f"✅ Indexed {len(valid_docs)} chunks to ChromaDB")
    return vector_store


def test_query(vector_store: Chroma):
    """Test the indexed vector store with a few queries."""
    print("\n=== Testing Queries ===")
    print("Note: Test queries require valid API key. Skipping live queries.")
    print("Run the chat interface to test: make okf-chat-nvidia")


def main():
    print("=== Phase 8: Index OKF Chunks to ChromaDB ===")
    print(f"Embeddings dir: {EMBEDDINGS_DIR}")
    print(f"Chroma dir: {CHROMA_DIR}")
    
    if not EMBEDDINGS_DIR.exists():
        print(f"ERROR: Embeddings directory not found: {EMBEDDINGS_DIR}")
        sys.exit(1)
    
    # Load embeddings
    chunks = load_embeddings(EMBEDDINGS_DIR)
    if not chunks:
        print("No chunks found!")
        sys.exit(1)
    
    # Index to ChromaDB
    vector_store = index_to_chromadb(chunks, CHROMA_DIR, COLLECTION_NAME)
    
    # Test queries
    test_query(vector_store)
    
    print(f"\n✅ ChromaDB ready at {CHROMA_DIR}")
    print(f"Collection: {COLLECTION_NAME}")
    print("Use with: vector_store.similarity_search('your query', k=5)")


if __name__ == "__main__":
    main()