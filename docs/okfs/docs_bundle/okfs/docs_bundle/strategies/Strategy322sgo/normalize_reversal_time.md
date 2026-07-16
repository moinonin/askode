---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/normalize_reversal_time
description: 'def _normalize_reversal_time(value: datetime) -> datetime'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/normalize_reversal_time.md
tags:
- sgo
- ext:md
- strategy
- domain:okfs
timestamp: '2026-07-16T03:50:26.936081Z'
title: _normalize_reversal_time
type: Document
---

# _normalize_reversal_time

## Signature

```python
def _normalize_reversal_time(value: datetime) -> datetime
```

## Decorators

- `staticmethod`

## Parameters

| Name | Type | Default |
|------|------|---------|
| `value` | `datetime` | `—` |

## Returns
`datetime`

## Source
Lines 1213–1216 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| called_by | [_block_same_direction_reentry](/strategies/Strategy322sgo/block_same_direction_reentry.md) |
| called_by | [_expire_blocked_reentries](/strategies/Strategy322sgo/expire_blocked_reentries.md) |
| called_by | [_expire_pending_reversals](/strategies/Strategy322sgo/expire_pending_reversals.md) |
| called_by | [_latest_candle_time](/strategies/Strategy322sgo/latest_candle_time.md) |
| called_by | [order_filled](/strategies/Strategy322sgo/order_filled.md) |
| called_by | [_reversal_expiry](/strategies/Strategy322sgo/reversal_expiry.md) |
