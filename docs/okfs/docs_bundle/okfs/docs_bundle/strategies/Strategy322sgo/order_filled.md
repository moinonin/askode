---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/order_filled
description: Callback triggered when any order is filled.
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/order_filled.md
tags:
- sgo
- ext:md
- strategy
- domain:okfs
timestamp: '2026-07-16T03:50:26.938433Z'
title: order_filled
type: Document
---

# order_filled

Callback triggered when any order is filled.

## Signature

```python
def order_filled(self, pair: str, trade: Trade, order: Any, current_time: datetime) -> None
```

## Docstring

Callback triggered when any order is filled.
Schedules same-pair reversal after confirmed SGO collapse exits and
clears pending reversal after the reversal entry actually fills.

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `pair` | `str` | `—` |

| `trade` | `Trade` | `—` |

| `order` | `Any` | `—` |

| `current_time` | `datetime` | `—` |

## Returns
`None`

## Source
Lines 1114–1178 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_order_side](/strategies/Strategy322sgo/order_side.md) |
| calls | [_clear_trade_monitor_state](/strategies/Strategy322sgo/clear_trade_monitor_state.md) |
| calls | [_block_same_direction_reentry](/strategies/Strategy322sgo/block_same_direction_reentry.md) |
| calls | [_unlock_pair_for_reversal](/strategies/Strategy322sgo/unlock_pair_for_reversal.md) |
| calls | [_normalize_reversal_time](/strategies/Strategy322sgo/normalize_reversal_time.md) |
| calls | [_reversal_expiry](/strategies/Strategy322sgo/reversal_expiry.md) |
