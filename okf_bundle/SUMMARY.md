---
description: 'Top-level OKF summary: 98 concepts across 3 domains and 4 modules'
git_branch: main
git_repo: askode
okf_version: '0.2'
timestamp: '2026-07-16T00:49:49Z'
title: askode — Knowledge Summary
type: Index
---

# askode — Knowledge Summary

> OKF v0.2 bundle | 98 concepts | 3 domains | 4 modules

## Stats

| Type | Count |
|------|-------|
| Function | 56 |
| Dependency | 33 |
| Module | 4 |
| Class | 4 |
| Resource | 1 |

| Language | Concepts |
|----------|----------|
| python | 63 |
| manifest | 33 |
| yaml | 2 |

## Domain Map

Use these links to navigate the bundle or prime an AI agent with focused context.

### [docs](docs/index.md) — 47 concepts

- [docs/strategies/Strategy322sgo](docs/strategies/Strategy322sgo/index.md) (45 concepts)
- [docs/legacy-docker-compose](docs/legacy-docker-compose/index.md) (2 concepts) — YAML file: legacy-docker-compose.yml (1 document(s))

### [scripts](scripts/index.md) — 8 concepts

- [scripts/quizgen](scripts/quizgen/index.md) (8 concepts)

### [src](src/index.md) — 10 concepts

- [src/bot](src/bot/index.md) (10 concepts)

## Dependencies

> Full list at [`_dependencies/index.md`](/_dependencies/index.md) or `okf lookup --type Dependency`

| Ecosystem | Packages |
|----------|----------|
| pip | 24 |
| docker-compose | 5 |
| docker | 4 |

## Key Concepts

Highest-value concepts across all domains (Classes and Functions with rich descriptions).

| Concept | Type | Module | Description |
|---------|------|--------|-------------|
| [custom_stoploss](/docs/strategies/Strategy322sgo/custom_stoploss.md) | Function | `docs/strategies/Strategy322sgo.py` | long_timediff = ((current_time - timedelta(minutes=self.sell… |
| [bot_start](/docs/strategies/Strategy322sgo/bot_start.md) | Function | `docs/strategies/Strategy322sgo.py` | Load the HistoricalTrading policy and its exact training nor… |
| [OllamaEmbeddingsFixed](/src/bot/OllamaEmbeddingsFixed.md) | Class | `src/bot.py` | Custom Ollama embeddings that works without /tokenize endpoi… |
| [NVIDIAEmbeddings](/scripts/quizgen/NVIDIAEmbeddings.md) | Class | `scripts/quizgen.py` | Custom NVIDIA embeddings that bypasses tiktoken tokenization… |
| [NVIDIAEmbeddings](/src/bot/NVIDIAEmbeddings.md) | Class | `src/bot.py` | Custom NVIDIA embeddings that bypasses tiktoken tokenization… |
| [order_filled](/docs/strategies/Strategy322sgo/order_filled.md) | Function | `docs/strategies/Strategy322sgo.py` | Callback triggered when any order is filled. |

## Usage with OpenCode

```bash
# Prime full context
RUN cat ./okf_bundle/SUMMARY.md

# Prime specific domain
RUN cat ./okf_bundle/docs/index.md

# Find a concept
RUN find ./okf_bundle -name '<ConceptName>.md' | xargs cat
```
