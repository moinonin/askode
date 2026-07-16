---
concept_id: strategies/Strategy322sgo/lock_pair_side_for_cooldown
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
title: _lock_pair_side_for_cooldown
type: Function
---

# _lock_pair_side_for_cooldown

## Signature

```python
def _lock_pair_side_for_cooldown(self, pair: str, side: str, until: datetime, reason: str) -> None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `pair` | `str` | `—` |

| `side` | `str` | `—` |

| `until` | `datetime` | `—` |

| `reason` | `str` | `—` |

## Returns
`None`

## Source
Lines 1274–1288 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| called_by | [_block_same_direction_reentry](/strategies/Strategy322sgo/block_same_direction_reentry.md) |
