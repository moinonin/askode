---
concept_id: strategies/Strategy322sgo/load_historical_policy
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
title: _load_historical_policy
type: Function
---

# _load_historical_policy

## Signature

```python
def _load_historical_policy(self) -> bool
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

## Returns
`bool`

## Source
Lines 413–515 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_resolve_artifact_path](/strategies/Strategy322sgo/resolve_artifact_path.md) |
| calls | [_resolve_strategy_health_path](/strategies/Strategy322sgo/resolve_strategy_health_path.md) |
| called_by | [bot_start](/strategies/Strategy322sgo/bot_start.md) |
| called_by | [_historical_inference](/strategies/Strategy322sgo/historical_inference.md) |
| called_by | [populate_indicators](/strategies/Strategy322sgo/populate_indicators.md) |
