---
concept_id: scripts/quizgen/embed_query
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
title: embed_query
type: Function
---

# embed_query

## Signature

```python
def embed_query(self, text: str) -> list[float]
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `text` | `str` | `—` |

## Returns
`list[float]`

## Source
Lines 32–33 in `scripts/quizgen.py`

## Relationships

| Type | Target |
|------|--------|
| related | [NVIDIAEmbeddings](/scripts/quizgen/NVIDIAEmbeddings.md) |
| calls | [embed_documents](/scripts/quizgen/embed_documents.md) |
