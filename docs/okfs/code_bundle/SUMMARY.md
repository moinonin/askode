---
description: 'Top-level OKF summary: 10 concepts across 1 domains and 1 modules'
git_branch: main
git_repo: askode
okf_version: '0.2'
timestamp: '2026-07-16T00:54:41Z'
title: src — Knowledge Summary
type: Index
---

# src — Knowledge Summary

> OKF v0.2 bundle | 10 concepts | 1 domains | 1 modules

## Stats

| Type | Count |
|------|-------|
| Function | 7 |
| Class | 2 |
| Module | 1 |

| Language | Concepts |
|----------|----------|
| python | 10 |

## Domain Map

Use these links to navigate the bundle or prime an AI agent with focused context.

### [bot.py](bot.py/index.md) — 10 concepts

- [bot](bot/index.md) (10 concepts)

## Key Concepts

Highest-value concepts across all domains (Classes and Functions with rich descriptions).

| Concept | Type | Module | Description |
|---------|------|--------|-------------|
| [OllamaEmbeddingsFixed](/bot/OllamaEmbeddingsFixed.md) | Class | `bot.py` | Custom Ollama embeddings that works without /tokenize endpoi… |
| [NVIDIAEmbeddings](/bot/NVIDIAEmbeddings.md) | Class | `bot.py` | Custom NVIDIA embeddings that bypasses tiktoken tokenization… |

## Usage with OpenCode

```bash
# Prime full context
RUN cat ./okf_bundle/SUMMARY.md

# Prime specific domain
RUN cat ./okf_bundle/bot.py/index.md

# Find a concept
RUN find ./okf_bundle -name '<ConceptName>.md' | xargs cat
```
