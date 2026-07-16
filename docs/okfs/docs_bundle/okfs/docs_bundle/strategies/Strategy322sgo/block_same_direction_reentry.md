---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/block_same_direction_reentry
description: 'def _block_same_direction_reentry(self, pair: str, side: str, now: datetime,
  reason: str) -> None'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/block_same_direction_reentry.md
tags:
- sgo
- ext:md
- strategy
- domain:okfs
timestamp: '2026-07-16T03:50:26.957782Z'
title: _block_same_direction_reentry
type: Document
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
Lines 1223–1233 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_normalize_reversal_time](/strategies/Strategy322sgo/normalize_reversal_time.md) |
| calls | [_lock_pair_side_for_cooldown](/strategies/Strategy322sgo/lock_pair_side_for_cooldown.md) |
| called_by | [order_filled](/strategies/Strategy322sgo/order_filled.md) |
