---
concept_id: src/bot/embed_query_1
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
Lines 63–64 in `src/bot.py`

## Relationships

| Type | Target |
|------|--------|
| related | [NVIDIAEmbeddings](/src/bot/NVIDIAEmbeddings.md) |
