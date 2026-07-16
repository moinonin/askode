---
concept_id: docs/strategies/Strategy322sgo/refresh_strategy_health_snapshot
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
title: _refresh_strategy_health_snapshot
type: Function
---

# _refresh_strategy_health_snapshot

## Signature

```python
def _refresh_strategy_health_snapshot(self) -> Optional[dict[str, Any]]
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

## Returns
`Optional[dict[str, Any]]`

## Source
Lines 303–334 in `docs/strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/docs/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_resolve_strategy_health_path](/docs/strategies/Strategy322sgo/resolve_strategy_health_path.md) |
| calls | [_safe_margin](/docs/strategies/Strategy322sgo/safe_margin.md) |
| called_by | [_historical_required_margin](/docs/strategies/Strategy322sgo/historical_required_margin.md) |
| called_by | [_historical_side_armed](/docs/strategies/Strategy322sgo/historical_side_armed.md) |
| called_by | [_historical_trading_armed](/docs/strategies/Strategy322sgo/historical_trading_armed.md) |
