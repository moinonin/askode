---
concept_id: scripts/quizgen/load_project_files
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
title: load_project_files
type: Function
---

# load_project_files

## Signature

```python
def load_project_files(directory_path: str)
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `directory_path` | `str` | `—` |

## Source
Lines 66–83 in `scripts/quizgen.py`

## Relationships

| Type | Target |
|------|--------|
| related | [quizgen](/scripts/quizgen.md) |
| called_by | [run_generation](/scripts/quizgen/run_generation.md) |
