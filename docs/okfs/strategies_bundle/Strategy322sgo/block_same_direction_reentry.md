---
concept_id: Strategy322sgo/block_same_direction_reentry
language: python
okf_version: '0.2'
resource: Strategy322sgo.py
tags:
- lang:python
- type:Function
- module:Strategy322sgo.py
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
Lines 1223–1233 in `Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/Strategy322sgo/Strategy322sgo.md) |
| calls | [_normalize_reversal_time](/Strategy322sgo/normalize_reversal_time.md) |
| calls | [_lock_pair_side_for_cooldown](/Strategy322sgo/lock_pair_side_for_cooldown.md) |
| called_by | [order_filled](/Strategy322sgo/order_filled.md) |
