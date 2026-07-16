# Karakana Local Context Engine 🤖📚

**Multi-Provider RAG System** — Ingest engineering docs and code into a queryable knowledge base served via Chainlit chat UI. Supports three inference backends: Local (Ollama), NVIDIA API, and OpenAI Cloud.

---

## 🎯 What This Does

1. **Ingest**: Scans `./docs` for `.md` and `.py` files
2. **Generate Q&A**: Two-pass LLM pipeline creates question-answer pairs:
   - Pass 1 (Macro): 3 high-level architectural Q&A per file
   - Pass 2 (Micro): 2 detailed code-level Q&A per 1500-char chunk
3. **Index**: Embeds Q&A pairs into ChromaDB vector store
4. **Serve**: Chainlit chat UI at `http://localhost:3000` with streaming responses and source citations

---

## 🏗️ Architecture

```
docs/*.md, *.py
       │
       ▼
┌─────────────────────────────────────┐
│  Dual-Pass Q&A Generation           │
│  (configurable model provider)      │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  ChromaDB Vector Store              │
│  (persistent .chroma/)              │
└─────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────┐
│  Chainlit Chat UI (port 3000)       │
│  RAG: Retriever → Prompt → LLM      │
│  Streaming + Source Citations       │
└─────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
make setup
```

### 2. Choose Your Provider

| Provider | Command | Requirements |
|----------|---------|--------------|
| **Local (Ollama)** | `make run-local` | `ollama serve` + `ollama pull mistral-nemo:12b nomic-embed-text` |
| **NVIDIA API** | `make run-nvidia` | `export NVIDIA_API_KEY=...` |
| **OpenAI Cloud** | `make run-cloud` | `export OPENAI_API_KEY=...` |

### 3. Generate Knowledge Base
```bash
# First run auto-generates, or run explicitly:
make generate
```

### 4. Chat
Open `http://localhost:3000` and ask questions about your codebase.

---

## ⚙️ Configuration

All settings via `.env` (or Makefile overrides):

```ini
# Provider: local | nvidia | cloud
LLM_PROVIDER=nvidia

# Model selection (auto-defaults per provider)
LLM_MODEL=nvidia/nemotron-3-ultra-550b-a55b
EMBEDDING_MODEL=nvidia/nv-embed-v1

# Base URLs (auto-defaults)
LLM_BASE_URL=https://integrate.api.nvidia.com/v1

# API Keys
NVIDIA_API_KEY=your-key
# OPENAI_API_KEY=your-key  (for cloud)
```

**Makefile Overrides:**
```bash
make run PROVIDER=nvidia MODEL=nvidia/llama-3.1-nemotron-70b-instruct
make generate PROVIDER=local MODEL=llama3.1:8b
```

---

## 📁 Project Structure

```
askode/
├── Makefile              # Provider-aware orchestration
├── .env                  # Runtime config (not in git)
├── src/
│   └── bot.py           # Chainlit RAG server
├── scripts/
│   └── quizgen.py       # Dual-pass Q&A generator
├── docs/                # Your engineering docs go here
├── qa_pairs.jsonl       # Generated Q&A (gitignored)
├── .chroma/             # ChromaDB vector store (gitignored)
└── chat_history.txt     # Chat logs (gitignored)
```

---

## 🔧 Make Targets

### Core Pipeline
| Target | Description |
|--------|-------------|
| `make setup` | Install Python deps |
| `make generate` | Run dual-pass Q&A generation |
| `make run-local` | Run with Ollama (local) |
| `make run-nvidia` | Run with NVIDIA API |
| `make run-cloud` | Run with OpenAI |
| `make clean` | Remove generated artifacts |

### OKF Knowledge Bundles (AST + Docs)
| Target | Description |
|--------|-------------|
| `make okf-generate-all` | Generate all 4 bundles (code, scripts, strategies, docs) |
| `make okf-generate-code` | AST-extract `src/` → `code_bundle` |
| `make okf-generate-scripts` | AST-extract `scripts/` → `scripts_bundle` |
| `make okf-generate-strategies` | AST-extract `docs/strategies/` → `strategies_bundle` |
| `make okf-generate-docs` | Convert `docs/*.md` → `docs_bundle` |
| `make okf-update-all` | Fast incremental update all bundles |
| `make okf-update-code` | Update `code_bundle` from `src/` |
| `make okf-update-scripts` | Update `scripts_bundle` from `scripts/` |
| `make okf-update-strategies` | Update `strategies_bundle` from `docs/strategies/` |
| `make okf-update-docs` | Update `docs_bundle` from `docs/` |
| `make okf-watch-code` | Watch `src/` for continuous updates |
| `make okf-watch-scripts` | Watch `scripts/` for continuous updates |
| `make okf-watch-strategies` | Watch `docs/strategies/` for continuous updates |
| `make okf-watch-docs` | Watch `docs/` for continuous updates |
| `make okf-chunk` | Semantic chunking (Phase 6) |
| `make okf-embed` | Generate embeddings (Phase 7) |
| `make okf-index` | Index to ChromaDB (Phase 8) |
| `make okf-pipeline` | Run chunk → embed → index |
| `make okf-link` | Add cross-bundle links (docs ↔ code) |
| `make okf-viz-all` | Visualize all 4 bundles as HTML |
| `make okf-viz-code` | Visualize `code_bundle` |
| `make okf-viz-scripts` | Visualize `scripts_bundle` |
| `make okf-viz-strategies` | Visualize `strategies_bundle` |
| `make okf-viz-docs` | Visualize `docs_bundle` |
| `make okf-dashboard` | Live dashboard for `code_bundle` (port 8700) |
| `make okf-install-agents` | Install OKF skills for Cursor, Copilot, Windsurf, Cline, OpenCode |
| `make okf-lookup CONCEPT=<name> BUNDLE=<bundle>` | CLI lookup by concept ID |

### OKF Chat (ChromaDB RAG)
| Target | Description |
|--------|-------------|
| `make okf-chat-local` | Chainlit chat with local embeddings (port 3000) |
| `make okf-chat-nvidia` | Chainlit chat with NVIDIA embeddings |
| `make okf-chat-cloud` | Chainlit chat with OpenAI embeddings |

### Evaluation
| Target | Description |
|--------|-------------|
| `make okf-eval` | Run retrieval evaluation (concept accuracy + cross-bundle) |

---

## 📋 Requirements

- Python 3.11+
- For local: Ollama 0.31+ with `mistral-nemo:12b` and `nomic-embed-text`
- For NVIDIA: API key from [build.nvidia.com](https://build.nvidia.com)
- For OpenAI: API key from [platform.openai.com](https://platform.openai.com)

---

## 📝 Generated Q&A Format

Each entry in `qa_pairs.jsonl`:
```json
{
  "id": "qa_42",
  "source": "architecture.md",
  "question": "How does the deployment architecture enforce separation between the Freqtrade engine and user-specific strategy artifacts?",
  "answer": "The deployment keeps all user-specific artifacts (strategies, SQLite DBs, configs, policies, logs, reports) outside the container under a host `user_data/` directory..."
}
```

---

## 🎯 Use Cases

- **Onboarding**: New engineers query the codebase via natural language
- **Architecture Reviews**: Quick lookup of design decisions and data flows
- **Debugging**: Trace config keys, error handling, and invariants
- **Knowledge Retention**: Preserve tribal knowledge in queryable form