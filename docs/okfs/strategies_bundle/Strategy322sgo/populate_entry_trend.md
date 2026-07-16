---
concept_id: Strategy322sgo/populate_entry_trend
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
Lines 727–829 in `Strategy322sgo.py`

## Relationships
* implements_section: [FREQTRADE_STRATEGY_SPEC](/docs_bundle/FREQTRADE_STRATEGY_SPEC.md) (in docs_bundle)


| Type | Target |
|------|--------|
| related | [Strategy322sgo](/Strategy322sgo/Strategy322sgo.md) |
| calls | [_latest_candle_time](/Strategy322sgo/latest_candle_time.md) |
| calls | [_expire_pending_reversals](/Strategy322sgo/expire_pending_reversals.md) |
| calls | [_historical_required_margin](/Strategy322sgo/historical_required_margin.md) |
| calls | [_historical_trading_armed](/Strategy322sgo/historical_trading_armed.md) |
| calls | [_historical_side_armed](/Strategy322sgo/historical_side_armed.md) |
| calls | [_has_pending_reversal](/Strategy322sgo/has_pending_reversal.md) |
| calls | [_pending_reversal_side](/Strategy322sgo/pending_reversal_side.md) |
| calls | [_unlock_pair_for_reversal](/Strategy322sgo/unlock_pair_for_reversal.md) |
| calls | [_resolve_strategy_health_path](/Strategy322sgo/resolve_strategy_health_path.md) |
