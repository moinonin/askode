---
concept_id: strategies/Strategy322sgo/bot_start
description: Load the HistoricalTrading policy and its exact training normalization.
language: python
okf_version: '0.2'
resource: strategies/Strategy322sgo.py
tags:
- lang:python
- type:Function
- module:strategies
- domain:Strategy322sgo.py
- git:branch:main
- git:repo:askode
timestamp: '2026-07-10T05:38:37Z'
title: bot_start
type: Function
---

# bot_start

Load the HistoricalTrading policy and its exact training normalization.

## Signature

```python
def bot_start(self) -> None
```

## Docstring

Load the HistoricalTrading policy and its exact training normalization.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

## Returns
`None`

## Source
Lines 228–245 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_load_historical_policy](/strategies/Strategy322sgo/load_historical_policy.md) |
