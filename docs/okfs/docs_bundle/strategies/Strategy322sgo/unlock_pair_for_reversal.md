---
concept_id: strategies/Strategy322sgo/unlock_pair_for_reversal
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
title: _unlock_pair_for_reversal
type: Function
---

# _unlock_pair_for_reversal

## Signature

```python
def _unlock_pair_for_reversal(self, pair: str) -> None
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `pair` | `str` | `—` |

## Returns
`None`

## Source
Lines 1264–1272 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| called_by | [confirm_trade_entry](/strategies/Strategy322sgo/confirm_trade_entry.md) |
| called_by | [order_filled](/strategies/Strategy322sgo/order_filled.md) |
| called_by | [populate_entry_trend](/strategies/Strategy322sgo/populate_entry_trend.md) |
