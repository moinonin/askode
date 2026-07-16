---
concept_id: rdql-karakana-freqtrade-workflow
description: This document describes the current training-to-inference procedure for
  this
git_branch: main
git_repo: askode
okf_version: '0.2'
resource: github.com/your/repo/blob/main//Users/nickrotich/Desktop/portfolio/projects/python/askode/docs/rdql-karakana-freqtrade-workflow.md
tags:
- sgo
- threshold
- deployment
- strategy
- trading
- rl
- training
- karakana
- shadow-trading
- inference
- freqtrade
- policy
- ext:md
- governor
- artifacts
timestamp: '2026-07-16T03:54:30.972316Z'
title: Rdql Karakana Freqtrade Workflow
type: Workflow
---

# RDQL to Karakana to Freqtrade Workflow

This document describes the current training-to-inference procedure for this
repo after the Karakana offline trainer integration.

The short version is:

1. Run the existing RDQL trainer first to generate a large logged trading
   dataset.
2. Run `make karakana-offline` to adapt that dataset and train/evaluate
   Karakana's offline trading trainer.
3. Use RDQL/Q-table artifacts for Freqtrade inference until the Karakana policy
   export bridge is implemented.

Karakana is now part of the offline training and evaluation workflow, but it is
not yet the production inference artifact used by Freqtrade.

## Current Architecture

There are two model tracks in the repo today.

### 1. RDQL Track

This is the production-ready track.

The RDQL path:

- reads historical or live market data;
- creates `(ask, bid, sma_compare, position_status)` states;
- trains the tabular `BidsAgent`;
- writes a large logged transition dataset to `user_data/reports/trade_history.csv`;
- saves Q-table artifacts under `pkls/` directories;
- provides the artifacts currently used for Freqtrade inference.

Important files:

- `core/bid_agent.py`
- `core/rl/agent.py`
- `core/rl/trainer.py`
- `user_data/reports/trade_history.csv`
- `core/rl/pkls/q_table.pkl`
- `core/rl/pkls/state_to_index.pkl`
- `user_data/optimization_results/.../pkls/q_table.pkl`
- `user_data/optimization_results/.../pkls/state_to_index.pkl`

### 2. Karakana Offline Track

This is the new offline structural trainer/evaluator track.

The Karakana path:

- reads `user_data/reports/trade_history.csv`;
- creates a trainer-compatible copy at
  `user_data/reports/karakana_trade_history.csv`;
- derives `next_state` for older history files if needed;
- repartitions rows into at least ten Karakana episodes if the source file has
  too few episode IDs;
- runs `karakana.trainers.offline_trading.OfflineTradingTrainer`;
- writes metrics to `user_data/reports/karakana_offline_metrics.json`.

Important files:

- `scripts/train_karakana_offline.py`
- `karakana/karakana/trainers/offline_trading.py`
- `user_data/reports/karakana_trade_history.csv`
- `user_data/reports/karakana_offline_metrics.json`

This path currently validates and trains a Karakana neural Q-policy, but that
policy is not yet exported into the Freqtrade inference path.

## Stage 1: Generate the RDQL Dataset

Run:

```bash
make train
```

This executes:

```bash
.venv/bin/python core/bid_agent.py
```

The main output for Karakana is:

```text
user_data/reports/trade_history.csv
```

For the Karakana offline trainer, the expected columns are:

```text
state
action
reward
episode_number
next_state
logged_at
```

The current repo also writes additional useful columns:

```text
position_status
next_position_status
teacher_side
trade_position
base_reward
```

Column meanings:

- `state`: four-value RDQL state tuple. The fourth value is the controlled
  position side after the recent closed-loop fix.
- `action`: one of `go_long`, `go_short`, `do_nothing`.
- `reward`: reward used by training.
- `next_state`: next controlled state after the action.
- `position_status`: controlled position side before action; `0` means long
  side, `1` means short side.
- `next_position_status`: controlled position side after action.
- `teacher_side`: side suggested by the pretrained teacher signal. This is
  diagnostic only and is no longer treated as the agent-controlled state.
- `trade_position`: original trade label from the data pipeline.
- `base_reward`: reward before any later shaping.
- `episode_number`: batch/episode ID.
- `logged_at`: timestamp when the row was written.

The dataset should be large. Karakana can smoke-test on a small file, but
useful offline training requires broad state and action coverage.

## Stage 2: Run Karakana Offline Training

Run:

```bash
make karakana-offline
```

This executes:

```bash
.venv/bin/python scripts/train_karakana_offline.py \
  --source user_data/reports/trade_history.csv \
  --output user_data/reports/karakana_trade_history.csv \
  --metrics-output user_data/reports/karakana_offline_metrics.json \
  --export-dir user_data/karakana_policy \
  --epochs 5
```

The adapter does not mutate `trade_history.csv`. It writes a separate prepared
file:

```text
user_data/reports/karakana_trade_history.csv
```

The metrics artifact is:

```text
user_data/reports/karakana_offline_metrics.json
```

The exported Karakana inference artifacts are:

```text
user_data/karakana_policy/best_policy.pt
user_data/karakana_policy/latest_policy.pt
user_data/karakana_policy/offline_preprocessing.json
user_data/karakana_policy/manifest.json
```

The exported `manifest.json` records the default inference thresholds used by
downstream policy consumers:

```json
{
  "inference_thresholds": {
    "long_action_margin": 1.3,
    "short_action_margin": 0.07
  }
}
```

Useful make overrides:

```bash
make karakana-offline epochs=20
```

The legacy variable name is still supported:

```bash
make karakana-offline karakana_epochs=20
```

Do not use `make karakana-offline --epochs=20`; Make does not forward that flag
to the Python trainer.

```bash
make karakana-offline \
  karakana_source=user_data/reports/trade_history.csv \
  karakana_dataset=user_data/reports/karakana_trade_history.csv \
  karakana_metrics=user_data/reports/karakana_offline_metrics.json \
  karakana_export_dir=user_data/karakana_policy
```

For a faster smoke run:

```bash
.venv/bin/python scripts/train_karakana_offline.py \
  --epochs 1 \
  --updates-per-epoch 2 \
  --batch-size 64 \
  --max-rows 512
```

## What Karakana Consumes

`OfflineTradingTrainer` requires:

```text
state
action
reward
episode_number
next_state
```

It accepts optional `logged_at`.

The trainer action vocabulary matches this repo:

```text
go_long
go_short
do_nothing
```

The state must be a four-number tuple:

```text
(ask, bid, sma_compare, position_status)
```

The adapter handles two compatibility issues:

1. If `next_state` is missing, it derives it from the next row inside each
   source episode.
2. If the source CSV has fewer than ten unique `episode_number` values, it
   repartitions rows into enough Karakana episodes for train/validation/test
   splitting.

Because the default Karakana run uses `gamma=0.0`, these repartitioned episodes
are treated as contextual logged samples rather than strong sequential PnL
claims.

## Stage 3: Interpret Karakana Metrics

Open:

```text
user_data/reports/karakana_offline_metrics.json
```

Important fields:

- `dataset_adapter.rows_out`: number of rows passed to Karakana.
- `dataset_adapter.karakana_episode_count`: number of adapted episodes.
- `dataset_adapter.action_counts`: action support in the prepared dataset.
- `trainer_dataset_summary.warnings`: limitations detected by Karakana.
- `last_metrics.behavior_action_agreement`: agreement on validation data.
- `test_metrics.behavior_action_agreement`: agreement on test data.
- `test_metrics.matched_logged_reward_mean`: logged reward mean where the
  learned policy matched the historical action.
- `test_metrics.structural_health`: Karakana structural-health score.
- `preprocessing_contract`: feature order, scaling, action labels, and reward
  scaling needed for future inference export.

Do not treat the Karakana metrics as live profitability yet. They are
offline logged-data diagnostics unless followed by a replay/backtest/paper
trading validation.

## Stage 4: Compare RDQL And Karakana

After the watcher has produced one or more Karakana runs, compare the current
tabular RDQL history against Karakana offline metrics:

```bash
make karakana-compare-histories
```

This writes:

```text
user_data/reports/rdql_karakana_comparison.csv
user_data/reports/rdql_karakana_comparison.json
```

The comparison uses the same RDQL-generated history windows consumed by each
Karakana watcher run. For rolling windows, aggregate row counts are overlapping
and should not be treated as unique market-history coverage.

Primary comparison keys:

- `karakana_last_10.matched_minus_rdql_reward_mean_weighted_mean`: recent
  matched logged reward delta. This is the most useful short-horizon indicator
  of whether Karakana is improving as watcher training progresses.
- `karakana_full.matched_minus_rdql_reward_mean_weighted_mean`: full overlapping
  watcher-history reward delta. This is more conservative, but older runs may
  include weak early policies.
- `latest_run.karakana_structural_health`: latest structural-health score.
- `latest_run.karakana_behavior_agreement`: how often Karakana matched logged
  RDQL actions on the test split.
- `karakana_last_10.karakana_action_rate_*_weighted_mean`: recent action
  distribution. Watch for collapse into one side or permanent `do_nothing`.
- `decision_gate.promote_to_default`: explicit report-level promotion flag.

Current interpretation rule:

```text
Promote Karakana to default only when recent reward delta is positive,
structural health is strong, action distribution has not collapsed, and
Freqtrade backtest/dry-run P&L does not degrade.
```

The comparison JSON currently sets `decision_gate.promote_to_default=false`
whenever downstream Freqtrade P&L is unavailable. Matched logged reward is an
offline proxy, not a counterfactual fill/P&L model.

The latest observed comparison had:

```text
last_10 matched reward delta: positive
latest structural health: strong
full overlapping reward delta: negative
downstream Freqtrade P&L: unavailable
decision: keep Karakana as validation/inference candidate, not default
```

## Stage 5: Downstream Freqtrade Trade CSV Gate

Freqtrade backtesting can export signals and trades. For G7, use exported
Freqtrade trade CSVs as the required downstream comparison input instead of
trying to infer fills from RDQL/Karakana offline history.

Run RDQL and Karakana backtests on the same timerange/config, then export two
trade files:

```text
user_data/reports/freqtrade_trades_rdql.csv
user_data/reports/freqtrade_trades_karakana.csv
```

Required CSV columns:

```text
is_short
profit_ratio OR close_profit
open_date
close_date
enter_tag
exit_reason
stake_amount
amount
pair
duration
```

`profit_ratio` and `close_profit` are aliases for the same comparison concept.
At least one must be present. If both exist, prefer `profit_ratio` for ratio
metrics and keep `close_profit` for compatibility with Freqtrade exports.

Column meanings:

| Column | Meaning |
| --- | --- |
| `is_short` | Trade side. Truthy/`1` means short, falsy/`0` means long. |
| `profit_ratio` | Closed-trade profit ratio. Preferred P&L ratio column. |
| `close_profit` | Freqtrade closed-trade profit ratio alias. Used if `profit_ratio` is absent. |
| `open_date` | Trade open timestamp. |
| `close_date` | Trade close timestamp. |
| `enter_tag` | Entry tag, used to verify RDQL/Karakana entry provenance. |
| `exit_reason` | Exit reason, used to compare stop/ROI/custom-exit behavior. |
| `stake_amount` | Stake size for the trade. |
| `amount` | Asset amount/contracts for the trade. |
| `pair` | Trading pair. |
| `duration` | Trade duration. `trade_duration` is also accepted. If both are absent, derive it from `close_date - open_date` before comparison. |

Recommended derived comparison artifacts:

```text
user_data/reports/freqtrade_downstream_trades_ab.csv
user_data/reports/freqtrade_downstream_trades_ab.json
```

The CSV should be a normalized concatenation of the RDQL and Karakana exported
trades, including a run label. The JSON should contain summary metrics and a
promotion decision gate.

Run the gate:

```bash
make freqtrade-downstream-compare
```

Override paths if needed:

```bash
make freqtrade-downstream-compare \
  freqtrade_rdql_csv=user_data/reports/freqtrade_trades_rdql.csv \
  freqtrade_karakana_csv=user_data/reports/freqtrade_trades_karakana.csv
```

SQLite remains acceptable as a fallback input if CSV export is unavailable.
In that case, query the same fields from Freqtrade's `trades` table and export
them into the CSV contract above before running G7.

Existing SQLite helper:

```bash
make freqtrade-downstream-sqlite-compare \
  freqtrade_rdql_db=/path/to/rdql.sqlite \
  freqtrade_karakana_db=/path/to/karakana.sqlite
```

If both runs live in the same SQLite file, filter by strategy name:

```bash
make freqtrade-downstream-sqlite-compare \
  freqtrade_rdql_db=/path/to/trades.sqlite \
  freqtrade_karakana_db=/path/to/trades.sqlite \
  freqtrade_rdql_strategy=Strategy319Rdql \
  freqtrade_karakana_strategy=Strategy322sgo
```

Primary downstream keys:

- `delta_karakana_minus_rdql.profit_ratio_sum`: summed profit-ratio delta.
- `delta_karakana_minus_rdql.profit_ratio_mean`: average profit-ratio delta.
- `delta_karakana_minus_rdql.max_drawdown`: drawdown delta. Less negative is
  better.
- `karakana.long_trade_rate` and `karakana.short_trade_rate`: side balance.
- `karakana.long_profit_ratio_sum` and `karakana.short_profit_ratio_sum`: side
  P&L ratio.
- `decision_gate.promote_to_default`: whether Karakana passes the current
  downstream gate.

Current G7 rule:

```text
Karakana can be promoted only if exported Freqtrade trades show no total P&L
ratio degradation, no drawdown worsening, and no collapse into one side.
```

Current Stage 5 result:

```text
inputs:
  user_data/reports/freqtrade_trades_rdql.csv
  user_data/reports/freqtrade_trades_karakana.csv
Karakana - RDQL profit_ratio_sum: +0.6708518919
Karakana - RDQL profit_abs_sum:   +96.12317165
Karakana - RDQL max_drawdown_abs: +118.6827684
Karakana long/short trade rates:  48.88% / 51.12%
decision_gate.promote_to_default: true
```

## Stage 6: Current Freqtrade Inference

Today, Freqtrade should still use the RDQL Q-table artifacts.

A deployable RDQL model directory must contain:

```text
pkls/q_table.pkl
pkls/state_to_index.pkl
```

Common locations:

```text
core/rl/pkls/
user_data/optimization_results/<candidate>/pkls/
user_data/optimization_results/<candidate>/<alpha_dir>/pkls/
```

`optimization_results.json` now separates two different stability concepts:

| Field | Meaning |
| --- | --- |
| `is_distributionally_stable` | n-learn/Karakana structural stability across outcome magnitude bins. This is not a long/short balance check. |
| `has_learned_both_directions` | `true` only when the generated trade set contains at least one long and at least one short trade. |
| `is_directionally_balanced` | `true` only when both directions are present, the minority side is at least 10% of trades, and directional imbalance is not above 80%. |
| `directional_balance_score` | `1 - abs(short_trades - long_trades) / total_trades`; higher means more balanced. |
| `directional_min_trade_rate` | Smaller of `long_trade_rate` and `short_trade_rate`. |

Model saving now requires `is_directionally_balanced=true`, so a candidate with
`99` long trades and `0` short trades should fail the hard gate even if its
structural geometry metrics look good.

`ranking_score` is the repo-local model-selection score. Lower is better and
it is intentionally breakeven-first, then directional balance, then learned
both directions, then `alpha_s_sil`, MSE cofactors, epsilon, cofactor norm
delta, `s`, raw alpha, and finally raw n-learn rank as the last tie-breaker.
The original structural score from n-learn is still stored separately as
`nlearn_ranking_score`.

The live strategy must compute the same state components as training:

```text
ask
bid
sma_compare
is_short
```

Where:

- `is_short=0` means evaluate the long-side state.
- `is_short=1` means evaluate the short-side state.

The side-consistent inference rule is:

```text
is_short=0 -> compare go_long vs do_nothing
is_short=1 -> compare go_short vs do_nothing
```

This avoids the previous conflict where a short-side state could emit
`go_long`, or a long-side state could emit `go_short`.

Use the side-consistent logic in:

```text
core/bid_agent.py
core/rl/agent.py
```

Avoid using legacy raw-argmax inference paths for production. Any production
path must enforce the side-consistent rule above.

## Stage 7: Karakana Inference Bridge

The repo now exports a local PyTorch checkpoint bridge for Karakana offline
policies.

The bridge consists of:

```text
scripts/train_karakana_offline.py
karakana.runtime.policy.KarakanaOfflinePolicy
karakana.runtime.shadow_trader
karakana.runtime.strategy_health
core/inference/karakana_policy.py              # compatibility wrapper
scripts/karakana_inference.py
user_data/karakana_policy/best_policy.pt
user_data/karakana_policy/offline_preprocessing.json
user_data/karakana_policy/manifest.json
```

The loader accepts raw Freqtrade-side values:

```text
ask
bid
sma_compare
is_short
```

It applies `offline_preprocessing.json`, runs Karakana's neural Q-policy, and
returns the repo-standard action labels:

```text
go_long
go_short
do_nothing
```

By default the loader enforces side-consistent action selection:

```text
is_short=0 -> compare go_long vs do_nothing
is_short=1 -> compare go_short vs do_nothing
```

It also applies the same confidence threshold used by the Freqtrade strategy:

```text
selected side is accepted only when:
is_short=0 -> Q(go_long)  - Q(do_nothing) >= 1.3
is_short=1 -> Q(go_short) - Q(do_nothing) >= 0.07
```

Override this with `KARAKANA_MIN_LONG_ACTION_MARGIN` and
`KARAKANA_MIN_SHORT_ACTION_MARGIN`, the CLI `--min-long-action-margin` and
`--min-short-action-margin` arguments, or `make karakana-predict
karakana_min_long_action_margin=... karakana_min_short_action_margin=...`.
The legacy symmetric `KARAKANA_MIN_ACTION_MARGIN` and `--min-action-margin`
remain available for one-off tests.

Optional Directional Strategy Health governor:

```bash
make directional-strategy-health
```

This writes:

```text
user_data/reports/directional_strategy_health.csv
user_data/reports/directional_strategy_health.jsonl
user_data/reports/directional_strategy_health_summary.json
```

For live/paper trading, prefer generating the health source from shadow
Karakana decisions instead of waiting for closed real trades:

```bash
make karakana-shadow-trader \
  shadow_source=user_data/freqtrade_signals_karakana.csv \
  shadow_policy_root=user_data/karakana_policy/watch \
  shadow_horizon_rows=12 \
  shadow_long_threshold=1.3 \
  shadow_short_threshold=0.07 \
  shadow_admission_mode=winner

make directional-strategy-health \
  directional_health_source=user_data/reports/karakana_shadow_trade_history.csv
```

Equivalent shortcut:

```bash
make karakana-shadow-health
```

During repository-side training/data generation, the single orchestration
command now starts RDQL live data generation, the Karakana offline watcher, the
shadow trader, and the shadow health watcher:

```bash
make train-karakana-flow \
  karakana_window_mode=rolling \
  karakana_rolling_rows=4096
```

The shadow pieces are enabled by default for this flow:

```text
flow_shadow_enabled=1
flow_health_enabled=1
```

Disable them only for debugging:

```bash
make train-karakana-flow flow_shadow_enabled=0 flow_health_enabled=0
```

During Freqtrade live/dry-run inference, `Strategy322sgo.py` is the versioned
strategy. It should export signal rows for the external shadow process and read
the generated health CSV for dynamic thresholds:

```bash
KARAKANA_SHADOW_SIGNAL_EXPORT_PATH=user_data/freqtrade_signals_karakana.csv
KARAKANA_HISTORICAL_THRESHOLD_GOVERNOR_ENABLED=1
KARAKANA_HISTORICAL_STRATEGY_HEALTH_PATH=user_data/reports/directional_strategy_health.csv
KARAKANA_HISTORICAL_REQUIRE_ARMED=1
```

`KARAKANA_SHADOW_SIGNAL_EXPORT_PATH` now defaults to
`user_data/freqtrade_signals_karakana.csv` in `Strategy322sgo.py`, so the
explicit env var is only needed when the container layout differs. Keep this
CSV inside the Freqtrade `user_data` mount, next to the external sqlite files,
so Freqtrade, the shadow trader, and the health writer see the same filesystem.

Then run the shadow sidecars continuously against that exported signal stream:

```bash
karakana-shadow-trader \
  --source user_data/freqtrade_signals_karakana.csv \
  --policy-root user_data/karakana_policy/watch \
  --watch \
  --poll-seconds 60

karakana-shadow-health \
  --watch \
  --poll-seconds 60
```

`karakana-shadow-health --watch` is a continuous watcher. It polls
`user_data/reports/karakana_shadow_trade_history.csv`, rebuilds the latest
health windows when the file changes, and writes
`user_data/reports/directional_strategy_health.csv` for Strategy322 to read.
It should run alongside the shadow trader for live dynamic thresholds.

The repository Make targets remain as compatibility shortcuts:

```bash
make karakana-shadow-trader shadow_watch=1 shadow_poll_seconds=60
make karakana-shadow-health shadow_health_watch=1 shadow_poll_seconds=60
```

The shadow source must contain either:

| Column | Meaning |
| --- | --- |
| `state` | Tuple/list with at least `(ask, bid, sma_compare)`. A fourth `is_short` value is ignored because the shadow trader evaluates both candidate sides. |

Or these explicit market columns:

| Column | Meaning |
| --- | --- |
| `ask` | Current ask-side feature used by the Karakana policy. |
| `bid` | Current bid-side feature used by the Karakana policy. |
| `sma-compare` | Integer SMA/regime comparison feature. `sma_compare`, `sma_compare_flag`, and `sma-trend-flag` are accepted aliases. |
| `mid-price` | Optional mark price for virtual P&L. If absent, `(ask + bid) / 2` is used. `mid_price`, `mid`, and `close` are accepted aliases. |

The shadow output is trade-history-compatible and is designed to feed
Directional Strategy Health:

```text
user_data/reports/karakana_shadow_trade_history.csv
user_data/reports/karakana_shadow_trade_history_summary.json
user_data/reports/karakana_shadow_trader_state.json
```

It contains `state`, `next_state`, `action`, `reward`, `episode_number`,
`position_status`, `trade_position`, side thresholds, Q margins, directional Q,
and do-nothing Q.  The reward is virtual forward return over
`shadow_horizon_rows`; long reward is `(future_mid - entry_mid) / entry_mid`,
and short reward is the inverse.  `shadow_fee_bps` can subtract an estimated
round-trip cost.

`shadow_admission_mode=winner` is the default and admits only the strongest
passing side per source row.  Use `shadow_admission_mode=both` only for
diagnostics, because admitting both sides on every row can produce mirror-image
long/short rewards and keep the health regime artificially neutral.

`directional_strategy_health.csv` is an append-style window report. The
Karakana inference governor reads the latest row. For threshold scaling it
consumes:

```text
effective_long_threshold
effective_short_threshold
```

If `KARAKANA_HISTORICAL_REQUIRE_ARMED=1`, Strategy322 also refuses all entries
until the latest health row satisfies the arming contract:

```text
rows >= KARAKANA_HISTORICAL_MIN_ARMED_ROWS
long_count >= KARAKANA_HISTORICAL_MIN_ARMED_LONG_COUNT
short_count >= KARAKANA_HISTORICAL_MIN_ARMED_SHORT_COUNT
regime_confidence >= KARAKANA_HISTORICAL_MIN_ARMED_REGIME_CONFIDENCE
```

Default arming thresholds are `1024` rows, `64` long samples, `64` short
samples, and `0.0` minimum confidence. This gate only blocks entries; exits
remain available.

The full CSV column contract is:

| Column | Meaning |
| --- | --- |
| `start_row` | Inclusive source row offset for the audited window. |
| `end_row` | Exclusive source row offset for the audited window. |
| `rows` | Number of rows in the audited window. |
| `regime` | Projected directional regime: `bullish`, `bearish`, `transitioning`, or `chaotic`. |
| `regime_confidence` | Confidence in the projected regime, normalized to `0..1`. |
| `alpha_divergence` | Absolute difference between long and short alpha health. |
| `velocity_divergence` | Absolute difference between long and short alpha-health velocity. |
| `asymmetry_index` | Normalized directional health asymmetry. |
| `long_count` | Number of long-side samples in the window. |
| `short_count` | Number of short-side samples in the window. |
| `long_alpha_health` | Long-side structural alpha health, where higher is healthier. |
| `short_alpha_health` | Short-side structural alpha health, where higher is healthier. |
| `long_v_alpha` | Long-side alpha-health velocity from `AlphaMomentumTracker`. |
| `short_v_alpha` | Short-side alpha-health velocity from `AlphaMomentumTracker`. |
| `long_m_alpha` | Long-side alpha-health momentum from `AlphaMomentumTracker`. |
| `short_m_alpha` | Short-side alpha-health momentum from `AlphaMomentumTracker`. |
| `long_horizon` | Projected long-side collapse horizon. |
| `short_horizon` | Projected short-side collapse horizon. |
| `long_alpha_s_sil` | Long-side distributional alpha S-SIL score. Lower is healthier. |
| `short_alpha_s_sil` | Short-side distributional alpha S-SIL score. Lower is healthier. |
| `long_fragility` | Long-side fragility score from the decayed component function. |
| `short_fragility` | Short-side fragility score from the decayed component function. |
| `base_long_threshold` | Static long Q-margin threshold before governance. |
| `base_short_threshold` | Static short Q-margin threshold before governance. |
| `effective_long_threshold` | Long Q-margin threshold after Strategy Health governance. |
| `effective_short_threshold` | Short Q-margin threshold after Strategy Health governance. |
| `long_reward_mean` | Mean logged reward for long-side samples in the window. |
| `short_reward_mean` | Mean logged reward for short-side samples in the window. |

Enable the governor explicitly. It is disabled by default:

```bash
make karakana-predict \
  karakana_threshold_governor=1 \
  karakana_strategy_health_path=user_data/reports/directional_strategy_health.csv \
  predict_ask=14644.3433 \
  predict_bid=14622.9567 \
  predict_sma=1 \
  predict_is_short=1
```

CLI smoke test:

```bash
.venv/bin/python scripts/karakana_inference.py \
  --model-dir user_data/karakana_policy \
  --ask 14644.3433 \
  --bid 14622.9567 \
  --sma-compare 1 \
  --is-short 1 \
  --min-long-action-margin 1.3 \
  --min-short-action-margin 0.07
```

Equivalent make target:

```bash
make karakana-predict \
  predict_ask=14644.3433 \
  predict_bid=14622.9567 \
  predict_sma=1 \
  predict_is_short=1 \
  karakana_min_long_action_margin=1.3 \
  karakana_min_short_action_margin=0.07
```

Python usage inside a strategy-like runtime:

```python
from karakana.runtime.policy import KarakanaOfflinePolicy

policy = KarakanaOfflinePolicy("user_data/karakana_policy")
decision = policy.predict(
    ask=ask,
    bid=bid,
    sma_compare=sma_compare,
    is_short=is_short,
)
action = decision["action"]
```

To override the asymmetric defaults from Python:

```python
policy = KarakanaOfflinePolicy(
    "user_data/karakana_policy",
    min_long_action_margin=1.3,
    min_short_action_margin=0.07,
)
```

The bridge is ready for local backtest/dry-run validation. It should not become
the default live Freqtrade backend until it beats or matches the RDQL baseline
in Freqtrade validation.

Until that validation is complete, the conservative production procedure is:

```text
RDQL trains and exports Q-table artifacts.
Karakana evaluates/trains offline from RDQL-generated history.
Karakana exports a testable policy bridge.
Freqtrade production continues using RDQL Q-table artifacts.
```

After validation passes, the intended procedure becomes:

```text
RDQL generates massive logged trade history.
Karakana trains structural offline policy.
Karakana policy is exported.
Freqtrade loads Karakana policy for live decisions.
RDQL remains a fallback or data-generation backend.
```

## Recommended Full Workflow

For a clean experiment, clear prior RDQL/Karakana run state first:

```bash
make purge
```

This removes the old RDQL trade history, Karakana watcher state, watcher
outputs, offline metrics, and exported Karakana policy directory:

```text
user_data/reports/trade_history.csv
user_data/reports/karakana_trade_history.csv
user_data/reports/karakana_offline_metrics.json
user_data/reports/karakana_watch/
user_data/reports/karakana_watch_state.json
user_data/karakana_policy/
```

`user_data/karakana_policy/` is created automatically by `make
karakana-offline` or by the Karakana watcher during `make train-karakana-flow`.
It does not need to be created manually.

For a normal development run:

```bash
make train
make karakana-offline
```

For simulated continuous training, run the full flow with one command:

```bash
make train-karakana-flow karakana_window_mode=rolling karakana_rolling_rows=4096
```

This starts RDQL live data generation and the slower Karakana watcher as child
processes. If either process exits, the orchestrator stops the other process so
the flow does not leave an orphan trainer running.

For bounded smoke tests:

```bash
make train-karakana-flow \
  flow_live_max_iterations=1 \
  flow_karakana_max_runs=1
```

The manual equivalent is to run RDQL live data generation and the Karakana
watcher in separate terminals:

```bash
make train-live
```

```bash
make karakana-watch
```

The watcher does not ask RDQL for data. It only polls
`user_data/reports/trade_history.csv` and starts a Karakana run when the file
exists and enough rows are available.

Default watcher gates:

```text
poll interval: 300 seconds
minimum total rows: 512
minimum new rows since last Karakana run: 256
window mode: full
rolling rows: 4096
Karakana epochs per run: 3
updates per epoch: 50
```

Karakana watcher window modes:

```text
full    -> train each Karakana run on all rows from the start of trade_history.csv
rolling -> train each Karakana run on the last N rows only
fresh   -> train each Karakana run only on rows added since the previous run
```

Recommended continuous mode:

```bash
make train-karakana-flow karakana_window_mode=rolling karakana_rolling_rows=4096
```

Fresh-interval mode is available, but use it only when `karakana_min_new_rows`
is large enough to provide a useful standalone training set:

```bash
make train-karakana-flow \
  karakana_window_mode=fresh \
  karakana_min_total_rows=512 \
  karakana_min_new_rows=512
```

Override example:

```bash
make karakana-watch \
  karakana_poll_seconds=600 \
  karakana_min_total_rows=2000 \
  karakana_min_new_rows=1000 \
  karakana_window_mode=rolling \
  karakana_rolling_rows=8192 \
  karakana_watch_epochs=5
```

Watcher outputs:

```text
user_data/reports/karakana_watch/karakana_trade_history_run_*.csv
user_data/reports/karakana_watch/trade_history_window_*_run_*.csv
user_data/reports/karakana_watch/karakana_offline_metrics_run_*.json
user_data/karakana_policy/watch/run_*/
user_data/karakana_policy/watch/latest.json
user_data/reports/karakana_watch_state.json
```

Then inspect:

```text
user_data/reports/trade_history.csv
user_data/reports/karakana_trade_history.csv
user_data/reports/karakana_offline_metrics.json
user_data/karakana_policy/manifest.json
```

For conservative production Freqtrade deployment today:

```text
1. Run `make train` long enough to generate a large, diverse `trade_history.csv`.
2. Rank/select the best RDQL model directory from optimization outputs.
3. Point the Freqtrade strategy at that model directory's `pkls/`.
4. Ensure inference uses side-consistent action selection.
5. Run `make karakana-offline` as a structural audit/training comparison.
6. Backtest the exported Karakana bridge separately before making it default.
```

## Legacy Defirl Package Workflow

Older Freqtrade strategies consumed a PyPI-packaged RDQL model from the
`defirl` package. The package directory now lives at:

```text
defirl/
```

Use this only for backward compatibility with those older strategies. The
package should be built from the best RDQL model selected by:

```bash
.venv/bin/python scripts/hypothesis.py user_data/optimization_results --top 1
```

The important output is the `File` path, for example:

```text
candidate_alpha_0.0000_20260704_094012/alpha_neg_0.0000_20260704_094012/optimization_results.json
```

The corresponding pickle directory is the sibling `pkls/` directory:

```text
user_data/optimization_results/candidate_alpha_0.0000_20260704_094012/alpha_neg_0.0000_20260704_094012/pkls/
```

It must contain:

```text
q_table.pkl
state_to_index.pkl
q_table_a.pkl
q_table_b.pkl
episode_transitions.pkl
```

The root repo provides a compatibility wrapper:

```bash
make defirl-rdql-package
```

Dry-run first if you only want to inspect the selected model and commands:

```bash
make defirl-rdql-package defirl_dry_run=1
```

The wrapper selects the best model using the same ranking logic as
`scripts/hypothesis.py`, then executes the equivalent of these commands inside
`defirl/`:

```bash
make bump
make rdql-backup rdql_base=/absolute/path/to/rl-trade-trainer int_dir=user_data/optimization_results/<candidate>/<alpha_dir>/pkls
python inspect_pickles.py
make build
```

The default path is the direct `rdql-backup` path. It copies the already
selected best model's pickle files from this repo into the package directory.
It does not rebuild Q-tables from `trade_history.csv`.

Manual form:

```bash
cd defirl
make bump
make rdql-backup \
  rdql_base=/absolute/path/to/rl-trade-trainer \
  int_dir=user_data/optimization_results/<candidate>/<alpha_dir>/pkls
python inspect_pickles.py
make build
```

This copies the selected RDQL pickle artifacts into `defirl/src/defirl/`:

```text
defirl/src/defirl/rdql_q_table.pkl
defirl/src/defirl/rdql_state_to_index.pkl
defirl/src/defirl/q_table_a.pkl
defirl/src/defirl/q_table_b.pkl
defirl/src/defirl/rdql_episode_trans.pkl
```

Then it builds the legacy package distribution under:

```text
defirl/dist/
```

All Defirl package artifacts should remain under `defirl/` because it is a
separate package.

`defirl/Makefile` also has a `qtab` target that can rebuild pickle files from
`trade_history.csv`. That path is useful for one-off regeneration, but it is
not the default packaging path. The default compatibility workflow uses
`rdql-backup` so the package receives the exact pickle files from the selected
best model's `pkls/` directory.

`inspect_pickles.py` runs before `make build`. It validates that the copied
files exist inside `defirl/src/defirl/` and can be loaded as pickle objects,
then prints their type, shape/length, and first-object structure.

## Operational Checks

Before running Karakana:

```bash
.venv/bin/python - <<'PY'
import pandas as pd
df = pd.read_csv("user_data/reports/trade_history.csv")
print(df.shape)
print(df.columns.tolist())
print(df["action"].value_counts())
print("episodes:", df["episode_number"].nunique())
PY
```

Expected action labels:

```text
go_long
go_short
do_nothing
```

Expected minimum for Karakana:

```text
At least 10 adapted episodes
Non-empty state/action/reward/next_state columns
Reasonable support for all three actions
```

If `make karakana-offline` succeeds, the plumbing is valid.

If Karakana metrics look poor, that does not necessarily mean the command is
wrong. It may mean the RDQL-generated dataset is imbalanced, too small, too
noisy, or lacks enough examples of one action side.

## Current Limitations

- Karakana local offline training uses `karakana.trainers.offline_trading`
  directly. The public `KarakanaClient` is a REST API client, not a local
  trainer SDK.
- Karakana does not yet write `q_table.pkl` or `state_to_index.pkl`.
- Freqtrade should not consume `karakana_offline_metrics.json` as a live model.
- Production inference must use the side-consistent Karakana bridge or the
  side-consistent RDQL path, not raw three-action argmax.
- The Karakana bridge exports PyTorch checkpoints, not ONNX yet.
- The Karakana bridge still needs Freqtrade backtest/dry-run validation before
  it becomes the default live backend.
- Offline matched-reward diagnostics are not a substitute for Freqtrade
  backtest, dry-run, or live validation.

## Next Implementation Step

The next engineering task is a repeatable Freqtrade validation gate:

```text
run RDQL baseline backtest
-> run Karakana bridge backtest on the same timerange
-> compare P&L, drawdown, long/short expectancy, and action balance
-> if Karakana wins without side collapse, promote it behind config
```

If the Karakana policy wins, add an `offline_trainer` block to
`core/config/agent_config.json` and keep RDQL as an explicit fallback backend.

## Cross-Bundle Links

* describes_pipeline: [quizgen](/scripts_bundle/quizgen.md) (in scripts_bundle)

## Cross-Bundle Links

* uses_tool: [convert_docs_to_okf](/scripts_bundle/convert_docs_to_okf.md) (in scripts_bundle)

## Cross-Bundle Links

* describes_pipeline: [quizgen](/scripts_bundle/quizgen.md) (in scripts_bundle)

## Cross-Bundle Links

* uses_tool: [convert_docs_to_okf](/scripts_bundle/convert_docs_to_okf.md) (in scripts_bundle)
