---
concept_id: docker-compose
description: '---'
git_branch: main
git_repo: askode
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/docker-compose.yml
tags:
- sgo
- threshold
- strategy
- deployment
- rl
- karakana
- shadow-trading
- freqtrade
- policy
- ext:yml
- governor
- artifacts
- docker
timestamp: '2026-07-16T03:54:30.976073Z'
title: Docker Compose
type: Config
---

---
# docker-compose.yml - Freqtrade + Karakana Shadow Loop
#
# This is intentionally a 4-service Compose app, not several long-running
# commands in one container. All services use the same image and the same
# user_data bind mount, so they share sqlite, signal CSVs, policy artifacts,
# and health outputs while keeping process restarts isolated.
#
# Intended deployment path:
#   <freqtrade-root>/docker-compose.yml
#
# Run from <freqtrade-root> after copying this file there:
#   docker compose up -d
#
# Image contract:
#   - image is built FROM freqtradeorg/freqtrade
#   - karakana is installed with the freqtrade-runtime extra
#   - console scripts exist: karakana-shadow-trader, karakana-shadow-health
#   - strategies/config/sqlite/policies live in the external user_data mount
#
# Runtime artifact contract:
#   ./user_data/strategies/<strategy-file>.py
#   ./user_data/configbybit.json
#   ./user_data/karakana_policy/watch/best_policy.pt
#   ./user_data/karakana_policy/watch/offline_preprocessing.json

services:
  # ─── Freqtrade Strategy (produces signal CSV, consumes governor CSV) ───
  freqtrade:
    image: moinonin/freqtrade-karakana:1.0.0
    init: true
    #build:
    #  context: .
    #  dockerfile: docker/Dockerfile.test_0626
    container_name: freqtrade-karakana
    restart: unless-stopped
    environment:
      # Karakana strategy config
      - KARAKANA_HISTORICAL_CHECKPOINT=/freqtrade/user_data/karakana_policy/watch/best_policy.pt
      - KARAKANA_HISTORICAL_PREPROCESSING=/freqtrade/user_data/karakana_policy/watch/offline_preprocessing.json
      - KARAKANA_HISTORICAL_THRESHOLD_GOVERNOR_ENABLED=1
      - KARAKANA_HISTORICAL_STRATEGY_HEALTH_PATH=/freqtrade/user_data/reports/directional_strategy_health.csv
      - KARAKANA_SHADOW_SIGNAL_EXPORT_PATH=/freqtrade/user_data/freqtrade_signals_karakana.csv
      - KARAKANA_HISTORICAL_REQUIRE_ARMED=1
      - KARAKANA_HISTORICAL_MIN_ARMED_ROWS=256
      - KARAKANA_HISTORICAL_MIN_ARMED_LONG_COUNT=64
      - KARAKANA_HISTORICAL_MIN_ARMED_SHORT_COUNT=64
      - KARAKANA_HISTORICAL_MIN_ARMED_REGIME_CONFIDENCE=0.0
      # Freqtrade runtime
      - FT_CONFIG=/freqtrade/user_data/configbybit.json
      - FT_DB_URL=sqlite:////freqtrade/user_data/tradesv3bybit.sqlite
      - FT_LOG_FILE=/freqtrade/user_data/logs/freqtrade.log
      - FT_STRATEGY=Strategy322sgo
      - FT_STRATEGY_FILE=Strategy322sgo.py
      - FT_USER_DATA_DIR=/freqtrade/user_data
    volumes:
      - ./user_data:/freqtrade/user_data
    ports:
      - "127.0.0.1:8000:8000"  # Freqtrade REST API
    entrypoint: ["/bin/sh", "-c"]
    command:
      - >-
        mkdir -p /freqtrade/user_data/logs /freqtrade/user_data/reports &&
        test -f "/freqtrade/user_data/strategies/$${FT_STRATEGY_FILE:-$${FT_STRATEGY}.py}" &&
        test -f /freqtrade/user_data/configbybit.json &&
        test -f /freqtrade/user_data/karakana_policy/watch/best_policy.pt &&
        test -f /freqtrade/user_data/karakana_policy/watch/offline_preprocessing.json &&
        exec freqtrade trade
        --logfile /freqtrade/user_data/logs/freqtrade.log
        --db-url sqlite:////freqtrade/user_data/tradesv3bybit.sqlite
        --config /freqtrade/user_data/configbybit.json
        --strategy "$${FT_STRATEGY:-Strategy322sgo}"
    healthcheck:
      test: ["CMD-SHELL", "test -s /freqtrade/user_data/freqtrade_signals_karakana.csv || test -s /freqtrade/user_data/logs/freqtrade.log"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    stop_grace_period: 60s

  # ─── Shadow Trader (signal CSV → virtual trade history) ───
  karakana-shadow-trader:
    image: moinonin/freqtrade-karakana:1.0.0
    init: true
    build:
      context: .
      dockerfile: docker/Dockerfile.test_0626
    container_name: karakana-shadow-trader
    restart: unless-stopped
    environment:
      - KARAKANA_SHADOW_SOURCE=/freqtrade/user_data/freqtrade_signals_karakana.csv
      - KARAKANA_SHADOW_POLICY_ROOT=/freqtrade/user_data/karakana_policy/watch
      - KARAKANA_SHADOW_OUTPUT_CSV=/freqtrade/user_data/reports/karakana_shadow_trade_history.csv
      - KARAKANA_SHADOW_STATE_PATH=/freqtrade/user_data/reports/karakana_shadow_trader_state.json
      - KARAKANA_SHADOW_HORIZON_ROWS=12
      - KARAKANA_SHADOW_FEE_BPS=0
      - KARAKANA_SHADOW_LONG_THRESHOLD=1.3
      - KARAKANA_SHADOW_SHORT_THRESHOLD=0.07
      - KARAKANA_SHADOW_ADMISSION_MODE=winner
      - KARAKANA_SHADOW_POLL_SECONDS=60
    volumes:
      - ./user_data:/freqtrade/user_data
    depends_on:
      freqtrade:
        condition: service_started
    entrypoint: ["/bin/sh", "-c"]
    command:
      - >-
        mkdir -p /freqtrade/user_data/reports &&
        command -v karakana-shadow-trader >/dev/null &&
        exec karakana-shadow-trader
        --watch
        --source /freqtrade/user_data/freqtrade_signals_karakana.csv
        --policy-root /freqtrade/user_data/karakana_policy/watch
        --output-csv /freqtrade/user_data/reports/karakana_shadow_trade_history.csv
        --state-path /freqtrade/user_data/reports/karakana_shadow_trader_state.json
        --horizon-rows 12
        --fee-bps 0
        --long-threshold 1.3
        --short-threshold 0.07
        --admission-mode winner
        --poll-seconds 60
    healthcheck:
      test: ["CMD-SHELL", "test -s /freqtrade/user_data/reports/karakana_shadow_trade_history.csv || test -s /freqtrade/user_data/reports/karakana_shadow_trader_state.json"]
      interval: 60s
      timeout: 10s
      retries: 10
      start_period: 180s
    stop_grace_period: 30s

  # ─── Shadow Health (virtual trades → governor CSV with dynamic thresholds) ───
  karakana-shadow-health:
    image: moinonin/freqtrade-karakana:1.0.0
    init: true
    build:
      context: .
      dockerfile: docker/Dockerfile.test_0626
    container_name: karakana-shadow-health
    restart: unless-stopped
    environment:
      - KARAKANA_HEALTH_SOURCE=/freqtrade/user_data/reports/karakana_shadow_trade_history.csv
      - KARAKANA_HEALTH_OUTPUT_CSV=/freqtrade/user_data/reports/directional_strategy_health.csv
      - KARAKANA_HEALTH_WINDOW_SIZE=1024
      - KARAKANA_HEALTH_WINDOW_STEP=256
      - KARAKANA_HEALTH_BASE_LONG_THRESHOLD=1.3
      - KARAKANA_HEALTH_BASE_SHORT_THRESHOLD=0.07
      - KARAKANA_HEALTH_POLL_SECONDS=60
    volumes:
      - ./user_data:/freqtrade/user_data
    depends_on:
      karakana-shadow-trader:
        condition: service_started
    entrypoint: ["/bin/sh", "-c"]
    command:
      - >-
        mkdir -p /freqtrade/user_data/reports &&
        command -v karakana-shadow-health >/dev/null &&
        exec karakana-shadow-health
        --watch
        --source /freqtrade/user_data/reports/karakana_shadow_trade_history.csv
        --output-csv /freqtrade/user_data/reports/directional_strategy_health.csv
        --window-size 1024
        --window-step 256
        --base-long-threshold 1.3
        --base-short-threshold 0.07
        --poll-seconds 60
    healthcheck:
      test: ["CMD-SHELL", "test -s /freqtrade/user_data/reports/directional_strategy_health.csv"]
      interval: 60s
      timeout: 10s
      retries: 10
      start_period: 300s
    stop_grace_period: 30s

  # ─── Threshold Scheduler (periodic sweep → optional compose patch/restart) ───
  karakana-threshold-scheduler:
    image: moinonin/freqtrade-karakana:1.0.0
    init: true
    container_name: karakana-threshold-scheduler
    restart: unless-stopped
    environment:
      - KARAKANA_THRESHOLD_SCHEDULER_APPLY=1
      - KARAKANA_THRESHOLD_SCHEDULER_RESTART_SIDECARS=1
      - KARAKANA_THRESHOLD_SCHEDULER_RUN_ON_START=0
      - KARAKANA_THRESHOLD_SCHEDULER_MIN_SIGNAL_ROWS=20000
      - KARAKANA_THRESHOLD_SCHEDULER_MIN_NEW_ROWS=25000
      - KARAKANA_THRESHOLD_SCHEDULER_TAIL_ROWS=50000
      - KARAKANA_THRESHOLD_SCHEDULER_DEFAULT_INTERVAL_SECONDS=7200
      - KARAKANA_THRESHOLD_SCHEDULER_INTERVAL_SECONDS_VALUES=3600,7200,10800,21600
      - KARAKANA_THRESHOLD_SCHEDULER_LONG_RANGE=1.0:3.0:0.1
      - KARAKANA_THRESHOLD_SCHEDULER_SHORT_RANGE=0.05:1.5:0.05
      - KARAKANA_THRESHOLD_SCHEDULER_HEALTH_WINDOW_SIZES=128,256,512,1024
      - KARAKANA_THRESHOLD_SCHEDULER_HEALTH_WINDOW_STEPS=32,64,128,256
      - KARAKANA_THRESHOLD_SCHEDULER_HEALTH_POLL_SECONDS_VALUES=60
      - KARAKANA_THRESHOLD_SCHEDULER_MONITOR=1
      - KARAKANA_THRESHOLD_SCHEDULER_POLICY_RESET=1
      - KARAKANA_THRESHOLD_SCHEDULER_POLICY_RESET_FORCE=0
      - KARAKANA_THRESHOLD_SCHEDULER_POLICY_RESET_ON_FIRST_SEEN=0
      - KARAKANA_RUNTIME_SIGNALS_MAX_ROWS=250000
      - KARAKANA_RUNTIME_SHADOW_MAX_ROWS=100000
      - KARAKANA_RUNTIME_HEALTH_MAX_ROWS=20000
      - KARAKANA_RUNTIME_COUNT_TAIL_ROWS=10000
    volumes:
      - .:/work
      - ./user_data:/freqtrade/user_data
      # Required only when KARAKANA_THRESHOLD_SCHEDULER_RESTART_SIDECARS=1.
      - /var/run/docker.sock:/var/run/docker.sock
    depends_on:
      freqtrade:
        condition: service_started
      karakana-shadow-trader:
        condition: service_started
      karakana-shadow-health:
        condition: service_started
    entrypoint: ["/bin/sh", "-c"]
    command:
      - >-
        mkdir -p /work/user_data/reports &&
        test -f /work/rl-trade-trainer/artifacts/karakana_analysis/threshold_scheduler.py &&
        exec env PYTHONPATH=/work/rl-trade-trainer/karakana
        python /work/rl-trade-trainer/artifacts/karakana_analysis/threshold_scheduler.py
        --repo-root /work/rl-trade-trainer
        --sweep-script /work/rl-trade-trainer/artifacts/karakana_analysis/sweep_live_shadow_thresholds.py
        --source /work/user_data/freqtrade_signals_karakana.csv
        --policy-root /work/user_data/karakana_policy/watch
        --compose-file /work/custom-docker-compose.yml
        --output-csv /work/user_data/reports/karakana_live_threshold_sweep.csv
        --output-json /work/user_data/reports/karakana_live_threshold_sweep.json
        --state-json /work/user_data/reports/karakana_threshold_scheduler_state.json
        --log-file /work/user_data/reports/karakana_threshold_scheduler.log
        --monitor-script /work/rl-trade-trainer/artifacts/karakana_analysis/monitor_karakana_runtime.py
        --monitor-shadow-csv /work/user_data/reports/karakana_shadow_trade_history.csv
        --monitor-health-csv /work/user_data/reports/directional_strategy_health.csv
        --monitor-status-json /work/user_data/reports/karakana_runtime_status.json
        --monitor-archive-dir /work/user_data/reports/archive
        --monitor-signals-max-rows $${KARAKANA_RUNTIME_SIGNALS_MAX_ROWS:-250000}
        --monitor-shadow-max-rows $${KARAKANA_RUNTIME_SHADOW_MAX_ROWS:-100000}
        --monitor-health-max-rows $${KARAKANA_RUNTIME_HEALTH_MAX_ROWS:-20000}
        --monitor-count-tail-rows $${KARAKANA_RUNTIME_COUNT_TAIL_ROWS:-10000}
        --policy-reset-archive-dir /work/user_data/reports/archive
        --policy-reset-shadow-state /work/user_data/reports/karakana_shadow_trader_state.json
        --policy-reset-shadow-summary /work/user_data/reports/karakana_shadow_trade_history_summary.json
        --min-signal-rows $${KARAKANA_THRESHOLD_SCHEDULER_MIN_SIGNAL_ROWS:-20000}
        --min-new-rows-per-run $${KARAKANA_THRESHOLD_SCHEDULER_MIN_NEW_ROWS:-25000}
        --tail-rows $${KARAKANA_THRESHOLD_SCHEDULER_TAIL_ROWS:-50000}
        --long-thresholds $${KARAKANA_THRESHOLD_SCHEDULER_LONG_RANGE:-1.0:3.0:0.1}
        --short-thresholds $${KARAKANA_THRESHOLD_SCHEDULER_SHORT_RANGE:-0.05:1.5:0.05}
        --health-window-sizes $${KARAKANA_THRESHOLD_SCHEDULER_HEALTH_WINDOW_SIZES:-128,256,512,1024}
        --health-window-steps $${KARAKANA_THRESHOLD_SCHEDULER_HEALTH_WINDOW_STEPS:-32,64,128,256}
        --health-poll-seconds-values $${KARAKANA_THRESHOLD_SCHEDULER_HEALTH_POLL_SECONDS_VALUES:-60}
        --default-interval-seconds $${KARAKANA_THRESHOLD_SCHEDULER_DEFAULT_INTERVAL_SECONDS:-7200}
        --interval-seconds-values $${KARAKANA_THRESHOLD_SCHEDULER_INTERVAL_SECONDS_VALUES:-3600,7200,10800,21600}
        $$(test "$${KARAKANA_THRESHOLD_SCHEDULER_MONITOR:-1}" = "1" && printf %s " --monitor-enabled")
        $$(test "$${KARAKANA_THRESHOLD_SCHEDULER_POLICY_RESET:-1}" = "1" && printf %s " --policy-reset-enabled")
        $$(test "$${KARAKANA_THRESHOLD_SCHEDULER_POLICY_RESET_FORCE:-0}" = "1" && printf %s " --policy-reset-force")
        $$(test "$${KARAKANA_THRESHOLD_SCHEDULER_POLICY_RESET_ON_FIRST_SEEN:-0}" = "1" && printf %s " --policy-reset-on-first-seen")
        $$(test "$${KARAKANA_THRESHOLD_SCHEDULER_APPLY:-0}" = "1" && printf %s " --apply-compose")
        $$(test "$${KARAKANA_THRESHOLD_SCHEDULER_RESTART_SIDECARS:-0}" = "1" && printf %s " --restart-sidecars")
        $$(test "$${KARAKANA_THRESHOLD_SCHEDULER_RUN_ON_START:-0}" = "1" && printf %s " --run-on-start")
    healthcheck:
      test: ["CMD-SHELL", "test -s /work/user_data/reports/karakana_threshold_scheduler.log || test -s /work/user_data/reports/karakana_threshold_scheduler_state.json"]
      interval: 300s
      timeout: 10s
      retries: 5
      start_period: 120s
    stop_grace_period: 30s
