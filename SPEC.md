# Karakana Local Context Engine — Specification

**Version:** 1.0  
**Status:** Implemented (dual-pass ingestion + RAG serving)  
**Last Updated:** 2026-07-10

---

## 1. System Overview

### 1.1 Purpose
Transform a directory of engineering documentation (`.md`) and source code (`.py`) into a queryable knowledge base served via a conversational chat interface. The system performs **two-pass LLM-driven Q&A generation** followed by **semantic vector retrieval** and **streaming LLM responses**.

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DOCS DIRECTORY (./docs)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │
│  │  README.md  │  │  ARCH.md    │  │  module.py  │  │  config.py │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬─────┘  │
└─────────┼────────────────┼────────────────┼───────────────┼────────┘
          │                │                │               │
          ▼                ▼                ▼               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PASS 1: MACRO INGESTION                           │
│  • Load full documents (truncated to 12,000 chars)                  │
│  • Prompt: "expert Technical Architect" → high-level overview Q&A   │
│  • Output: GLOBAL_QUESTIONS_PER_FILE (default 3) Q&A per file       │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    PASS 2: GRANULAR LOGIC SPLIT                      │
│  • RecursiveCharacterTextSplitter (chunk_size=1500, overlap=150)    │
│  • Prompt: "senior Software Engineer" → code logic Q&A              │
│  • Output: CODE_QUESTIONS_PER_CHUNK (default 2) Q&A per chunk       │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    QA_PAIRS.JSONL (persisted artifact)               │
│  {id, source, question, answer}  ×  N records                        │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SERVING LAYER (src/bot.py)                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │ Load JSONL      │  │ Embed + Index   │  │ Chainlit Chat UI    │  │
│  │ → Documents     │──│ → ChromaDB      │──│ (port 8000)         │  │
│  └─────────────────┘  └─────────────────┘  └──────────┬──────────┘  │
│                                                        │             │
│  ┌────────────────────────────────────────────────────┘             │
│  │ RAG Chain: Retriever(top-k=4) → Prompt → LLM → Stream            │
│  └──────────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Specifications

### 2.1 Pass 1: Macro Ingestion (`scripts/quizgen.py` lines 103–112)

| Parameter | Value | Config |
|-----------|-------|--------|
| Input | Full document content (max 12,000 chars) | — |
| Prompt Template | `global_prompt` (Technical Architect persona) | — |
| Questions per file | 3 | `GLOBAL_QUESTIONS_PER_FILE` |
| LLM | `ChatOpenAI` (Ollama or OpenAI) | `LLM_MODEL`, `LLM_BASE_URL`, `LLM_API_KEY` |
| Temperature | 0.2 | `LLM_TEMPERATURE` |
| Output Parser | `JsonOutputParser` | — |
| Rate Limit | 0.2s sleep between files | — |

**Prompt Contract:**
```
You are an expert Technical Architect documenting a software system.
Generate {num_questions} high-level conceptual question-answer pairs that explain:
- The document's purpose and role in the system
- Key architectural decisions and trade-offs
- Important configurations, interfaces, or data flows
- Non-obvious assumptions or invariants

Each question must be answerable from the document alone. 
Avoid generic questions (e.g., 'What is this file?'). 
Prefer specific, referenceable insights.

Document: {source}
Content:
{text}

{format_instructions}
Return ONLY raw JSON array. No backticks, no markdown.
```

**Expected JSON Output Format:**
```json
[
  {"question": "...", "answer": "..."},
  {"question": "...", "answer": "..."}
]
```
(Also accepts `q`/`a` keys for robustness)

---

### 2.2 Pass 2: Granular Logic Split (`scripts/quizgen.py` lines 114–125)

| Parameter | Value | Config |
|-----------|-------|--------|
| Splitter | `RecursiveCharacterTextSplitter` | — |
| Chunk Size | 1500 chars | `CHUNKING_SIZE` |
| Chunk Overlap | 150 chars | `CHUNKING_OVERLAP` |
| Prompt Template | `code_prompt` (Senior Software Engineer persona) | — |
| Questions per chunk | 2 | `CODE_QUESTIONS_PER_CHUNK` |
| LLM | Same as Pass 1 | — |
| Temperature | 0.2 | `LLM_TEMPERATURE` |
| Rate Limit | 0.2s sleep between chunks | — |

**Prompt Contract:**
```
You are a Senior Software Engineer creating a technical Q&A reference for this codebase.
Generate {num_questions} precise question-answer pairs covering:
- Specific function/class behavior, parameters, return values
- Edge cases, error handling, invariants
- Configuration keys, environment variables, constants
- Non-obvious logic, algorithms, or side effects
- Dependencies and coupling

Each Q&A must be grounded in the snippet. 
If the snippet is too generic (boilerplate, imports only), return empty array [].
Do not hallucinate beyond the provided text.

Source file: {source}
Snippet:
{text}

{format_instructions}
Return ONLY raw JSON array. No backticks, no markdown.
```

---

### 2.3 Q&A Aggregation & Persistence (`scripts/quizgen.py` lines 90–101, 127–131)

| Field | Description |
|-------|-------------|
| `id` | Auto-increment: `qa_0`, `qa_1`, ... |
| `source` | Original filename (from `Document.metadata["source"]`) |
| `question` | Extracted from `question` or `q` key |
| `answer` | Extracted from `answer` or `a` key |

**Output File:** `qa_pairs.jsonl` (JSON Lines, UTF-8)

---

### 2.4 Serving Layer — Embedding & Indexing (`src/bot.py` lines 25–55)

| Component | Local Mode | Cloud Mode |
|-----------|------------|------------|
| Embeddings | `OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=ollama_root)` | `OpenAIEmbeddings(model="text-embedding-3-small")` |
| Vector Store | `Chroma.from_documents()` (persists to `.chroma/`) | Same |
| Retriever | `vector_store.as_retriever(search_kwargs={"k": RETRIEVER_TOP_K})` | Same |

**Config:**
- `EMBEDDING_MODEL` default: `nomic-embed-text`
- `RETRIEVER_TOP_K` default: `4`
- `LLM_BASE_URL` default: `http://localhost:11434/v1` (Ollama)
- Ollama base URL derived by stripping `/v1` from `LLM_BASE_URL`

---

### 2.5 Serving Layer — RAG Chain (`src/bot.py` lines 57–77)

**Prompt Template:**
```
System: You are a technical expert answering questions about a software project using a curated Q&A knowledge base.
Each context entry has a source file (shown as 'Source: filename'). Use this to ground your answer.

Rules:
1. Answer ONLY from the provided context. Do not use external knowledge.
2. Cite sources inline like [Source: filename] after each claim.
3. If context is irrelevant or missing, say: 'I cannot find that in my project files.'
4. If context partially answers, give what you have and note gaps.
5. Be concise. Prefer code-level specifics over generalities.

--- CONTEXT ---
{context}
----------------

Human: {question}
```

**Chain:** `prompt_template | local_llm | StrOutputParser()`

**LLM Config:**
- `ChatOpenAI(model=LLM_MODEL, base_url=LLM_BASE_URL, api_key=LLM_API_KEY, temperature=LLM_TEMPERATURE)`
- `LLM_TEMPERATURE` default: `0.3` (serving) vs `0.2` (generation)

---

### 2.6 Chainlit Chat Interface (`src/bot.py` lines 73–99)

| Feature | Implementation |
|---------|----------------|
| Message Handler | `@cl.on_message` async `main(message: cl.Message)` |
| Retrieval | `retriever.invoke(user_query)` (sync) |
| Streaming | `rag_chain.astream({"context": context, "question": user_query})` |
| Token Streaming | `msg.stream_token(chunk)` per chunk |
| History Logging | Appends to `chat_history.txt` with `--- Chat Turn ---` delimiters |

---

## 3. Configuration Reference

### 3.1 Environment Variables (`.env`)

| Variable | Default | Pass 1 | Pass 2 | Serving | Description |
|----------|---------|--------|--------|---------|-------------|
| `DOCS_DIR` | `./docs` | ✓ | ✓ | — | Source directory for ingestion |
| `LLM_PROVIDER` | `local` | ✓ | ✓ | ✓ | `local` (Ollama) or `cloud` (OpenAI) |
| `LLM_MODEL` | `mistral-nemo:12b` | ✓ | ✓ | ✓ | Generation/chat model name |
| `EMBEDDING_MODEL` | `nomic-embed-text` | — | — | ✓ | Embedding model (local mode) |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | ✓ | ✓ | ✓ | Ollama/OpenAI base URL |
| `LLM_API_KEY` | `local-no-key-needed` | ✓ | ✓ | ✓ | API key (unused for local) |
| `LLM_TEMPERATURE` | `0.2` (gen) / `0.3` (serve) | ✓ | ✓ | ✓ | Generation temperature |
| `GLOBAL_QUESTIONS_PER_FILE` | `3` | ✓ | — | — | Pass 1 questions per file |
| `CODE_QUESTIONS_PER_CHUNK` | `2` | — | ✓ | — | Pass 2 questions per chunk |
| `CHUNKING_SIZE` | `1500` | — | ✓ | — | Text splitter chunk size |
| `CHUNKING_OVERLAP` | `150` | — | ✓ | — | Text splitter overlap |
| `RETRIEVER_TOP_K` | `4` | — | — | ✓ | Retriever top-k results |

### 3.2 Makefile Targets

| Target | Command | Description |
|--------|---------|-------------|
| `make setup` | `pip install --upgrade pip && pip install -r requirements.txt` | Install dependencies |
| `make generate` | `python scripts/quizgen.py` | Run dual-pass Q&A generation (creates `qa_pairs.jsonl`) |
| `make run` | `chainlit run src/bot.py -w` | Launch Chainlit UI (auto-runs generate if missing) |
| `make clean` | `rm -f qa_pairs.jsonl && rm -rf .chroma && find . -name __pycache__ -exec rm -rf {} +` | Clean generated artifacts |

---

## 4. Data Flow Summary

### 4.1 Generation Phase (`make generate`)

```
Input:  ./docs/*.md, ./docs/*.py
         │
         ▼
Load → Document objects (source metadata preserved)
         │
         ├─► PASS 1: Full doc (≤12k chars) → global_prompt → LLM → 3 Q&A/file
         │
         ├─► PASS 2: Split → chunks → code_prompt → LLM → 2 Q&A/chunk
         │
         ▼
Aggregate → Deduplicate by (question, answer) → qa_pairs.jsonl
```

### 4.2 Serving Phase (`make run`)

```
Input:  User query (chat)
         │
         ▼
Retriever(query) → top-k=4 Documents from ChromaDB
         │
         ▼
Format context: "Question: ...\nAnswer: ...\nSource: ..." joined by \n\n
         │
         ▼
Prompt Template + Context + Query → LLM (streaming)
         │
         ▼
Chainlit UI: token-by-token stream → chat_history.txt log
```

---

## 5. Assumptions & Constraints

| Category | Detail |
|----------|--------|
| **File Types** | Only `.md` and `.py` files are ingested (hardcoded in `load_project_files`) |
| **Doc Truncation** | Pass 1 truncates to 12,000 chars — large files lose tail content |
| **Chunking** | RecursiveCharacterTextSplitter — no semantic/structural awareness (e.g., function boundaries) |
| **Embeddings** | Single embedding model for all content — no hybrid lexical+semantic |
| **Retrieval** | Top-k only — no reranking, no query expansion, no metadata filtering |
| **Persistence** | ChromaDB persists to `.chroma/` — survives restarts; `qa_pairs.jsonl` is source of truth |
| **Concurrency** | Single-user Chainlit session — no multi-tenant isolation |
| **LLM Provider** | Binary switch: local (Ollama) OR cloud (OpenAI) — no multi-provider routing |
| **Rate Limiting** | Fixed 0.2s sleep between LLM calls — no exponential backoff or retry logic |
| **Error Handling** | Print-and-continue on LLM failures — no dead-letter queue or retry |

---

## 6. Deployment Checklist

### 6.1 Local Development (Ollama)

```bash
# 1. Start Ollama
ollama serve

# 2. Pull required models
ollama pull mistral-nemo:12b
ollama pull nomic-embed-text

# 3. Configure .env (see README.md for template)
cp .env.example .env  # or create manually

# 4. Run pipeline
make setup
make generate
make run
```

### 6.2 Cloud Deployment (OpenAI)

```bash
# Update .env
LLM_PROVIDER=cloud
LLM_MODEL=gpt-4o-mini
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small  # ignored in cloud mode (hardcoded)
```

### 6.3 Production Considerations

| Area | Recommendation |
|------|----------------|
| **Vector Store** | Migrate to persistent ChromaDB server or pgvector for multi-instance |
| **Auth** | Add Chainlit OAuth (GitHub, Google) or custom auth middleware |
| **Observability** | Integrate LangSmith (already in deps) for tracing |
| **Scaling** | Run Chainlit behind load balancer with sticky sessions |
| **Backup** | Version `qa_pairs.jsonl` and `.chroma/` in git/artifact store |
| **Evaluation** | Add RAGAS or custom eval harness for retrieval/generation quality |

---

## 7. Extension Points (Future Work)

| Extension | Location | Effort |
|-----------|----------|--------|
| **Pass 3: Dependency Graph** | New script → `scripts/graphgen.py` | Medium |
| **Hybrid Retrieval (BM25 + Vector)** | `src/bot.py` retriever initialization | Medium |
| **Metadata Filtering (by file, type, tags)** | ChromaDB `where` clauses + Document metadata | Low |
| **Query Rewriting/Expansion** | Pre-retrieval LLM call in `main()` | Low |
| **Reranking (Cross-Encoder)** | Post-retrieval step before prompt | Medium |
| **Multi-Provider Routing** | Abstract `LLMProvider` class | Medium |
| **Incremental Updates** | Watch `docs/` → re-index changed files only | High |
| **Evaluation Harness** | `tests/eval_rag.py` with golden Q&A | Medium |

---

## 8. File Manifest

```
askode/
├── AGENTS.md              # Agent instructions (this project's context)
├── SPEC.md                # This file — system specification
├── SPECS.txt              # Vision document (AI-native repository concept)
├── SPRINTS.md             # Sprint tracking (empty)
├── README.md              # User-facing quickstart & architecture
├── Makefile               # Pipeline orchestration
├── requirements.txt       # Python dependencies (224 packages)
├── .env                   # Runtime config (not in git)
├── scripts/
│   └── quizgen.py         # Dual-pass Q&A generation (131 lines)
├── src/
│   └── bot.py             # Chainlit RAG chat server (100 lines)
├── docs/                  # User content goes here (created by make generate)
├── qa_pairs.jsonl         # Generated artifact (gitignored)
├── .chroma/               # ChromaDB persistence (gitignored)
├── chat_history.txt       # Chat logs (gitignored)
└── .venv/                 # Virtual environment (gitignored)
```

---

## 9. Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-07-10 | Initial spec matching implemented codebase |

---

*This SPEC.md is derived from the actual implementation in `scripts/quizgen.py` and `src/bot.py`. It should be updated whenever the code changes.*