---
concept_id: convert_docs_to_okf/extract_description
description: Extract first meaningful paragraph as description.
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
title: extract_description
type: Function
---

# extract_description

Extract first meaningful paragraph as description.

## Signature

```python
def extract_description(content: str, max_len: int = 200) -> str
```

## Docstring

Extract first meaningful paragraph as description.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `content` | `str` | `—` |

| `max_len` | `int` | `200` |

## Returns
`str`

## Source
Lines 114–129 in `convert_docs_to_okf.py`

## Relationships

| Type | Target |
|------|--------|
| related | [convert_docs_to_okf](/convert_docs_to_okf.md) |
| called_by | [convert_file](/convert_docs_to_okf/convert_file.md) |
