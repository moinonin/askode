---
concept_id: strategies/Strategy322sgo/populate_indicators
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
title: populate_indicators
type: Function
---

# populate_indicators

## Signature

```python
def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `dataframe` | `DataFrame` | `—` |

| `metadata` | `dict` | `—` |

## Returns
`DataFrame`

## Source
Lines 603–724 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_export_shadow_signal_row](/strategies/Strategy322sgo/export_shadow_signal_row.md) |
| calls | [_load_historical_policy](/strategies/Strategy322sgo/load_historical_policy.md) |
| calls | [_historical_inference](/strategies/Strategy322sgo/historical_inference.md) |
