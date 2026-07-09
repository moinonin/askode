# Karakana Local Context Engine 🤖📚

An adaptive, configurable Retrieval-Augmented Generation (RAG) codebase designed to ingest localized engineering documentation (`.md`) and code layers (`.py`), synthesize them into robust Question-Answer maps, and serve them via a local Semantic Vector Knowledge Base.

Built using **LangChain Expression Language (LCEL)**, **ChromaDB**, and **Chainlit**, it is fully parameterized to toggle seamlessly between high-performance local inference instances (such as a native `mistral-nemo:12b` node) or cloud infrastructure fabrics.

---

## 🏗️ Architecture Blueprint

1. **Pass 1 - Macro Ingestion**: `scripts/quizgen.py` reads entire documents from the target file system and instructs a Language Model to compile comprehensive, high-level summary arrays outlining general workflows and systems layouts.
2. **Pass 2 - Granular Logic Split**: Documents are broken down via structural, overlapping text splitters to derive targeted questions detailing syntax edge-cases, specific configuration keys, and functional variables.
3. **Serving Layer - Semantic Vector Search**: `src/bot.py` indexes the generated dataset into an in-memory Chroma Vector Database using context embedding logic. When a human questions the layout, nearest-neighbor matching finds the exact conceptual fragments and structures a safe response through the LLM.

---

## 🛠️ Quickstart Runbook (On Clean Git Clone)

Follow this execution loop immediately after cloning the repository workspace to initialize your system.

### 1. Prepare Your Environment
Create an `.env` file in the root of the project to customize the engine limits. If your environment already exports these variables, these configurations will serve as an automatic fallback:

```ini
# --- TARGET CONFIGURATION ---
DOCS_DIR=./docs

# --- RUNTIME CORE CONFIGURATION ---
LLM_PROVIDER=local
LLM_MODEL=mistral-nemo:12b
EMBEDDING_MODEL=mistral-nemo:12b
LLM_BASE_URL=http://localhost:11434/v1
LLM_API_KEY=local-no-key-needed

# --- PERFORMANCE TUNING SEEDS ---
LLM_TEMPERATURE=0.2
GLOBAL_QUESTIONS_PER_FILE=3
CODE_QUESTIONS_PER_CHUNK=2
CHUNKING_SIZE=1500
CHUNKING_OVERLAP=150
RETRIEVER_TOP_K=4
```

### 2. Execute the Automated Pipeline

```bash
# Step A: Install the package landscape
make setup

# Step B: Compile your code mappings (One-off generation task)
make generate

# Step C: Boot the interactive interface agent
make run
```

---

## ⚙️ Makefile Control Center Reference

| Command | Action |
| :--- | :--- |
| `make setup` | Upgrades core Python package wrappers and pulls dependencies mapped via `requirements.txt`. |
| `make generate` | Runs the dual-pass system mapping parser loop. Overwrites `qa_pairs.jsonl`. |
| `make run` | Instantiates a stateful context router and boots the UI dashboard room via port `8000`. |
| `make clean` | Flushes structural database footprints, dynamic file arrays, and compiler artifacts. |

---

## 🔄 Transitioning to Cloud Infrastructures

To scale your deployment model directly into production using remote server nodes (like OpenAI's cluster models) rather than your running machine assets, update your environment properties inside `.env`:

```ini
LLM_PROVIDER=cloud
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://openai.com
LLM_API_KEY=sk-proj-YOUR_SECRET_CLOUD_TOKEN_HERE
```
No manual script manipulations, adjustments, or framework rewrites are required.