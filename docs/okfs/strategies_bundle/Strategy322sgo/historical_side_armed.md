---
concept_id: Strategy322sgo/historical_side_armed
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
title: _historical_side_armed
type: Function
---

# _historical_side_armed

## Signature

```python
def _historical_side_armed(self, side: str) -> tuple[bool, str]
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `side` | `str` | `—` |

## Returns
`tuple[bool, str]`

## Source
Lines 393–411 in `Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/Strategy322sgo/Strategy322sgo.md) |
| calls | [_refresh_strategy_health_snapshot](/Strategy322sgo/refresh_strategy_health_snapshot.md) |
| calls | [_snapshot_int](/Strategy322sgo/snapshot_int.md) |
| called_by | [populate_entry_trend](/Strategy322sgo/populate_entry_trend.md) |
