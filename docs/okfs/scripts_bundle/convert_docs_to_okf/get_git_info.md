---
concept_id: convert_docs_to_okf/get_git_info
description: Get git metadata for tagging.
language: python
okf_version: '0.2'
resource: convert_docs_to_okf.py
tags:
- lang:python
- type:Function
- module:convert_docs_to_okf.py
- git:branch:main
- git:repo:askode
timestamp: '2026-07-16T00:52:53Z'
title: get_git_info
type: Function
---

# get_git_info

Get git metadata for tagging.

## Signature

```python
def get_git_info(source_dir: Path) -> dict
```

## Docstring

Get git metadata for tagging.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `source_dir` | `Path` | `—` |

## Returns
`dict`

## Source
Lines 214–235 in `convert_docs_to_okf.py`

## Relationships

| Type | Target |
|------|--------|
| related | [convert_docs_to_okf](/convert_docs_to_okf.md) |
| called_by | [main](/convert_docs_to_okf/main.md) |
