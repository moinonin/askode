#!/usr/bin/env python3
"""
OKF RAG Chat Interface — Chainlit app querying OKF bundles in ChromaDB.

Features:
- Metadata filtering (type, bundle, tags, language)
- Cross-bundle search with bundle-aware citations
- Query classification → bundle routing
- Streaming responses with source citations
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, List, Any

import chainlit as cl
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr
from langchain_core.runnables import RunnablePassthrough


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
        if not hasattr(self, '_nvidia_client') or self._nvidia_client is None:
            from openai import OpenAI
            self._nvidia_client = OpenAI(
                base_url=self.openai_api_base,
                api_key=self.openai_api_key,
            )
        response = self._nvidia_client.embeddings.create(
            input=texts,
            model=self.model,
        )
        return [d.embedding for d in response.data]

# ─── Configuration ──────────────────────────────────────────────────────
CHROMA_BASE_DIR = Path(os.getenv("CHROMA_BASE_DIR", "docs/okfs/chromadb"))
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")  # local | cloud | nvidia

# Provider-specific configurations with LLM model defaults
PROVIDER_CONFIG = {
    "local": {
        "collection": "okf_knowledge_local",
        "embedding_model": "nomic-embed-text",
        "llm_model": "mistral-nemo:12b",
        "embedding_dim": 768,
        "chroma_dir": CHROMA_BASE_DIR / "local",
        "base_url": "http://localhost:11434",
    },
    "nvidia": {
        "collection": "okf_knowledge_nvidia",
        "embedding_model": "nvidia/nv-embed-v1",
        "llm_model": "nvidia/nemotron-3-ultra-550b-a55b",
        "embedding_dim": 4096,
        "chroma_dir": CHROMA_BASE_DIR / "nvidia",
        "base_url": "https://integrate.api.nvidia.com/v1",
        "api_key": os.getenv("LLM_API_KEY", ""),
    },
    "cloud": {
        "collection": "okf_knowledge_cloud",
        "embedding_model": "text-embedding-3-small",
        "llm_model": "gpt-4o-mini",
        "embedding_dim": 1536,
        "chroma_dir": CHROMA_BASE_DIR / "cloud",
        "base_url": "https://api.openai.com/v1",
        "api_key": os.getenv("LLM_API_KEY", ""),
    },
}

# Get current provider config
_provider_config = PROVIDER_CONFIG.get(LLM_PROVIDER, PROVIDER_CONFIG["local"])

# Provider-specific defaults take precedence over .env
# .env is only used if explicitly set for current provider via LLM_MODEL_LOCAL etc.
provider_llm_env = f"LLM_MODEL_{LLM_PROVIDER.upper()}"
LLM_MODEL = os.getenv(provider_llm_env) or _provider_config["llm_model"]
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", _provider_config["embedding_model"])
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", _provider_config.get("base_url", "https://integrate.api.nvidia.com/v1"))
LLM_API_KEY = os.getenv("LLM_API_KEY", _provider_config.get("api_key", ""))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K", "6"))
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "4"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
RETRIEVER_TOP_K = int(os.getenv("RETRIEVER_TOP_K", "6"))
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "4"))

# Provider-specific paths (derived from provider config)
_provider_config = PROVIDER_CONFIG.get(LLM_PROVIDER, PROVIDER_CONFIG["local"])
COLLECTION_NAME = _provider_config["collection"]
CHROMA_DIR = _provider_config["chroma_dir"]
EMBEDDING_DIM = _provider_config["embedding_dim"]
BASE_URL = _provider_config["base_url"]
API_KEY = _provider_config.get("api_key", "")

# Ensure chroma directory exists
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# ─── Bundle Metadata ───────────────────────────────────────────────────
BUNDLES = {
    "code_bundle": {
        "name": "Code Bundle",
        "description": "AST-extracted concepts from src/ (classes, functions, modules)",
        "keywords": ["class", "function", "method", "module", "import", "inheritance", "signature"],
    },
    "scripts_bundle": {
        "name": "Scripts Bundle", 
        "description": "AST-extracted concepts from scripts/ (generation, conversion, quizgen)",
        "keywords": ["script", "generate", "convert", "quizgen", "pipeline", "embedding"],
    },
    "strategies_bundle": {
        "name": "Strategies Bundle",
        "description": "Strategy322sgo implementation (entry, exit, risk, position management)",
        "keywords": ["strategy", "entry", "exit", "populate", "indicator", "trade", "risk", "karakana", "freqtrade"],
    },
    "docs_bundle": {
        "name": "Documentation Bundle",
        "description": "Specs, deployment guides, workflows, quickstarts, configs",
        "keywords": ["spec", "deployment", "workflow", "quickstart", "config", "threshold", "docker", "specifies", "guides"],
    },
}

# ─── Initialize Embeddings & Vector Store ──────────────────────────────
if LLM_PROVIDER == "cloud":
    embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
elif LLM_PROVIDER == "nvidia":
    embeddings = NVIDIAEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=PROVIDER_CONFIG["nvidia"]["base_url"],
        api_key=SecretStr(PROVIDER_CONFIG["nvidia"]["api_key"]) if PROVIDER_CONFIG["nvidia"]["api_key"] else None,
    )
else:
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )

vector_store = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddings,
    persist_directory=str(CHROMA_DIR),
)

# ─── LLM ───────────────────────────────────────────────────────────────
if LLM_PROVIDER == "cloud":
    llm = ChatOpenAI(
        model=PROVIDER_CONFIG["cloud"]["llm_model"],
        temperature=LLM_TEMPERATURE,
        streaming=True,
    )
elif LLM_PROVIDER == "nvidia":
    llm = ChatOpenAI(
        model=PROVIDER_CONFIG["nvidia"]["llm_model"],
        base_url=PROVIDER_CONFIG["nvidia"]["base_url"],
        api_key=SecretStr(PROVIDER_CONFIG["nvidia"]["api_key"]) if PROVIDER_CONFIG["nvidia"]["api_key"] else None,
        temperature=LLM_TEMPERATURE,
        streaming=True,
    )
else:
    llm = ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=LLM_TEMPERATURE,
    )

# ─── Query Classification ──────────────────────────────────────────────
CLASSIFIER_PROMPT = """Classify the user's query into ONE intent category:

Categories:
- HOW_TO: Deployment, configuration, setup, quickstart, "how do I", "run", "start", "launch"
- DEBUG: Error handling, troubleshooting, "why does", "fix", "error"
- ARCH: Architecture, modules, data flow, "how does it work", "overview"
- CODE: Function signatures, class details, parameters, "what does X do", "show me"
- CONFIG: Thresholds, parameters, docker, yaml, "what value", "setting"
- WORKFLOW: Training, inference, pipeline, "process", "steps", "flow", "karakana"

Query: {query}

Return ONLY the category name (HOW_TO, DEBUG, ARCH, CODE, CONFIG, WORKFLOW)."""

INTENT_TO_BUNDLES = {
    "HOW_TO": ["freqtrade-karakana-deployment", "freqtrade-karakana-quickstart", "docker-compose", "freqtrade-karakana-thresholds", "FREQTRADE_STRATEGY_SPEC", "rdql-karakana-freqtrade-workflow"],
    "DEBUG": ["strategies", "Strategy322sgo", "okfs", "bot", "quizgen", "convert_docs_to_okf"],
    "ARCH": ["strategies", "Strategy322sgo", "okfs", "bot", "quizgen", "convert_docs_to_okf", "freqtrade-karakana-deployment", "rdql-karakana-freqtrade-workflow"],
    "CODE": ["strategies", "Strategy322sgo", "okfs", "bot", "quizgen", "convert_docs_to_okf"],
    "CONFIG": ["freqtrade-karakana-deployment", "freqtrade-karakana-quickstart", "docker-compose", "freqtrade-karakana-thresholds", "strategies", "Strategy322sgo"],
    "WORKFLOW": ["rdql-karakana-freqtrade-workflow", "freqtrade-karakana-deployment", "freqtrade-karakana-quickstart", "quizgen", "convert_docs_to_okf"],
}

DEFAULT_BUNDLES = ["strategies", "freqtrade-karakana-deployment", "Strategy322sgo", "okfs", "freqtrade-karakana-quickstart", "rdql-karakana-freqtrade-workflow"]

async def classify_query(query: str) -> List[str]:
    """Classify query and return relevant bundle names."""
    try:
        # Quick keyword-based classification (fallback to LLM if needed)
        query_lower = query.lower()
        
        # Keyword matching first - return actual ChromaDB bundle values
        if any(kw in query_lower for kw in ["deploy", "docker", "quickstart", "setup", "install", "configure", "run", "start", "launch"]):
            return ["freqtrade-karakana-deployment", "freqtrade-karakana-quickstart", "docker-compose", "freqtrade-karakana-thresholds", "FREQTRADE_STRATEGY_SPEC", "rdql-karakana-freqtrade-workflow"]
        if any(kw in query_lower for kw in ["error", "fix", "debug", "fail", "exception", "troubleshoot"]):
            return ["strategies", "Strategy322sgo", "okfs", "bot", "quizgen", "convert_docs_to_okf"]
        if any(kw in query_lower for kw in ["architecture", "overview", "modules", "data flow", "structure"]):
            return ["strategies", "Strategy322sgo", "okfs", "bot", "quizgen", "convert_docs_to_okf", "freqtrade-karakana-deployment", "rdql-karakana-freqtrade-workflow"]
        if any(kw in query_lower for kw in ["signature", "parameter", "return", "class", "function", "method", "what does"]):
            return ["strategies", "Strategy322sgo", "okfs", "bot", "quizgen", "convert_docs_to_okf"]
        if any(kw in query_lower for kw in ["threshold", "config", "parameter", "setting", "yaml", "docker"]):
            return ["freqtrade-karakana-deployment", "freqtrade-karakana-quickstart", "docker-compose", "freqtrade-karakana-thresholds", "strategies", "Strategy322sgo"]
        if any(kw in query_lower for kw in ["workflow", "pipeline", "train", "inference", "process", "steps", "flow", "karakana"]):
            return ["rdql-karakana-freqtrade-workflow", "freqtrade-karakana-deployment", "freqtrade-karakana-quickstart", "quizgen", "convert_docs_to_okf"]
        
        # LLM classification for ambiguous queries
        prompt = ChatPromptTemplate.from_template(CLASSIFIER_PROMPT)
        chain = prompt | llm | StrOutputParser()
        category = await chain.ainvoke({"query": query})
        return INTENT_TO_BUNDLES.get(category.strip().upper(), DEFAULT_BUNDLES)
    except Exception:
        return DEFAULT_BUNDLES

# ─── Metadata Filter Builder ───────────────────────────────────────────
def build_metadata_filter(bundles: List[str], type_filter: Optional[str] = None, tag_filter: Optional[str] = None) -> Dict[str, Any]:
    """Build ChromaDB metadata filter."""
    filter_dict = {}
    
    if bundles:
        filter_dict["bundle"] = {"$in": bundles}
    
    if type_filter:
        filter_dict["type"] = type_filter
    
    if tag_filter:
        filter_dict["tags"] = {"$contains": tag_filter}
    
    return filter_dict if filter_dict else None

# ─── Retrieval ─────────────────────────────────────────────────────────
async def retrieve_context(query: str, bundles: Optional[List[str]] = None, 
                          type_filter: Optional[str] = None, 
                          tag_filter: Optional[str] = None) -> List[Document]:
    """Retrieve relevant chunks with metadata filtering."""
    if bundles is None:
        bundles = await classify_query(query)
    
    metadata_filter = build_metadata_filter(bundles, type_filter, tag_filter)
    
    if metadata_filter:
        results = vector_store.similarity_search_with_score(
            query, k=RETRIEVER_TOP_K, filter=metadata_filter
        )
    else:
        results = vector_store.similarity_search_with_score(query, k=RETRIEVER_TOP_K)
    
    # Deduplicate by concept_id (keep highest score)
    seen = {}
    for doc, score in results:
        concept_id = doc.metadata.get("concept_id", "")
        if concept_id not in seen or score < seen[concept_id][1]:
            seen[concept_id] = (doc, score)
    
    # Sort by score (lower = more similar in ChromaDB)
    sorted_docs = [doc for doc, score in sorted(seen.values(), key=lambda x: x[1])]
    
    return sorted_docs[:RERANK_TOP_K]

# ─── Prompt Template ───────────────────────────────────────────────────
RAG_PROMPT = """You are a technical expert answering questions about a software project using a curated OKF knowledge base.

Each context entry has:
- Source bundle: {bundle}
- Concept type: {type}
- Concept ID: {concept_id}
- Title: {title}
- Tags: {tags}

Rules:
1. Answer ONLY from the provided context. Do not use external knowledge.
2. Cite sources inline like [Source: {bundle}/{concept_id}] after each claim.
3. If context is irrelevant or missing, say: "I cannot find that in my project files."
4. If context partially answers, give what you have and note gaps.
5. Be concise. Prefer code-level specifics over generalities.
6. For code questions, include signatures, parameters, and return types when available.

--- CONTEXT ---
{context}
----------------

Human: {question}"""

def format_context(docs: List[Document]) -> str:
    """Format retrieved documents for prompt."""
    if not docs:
        return "No relevant context found."
    
    lines = []
    for i, doc in enumerate(docs):
        meta = doc.metadata
        bundle = meta.get("bundle", "unknown")
        concept_id = meta.get("concept_id", "unknown")
        ctype = meta.get("type", "Unknown")
        title = meta.get("title", "Untitled")
        tags = meta.get("tags", [])
        
        lines.append(f"[Context {i+1}]")
        lines.append(f"Bundle: {bundle}")
        lines.append(f"Type: {ctype}")
        lines.append(f"Concept ID: {concept_id}")
        lines.append(f"Title: {title}")
        lines.append(f"Tags: {', '.join(tags) if tags else 'none'}")
        lines.append(f"Content:\n{doc.page_content[:1500]}")
        lines.append("---")
    
    return "\n".join(lines)

# ─── Chainlit Handlers ─────────────────────────────────────────────────
@cl.on_chat_start
async def start():
    await cl.Message(
        content=f"""# 🧠 OKF Knowledge Assistant

Welcome! I can answer questions about this project using **4 OKF knowledge bundles**:

| Bundle | Concepts | Focus |
|--------|----------|-------|
| **Code Bundle** | 10 | AST from `src/` (classes, functions, modules) |
| **Scripts Bundle** | 18 | AST from `scripts/` (quizgen, converters, pipeline) |
| **Strategies Bundle** | 45 | Strategy322sgo implementation (entry/exit/risk) |
| **Docs Bundle** | 7 | Specs, deployment, workflows, quickstarts, configs |

**Try asking:**
- "How does `populate_entry_trend` work in Strategy322sgo?"
- "What is the FREQTRADE_STRATEGY_SPEC about?"
- "Docker compose configuration for freqtrade karakana"
- "Show me the NVIDIAEmbeddings class signature"
- "How do I deploy this strategy?"

**Features:**
- 🔍 Metadata filtering (type, bundle, tags)
- 🧭 Auto-routing to relevant bundles
- 📎 Citations with concept IDs
- ⚡ Sub-100ms `okf lookup` for agents

*Powered by OKF v0.2 + ChromaDB + Ollama ({LLM_MODEL})*""",
    ).send()

@cl.on_message
async def main(message: cl.Message):
    query = message.content.strip()
    
    # Parse optional filters from message
    # Format: "query --type Function --bundle strategies_bundle --tag karakana"
    parts = query.split(" --")
    clean_query = parts[0].strip()
    
    type_filter = None
    bundle_filter = None
    tag_filter = None
    
    for part in parts[1:]:
        if part.startswith("type "):
            type_filter = part[5:].strip()
        elif part.startswith("bundle "):
            bundle_filter = part[7:].strip()
        elif part.startswith("tag "):
            tag_filter = part[4:].strip()
    
    bundles = [bundle_filter] if bundle_filter else None
    
    # Show thinking
    thinking = cl.Message(content=f"🔍 Searching {bundles or 'all bundles'}...")
    await thinking.send()
    
    # Retrieve
    docs = await retrieve_context(clean_query, bundles, type_filter, tag_filter)
    
    # Update thinking message
    await thinking.remove()
    
    if not docs:
        await cl.Message(content="I cannot find that in my project files.").send()
        return
    
    # Show retrieval info
    sources = []
    for doc in docs:
        meta = doc.metadata
        sources.append(f"`{meta.get('bundle')}/{meta.get('concept_id')}` ({meta.get('type')})")
    
    sources_msg = cl.Message(content=f"**Sources:** {' | '.join(sources)}")
    await sources_msg.send()
    
    # Format context
    context = format_context(docs)
    
    # Stream answer
    prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
    chain = prompt | llm | StrOutputParser()
    
    msg = cl.Message(content="")
    await msg.send()
    
    async for chunk in chain.astream({
        "context": context,
        "question": clean_query,
        "bundle": docs[0].metadata.get("bundle", "unknown"),
        "type": docs[0].metadata.get("type", "Unknown"),
        "concept_id": docs[0].metadata.get("concept_id", "unknown"),
        "title": docs[0].metadata.get("title", "Untitled"),
        "tags": ", ".join(docs[0].metadata.get("tags", [])),
    }):
        await msg.stream_token(chunk)
    
    await msg.update()

@cl.action_callback("okf_lookup")
async def on_lookup(action: cl.Action):
    """Handle 'Open in Editor' / 'Show Callers' actions."""
    concept_id = action.payload.get("concept_id")
    bundle = action.payload.get("bundle")
    
    # This would integrate with `okf lookup` CLI or MCP tool
    await cl.Message(content=f"`okf lookup --bundle ./docs/okfs/{bundle} {concept_id}`").send()

# ─── Utility Commands ──────────────────────────────────────────────────
@cl.step(type="tool")
async def run_okf_lookup(concept: str, bundle: str = "code_bundle") -> str:
    """Run okf lookup command and return formatted result."""
    import subprocess
    try:
        result = subprocess.run(
            [".venv/bin/okf", "lookup", "--bundle", f"./docs/okfs/{bundle}", concept],
            capture_output=True, text=True, timeout=10, cwd="/Users/nickrotich/Desktop/portfolio/projects/python/askode"
        )
        return result.stdout or result.stderr
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    # For direct testing
    import asyncio
    
    async def test():
        query = "How does populate_entry_trend work?"
        docs = await retrieve_context(query)
        print(f"Query: {query}")
        print(f"Retrieved {len(docs)} docs:")
        for d in docs:
            print(f"  {d.metadata.get('bundle')}/{d.metadata.get('concept_id')} ({d.metadata.get('type')})")
    
    asyncio.run(test())