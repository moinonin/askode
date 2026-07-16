---
concept_id: convert_docs_to_okf/generate_log
description: Generate log.md for the bundle.
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
title: generate_log
type: Function
---

# generate_log

Generate log.md for the bundle.

## Signature

```python
def generate_log(bundle_dir: Path) -> None
```

## Docstring

Generate log.md for the bundle.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `bundle_dir` | `Path` | `—` |

## Returns
`None`

## Source
Lines 203–211 in `convert_docs_to_okf.py`

## Relationships

| Type | Target |
|------|--------|
| related | [convert_docs_to_okf](/convert_docs_to_okf.md) |
| called_by | [main](/convert_docs_to_okf/main.md) |
