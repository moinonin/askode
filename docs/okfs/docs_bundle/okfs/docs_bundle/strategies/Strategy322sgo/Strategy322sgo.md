---
concept_id: okfs/docs_bundle/strategies/Strategy322sgo/Strategy322sgo
description: '- `IStrategy`'
git_branch: main
git_repo: askode
language: python
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/okfs/docs_bundle/strategies/Strategy322sgo/Strategy322sgo.md
tags:
- ext:md
- policy
- inference
- strategy
- trading
- domain:okfs
- shadow-trading
- sgo
- karakana
- artifacts
timestamp: '2026-07-16T03:50:26.916812Z'
title: Strategy322sgo
type: Strategy
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
Lines 55–1306 in `strategies/Strategy322sgo.py`

## Relationships

| Type | Target |
|------|--------|
| related | [Strategy322sgo](/strategies/Strategy322sgo.md) |
| related | [stop_loss_decay](/strategies/Strategy322sgo/stop_loss_decay.md) |
| related | [version](/strategies/Strategy322sgo/version.md) |
| related | [__init__](/strategies/Strategy322sgo/init.md) |
| related | [bot_start](/strategies/Strategy322sgo/bot_start.md) |
| related | [_resolve_artifact_path](/strategies/Strategy322sgo/resolve_artifact_path.md) |
| related | [_safe_margin](/strategies/Strategy322sgo/safe_margin.md) |
| related | [_resolve_strategy_health_path](/strategies/Strategy322sgo/resolve_strategy_health_path.md) |
| related | [_refresh_strategy_health_snapshot](/strategies/Strategy322sgo/refresh_strategy_health_snapshot.md) |
| related | [_historical_required_margin](/strategies/Strategy322sgo/historical_required_margin.md) |
| related | [_snapshot_int](/strategies/Strategy322sgo/snapshot_int.md) |
| related | [_snapshot_float](/strategies/Strategy322sgo/snapshot_float.md) |
| related | [_historical_trading_armed](/strategies/Strategy322sgo/historical_trading_armed.md) |
| related | [_historical_side_armed](/strategies/Strategy322sgo/historical_side_armed.md) |
| related | [_load_historical_policy](/strategies/Strategy322sgo/load_historical_policy.md) |
| related | [_historical_inference](/strategies/Strategy322sgo/historical_inference.md) |
| related | [_export_shadow_signal_row](/strategies/Strategy322sgo/export_shadow_signal_row.md) |
| related | [informative_pairs](/strategies/Strategy322sgo/informative_pairs.md) |
| related | [populate_indicators](/strategies/Strategy322sgo/populate_indicators.md) |
| related | [populate_entry_trend](/strategies/Strategy322sgo/populate_entry_trend.md) |
| related | [populate_exit_trend](/strategies/Strategy322sgo/populate_exit_trend.md) |
| related | [confirm_trade_entry](/strategies/Strategy322sgo/confirm_trade_entry.md) |
| related | [_latest_edge](/strategies/Strategy322sgo/latest_edge.md) |
| related | [_evaluate_karakana_exit](/strategies/Strategy322sgo/evaluate_karakana_exit.md) |
| related | [custom_exit](/strategies/Strategy322sgo/custom_exit.md) |
| related | [custom_stoploss](/strategies/Strategy322sgo/custom_stoploss.md) |
| related | [confirm_trade_exit](/strategies/Strategy322sgo/confirm_trade_exit.md) |
| related | [order_filled](/strategies/Strategy322sgo/order_filled.md) |
| related | [_clear_trade_monitor_state](/strategies/Strategy322sgo/clear_trade_monitor_state.md) |
| related | [_latest_candle_time](/strategies/Strategy322sgo/latest_candle_time.md) |
| related | [_reversal_expiry](/strategies/Strategy322sgo/reversal_expiry.md) |
| related | [_expire_pending_reversals](/strategies/Strategy322sgo/expire_pending_reversals.md) |
| related | [_normalize_reversal_time](/strategies/Strategy322sgo/normalize_reversal_time.md) |
| related | [_has_pending_reversal](/strategies/Strategy322sgo/has_pending_reversal.md) |
| related | [_block_same_direction_reentry](/strategies/Strategy322sgo/block_same_direction_reentry.md) |
| related | [_expire_blocked_reentries](/strategies/Strategy322sgo/expire_blocked_reentries.md) |
| related | [_is_same_direction_blocked](/strategies/Strategy322sgo/is_same_direction_blocked.md) |
| related | [_pending_reversal_side](/strategies/Strategy322sgo/pending_reversal_side.md) |
| related | [_is_reversal_entry](/strategies/Strategy322sgo/is_reversal_entry.md) |
| related | [_pending_reversal_summary](/strategies/Strategy322sgo/pending_reversal_summary.md) |
| related | [_unlock_pair_for_reversal](/strategies/Strategy322sgo/unlock_pair_for_reversal.md) |
| related | [_lock_pair_side_for_cooldown](/strategies/Strategy322sgo/lock_pair_side_for_cooldown.md) |
| related | [_order_side](/strategies/Strategy322sgo/order_side.md) |
| related | [_signed_open_trade_return](/strategies/Strategy322sgo/signed_open_trade_return.md) |
