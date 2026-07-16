---
concept_id: convert_docs_to_okf/convert_file
description: Convert a single markdown file to OKF format.
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
title: convert_file
type: Function
---

# convert_file

Convert a single markdown file to OKF format.

## Signature

```python
def convert_file(src: Path, dest: Path, source_dir: Path, repo_info: dict) -> None
```

## Docstring

Convert a single markdown file to OKF format.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `src` | `Path` | `—` |

| `dest` | `Path` | `—` |

| `source_dir` | `Path` | `—` |

| `repo_info` | `dict` | `—` |

## Returns
`None`

## Source
Lines 132–167 in `convert_docs_to_okf.py`

## Relationships

| Type | Target |
|------|--------|
| related | [convert_docs_to_okf](/convert_docs_to_okf.md) |
| calls | [extract_frontmatter](/convert_docs_to_okf/extract_frontmatter.md) |
| calls | [infer_type_and_title](/convert_docs_to_okf/infer_type_and_title.md) |
| calls | [build_tags](/convert_docs_to_okf/build_tags.md) |
| calls | [extract_description](/convert_docs_to_okf/extract_description.md) |
| called_by | [main](/convert_docs_to_okf/main.md) |
