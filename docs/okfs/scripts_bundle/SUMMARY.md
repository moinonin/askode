---
description: 'Top-level OKF summary: 18 concepts across 2 domains and 2 modules'
git_branch: main
git_repo: askode
okf_version: '0.2'
timestamp: '2026-07-16T00:54:54Z'
title: scripts — Knowledge Summary
type: Index
---

# scripts — Knowledge Summary

> OKF v0.2 bundle | 18 concepts | 2 domains | 2 modules

## Stats

| Type | Count |
|------|-------|
| Function | 15 |
| Module | 2 |
| Class | 1 |

| Language | Concepts |
|----------|----------|
| python | 18 |

## Domain Map

Use these links to navigate the bundle or prime an AI agent with focused context.

### [convert_docs_to_okf.py](convert_docs_to_okf.py/index.md) — 10 concepts

- [convert_docs_to_okf](convert_docs_to_okf/index.md) (10 concepts) — Convert markdown documentation files to OKF v0.2 format.

### [quizgen.py](quizgen.py/index.md) — 8 concepts

- [quizgen](quizgen/index.md) (8 concepts)

## Key Concepts

Highest-value concepts across all domains (Classes and Functions with rich descriptions).

| Concept | Type | Module | Description |
|---------|------|--------|-------------|
| [NVIDIAEmbeddings](/quizgen/NVIDIAEmbeddings.md) | Class | `quizgen.py` | Custom NVIDIA embeddings that bypasses tiktoken tokenization… |
| [infer_type_and_title](/convert_docs_to_okf/infer_type_and_title.md) | Function | `convert_docs_to_okf.py` | Infer OKF type and title from filename and content. |
| [extract_description](/convert_docs_to_okf/extract_description.md) | Function | `convert_docs_to_okf.py` | Extract first meaningful paragraph as description. |
| [extract_frontmatter](/convert_docs_to_okf/extract_frontmatter.md) | Function | `convert_docs_to_okf.py` | Extract existing YAML frontmatter if present. |
| [convert_file](/convert_docs_to_okf/convert_file.md) | Function | `convert_docs_to_okf.py` | Convert a single markdown file to OKF format. |

## Usage with OpenCode

```bash
# Prime full context
RUN cat ./okf_bundle/SUMMARY.md

# Prime specific domain
RUN cat ./okf_bundle/convert_docs_to_okf.py/index.md

# Find a concept
RUN find ./okf_bundle -name '<ConceptName>.md' | xargs cat
```
