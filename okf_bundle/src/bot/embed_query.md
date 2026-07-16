---
concept_id: src/bot/embed_query
language: python
okf_version: '0.2'
resource: src/bot.py
tags:
- lang:python
- type:Function
- module:src
- domain:bot.py
- git:branch:main
- git:repo:askode
timestamp: '2026-07-13T05:03:14Z'
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
Lines 43–44 in `src/bot.py`

## Relationships

| Type | Target |
|------|--------|
| related | [OllamaEmbeddingsFixed](/src/bot/OllamaEmbeddingsFixed.md) |
