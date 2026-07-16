---
concept_id: docs/strategies/Strategy322sgo/has_pending_reversal
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
title: _has_pending_reversal
type: Function
---

# _has_pending_reversal

## Signature

```python
def _has_pending_reversal(self, pair: str | None = None) -> bool
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `pair` | `str | None` | `None` |

## Returns
`bool`

## Source
Lines 1218–1221 in `docs/strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/docs/strategies/Strategy322sgo/Strategy322sgo.md) |
| called_by | [confirm_trade_entry](/docs/strategies/Strategy322sgo/confirm_trade_entry.md) |
| called_by | [populate_entry_trend](/docs/strategies/Strategy322sgo/populate_entry_trend.md) |
