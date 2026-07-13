# SPRINTS.md — Karakana Local Context Engine

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

## Sprint 1 — Continuous Improvement: Retrieval & Chunking (Week 1-2)

**Goal**: Fix the #1 quality bottleneck — semantic chunking and retrieval precision

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| CI-1 | Replace `RecursiveCharacterTextSplitter` with semantic splitters | - Python: `PythonCodeTextSplitter` (AST-based)<br>- Markdown: `MarkdownHeaderTextSplitter`<br>- No mid-function/class splits | 3 pts |
| CI-2 | Remove 12k char truncation in Pass 1 | Full document ingestion via sliding window with overlap | 2 pts |
| CI-3 | Replace fixed 1500-char windows in Pass 2 with semantic chunks | Chunks align to logical units (functions, classes, sections) | 3 pts |
| CI-4 | Add cross-encoder reranker (bge-reranker-base) | Top-k=8 → rerank to 4; measurable recall@4 improvement | 2 pts |
| CI-5 | Add metadata filtering to retriever | Filter by file_type (md/py), module path, tag | 2 pts |

### Definition of Done
- [ ] Golden Q&A set (20 questions) created from docs
- [ ] RAGAS evaluation baseline recorded
- [ ] CI-1 through CI-5 implemented
- [ ] RAGAS recall@4 improves ≥20% vs baseline

---

## Sprint 2 — Continuous Improvement: Generation Quality (Week 3-4)

**Goal**: Improve answer correctness and completeness

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| CI-6 | Add few-shot examples to Pass 1/2 generation prompts | 3 examples per pass; format matches expected JSONL | 2 pts |
| CI-7 | Add explicit "abstain if insufficient context" instruction | LLM returns "I cannot find that" when context lacks answer | 1 pt |
| CI-8 | Add citation format enforcement in generation | All answers include `[Source: filename]` inline | 1 pt |
| CI-9 | Temperature sweep + config (optional: evaluation | Find optimal temp per provider (0.1-0.5) | 2 pts |
| CI-10 | Add query expansion (synonyms, abbreviations) | Retrieval recall improves on terminology-mismatch queries | 3 pts |

### Definition of Done
- [ ] Answer accuracy (human eval on 20 Q) improves ≥25%
- [ ] Abstain rate on out-of-scope queries ≥80%
- [ ] Citation compliance 100% on in-scope answers

---

## Sprint 3 — Continuous Improvement: Deduplication & Coverage (Week 5)

**Goal**: Eliminate noise, improve knowledge coverage

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| CI-11 | Semantic deduplication of Q&A pairs | Embedding similarity threshold (e.g., 0.92) removes near-duplicates | 2 pts |
| CI-12 | Coverage analysis: which docs/chunks generated 0 Q&A | Report showing un-queried sections | 2 pts |
| CI-13 | Adaptive question count per chunk complexity | More questions for dense logic, fewer for boilerplate | 3 pts |
| CI-14 | Pass 2: chunk-aware prompt (pass chunk metadata to LLM) | LLM knows function/class name when generating Q&A | 2 pts |

### Definition of Done
- [ ] Q&A count reduced ≥15% via dedup with no recall loss
- [ ] Coverage report shows ≥95% of non-boilerplate chunks have ≥1 Q&A
- [ ] Generated Q&A reference specific functions/classes (not generic)

---

## Sprint 4 — Continuous Improvement: Evaluation & Monitoring (Week 6)

**Goal**: Make quality measurable and regression-proof

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| CI-15 | Integrate RAGAS (faithfulness, answer_relevancy, context_precision) | Automated eval on golden set after each sprint | 3 pts |
| CI-16 | Golden Q&A curation: 50 human-verified Q/A pairs | Covers architecture, configs, data flows, error handling | 3 pts |
| CI-17 | CI pipeline: run eval on PR, fail if regression >5% | GitHub Actions / local script | 2 pts |
| CI-18 | Dashboard: retrieval latency, answer latency, token usage | Basic logging + optional Grafana/Prometheus | 2 pts |

### Definition of Done
- [ ] RAGAS runs automatically on `make eval`
- [ ] Golden set ≥50 Q&A
- [ ] Regression gate active in CI

---

## Sprint 5 — Continuous Improvement: Advanced Retrieval (Week 7-8)

**Goal**: Production-grade retrieval

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| CI-19 | Hybrid search (BM25 + vector) | Keyword + semantic fusion; better exact-match recall | 3 pts |
| CI-20 | Parent document retrieval | Retrieve full parent doc for small chunks | 3 pts |
| CI-21 | Query classification → routing | Detect "how-to", "debug", "arch", "config" → different prompts | 3 pts |
| CI-22 | Incremental indexing | Only re-embed changed files on `make generate` | 3 pts |

### Definition of Done
- [ ] Hybrid search improves exact-match queries ≥30%
- [ ] Incremental generate <10s for single file change
- [ ] Query routing improves specialized answer quality

---

## Sprint 6 — Continuous Improvement: UX & Polish (Week 9)

**Goal**: Developer experience

### Stories

| ID | Story | Acceptance Criteria | Effort |
|----|-------|---------------------|--------|
| CI-23 | Source preview in chat UI (click to open file:line) | Chainlit action buttons open source in editor | 3 pts |
| CI-24 | Conversation history persistence across restarts | SQLite/JSONL session store | 2 pts |
| CI-25 | Feedback buttons (👍/👎) on answers | Logs for RLHF / prompt iteration | 2 pts |
| CI-26 | Dark/light theme toggle | Chainlit config | 1 pt |

---

## Backlog (Post-Sprint 6)

| ID | Idea | Priority |
|----|------|----------|
| B-1 | Multi-hop reasoning (decompose → retrieve → synthesize) | High |
| B-2 | Code-aware embeddings (CodeBERT, UniXcoder) | High |
| B-3 | Graph RAG (entity-relationship from code) | Medium |
| B-4 | Auto-update Q&A on git push (webhook) | Medium |
| B-5 | Multi-repo federation | Low |
| B-6 | Private LLM fine-tuning on Q&A pairs | Low |

---

## Quality Metrics Dashboard

| Metric | Baseline (Sprint 0) | Sprint 1 Target | Sprint 2 Target | Sprint 3 Target | Sprint 4 Target |
|--------|---------------------|-----------------|-----------------|-----------------|-----------------|
| Recall@4 (RAGAS) | TBD | +20% | +30% | +35% | +40% |
| Faithfulness | TBD | — | +15% | +25% | +30% |
| Answer Relevancy | TBD | — | +20% | +25% | +30% |
| Abstain Rate (OOS) | TBD | — | 80% | 90% | 95% |
| Citation Compliance | TBD | — | 100% | 100% | 100% |
| Q&A Dedup Reduction | 0% | — | — | 15% | 20% |
| Coverage (non-boilerplate) | TBD | — | — | 95% | 98% |
| Retrieval Latency (p95) | TBD | <2s | <1.5s | <1s | <1s |
| Generation Latency (p95) | TBD | <5s | <4s | <3s | <3s |

---

## Evaluation Protocol

### Golden Set Creation (Sprint 4)
1. Sample 50 questions from real usage + architecture docs
2. Human expert writes ideal answer with citations
3. Store as `eval/golden_qa.jsonl`

### Per-Sprint Evaluation
```bash
make eval  # Runs RAGAS on golden set, outputs JSON report
```

### Regression Gate
```yaml
# .github/workflows/eval.yml
- run: make eval
- uses: actions/github-script@v7
  if: ${{ steps.eval.outputs.faithfulness < 0.75 }}
  with:
    script: core.setFailed('Faithfulness regression detected')
```

---

## Notes for Implementers

### Semantic Chunking Options (CI-1)
| Language | Splitter | Install |
|----------|----------|---------|
| Python | `langchain_text_splitters.PythonCodeTextSplitter` | `langchain-text-splitters` |
| Markdown | `langchain_text_splitters.MarkdownHeaderTextSplitter` | `langchain-text-splitters` |
| Generic | `langchain_experimental.text_splitter.SemanticChunker` | `langchain-experimental` |

### Reranker Options (CI-4)
| Model | Dim | Speed | Quality |
|-------|-----|-------|---------|
| bge-reranker-base | 768 | Fast | Good |
| bge-reranker-large | 1024 | Medium | Best |
| cross-encoder/ms-marco-MiniLM-L-6-v2 | 384 | Very Fast | Adequate |

### Query Expansion (CI-10)
- Use LLM to generate 3-5 query variants (synonyms, abbreviations, related terms)
- Retrieve union, deduplicate, rerank
- Cost: +1 LLM call per query; acceptable for chat latency budget