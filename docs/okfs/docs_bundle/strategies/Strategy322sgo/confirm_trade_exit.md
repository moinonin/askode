---
concept_id: strategies/Strategy322sgo/confirm_trade_exit
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
title: confirm_trade_exit
type: Function
---

# confirm_trade_exit

## Signature

```python
def confirm_trade_exit(self, pair: str, trade: Trade, order_type: str, amount: float, rate: float, time_in_force: str, exit_reason: str, current_time: datetime) -> bool
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `pair` | `str` | `—` |

| `trade` | `Trade` | `—` |

| `order_type` | `str` | `—` |

| `amount` | `float` | `—` |

| `rate` | `float` | `—` |

| `time_in_force` | `str` | `—` |

| `exit_reason` | `str` | `—` |

| `current_time` | `datetime` | `—` |

## Returns
`bool`

## Source
Lines 1075–1112 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_signed_open_trade_return](/strategies/Strategy322sgo/signed_open_trade_return.md) |
| calls | [_evaluate_karakana_exit](/strategies/Strategy322sgo/evaluate_karakana_exit.md) |
