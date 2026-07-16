---
concept_id: docs/strategies/Strategy322sgo/custom_exit
language: python
okf_version: '0.2'
resource: docs/strategies/Strategy322sgo.py
tags:
- lang:python
- type:Function
- module:docs
- domain:strategies
- git:branch:main
- git:repo:askode
timestamp: '2026-07-10T05:38:37Z'
title: custom_exit
type: Function
---

# custom_exit

## Signature

```python
def custom_exit(self, pair: str, trade: Trade, current_time: datetime, current_rate: float, current_profit: float) -> str | None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `pair` | `str` | `—` |

| `trade` | `Trade` | `—` |

| `current_time` | `datetime` | `—` |

| `current_rate` | `float` | `—` |

| `current_profit` | `float` | `—` |

## Returns
`str | None`

## Source
Lines 994–1015 in `docs/strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/docs/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_evaluate_karakana_exit](/docs/strategies/Strategy322sgo/evaluate_karakana_exit.md) |
