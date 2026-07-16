---
concept_id: strategies/Strategy322sgo/confirm_trade_entry
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
title: confirm_trade_entry
type: Function
---

# confirm_trade_entry

## Signature

```python
def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float, time_in_force: str, current_time: datetime, entry_tag: str | None, side: str) -> bool
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `pair` | `str` | `—` |

| `order_type` | `str` | `—` |

| `amount` | `float` | `—` |

| `rate` | `float` | `—` |

| `time_in_force` | `str` | `—` |

| `current_time` | `datetime` | `—` |

| `entry_tag` | `str | None` | `—` |

| `side` | `str` | `—` |

## Returns
`bool`

## Source
Lines 835–882 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_expire_pending_reversals](/strategies/Strategy322sgo/expire_pending_reversals.md) |
| calls | [_expire_blocked_reentries](/strategies/Strategy322sgo/expire_blocked_reentries.md) |
| calls | [_historical_trading_armed](/strategies/Strategy322sgo/historical_trading_armed.md) |
| calls | [_is_reversal_entry](/strategies/Strategy322sgo/is_reversal_entry.md) |
| calls | [_has_pending_reversal](/strategies/Strategy322sgo/has_pending_reversal.md) |
| calls | [_is_same_direction_blocked](/strategies/Strategy322sgo/is_same_direction_blocked.md) |
| calls | [_unlock_pair_for_reversal](/strategies/Strategy322sgo/unlock_pair_for_reversal.md) |
| calls | [_pending_reversal_summary](/strategies/Strategy322sgo/pending_reversal_summary.md) |
