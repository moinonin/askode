---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/populate_entry_trend
description: 'def populate_entry_trend(self, dataframe: DataFrame, metadata: dict)
  -> DataFrame'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/populate_entry_trend.md
tags:
- ext:md
- strategy
- trading
- domain:okfs
- sgo
timestamp: '2026-07-16T03:50:26.948905Z'
title: populate_entry_trend
type: Document
---

# populate_entry_trend

## Signature

```python
def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame
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
Lines 727–829 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_latest_candle_time](/strategies/Strategy322sgo/latest_candle_time.md) |
| calls | [_expire_pending_reversals](/strategies/Strategy322sgo/expire_pending_reversals.md) |
| calls | [_historical_required_margin](/strategies/Strategy322sgo/historical_required_margin.md) |
| calls | [_historical_trading_armed](/strategies/Strategy322sgo/historical_trading_armed.md) |
| calls | [_historical_side_armed](/strategies/Strategy322sgo/historical_side_armed.md) |
| calls | [_has_pending_reversal](/strategies/Strategy322sgo/has_pending_reversal.md) |
| calls | [_pending_reversal_side](/strategies/Strategy322sgo/pending_reversal_side.md) |
| calls | [_unlock_pair_for_reversal](/strategies/Strategy322sgo/unlock_pair_for_reversal.md) |
| calls | [_resolve_strategy_health_path](/strategies/Strategy322sgo/resolve_strategy_health_path.md) |
