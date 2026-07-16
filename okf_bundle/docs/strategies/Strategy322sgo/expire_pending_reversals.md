---
concept_id: docs/strategies/Strategy322sgo/expire_pending_reversals
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
Lines 1202–1210 in `docs/strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/docs/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_normalize_reversal_time](/docs/strategies/Strategy322sgo/normalize_reversal_time.md) |
| calls | [_reversal_expiry](/docs/strategies/Strategy322sgo/reversal_expiry.md) |
| called_by | [confirm_trade_entry](/docs/strategies/Strategy322sgo/confirm_trade_entry.md) |
| called_by | [populate_entry_trend](/docs/strategies/Strategy322sgo/populate_entry_trend.md) |
