---
concept_id: freqtrade-karakana-thresholds
description: RL_TRADE_TRAINER_DIR ?= rl-trade-trainer
git_branch: main
git_repo: askode
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/freqtrade-karakana-thresholds.mk
tags:
- threshold
- strategy
- ext:mk
- rl
- karakana
- shadow-trading
- makefile
- freqtrade
- policy
- artifacts
- docker
timestamp: '2026-07-16T03:54:30.974342Z'
title: Freqtrade Karakana Thresholds
type: Config
---

# Karakana live threshold sweep targets for the external Freqtrade root.
#
# Copy or include this file from <freqtrade-root>, where:
#   ./rl-trade-trainer
#   ./user_data
#   ./custom-docker-compose.yml
# exist.

RL_TRADE_TRAINER_DIR ?= rl-trade-trainer
THRESHOLD_IMAGE ?= moinonin/freqtrade-karakana:1.0.0
THRESHOLD_PLATFORM ?= linux/amd64
THRESHOLD_DOCKER_RUN = docker run --rm --platform=$(THRESHOLD_PLATFORM) --entrypoint sh -v $(CURDIR):/work -w /work $(THRESHOLD_IMAGE) -lc

live_threshold_source ?= user_data/freqtrade_signals_karakana.csv
live_threshold_policy_root ?= user_data/karakana_policy/watch
live_threshold_long_range ?= 1.0:3.0:0.1
live_threshold_short_range ?= 0.05:1.5:0.05
live_threshold_health_window_sizes ?= 128,256,512,1024
live_threshold_health_window_steps ?= 32,64,128,256
live_threshold_health_poll_seconds_values ?= 60
live_threshold_tail_rows ?= 20000
live_threshold_max_rows ?=
live_threshold_horizon_rows ?= 12
live_threshold_horizon_mode ?= pair
live_threshold_min_trades ?= 128
live_threshold_min_side_trades ?= 8
live_threshold_win_rate_weight ?= 0.1
live_threshold_balance_weight ?= 0.1
live_threshold_health_weight ?= 0.05
live_threshold_poll_seconds_weight ?= 0.0
live_threshold_output_csv ?= user_data/reports/karakana_live_threshold_sweep.csv
live_threshold_output_json ?= user_data/reports/karakana_live_threshold_sweep.json
live_threshold_compose_file ?= custom-docker-compose.yml
live_threshold_apply_health_window_size ?=
live_threshold_apply_health_window_step ?=
live_threshold_apply_health_poll_seconds ?=
threshold_scheduler_min_signal_rows ?= 20000
threshold_scheduler_min_new_rows ?= 25000
threshold_scheduler_tail_rows ?= 50000
threshold_scheduler_interval_seconds ?=
threshold_scheduler_default_interval_seconds ?= 7200
threshold_scheduler_interval_values ?= 3600,7200,10800,21600
threshold_scheduler_apply ?= 0
threshold_scheduler_restart_sidecars ?= 0
threshold_scheduler_once ?= 0
threshold_scheduler_run_on_start ?= 0
threshold_scheduler_state_json ?= user_data/reports/karakana_threshold_scheduler_state.json
threshold_scheduler_log_file ?= user_data/reports/karakana_threshold_scheduler.log
karakana_runtime_status_json ?= user_data/reports/karakana_runtime_status.json
karakana_runtime_archive_dir ?= user_data/reports/archive
karakana_runtime_signals_max_rows ?= 250000
karakana_runtime_shadow_max_rows ?= 100000
karakana_runtime_health_max_rows ?= 20000
karakana_runtime_count_tail_rows ?= 10000
threshold_scheduler_monitor ?= 1
threshold_scheduler_policy_reset ?= 1
threshold_scheduler_policy_reset_force ?= 0
threshold_scheduler_policy_reset_on_first_seen ?= 0
threshold_scheduler_policy_reset_archive_dir ?= user_data/reports/archive
threshold_scheduler_policy_reset_shadow_state ?= user_data/reports/karakana_shadow_trader_state.json
threshold_scheduler_policy_reset_shadow_summary ?= user_data/reports/karakana_shadow_trade_history_summary.json

.PHONY: karakana-live-threshold-sweep karakana-live-threshold-apply karakana-runtime-monitor karakana-threshold-scheduler restart-karakana-sidecars

karakana-live-threshold-sweep:
	$(THRESHOLD_DOCKER_RUN) 'PYTHONPATH=$(RL_TRADE_TRAINER_DIR)/karakana python $(RL_TRADE_TRAINER_DIR)/artifacts/karakana_analysis/sweep_live_shadow_thresholds.py --repo-root $(RL_TRADE_TRAINER_DIR) --source $(live_threshold_source) --policy-root $(live_threshold_policy_root) --long-thresholds $(live_threshold_long_range) --short-thresholds $(live_threshold_short_range) --health-window-sizes $(live_threshold_health_window_sizes) --health-window-steps $(live_threshold_health_window_steps) --health-poll-seconds-values $(live_threshold_health_poll_seconds_values) --tail-rows $(live_threshold_tail_rows) $(if $(live_threshold_max_rows),--max-rows $(live_threshold_max_rows),) --horizon-rows $(live_threshold_horizon_rows) --horizon-mode $(live_threshold_horizon_mode) --min-trades $(live_threshold_min_trades) --min-side-trades $(live_threshold_min_side_trades) --win-rate-weight $(live_threshold_win_rate_weight) --balance-weight $(live_threshold_balance_weight) --health-weight $(live_threshold_health_weight) --poll-seconds-weight $(live_threshold_poll_seconds_weight) --output-csv $(live_threshold_output_csv) --output-json $(live_threshold_output_json)'

karakana-live-threshold-apply:
	$(THRESHOLD_DOCKER_RUN) 'PYTHONPATH=$(RL_TRADE_TRAINER_DIR)/karakana python $(RL_TRADE_TRAINER_DIR)/artifacts/karakana_analysis/sweep_live_shadow_thresholds.py --repo-root $(RL_TRADE_TRAINER_DIR) --source $(live_threshold_source) --policy-root $(live_threshold_policy_root) --long-thresholds $(live_threshold_long_range) --short-thresholds $(live_threshold_short_range) --health-window-sizes $(live_threshold_health_window_sizes) --health-window-steps $(live_threshold_health_window_steps) --health-poll-seconds-values $(live_threshold_health_poll_seconds_values) --tail-rows $(live_threshold_tail_rows) $(if $(live_threshold_max_rows),--max-rows $(live_threshold_max_rows),) --horizon-rows $(live_threshold_horizon_rows) --horizon-mode $(live_threshold_horizon_mode) --min-trades $(live_threshold_min_trades) --min-side-trades $(live_threshold_min_side_trades) --win-rate-weight $(live_threshold_win_rate_weight) --balance-weight $(live_threshold_balance_weight) --health-weight $(live_threshold_health_weight) --poll-seconds-weight $(live_threshold_poll_seconds_weight) --output-csv $(live_threshold_output_csv) --output-json $(live_threshold_output_json) --compose-file $(live_threshold_compose_file) --apply-compose $(if $(live_threshold_apply_health_window_size),--apply-health-window-size $(live_threshold_apply_health_window_size),) $(if $(live_threshold_apply_health_window_step),--apply-health-window-step $(live_threshold_apply_health_window_step),) $(if $(live_threshold_apply_health_poll_seconds),--apply-health-poll-seconds $(live_threshold_apply_health_poll_seconds),)'

karakana-runtime-monitor:
	$(THRESHOLD_DOCKER_RUN) 'python $(RL_TRADE_TRAINER_DIR)/artifacts/karakana_analysis/monitor_karakana_runtime.py --signals-csv $(live_threshold_source) --shadow-csv user_data/reports/karakana_shadow_trade_history.csv --health-csv user_data/reports/directional_strategy_health.csv --status-json $(karakana_runtime_status_json) --archive-dir $(karakana_runtime_archive_dir) --signals-max-rows $(karakana_runtime_signals_max_rows) --shadow-max-rows $(karakana_runtime_shadow_max_rows) --health-max-rows $(karakana_runtime_health_max_rows) --count-tail-rows $(karakana_runtime_count_tail_rows)'

karakana-threshold-scheduler:
	$(THRESHOLD_DOCKER_RUN) 'PYTHONPATH=$(RL_TRADE_TRAINER_DIR)/karakana python $(RL_TRADE_TRAINER_DIR)/artifacts/karakana_analysis/threshold_scheduler.py --repo-root $(RL_TRADE_TRAINER_DIR) --sweep-script $(RL_TRADE_TRAINER_DIR)/artifacts/karakana_analysis/sweep_live_shadow_thresholds.py --source $(live_threshold_source) --policy-root $(live_threshold_policy_root) --compose-file $(live_threshold_compose_file) --output-csv $(live_threshold_output_csv) --output-json $(live_threshold_output_json) --state-json $(threshold_scheduler_state_json) --log-file $(threshold_scheduler_log_file) --monitor-script $(RL_TRADE_TRAINER_DIR)/artifacts/karakana_analysis/monitor_karakana_runtime.py --monitor-shadow-csv user_data/reports/karakana_shadow_trade_history.csv --monitor-health-csv user_data/reports/directional_strategy_health.csv --monitor-status-json $(karakana_runtime_status_json) --monitor-archive-dir $(karakana_runtime_archive_dir) --monitor-signals-max-rows $(karakana_runtime_signals_max_rows) --monitor-shadow-max-rows $(karakana_runtime_shadow_max_rows) --monitor-health-max-rows $(karakana_runtime_health_max_rows) --monitor-count-tail-rows $(karakana_runtime_count_tail_rows) --policy-reset-archive-dir $(threshold_scheduler_policy_reset_archive_dir) --policy-reset-shadow-state $(threshold_scheduler_policy_reset_shadow_state) --policy-reset-shadow-summary $(threshold_scheduler_policy_reset_shadow_summary) --min-signal-rows $(threshold_scheduler_min_signal_rows) --min-new-rows-per-run $(threshold_scheduler_min_new_rows) --tail-rows $(threshold_scheduler_tail_rows) --long-thresholds $(live_threshold_long_range) --short-thresholds $(live_threshold_short_range) --health-window-sizes $(live_threshold_health_window_sizes) --health-window-steps $(live_threshold_health_window_steps) --health-poll-seconds-values $(live_threshold_health_poll_seconds_values) --horizon-rows $(live_threshold_horizon_rows) --horizon-mode $(live_threshold_horizon_mode) --min-trades $(live_threshold_min_trades) --min-side-trades $(live_threshold_min_side_trades) --win-rate-weight $(live_threshold_win_rate_weight) --balance-weight $(live_threshold_balance_weight) --health-weight $(live_threshold_health_weight) --poll-seconds-weight $(live_threshold_poll_seconds_weight) --default-interval-seconds $(threshold_scheduler_default_interval_seconds) --interval-seconds-values $(threshold_scheduler_interval_values) $(if $(threshold_scheduler_interval_seconds),--interval-seconds $(threshold_scheduler_interval_seconds),) $(if $(filter 1 true yes on,$(threshold_scheduler_monitor)),--monitor-enabled,) $(if $(filter 1 true yes on,$(threshold_scheduler_policy_reset)),--policy-reset-enabled,) $(if $(filter 1 true yes on,$(threshold_scheduler_policy_reset_force)),--policy-reset-force,) $(if $(filter 1 true yes on,$(threshold_scheduler_policy_reset_on_first_seen)),--policy-reset-on-first-seen,) $(if $(filter 1 true yes on,$(threshold_scheduler_apply)),--apply-compose,) $(if $(filter 1 true yes on,$(threshold_scheduler_restart_sidecars)),--restart-sidecars,) $(if $(filter 1 true yes on,$(threshold_scheduler_once)),--once,) $(if $(filter 1 true yes on,$(threshold_scheduler_run_on_start)),--run-on-start,)'

restart-karakana-sidecars:
	docker compose -f $(live_threshold_compose_file) up -d --force-recreate karakana-shadow-trader karakana-shadow-health
