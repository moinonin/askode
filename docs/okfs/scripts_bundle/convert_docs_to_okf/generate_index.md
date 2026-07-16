---
concept_id: convert_docs_to_okf/generate_index
description: Generate root index.md for the bundle.
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
title: generate_index
type: Function
---

# generate_index

Generate root index.md for the bundle.

## Signature

```python
def generate_index(bundle_dir: Path, source_dir: Path) -> None
```

## Docstring

Generate root index.md for the bundle.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `bundle_dir` | `Path` | `—` |

| `source_dir` | `Path` | `—` |

## Returns
`None`

## Source
Lines 170–200 in `convert_docs_to_okf.py`

## Relationships

| Type | Target |
|------|--------|
| related | [convert_docs_to_okf](/convert_docs_to_okf.md) |
| called_by | [main](/convert_docs_to_okf/main.md) |
