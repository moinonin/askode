---
concept_id: convert_docs_to_okf/infer_type_and_title
description: Infer OKF type and title from filename and content.
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
title: infer_type_and_title
type: Function
---

# infer_type_and_title

Infer OKF type and title from filename and content.

## Signature

```python
def infer_type_and_title(filepath: Path, content: str) -> tuple[str, str]
```

## Docstring

Infer OKF type and title from filename and content.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `filepath` | `Path` | `—` |

| `content` | `str` | `—` |

## Returns
`tuple[str, str]`

## Source
Lines 68–85 in `convert_docs_to_okf.py`

## Relationships

| Type | Target |
|------|--------|
| related | [convert_docs_to_okf](/convert_docs_to_okf.md) |
| called_by | [convert_file](/convert_docs_to_okf/convert_file.md) |
