---
concept_id: quizgen/embed_documents
language: python
okf_version: '0.2'
resource: quizgen.py
tags:
- lang:python
- type:Function
- module:quizgen.py
- git:branch:main
- git:repo:askode
timestamp: '2026-07-12T13:46:54Z'
title: embed_documents
type: Function
---

# embed_documents

## Signature

```python
def embed_documents(self, texts: list[str]) -> list[list[float]]
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `texts` | `list[str]` | `—` |

## Returns
`list[list[float]]`

## Source
Lines 25–30 in `quizgen.py`

## Relationships

| Type | Target |
|------|--------|
| related | [NVIDIAEmbeddings](/quizgen/NVIDIAEmbeddings.md) |
| called_by | [embed_query](/quizgen/embed_query.md) |
