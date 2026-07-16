---
concept_id: docs/strategies/Strategy322sgo/block_same_direction_reentry
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
title: _block_same_direction_reentry
type: Function
---

# _block_same_direction_reentry

## Signature

```python
def _block_same_direction_reentry(self, pair: str, side: str, now: datetime, reason: str) -> None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `pair` | `str` | `—` |

| `side` | `str` | `—` |

| `now` | `datetime` | `—` |

| `reason` | `str` | `—` |

## Returns
`None`

## Source
Lines 1223–1233 in `docs/strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/docs/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_normalize_reversal_time](/docs/strategies/Strategy322sgo/normalize_reversal_time.md) |
| calls | [_lock_pair_side_for_cooldown](/docs/strategies/Strategy322sgo/lock_pair_side_for_cooldown.md) |
| called_by | [order_filled](/docs/strategies/Strategy322sgo/order_filled.md) |
