---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/historical_trading_armed
description: def _historical_trading_armed(self) -> tuple[bool, str]
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/historical_trading_armed.md
tags:
- ext:md
- strategy
- trading
- domain:okfs
- sgo
timestamp: '2026-07-16T03:50:26.934931Z'
title: _historical_trading_armed
type: Document
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
Lines 366–391 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_refresh_strategy_health_snapshot](/strategies/Strategy322sgo/refresh_strategy_health_snapshot.md) |
| calls | [_snapshot_int](/strategies/Strategy322sgo/snapshot_int.md) |
| calls | [_snapshot_float](/strategies/Strategy322sgo/snapshot_float.md) |
| called_by | [confirm_trade_entry](/strategies/Strategy322sgo/confirm_trade_entry.md) |
| called_by | [populate_entry_trend](/strategies/Strategy322sgo/populate_entry_trend.md) |
