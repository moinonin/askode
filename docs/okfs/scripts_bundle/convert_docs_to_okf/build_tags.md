---
concept_id: convert_docs_to_okf/build_tags
description: Generate tags from path and content.
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
title: build_tags
type: Function
---

# build_tags

Generate tags from path and content.

## Signature

```python
def build_tags(filepath: Path, content: str, source_dir: Path) -> list[str]
```

## Docstring

Generate tags from path and content.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `filepath` | `Path` | `—` |

| `content` | `str` | `—` |

| `source_dir` | `Path` | `—` |

## Returns
`list[str]`

## Source
Lines 88–111 in `convert_docs_to_okf.py`

## Relationships

| Type | Target |
|------|--------|
| related | [convert_docs_to_okf](/convert_docs_to_okf.md) |
| called_by | [convert_file](/convert_docs_to_okf/convert_file.md) |
