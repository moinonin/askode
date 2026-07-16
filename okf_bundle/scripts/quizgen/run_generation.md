---
concept_id: scripts/quizgen/run_generation
description: Run the full Q&A generation pipeline.
language: python
okf_version: '0.2'
resource: scripts/quizgen.py
tags:
- lang:python
- type:Function
- module:scripts
- domain:quizgen.py
- git:branch:main
- git:repo:askode
timestamp: '2026-07-12T13:46:54Z'
title: run_generation
type: Function
---

# run_generation

Run the full Q&A generation pipeline.

## Signature

```python
def run_generation()
```

## Docstring

Run the full Q&A generation pipeline.

## Source
Lines 104–199 in `scripts/quizgen.py`

## Relationships

| Type | Target |
|------|--------|
| related | [quizgen](/scripts/quizgen.md) |
| calls | [load_project_files](/scripts/quizgen/load_project_files.md) |
| calls | [init_llm](/scripts/quizgen/init_llm.md) |
