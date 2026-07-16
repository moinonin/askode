---
concept_id: src/bot/main
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
title: main
type: Function
---

# main

## Signature

```python
async def main(message: cl.Message)
```

## Decorators

- `cl.on_message`

## Parameters

| Name | Type | Default |
|------|------|---------|
| `message` | `cl.Message` | `—` |

## Source
Lines 141–166 in `src/bot.py`

## Relationships

| Type | Target |
|------|--------|
| related | [bot](/src/bot.md) |
