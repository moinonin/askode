---
concept_id: strategies/Strategy322sgo/signed_open_trade_return
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
title: _signed_open_trade_return
type: Function
---

# _signed_open_trade_return

## Signature

```python
def _signed_open_trade_return(trade: Trade, current_rate: float) -> float
```

## Decorators

- `staticmethod`

## Parameters

| Name | Type | Default |
|------|------|---------|
| `trade` | `Trade` | `—` |

| `current_rate` | `float` | `—` |

## Returns
`float`

## Source
Lines 1299–1306 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| called_by | [confirm_trade_exit](/strategies/Strategy322sgo/confirm_trade_exit.md) |
