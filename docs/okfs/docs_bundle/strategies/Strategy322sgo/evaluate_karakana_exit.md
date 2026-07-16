---
concept_id: strategies/Strategy322sgo/evaluate_karakana_exit
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
title: _evaluate_karakana_exit
type: Function
---

# _evaluate_karakana_exit

## Signature

```python
def _evaluate_karakana_exit(self, trade: Trade, current_time: datetime, current_rate: float, pnl: float) -> str | None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `trade` | `Trade` | `—` |

| `current_time` | `datetime` | `—` |

| `current_rate` | `float` | `—` |

| `pnl` | `float` | `—` |

## Returns
`str | None`

## Source
Lines 894–992 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| called_by | [confirm_trade_exit](/strategies/Strategy322sgo/confirm_trade_exit.md) |
| called_by | [custom_exit](/strategies/Strategy322sgo/custom_exit.md) |
