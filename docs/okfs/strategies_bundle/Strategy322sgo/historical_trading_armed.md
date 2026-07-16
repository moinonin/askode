---
concept_id: Strategy322sgo/historical_trading_armed
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
title: _historical_trading_armed
type: Function
---

# _historical_trading_armed

## Signature

```python
def _historical_trading_armed(self) -> tuple[bool, str]
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

## Returns
`tuple[bool, str]`

## Source
Lines 366–391 in `Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/Strategy322sgo/Strategy322sgo.md) |
| calls | [_refresh_strategy_health_snapshot](/Strategy322sgo/refresh_strategy_health_snapshot.md) |
| calls | [_snapshot_int](/Strategy322sgo/snapshot_int.md) |
| calls | [_snapshot_float](/Strategy322sgo/snapshot_float.md) |
| called_by | [confirm_trade_entry](/Strategy322sgo/confirm_trade_entry.md) |
| called_by | [populate_entry_trend](/Strategy322sgo/populate_entry_trend.md) |
