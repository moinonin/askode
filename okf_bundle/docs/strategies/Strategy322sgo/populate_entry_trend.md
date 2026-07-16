---
concept_id: docs/strategies/Strategy322sgo/populate_entry_trend
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
title: populate_entry_trend
type: Function
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
Lines 727–829 in `docs/strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/docs/strategies/Strategy322sgo/Strategy322sgo.md) |
| calls | [_latest_candle_time](/docs/strategies/Strategy322sgo/latest_candle_time.md) |
| calls | [_expire_pending_reversals](/docs/strategies/Strategy322sgo/expire_pending_reversals.md) |
| calls | [_historical_required_margin](/docs/strategies/Strategy322sgo/historical_required_margin.md) |
| calls | [_historical_trading_armed](/docs/strategies/Strategy322sgo/historical_trading_armed.md) |
| calls | [_historical_side_armed](/docs/strategies/Strategy322sgo/historical_side_armed.md) |
| calls | [_has_pending_reversal](/docs/strategies/Strategy322sgo/has_pending_reversal.md) |
| calls | [_pending_reversal_side](/docs/strategies/Strategy322sgo/pending_reversal_side.md) |
| calls | [_unlock_pair_for_reversal](/docs/strategies/Strategy322sgo/unlock_pair_for_reversal.md) |
| calls | [_resolve_strategy_health_path](/docs/strategies/Strategy322sgo/resolve_strategy_health_path.md) |
