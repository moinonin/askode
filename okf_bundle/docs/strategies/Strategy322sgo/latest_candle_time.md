---
concept_id: docs/strategies/Strategy322sgo/latest_candle_time
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
title: _latest_candle_time
type: Function
---

# _latest_candle_time

## Signature

```python
def _latest_candle_time(self, dataframe: DataFrame) -> datetime
```

## Parameters

| Name | Type | Default |
|------|------|---------|
| `self` | `—` | `—` |

| `dataframe` | `DataFrame` | `—` |

## Returns
`datetime`

## Source
Lines 1189–1197 in `docs/strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/docs/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_normalize_reversal_time](/docs/strategies/Strategy322sgo/normalize_reversal_time.md) |
| called_by | [populate_entry_trend](/docs/strategies/Strategy322sgo/populate_entry_trend.md) |
