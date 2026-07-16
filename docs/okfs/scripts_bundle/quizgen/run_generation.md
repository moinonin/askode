---
concept_id: quizgen/run_generation
description: Run the full Q&A generation pipeline.
language: python
okf_version: '0.2'
resource: quizgen.py
tags:
- lang:python
- type:Function
- module:quizgen.py
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
Lines 104–199 in `quizgen.py`

## Relationships

| Type | Target |
|------|--------|
| related | [quizgen](/quizgen.md) |
| calls | [load_project_files](/quizgen/load_project_files.md) |
| calls | [init_llm](/quizgen/init_llm.md) |
