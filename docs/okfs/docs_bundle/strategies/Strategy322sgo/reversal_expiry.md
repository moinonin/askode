---
concept_id: strategies/Strategy322sgo/reversal_expiry
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
title: _reversal_expiry
type: Function
---

# _reversal_expiry

## Signature

```python
def _reversal_expiry(self, created_at: datetime) -> datetime
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `created_at` | `datetime` | `—` |

## Returns
`datetime`

## Source
Lines 1199–1200 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_normalize_reversal_time](/strategies/Strategy322sgo/normalize_reversal_time.md) |
| called_by | [_expire_pending_reversals](/strategies/Strategy322sgo/expire_pending_reversals.md) |
| called_by | [order_filled](/strategies/Strategy322sgo/order_filled.md) |
