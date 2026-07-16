---
concept_id: docs/strategies/Strategy322sgo/Strategy322sgo
language: python
okf_version: '0.2'
resource: docs/strategies/Strategy322sgo.py
tags:
- lang:python
- type:Class
- module:docs
- domain:strategies
- git:branch:main
- git:repo:askode
timestamp: '2026-07-10T05:38:37Z'
title: Strategy322sgo
type: Class
---

# Strategy322sgo

## Inheritance

- `IStrategy`

## Fields

| Name | Type | Visibility |
|------|------|------------|
| `startup_candle_count` | `int` | `` |

## Methods

- `stop_loss_decay`
- `version`
- `__init__`
- `bot_start`
- `_resolve_artifact_path`
- `_safe_margin`
- `_resolve_strategy_health_path`
- `_refresh_strategy_health_snapshot`
- `_historical_required_margin`
- `_snapshot_int`
- `_snapshot_float`
- `_historical_trading_armed`
- `_historical_side_armed`
- `_load_historical_policy`
- `_historical_inference`
- `_export_shadow_signal_row`
- `informative_pairs`
- `populate_indicators`
- `populate_entry_trend`
- `populate_exit_trend`
- `confirm_trade_entry`
- `_latest_edge`
- `_evaluate_karakana_exit`
- `custom_exit`
- `custom_stoploss`
- `confirm_trade_exit`
- `order_filled`
- `_clear_trade_monitor_state`
- `_latest_candle_time`
- `_reversal_expiry`
- `_expire_pending_reversals`
- `_normalize_reversal_time`
- `_has_pending_reversal`
- `_block_same_direction_reentry`
- `_expire_blocked_reentries`
- `_is_same_direction_blocked`
- `_pending_reversal_side`
- `_is_reversal_entry`
- `_pending_reversal_summary`
- `_unlock_pair_for_reversal`
- `_lock_pair_side_for_cooldown`
- `_order_side`
- `_signed_open_trade_return`

## Source
Lines 55–1306 in `docs/strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/docs/strategies/Strategy322sgo.md) |
| related | [stop_loss_decay](/docs/strategies/Strategy322sgo/stop_loss_decay.md) |
| related | [version](/docs/strategies/Strategy322sgo/version.md) |
| related | [__init__](/docs/strategies/Strategy322sgo/init.md) |
| related | [bot_start](/docs/strategies/Strategy322sgo/bot_start.md) |
| related | [_resolve_artifact_path](/docs/strategies/Strategy322sgo/resolve_artifact_path.md) |
| related | [_safe_margin](/docs/strategies/Strategy322sgo/safe_margin.md) |
| related | [_resolve_strategy_health_path](/docs/strategies/Strategy322sgo/resolve_strategy_health_path.md) |
| related | [_refresh_strategy_health_snapshot](/docs/strategies/Strategy322sgo/refresh_strategy_health_snapshot.md) |
| related | [_historical_required_margin](/docs/strategies/Strategy322sgo/historical_required_margin.md) |
| related | [_snapshot_int](/docs/strategies/Strategy322sgo/snapshot_int.md) |
| related | [_snapshot_float](/docs/strategies/Strategy322sgo/snapshot_float.md) |
| related | [_historical_trading_armed](/docs/strategies/Strategy322sgo/historical_trading_armed.md) |
| related | [_historical_side_armed](/docs/strategies/Strategy322sgo/historical_side_armed.md) |
| related | [_load_historical_policy](/docs/strategies/Strategy322sgo/load_historical_policy.md) |
| related | [_historical_inference](/docs/strategies/Strategy322sgo/historical_inference.md) |
| related | [_export_shadow_signal_row](/docs/strategies/Strategy322sgo/export_shadow_signal_row.md) |
| related | [informative_pairs](/docs/strategies/Strategy322sgo/informative_pairs.md) |
| related | [populate_indicators](/docs/strategies/Strategy322sgo/populate_indicators.md) |
| related | [populate_entry_trend](/docs/strategies/Strategy322sgo/populate_entry_trend.md) |
| related | [populate_exit_trend](/docs/strategies/Strategy322sgo/populate_exit_trend.md) |
| related | [confirm_trade_entry](/docs/strategies/Strategy322sgo/confirm_trade_entry.md) |
| related | [_latest_edge](/docs/strategies/Strategy322sgo/latest_edge.md) |
| related | [_evaluate_karakana_exit](/docs/strategies/Strategy322sgo/evaluate_karakana_exit.md) |
| related | [custom_exit](/docs/strategies/Strategy322sgo/custom_exit.md) |
| related | [custom_stoploss](/docs/strategies/Strategy322sgo/custom_stoploss.md) |
| related | [confirm_trade_exit](/docs/strategies/Strategy322sgo/confirm_trade_exit.md) |
| related | [order_filled](/docs/strategies/Strategy322sgo/order_filled.md) |
| related | [_clear_trade_monitor_state](/docs/strategies/Strategy322sgo/clear_trade_monitor_state.md) |
| related | [_latest_candle_time](/docs/strategies/Strategy322sgo/latest_candle_time.md) |
| related | [_reversal_expiry](/docs/strategies/Strategy322sgo/reversal_expiry.md) |
| related | [_expire_pending_reversals](/docs/strategies/Strategy322sgo/expire_pending_reversals.md) |
| related | [_normalize_reversal_time](/docs/strategies/Strategy322sgo/normalize_reversal_time.md) |
| related | [_has_pending_reversal](/docs/strategies/Strategy322sgo/has_pending_reversal.md) |
| related | [_block_same_direction_reentry](/docs/strategies/Strategy322sgo/block_same_direction_reentry.md) |
| related | [_expire_blocked_reentries](/docs/strategies/Strategy322sgo/expire_blocked_reentries.md) |
| related | [_is_same_direction_blocked](/docs/strategies/Strategy322sgo/is_same_direction_blocked.md) |
| related | [_pending_reversal_side](/docs/strategies/Strategy322sgo/pending_reversal_side.md) |
| related | [_is_reversal_entry](/docs/strategies/Strategy322sgo/is_reversal_entry.md) |
| related | [_pending_reversal_summary](/docs/strategies/Strategy322sgo/pending_reversal_summary.md) |
| related | [_unlock_pair_for_reversal](/docs/strategies/Strategy322sgo/unlock_pair_for_reversal.md) |
| related | [_lock_pair_side_for_cooldown](/docs/strategies/Strategy322sgo/lock_pair_side_for_cooldown.md) |
| related | [_order_side](/docs/strategies/Strategy322sgo/order_side.md) |
| related | [_signed_open_trade_return](/docs/strategies/Strategy322sgo/signed_open_trade_return.md) |
