---
concept_id: src/bot/embed_documents_1
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
Lines 56–61 in `src/bot.py`

## Relationships

| Type | Target |
|------|--------|
| related | [NVIDIAEmbeddings](/src/bot/NVIDIAEmbeddings.md) |
