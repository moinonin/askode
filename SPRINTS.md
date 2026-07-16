# SPRINTS.md — Karakana Local Context Engine (OKF-Enhanced)

---

## Sprint 0 — Foundation (Completed)

**Goal**: Multi-provider RAG system with local, NVIDIA, and OpenAI backends

| Task | Status |
|------|--------|
| Local Ollama provider (mistral-nemo:12b + nomic-embed-text) | ✅ Done |
| NVIDIA API provider (nemotron-3-ultra-550b + nv-embed-v1) | ✅ Done |
| OpenAI Cloud provider (gpt-4o-mini + text-embedding-3-small) | ✅ Done |
| Dual-pass Q&A generation (macro + micro) | ✅ Done |
| Chainlit chat UI with streaming + citations | ✅ Done |
| Makefile provider orchestration | ✅ Done |
| Ollama embeddings fix (bypass /tokenize endpoint) | ✅ Done |
| README with precise 3-provider docs | ✅ Done |
| requirements.txt minimal cleanup (224 → 24 packages) | ✅ Done |

---

## Sprint 0.5 — OKF Knowledge Layer (Completed — **New**)

**Goal**: Build structured, agent-ready knowledge bundles from code + docs using OKF v0.2

| Task | Status | Artifacts |
|------|--------|-----------|
| Install okf-generator v0.1.49 | ✅ Done | `.venv/bin/okf` |
| Generate code bundle from `src/` (AST) | ✅ Done | `docs/okfs/code_bundle/` (10 concepts) |
| Generate scripts bundle from `scripts/` | ✅ Done | `docs/okfs/scripts_bundle/` (18 concepts) |
| Generate strategies bundle from `docs/strategies/` | ✅ Done | `docs/okfs/strategies_bundle/` (45 concepts) |
| Convert docs/*.md → OKF bundle (custom script) | ✅ Done | `docs/okfs/docs_bundle/` (7 concepts) |
| Semantic chunking (Phase 6) — 445 chunks | ✅ Done | `docs/okfs/chunks/*.jsonl` |
| Embeddings with inherited OKF metadata (Phase 7) | ✅ Done | `docs/okfs/embeddings/*.jsonl` (768-dim nomic-embed-text) |
| ChromaDB indexing with metadata filtering (Phase 8) | ✅ Done | `docs/okfs/chromadb/` (collection: `okf_knowledge`) |
| Cross-bundle links (14 bidirectional) | ✅ Done | `## Cross-Bundle Links` in OKF files |
| MCP server registration (4 bundles) | ✅ Done | `opencode.json` |
| Agent integration (Claude, OpenCode, Copilot, Cursor, Windsurf, Cline) | ✅ Done | `.cursorrules`, `.clinerules`, etc. |

**OKF Bundles Created:**
```
docs/okfs/
├── code_bundle/           # 10 concepts: Module, Class, Function from src/bot.py
├── scripts_bundle/        # 18 concepts: Module, Class, Function from scripts/
├── strategies_bundle/     # 45 concepts: Strategy322sgo class + 43 methods
├── docs_bundle/           # 7 concepts: Spec, DeploymentGuide, Workflow, Quickstart, Config
├── chunks/                # 445 semantic chunks (JSONL per bundle)
├── embeddings/            # 445 embeddings + metadata (JSONL per bundle)
└── chromadb/              # Persistent vector store (445 vectors, full metadata)
```

**Cross-Bundle Links (14):**
| Source Bundle | Source Concept | → | Target Bundle | Target Concept | Relationship |
|---------------|----------------|---|---------------|----------------|--------------|
| docs_bundle | FREQTRADE_STRATEGY_SPEC | → | strategies_bundle | Strategy322sgo | specifies / implements |
| docs_bundle | rdql-karakana-freqtrade-workflow | → | scripts_bundle | quizgen | describes_pipeline / generates_qa_for |
| docs_bundle | rdql-karakana-freqtrade-workflow | → | scripts_bundle | convert_docs_to_okf | uses_tool / converts_docs_for |
| docs_bundle | freqtrade-karakana-deployment | → | docs_bundle | docker-compose | references_config |
| docs_bundle | freqtrade-karakana-deployment | → | docs_bundle | freqtrade-karakana-thresholds | uses_thresholds |
| docs_bundle | freqtrade-karakana-quickstart | → | docs_bundle | freqtrade-karakana-deployment | guides_to |
| docs_bundle | freqtrade-karakana-quickstart | → | strategies_bundle | Strategy322sgo | starts_strategy / implements |
| strategies_bundle | Strategy322sgo | → | docs_bundle | FREQTRADE_STRATEGY_SPEC | implements |
| strategies_bundle | Strategy322sgo/populate_entry_trend | → | docs_bundle | FREQTRADE_STRATEGY_SPEC | implements_section |
| strategies_bundle | Strategy322sgo/populate_exit_trend | → | docs_bundle | FREQTRADE_STRATEGY_SPEC | implements_section |
| strategies_bundle | Strategy322sgo/confirm_trade_entry | → | docs_bundle | freqtrade-karakana-deployment | used_in_deployment |
| scripts_bundle | quizgen | → | docs_bundle | rdql-karakana-freqtrade-workflow | generates_qa_for |
| scripts_bundle | convert_docs_to_okf | → | docs_bundle | rdql-karakana-freqtrade-workflow | converts_docs_for |
| code_bundle | bot/NVIDIAEmbeddings | → | docs_bundle | rdql-karakana-freqtrade-workflow | provides_embeddings_for |

---

## Sprint 1 — RAG Chat Interface & Incremental Updates (Week 1)

**Goal**: Interactive querying over OKF bundles + keep bundles fresh during development

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| **OKF-1** | Chainlit RAG chat over ChromaDB with metadata filters | - Query: "How does populate_entry_trend work?"<br>- Filter: `type=Function AND tags=karakana`<br>- Citations show `[Source: bundle/concept]`<br>- Uses pre-computed embeddings (no re-generation) | 3 pts |
| **OKF-2** | Makefile targets for incremental bundle updates | `make okf-update-code` → `okf update ./src ./docs/okfs/code_bundle`<br>`make okf-update-docs` → `okf update ./docs ./docs/okfs/docs_bundle`<br>`make okf-update-all` → updates all 4 bundles<br>`make okf-watch` → watchdog-based auto-regen | 2 pts |
| **OKF-3** | Cross-bundle query routing | Detect query intent → route to relevant bundle(s)<br>- "how to deploy" → docs_bundle (DeploymentGuide)<br>- "what does populate_entry_trend do" → strategies_bundle<br>- "quizgen usage" → scripts_bundle | 2 pts |
| **OKF-4** | OKF lookup command for agents | `okf lookup --bundle ./docs/okfs/code_bundle NVIDIAEmbeddings`<br>Returns structured concept card (signature, params, calls, callers)<br>Agent integration: `/lookup NAME=<ConceptName>` in OpenCode | 1 pt |

### Definition of Done
- [ ] Chainlit app runs: `make okf-chat` → queries all 4 bundles
- [ ] Metadata filters work: `filter={"type": "Function", "tags": "karakana"}`
- [ ] Incremental update < 10s for single file change
- [ ] `okf lookup` returns concept card in < 100ms

---

## Sprint 2 — Knowledge Graph Visualization (Week 1-2)

**Goal**: Interactive visual exploration of code + doc relationships

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| **OKF-5** | Generate D3.js visualizations for all bundles | `make okf-viz-code` → `docs/okfs/viz/code_viz.html`<br>`make okf-viz-docs` → `docs/okfs/viz/docs_viz.html`<br>`make okf-viz-strategies` → `docs/okfs/viz/strategies_viz.html`<br>`make okf-viz-all` → combined graph | 2 pts |
| **OKF-6** | Live dashboard with 3-panel browser | `make okf-dashboard` → FastAPI at `http://localhost:8700`<br>Panel 1: Search/filter concepts<br>Panel 2: Concept detail (signature, relationships)<br>Panel 3: Force-directed graph (click to navigate) | 3 pts |
| **OKF-7** | Cross-bundle graph edges visible | Visual links between bundles:<br>- Spec → Strategy (implements)<br>- Workflow → Scripts (generates_qa_for)<br>- Quickstart → Strategy (starts_strategy)<br>Edge types colored by relationship | 2 pts |
| **OKF-8** | Export graph to GraphML/JSON for external tools | `okf visualize --format graphml ./docs/okfs/code_bundle`<br>Importable in Gephi, Neo4j, Graphistry | 1 pt |

### Definition of Done
- [ ] 4 HTML visualizations open in browser with search + filter
- [ ] Dashboard runs on `make okf-dashboard` with live reload
- [ ] Cross-bundle edges visible and clickable
- [ ] GraphML export loads in Gephi

---

## Sprint 3 — Evaluation Harness & Quality Gates (Week 2-3)

**Goal**: Measurable retrieval/generation quality with regression prevention

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| **OKF-9** | Golden Q&A curation (50 pairs) | `eval/golden_qa.jsonl` with 50 Q/A covering:<br>- 10 Architecture (modules, data flow)<br>- 10 Strategy logic (entry/exit/risk)<br>- 10 Deployment (docker, thresholds, config)<br>- 10 Code API (signatures, params, returns)<br>- 10 Workflow (training → inference → shadow)<br>Each: question, ideal_answer, expected_concept_ids[], difficulty | 3 pts |
| **OKF-10** | RAGAS evaluation pipeline | `make okf-eval` runs:<br>- Faithfulness (answer ↔ context)<br>- Answer Relevancy (answer ↔ question)<br>- Context Precision (retrieved ↔ relevant)<br>- Context Recall (golden concepts retrieved)<br>Outputs JSON report with per-query scores | 3 pts |
| **OKF-11** | Retrieval quality baseline | Measure on golden set:<br>- Recall@4 ≥ 0.75 (golden concept in top-4)<br>- MRR ≥ 0.6<br>- Latency p95 < 500ms<br>Document baseline in `eval/baseline_report.json` | 2 pts |
| **OKF-12** | CI regression gate | GitHub Action on PR:<br>`make okf-eval` → fail if faithfulness drops >5%<br>Post PR comment with score deltas<br>Artifact upload: eval report | 2 pts |
| **OKF-13** | OKF-specific eval metrics | - Concept retrieval accuracy (exact concept_id match)<br>- Cross-bundle link traversal success rate<br>- Metadata filter precision (type/tag/bundle)<br>- Chunk-to-concept mapping correctness | 2 pts |

### Definition of Done
- [ ] `eval/golden_qa.jsonl` with 50 expert-verified Q/A
- [ ] `make okf-eval` runs RAGAS + OKF metrics in < 2 min
- [ ] Baseline recorded: recall@4, MRR, latency
- [ ] GitHub Action fails PR on regression >5%
- [ ] PR comment shows before/after scores

---

## Sprint 4 — Production Hardening & Advanced Retrieval (Week 3-4)

**Goal**: Production-ready retrieval with hybrid search, incremental updates, query routing

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| **OKF-14** | Hybrid search (BM25 + vector) | ChromaDB + BM25 (rank-bm25):<br>- Keyword queries: "populate_entry_trend" → exact match first<br>- Semantic queries: "entry logic" → vector similarity<br>- Fusion: reciprocal rank fusion (RRF) with k=60<br>- Improves exact-match recall ≥30% | 3 pts |
| **OKF-15** | Parent document retrieval | For small chunks (< 500 chars):<br>- Retrieve parent concept (full OKF document)<br>- Return parent + chunk context<br>- Improves answer completeness for fragmented concepts | 2 pts |
| **OKF-16** | Query classification & routing | LLM classifier (cheap model) detects intent:<br>- `HOW_TO` → DeploymentGuide + Quickstart<br>- `DEBUG` → Function signatures + error handling<br>- `ARCH` → Spec + Module overview<br>- `CONFIG` → Config + Thresholds<br>Routes to relevant bundles + adjusts retrieval k | 3 pts |
| **OKF-17** | Incremental indexing pipeline | `okf update --watch` + file watcher:<br>- SHA256 manifest tracks mtime + content hash<br>- Only re-parse changed files<br>- Re-link only dirty concepts<br>- Edge-diff detects cascade changes<br>- Target: < 5s for single file change | 3 pts |
| **OKF-18** | Training data export | `okf pairs ./docs/okfs/code_bundle ./train.jsonl`<br>Generates 5 pair types: codegen, qa, doc, summarize, crosslink<br>Ready for fine-tuning private SLM on project knowledge | 2 pts |

### Definition of Done
- [ ] Hybrid search improves exact-match queries ≥30% recall
- [ ] `okf update --watch` re-indexes single file change in < 5s
- [ ] Query classifier routes 90%+ correctly on golden set
- [ ] Training JSONL has ≥ 500 pairs across 5 types

---

## Sprint 5 — UX & Agent Experience Polish (Week 4)

**Goal**: Seamless developer + agent experience

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| **OKF-19** | Source preview in chat UI | Click citation → opens OKF concept card in side panel<br>Shows: signature, docstring, callers, callees, source lines<br>Chainlit action buttons: "Open in Editor", "Show Callers", "Show Callees" | 3 pts |
| **OKF-20** | Conversation persistence | SQLite session store at `~/.okf/sessions/`<br>Survives restarts, multiple sessions per project<br>`make okf-chat --session <name>` | 2 pts |
| **OKF-21** | Feedback collection (👍/👎) | Buttons on each answer → logs to `eval/feedback.jsonl`<br>Includes: query, answer, retrieved concept_ids, user rating<br>Export for RLHF / prompt iteration | 2 pts |
| **OKF-22** | Agent instruction generation | `okf install all` updates:<br>- `.cursorrules` with bundle-specific lookup patterns<br>- `.github/copilot-instructions.md` with cross-bundle examples<br>- `.clinerules` with MCP tool usage<br>Auto-generated from bundle metadata | 2 pts |
| **OKF-23** | Dark/light theme + responsive UI | Chainlit theme toggle, mobile-friendly layout | 1 pt |

### Definition of Done
- [ ] Click citation → concept card opens with full context
- [ ] Sessions persist across restarts
- [ ] Feedback logs exportable for fine-tuning
- [ ] `okf install all` generates agent configs matching current bundles

---

## Sprint 6 — Multi-Repo Federation & Automation (Week 5)

**Goal**: Scale beyond single repo, automate knowledge freshness

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| **OKF-24** | Multi-repo bundle federation | `okf generate --federate ./repo1 ./repo2 ./repo3`<br>Creates `federated_bundle/` with cross-repo links<br>Resolves imports across repos (Git submodules or remote URLs) | 5 pts |
| **OKF-25** | GitHub webhook auto-update | GitHub Action on push:<br>- `okf update` on changed files<br>- Commits updated bundle to `okf-bundle` branch<br>- Opens PR with diff summary (`okf diff --impact`)<br>- Auto-merges if tests pass | 3 pts |
| **OKF-26** | Scheduled bundle refresh | Cron job (daily):<br>- `okf update --force` all bundles<br>- Re-embeds if model changed<br>- Runs eval, alerts on regression<br>- Updates dashboard cache | 2 pts |
| **OKF-27** | Bundle versioning & release | Semantic versioning for bundles:<br>- `okf bundle version bump --minor`<br>- Tags: `okf-bundle/v1.2.0`<br>- Changelog auto-generated from `log.md`<br>- Release artifacts: bundle.tar.gz, graphml, pairs.jsonl | 2 pts |

### Definition of Done
- [ ] Federated bundle links across 3+ repos
- [ ] GitHub Action auto-updates bundles on push
- [ ] Daily cron refreshes + eval + alerting
- [ ] Versioned releases with changelogs

---

## Sprint 7 — Remote Repository Knowledge Ingestion (Week 6)

**Goal**: Ingest knowledge directly from remote Git repositories without local checkout

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| **OKF-28** | GitHub/GitLab remote fetcher | `okf generate --remote https://github.com/owner/repo --ref main`<br>Fetches tree via GitHub/GitLab API (no local clone)<br>Supports `--path docs/src` for subdirectory<br>Supports `--ref main|develop|v1.0.0|abc123` | 5 pts |
| **OKF-29** | Private repo authentication | `GITHUB_TOKEN` / `GITLAB_TOKEN` env vars<br>`okf generate --remote git@github.com:org/private-repo --ref main`<br>Rate limit handling with exponential backoff | 3 pts |
| **OKF-30** | Selective path inclusion | `--include "src/**/*.py" --exclude "tests/**"`<br>Glob patterns for file filtering<br>Default: `**/*.py`, `**/*.md`, `**/*.yaml`, `**/*.yml` | 2 pts |
| **OKF-31** | Incremental remote sync | `okf update --remote https://github.com/owner/repo --ref main`<br>Uses GitHub API `since` parameter for changed files only<br>Detects force-push / rebase (commit SHA mismatch) | 3 pts |
| **OKF-32** | Remote bundle as dependency | `okf bundle add https://github.com/owner/lib --ref v1.0.0 --as external_lib`<br>Links external bundle concepts in current bundle<br>`okf lookup --bundle ./docs/okfs/external_lib SomeClass` | 3 pts |

### Definition of Done
- [ ] Generate OKF bundle from any public GitHub/GitLab repo
- [ ] Authenticated access to private repos
- [ ] Selective path inclusion with glob patterns
- [ ] Incremental sync detects changes via API
- [ ] External bundles linked as cross-bundle dependencies

---

## Sprint 8 — Multi-Repo Knowledge Graph & Federation (Week 7-8)

**Goal**: Build unified knowledge graph across remote + local bundles

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| **OKF-33** | Cross-repo dependency resolution | `okf generate --federate ./local_repo https://github.com/owner/lib`<br>Resolves imports: `from external_lib.module import Class`<br>Creates cross-bundle links: `local_module.function → external_lib.Class` | 5 pts |
| **OKF-34** | Federated knowledge graph | `okf graph --federate ./docs/okfs/code_bundle https://github.com/owner/lib`<br>Unified D3 visualization with cross-repo edges<br>Edge types: imports, implements, extends, calls | 4 pts |
| **OKF-35** | Remote bundle caching | Local cache at `~/.okf/cache/remote/`<br>TTL-based expiry (configurable: `--cache-ttl 24h`)<br>Hash-based invalidation on remote change | 3 pts |
| **OKF-36** | Team knowledge sharing | `okf bundle publish --to https://okf-registry.company.com`<br>Private registry for team bundles<br>`okf bundle pull org/repo@v1.2.0` | 4 pts |

### Definition of Done
- [ ] Cross-repo imports resolved to external bundle concepts
- [ ] Unified graph visualizes local + remote concepts
- [ ] Remote bundles cached locally with TTL
- [ ] Team registry for bundle sharing

---

## Quality Metrics Dashboard (Updated with OKF Baselines)

| Metric | Sprint 0 Baseline | Sprint 1 Target | Sprint 2 Target | Sprint 3 Target | Sprint 4 Target |
|--------|-------------------|-----------------|-----------------|-----------------|-----------------|
| Recall@4 (RAGAS) | TBD | 0.60 | 0.70 | 0.75 | 0.80 |
| MRR | TBD | 0.50 | 0.55 | 0.60 | 0.65 |
| Faithfulness | TBD | 0.70 | 0.80 | 0.85 | 0.90 |
| Answer Relevancy | TBD | 0.70 | 0.80 | 0.85 | 0.90 |
| Concept Retrieval Accuracy | TBD | 0.65 | 0.75 | 0.85 | 0.90 |
| Cross-Bundle Link Traversal | TBD | 0.80 | 0.85 | 0.90 | 0.95 |
| Metadata Filter Precision | TBD | 0.85 | 0.90 | 0.95 | 0.98 |
| Abstain Rate (OOS) | TBD | 60% | 75% | 85% | 90% |
| Citation Compliance | TBD | 90% | 95% | 100% | 100% |
| Retrieval Latency (p95) | TBD | <1s | <500ms | <300ms | <200ms |
| Incremental Update (1 file) | N/A | <10s | <5s | <3s | <2s |

---

## Evaluation Protocol (OKF-Enhanced)

### Golden Set Creation (Sprint 3)
1. Sample 50 questions from real usage + architecture docs + strategy code
2. Human expert writes ideal answer with citations to **concept_ids**
3. Store as `eval/golden_qa.jsonl`:
```jsonl
{"question": "How does populate_entry_trend work?", "ideal_answer": "...", "expected_concept_ids": ["strategies/Strategy322sgo/populate_entry_trend", "docs/FREQTRADE_STRATEGY_SPEC"], "difficulty": "medium", "bundle": "strategies_bundle"}
```

### Per-Sprint Evaluation
```bash
make okf-eval  # Runs RAGAS + OKF metrics, outputs JSON report
```

### Regression Gate (GitHub Actions)
```yaml
# .github/workflows/okf-eval.yml
- run: make okf-eval
- uses: actions/github-script@v7
  if: ${{ steps.eval.outputs.faithfulness < 0.75 }}
  with:
    script: core.setFailed('Faithfulness regression detected')
```

---

## OKF-Specific Implementation Notes

### Bundle Structure Reference
```
<bundle>/
├── index.md              # Bundle root — lists top-level dirs
├── log.md                # Generation history
├── <domain>/             # Mirrors source tree
│   ├── index.md          # Directory listing
│   ├── <module>.md       # Module concept
│   └── <module>/         # Subdir for class/function concepts
│       ├── <Class>.md
│       └── <function>.md
```

### Concept Frontmatter (OKF v0.2)
```yaml
---
okf_version: "0.2"
type: "Function"           # Module | Class | Function | Method | Dependency
title: "populate_entry_trend"
description: "Generates entry signals using SAR + RSI + volume"
resource: "strategies/Strategy322sgo.py"
tags: 
  - "lang:python"
  - "type:Function"
  - "module:strategies"
  - "domain:Strategy322sgo.py"
  - "git:branch:main"
  - "git:repo:askode"
  - "freqtrade"
  - "karakana"
  - "strategy"
timestamp: "2026-07-10T05:38:37Z"
concept_id: "strategies/Strategy322sgo/populate_entry_trend"
---
```

### Cross-Bundle Link Format
```markdown
## Cross-Bundle Links

* implements: [FREQTRADE_STRATEGY_SPEC](/docs_bundle/FREQTRADE_STRATEGY_SPEC.md) (in docs_bundle)
* called_by: [confirm_trade_entry](/strategies_bundle/Strategy322sgo/confirm_trade_entry.md)
```

### MCP Tools Available (11 per bundle)
| Tool | Purpose |
|------|---------|
| `lookup` | Search concepts by name/type/tag |
| `get_concept` | Full detail by concept_id |
| `find_callers` | Concepts that reference given concept |
| `find_callees` | Concepts referenced by given concept |
| `list_by_file` | All concepts from a source file |
| `list_dependencies` | External deps (pip, npm, cargo, etc.) |
| `bundle_info` | Bundle stats (counts by type) |
| `list_by_type` | Filter by Module/Class/Function |
| `search_by_tag` | Tag prefix search (e.g., `lang:python`) |
| `get_related` | Combined callers + callees + related |
| `get_manifest_source` | Manifest file for dependency concepts |

### Agent Integration Patterns
```markdown
# Add to agent instructions
This project has OKF knowledge bundles at ./docs/okfs/:
- code_bundle/ — src/ AST concepts
- scripts_bundle/ — scripts/ AST concepts  
- strategies_bundle/ — Strategy322sgo implementation
- docs_bundle/ — Specs, guides, workflows, configs

BEFORE reading any source file, ALWAYS run:
  okf lookup --bundle ./docs/okfs/<bundle> <ConceptName>

Common lookups:
  okf lookup --bundle ./docs/okfs/code_bundle NVIDIAEmbeddings
  okf lookup --bundle ./docs/okfs/strategies_bundle Strategy322sgo
  okf lookup --bundle ./docs/okfs/docs_bundle "Freqtrade Karakana Deployment"
```

---

## Next Actions (Priority Order)

1. **Sprint 1: OKF-1, OKF-2, OKF-3, OKF-4** — RAG chat + incremental updates + query routing + agent lookup
2. **Sprint 2: OKF-5, OKF-6, OKF-7, OKF-8** — Visualizations + dashboard
3. **Sprint 3: OKF-9, OKF-10, OKF-11, OKF-12, OKF-13** — Golden set + eval + CI gate
4. **Sprint 4: OKF-14, OKF-15, OKF-16, OKF-17, OKF-18** — Hybrid search + parent retrieval + query routing + incremental + training export
5. **Sprint 5: OKF-19, OKF-20, OKF-21, OKF-22, OKF-23** — Source preview + sessions + feedback + agent configs
6. **Sprint 6: OKF-24, OKF-25, OKF-26, OKF-27** — Federation + webhook + cron + versioning

---

## Makefile Targets to Add

```makefile
# OKF Bundle Generation
okf-generate-code:      okf generate ./src ./docs/okfs/code_bundle
okf-generate-scripts:   okf generate ./scripts ./docs/okfs/scripts_bundle
okf-generate-strategies: okf generate ./docs/strategies ./docs/okfs/strategies_bundle
okf-generate-docs:      python scripts/convert_docs_to_okf.py --source docs --output docs/okfs/docs_bundle
okf-generate-all:       okf-generate-code okf-generate-scripts okf-generate-strategies okf-generate-docs

# OKF Incremental Updates
okf-update-code:        okf update ./src ./docs/okfs/code_bundle
okf-update-docs:        okf update ./docs ./docs/okfs/docs_bundle
okf-update-strategies:  okf update ./docs/strategies ./docs/okfs/strategies_bundle
okf-update-scripts:     okf update ./scripts ./docs/okfs/scripts_bundle
okf-update-all:         okf-update-code okf-update-docs okf-update-strategies okf-update-scripts
okf-watch:              okf update ./src ./docs/okfs/code_bundle --watch & okf update ./docs ./docs/okfs/docs_bundle --watch

# OKF Pipeline
okf-chunk:              python scripts/chunk_okf_bundles.py --bundle docs/okfs/code_bundle --bundle docs/okfs/docs_bundle --bundle docs/okfs/scripts_bundle --bundle docs/okfs/strategies_bundle --output docs/okfs/chunks
okf-embed:              python scripts/generate_embeddings.py
okf-index:              python scripts/index_to_chromadb.py
okf-links:              python scripts/add_cross_bundle_links.py
okf-viz-code:           okf visualize ./docs/okfs/code_bundle docs/okfs/viz/code_viz.html
okf-viz-docs:           okf visualize ./docs/okfs/docs_bundle docs/okfs/viz/docs_viz.html
okf-viz-strategies:     okf visualize ./docs/okfs/strategies_bundle docs/okfs/viz/strategies_viz.html
okf-viz-all:            okf-viz-code okf-viz-docs okf-viz-strategies
okf-dashboard:          okf dashboard ./docs/okfs/code_bundle --open & okf dashboard ./docs/okfs/docs_bundle --open & okf dashboard ./docs/okfs/strategies_bundle --open

# OKF Chat & Eval
okf-chat:               chainlit run src/okf_chat.py -w
okf-eval:               python scripts/okf_eval.py --golden eval/golden_qa.jsonl --chroma docs/okfs/chromadb --collection okf_knowledge
okf-pairs:              okf pairs ./docs/okfs/code_bundle ./train.jsonl

# OKF Agent Setup
okf-install:            okf install all
okf-mcp-install:        okf mcp ./docs/okfs/code_bundle --install && okf mcp ./docs/okfs/docs_bundle --install && okf mcp ./docs/okfs/strategies_bundle --install && okf mcp ./docs/okfs/scripts_bundle --install
```

---

*Last Updated: 2026-07-16 — OKF Sprint 0.5 complete, ready for Sprint 1*