---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/confirm_trade_exit
description: 'def confirm_trade_exit(self, pair: str, trade: Trade, order_type: str,
  amount: float, rate: float, time_in_force: str, exit_reason: str, current_time:
  datetime) -> bool'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/confirm_trade_exit.md
tags:
- ext:md
- strategy
- domain:okfs
- sgo
- karakana
timestamp: '2026-07-16T03:50:26.954879Z'
title: confirm_trade_exit
type: Document
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
