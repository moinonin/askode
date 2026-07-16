---
concept_id: docs/strategies/Strategy322sgo/snapshot_int
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
title: _snapshot_int
type: Function
---

# _snapshot_int

## Signature

```python
def _snapshot_int(snapshot: Optional[dict[str, Any]], key: str) -> int
```

## Decorators

- `staticmethod`

## Parameters

| Name | Type | Default |
|------|------|---------|
| `snapshot` | `Optional[dict[str, Any]]` | `—` |

| `key` | `str` | `—` |

## Returns
`int`

## Source
Lines 348–354 in `docs/strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/docs/strategies/Strategy322sgo/Strategy322sgo.md) |
| called_by | [_historical_side_armed](/docs/strategies/Strategy322sgo/historical_side_armed.md) |
| called_by | [_historical_trading_armed](/docs/strategies/Strategy322sgo/historical_trading_armed.md) |
