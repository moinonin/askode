---
concept_id: convert_docs_to_okf/extract_frontmatter
description: Extract existing YAML frontmatter if present.
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
title: extract_frontmatter
type: Function
---

# extract_frontmatter

Extract existing YAML frontmatter if present.

## Signature

```python
def extract_frontmatter(content: str) -> tuple[dict, str]
```

## Docstring

Extract existing YAML frontmatter if present.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `content` | `str` | `—` |

## Returns
`tuple[dict, str]`

## Source
Lines 56–65 in `convert_docs_to_okf.py`

## Relationships

| Type | Target |
|------|--------|
| related | [convert_docs_to_okf](/convert_docs_to_okf.md) |
| called_by | [convert_file](/convert_docs_to_okf/convert_file.md) |
