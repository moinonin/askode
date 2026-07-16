---
concept_id: Strategy322sgo/expire_pending_reversals
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
title: _expire_pending_reversals
type: Function
---

# _expire_pending_reversals

## Signature

```python
def _expire_pending_reversals(self, now: datetime) -> None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `now` | `datetime` | `—` |

## Returns
`None`

## Source
Lines 1202–1210 in `Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/Strategy322sgo/Strategy322sgo.md) |
| calls | [_normalize_reversal_time](/Strategy322sgo/normalize_reversal_time.md) |
| calls | [_reversal_expiry](/Strategy322sgo/reversal_expiry.md) |
| called_by | [confirm_trade_entry](/Strategy322sgo/confirm_trade_entry.md) |
| called_by | [populate_entry_trend](/Strategy322sgo/populate_entry_trend.md) |
