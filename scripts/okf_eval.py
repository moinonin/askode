#!/usr/bin/env python3
"""
OKF Evaluation Harness — OKF-specific metrics + optional RAGAS.

Evaluates retrieval and generation quality over the golden Q&A set.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# ─── Configuration ──────────────────────────────────────────────────────
CHROMA_DIR = Path(os.getenv("CHROMA_DIR", "docs/okfs/chromadb"))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "okf_knowledge")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "mistral-nemo:12b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K", "6"))

# ─── Initialize Vector Store ────────────────────────────────────────────
def get_vector_store():
    if LLM_PROVIDER == "cloud":
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    else:
        embeddings = OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL,
        )
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

# ─── Load Golden Q&A ────────────────────────────────────────────────────
def load_golden_qa(golden_path: Path) -> List[Dict[str, Any]]:
    """Load golden Q&A pairs from JSONL."""
    qa_pairs = []
    with open(golden_path) as f:
        for line in f:
            line = line.strip()
            if line:
                qa_pairs.append(json.loads(line))
    return qa_pairs

# ─── Retrieve Context for Questions ────────────────────────────────────
def retrieve_context(vector_store: Chroma, questions: List[str], bundles: List[str] = None) -> List[List[str]]:
    """Retrieve top-k contexts for each question."""
    contexts = []
    filter_dict = {"bundle": {"$in": bundles}} if bundles else None
    
    for question in questions:
        if filter_dict:
            docs = vector_store.similarity_search(question, k=RETRIEVER_TOP_K, filter=filter_dict)
        else:
            docs = vector_store.similarity_search(question, k=RETRIEVER_TOP_K)
        context_texts = [doc.page_content for doc in docs]
        contexts.append(context_texts)
    return contexts

# ─── Generate Answers ───────────────────────────────────────────────────
async def generate_answers(questions: List[str], contexts: List[List[str]]) -> List[str]:
    """Generate answers using LLM."""
    if LLM_PROVIDER == "cloud":
        llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
            temperature=0.1,
        )
    else:
        llm = ChatOllama(
            model=LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0.1,
        )
    
    prompt = ChatPromptTemplate.from_template("""You are a technical expert answering questions about a software project using a curated OKF knowledge base.

Rules:
1. Answer ONLY from the provided context. Do not use external knowledge.
2. Cite sources inline like [Source: bundle/concept_id] after each claim.
3. If context is irrelevant or missing, say: "I cannot find that in my project files."
4. If context partially answers, give what you have and note gaps.
5. Be concise. Prefer code-level specifics over generalities.

--- CONTEXT ---
{context}
----------------

Human: {question}""")
    
    chain = prompt | llm
    
    answers = []
    for question, ctx in zip(questions, contexts):
        context_str = "\n\n".join(ctx)
        response = await chain.ainvoke({"context": context_str, "question": question})
        answers.append(response.content)
    
    return answers

# ─── OKF-Specific Metrics ──────────────────────────────────────────────
def compute_okf_metrics(
    golden: List[Dict[str, Any]], 
    contexts: List[List[str]], 
    answers: List[str],
    vector_store: Chroma
) -> Dict[str, float]:
    """Compute OKF-specific evaluation metrics."""
    
    # 1. Concept Retrieval Accuracy
    concept_hits = 0
    total_concepts = 0
    
    for i, qa in enumerate(golden):
        expected = qa.get("expected_concept_ids", [])
        if not expected:
            continue
        total_concepts += len(expected)
        
        docs = vector_store.similarity_search(qa["question"], k=RETRIEVER_TOP_K)
        retrieved_concept_ids = set()
        for doc in docs:
            cid = doc.metadata.get("concept_id", "")
            if cid:
                retrieved_concept_ids.add(cid)
        
        for exp in expected:
            if exp in retrieved_concept_ids:
                concept_hits += 1
    
    concept_accuracy = concept_hits / total_concepts if total_concepts > 0 else 0.0
    
    # 2. Cross-Bundle Link Traversal
    cross_bundle_correct = 0
    cross_bundle_expected = 0
    
    for i, qa in enumerate(golden):
        expected_bundles = qa.get("expected_bundles", [])
        if not expected_bundles:
            continue
        cross_bundle_expected += 1
        
        answer = answers[i]
        found = sum(1 for b in expected_bundles if b.lower() in answer.lower())
        if found > 0:
            cross_bundle_correct += 1
    
    cross_bundle_rate = cross_bundle_correct / cross_bundle_expected if cross_bundle_expected > 0 else 0.0
    
    # 3. Citation Compliance
    citation_count = sum(1 for a in answers if "Source:" in a)
    citation_rate = citation_count / len(answers) if answers else 0.0
    
    # 4. Abstention Rate (out-of-scope)
    abstain_count = sum(1 for a in answers if "cannot find" in a.lower() or "not find" in a.lower())
    abstain_rate = abstain_count / len(answers) if answers else 0.0
    
    # 5. Answer Length (sanity check)
    avg_answer_len = sum(len(a) for a in answers) / len(answers) if answers else 0.0
    
    return {
        "concept_retrieval_accuracy": concept_accuracy,
        "cross_bundle_traversal_rate": cross_bundle_rate,
        "citation_compliance": citation_rate,
        "abstain_rate": abstain_rate,
        "avg_answer_length": avg_answer_len,
    }

# ─── Main ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="OKF Evaluation Harness")
    parser.add_argument("--golden", default="eval/golden_qa.jsonl", help="Golden Q&A JSONL file")
    parser.add_argument("--output", default="eval/report.json", help="Output report JSON")
    parser.add_argument("--provider", default="local", choices=["local", "cloud"], help="LLM provider")
    parser.add_argument("--model", default="mistral-nemo:12b", help="LLM model name")
    parser.add_argument("--embedding", default="nomic-embed-text", help="Embedding model")
    parser.add_argument("--chroma", default="docs/okfs/chromadb", help="ChromaDB directory")
    parser.add_argument("--collection", default="okf_knowledge", help="Chroma collection name")
    parser.add_argument("--top-k", type=int, default=6, help="Retriever top-k")
    parser.add_argument("--bundles", nargs="+", help="Filter to specific bundles")
    args = parser.parse_args()
    
    # Update globals - must declare before any assignments
    global CHROMA_DIR, COLLECTION_NAME, LLM_PROVIDER, LLM_MODEL, EMBEDDING_MODEL, RETRIEVER_TOP_K
    CHROMA_DIR = Path(args.chroma)
    COLLECTION_NAME = args.collection
    LLM_PROVIDER = args.provider
    LLM_MODEL = args.model
    EMBEDDING_MODEL = args.embedding
    RETRIEVER_TOP_K = args.top_k
    
    golden_path = Path(args.golden)
    if not golden_path.exists():
        print(f"ERROR: Golden Q&A not found: {golden_path}")
        print("Create eval/golden_qa.jsonl first with 50 Q/A pairs")
        sys.exit(1)
    
    print(f"Loading golden Q&A from {golden_path}...")
    golden = load_golden_qa(golden_path)
    print(f"Loaded {len(golden)} Q&A pairs")
    
    print(f"Connecting to ChromaDB at {CHROMA_DIR}...")
    vector_store = get_vector_store()
    
    questions = [qa["question"] for qa in golden]
    bundles = args.bundles
    
    print(f"Retrieving contexts for {len(questions)} questions...")
    contexts = retrieve_context(vector_store, questions, bundles)
    
    print(f"Generating answers...")
    import asyncio
    answers = asyncio.run(generate_answers(questions, contexts))
    
    print("Computing OKF metrics...")
    okf_metrics = compute_okf_metrics(golden, contexts, answers, vector_store)
    
    # Combine results
    report = {
        "golden_pairs": len(golden),
        "retriever_top_k": RETRIEVER_TOP_K,
        "llm_provider": LLM_PROVIDER,
        "llm_model": LLM_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "okf_metrics": okf_metrics,
    }
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n{'='*60}")
    print("EVALUATION REPORT")
    print(f"{'='*60}")
    print(f"\nOKF Metrics:")
    for k, v in okf_metrics.items():
        print(f"  {k}: {v:.4f}")
    print(f"\nReport saved to {output_path}")

if __name__ == "__main__":
    main()