---
concept_id: scripts/quizgen/init_llm
description: Initialize the LLM based on provider.
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
title: init_llm
type: Function
---

# init_llm

Initialize the LLM based on provider.

## Signature

```python
def init_llm()
```

## Docstring

Initialize the LLM based on provider.

## Source
Lines 86–101 in `scripts/quizgen.py`

## Relationships

| Type | Target |
|------|--------|
| related | [quizgen](/scripts/quizgen.md) |
| called_by | [run_generation](/scripts/quizgen/run_generation.md) |
