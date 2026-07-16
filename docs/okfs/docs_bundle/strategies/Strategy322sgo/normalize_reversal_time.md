---
concept_id: strategies/Strategy322sgo/normalize_reversal_time
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
title: _normalize_reversal_time
type: Function
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
