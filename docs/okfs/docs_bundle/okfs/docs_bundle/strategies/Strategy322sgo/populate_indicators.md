---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/populate_indicators
description: 'def populate_indicators(self, dataframe: DataFrame, metadata: dict)
  -> DataFrame'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/populate_indicators.md
tags:
- ext:md
- policy
- inference
- strategy
- domain:okfs
- shadow-trading
- sgo
timestamp: '2026-07-16T03:50:26.944636Z'
title: populate_indicators
type: Document
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
