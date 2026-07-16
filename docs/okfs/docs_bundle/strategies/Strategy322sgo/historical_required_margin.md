---
concept_id: strategies/Strategy322sgo/historical_required_margin
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
title: _historical_required_margin
type: Function
---

# _historical_required_margin

## Signature

```python
def _historical_required_margin(self, candidate_is_short: int) -> float
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `candidate_is_short` | `int` | `—` |

## Returns
`float`

## Source
Lines 336–345 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_refresh_strategy_health_snapshot](/strategies/Strategy322sgo/refresh_strategy_health_snapshot.md) |
| called_by | [_historical_inference](/strategies/Strategy322sgo/historical_inference.md) |
| called_by | [populate_entry_trend](/strategies/Strategy322sgo/populate_entry_trend.md) |
