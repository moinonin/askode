# Freqtrade Karakana Deployment

This deployment keeps the legacy Freqtrade layout: strategy files, sqlite DBs,
configs, policies, logs, and reports stay outside the container under
`user_data`. The Docker image only provides the Freqtrade engine plus Karakana
runtime dependencies and sidecar CLIs.

For beginner-friendly daily operations, start with
`docs/freqtrade-karakana-quickstart.md`. This file is the detailed reference.

## Expected External Layout

Build from an external Freqtrade root directory:

```text
<root-dir>/
  docker/Dockerfile.test_0626
  .dockerignore
  rl-trade-trainer/
    karakana/
      pyproject.toml
      karakana/
      config/
  user_data/
    strategies/<strategy-file>.py
    configbybit.json
    tradesv3bybit.sqlite
    karakana_policy/watch/best_policy.pt
    karakana_policy/watch/offline_preprocessing.json
```

Copy `docs/Dockerfile.test_0626` to:

```text
<root-dir>/docker/Dockerfile.test_0626
```

Copy `docs/template-docker-ignore` to:

```text
<root-dir>/.dockerignore
```

Copy `docs/docker-compose.yml` to:

```text
<root-dir>/docker-compose.yml
```

Copy `docs/freqtrade-root-Makefile` to:

```text
<root-dir>/Makefile
```

## Build

Default build assumes this repo is copied as `<root-dir>/rl-trade-trainer`:

```bash
docker buildx build --cache-to=type=inline --platform=linux/amd64,linux/arm64 -f docker/Dockerfile.test_0626 -t moinonin/freqtrade-karakana:1.0.0 --push .
```

The Dockerfile copies only these Karakana runtime paths:

```text
rl-trade-trainer/karakana/pyproject.toml
rl-trade-trainer/karakana/README.md
rl-trade-trainer/karakana/karakana/
rl-trade-trainer/karakana/config/
```

It intentionally does not copy the whole `rl-trade-trainer/karakana` directory,
because that subtree can contain large generated artifacts such as CSVs, model
checkpoints, build outputs, and research data.

If the repo copy has a different folder name:

```bash
docker build \
  --build-arg RL_TRADE_TRAINER_DIR=<your-repo-folder> \
  -f docker/Dockerfile.test_0626 \
  -t moinonin/freqtrade-karakana:local .
```

If Docker still tries to copy large files, verify that the ignore file is named
exactly `<root-dir>/.dockerignore` and that the build context is `<root-dir>`.
The file `docs/template-docker-ignore` is only a template; Docker does not read
it unless it is copied/renamed to `.dockerignore`.

## Compose

After copying `docs/docker-compose.yml` to `<root-dir>/docker-compose.yml`, run:

```bash
docker compose up -d
```

Use `--build` only when the image inputs changed: Dockerfile, Python
dependencies, or Karakana runtime source copied into the image. Detached mode is
the recommended production mode. The scheduler is a long-lived
sidecar and writes status to both Docker stdout and:

```text
user_data/reports/karakana_threshold_scheduler.log
```

If you remove `-d`, Compose attaches to all service logs. That can make the
scheduler appear to block or dominate the Freqtrade terminal output even though
the other containers are still running. For foreground monitoring, prefer one of
these patterns from `<root-dir>`:

```bash
docker compose up -d
docker compose logs -f freqtrade karakana-shadow-trader karakana-shadow-health
```

Or, if you intentionally want `docker compose up` in the foreground:

```bash
docker compose up --no-attach karakana-threshold-scheduler
```

For a Freqtrade Makefile wrapper, keep startup detached and attach selected logs
as a second command:

```make
karakana-up:
	docker compose -f custom-docker-compose.yml up -d
	docker compose -f custom-docker-compose.yml logs -f freqtrade karakana-shadow-trader karakana-shadow-health
```

The compose file assumes it is executed from `<root-dir>`, so its bind mount is:

```text
./user_data:/freqtrade/user_data
```

If you run it from this repository using `docs/docker-compose.yml`, the mount is
different. The deployment target should be the copied root-level compose file.

## Compose Environment Variables

All four services must share the same `./user_data:/freqtrade/user_data` bind
mount. The paths below are container paths, not host paths. If a path is changed
in one service, update the matching producer/consumer service as well.

### Freqtrade Strategy Service

These variables are read directly by `Strategy322sgo.py` and should be declared
on the `freqtrade` service.

| Variable | Required | Recommended value | Purpose |
| --- | --- | --- | --- |
| `KARAKANA_HISTORICAL_CHECKPOINT` | Yes | `/freqtrade/user_data/karakana_policy/watch/best_policy.pt` | Absolute container path to the Karakana policy checkpoint loaded by Strategy322. |
| `KARAKANA_HISTORICAL_PREPROCESSING` | Yes | `/freqtrade/user_data/karakana_policy/watch/offline_preprocessing.json` | Absolute container path to the preprocessing contract for the checkpoint. |
| `KARAKANA_SHADOW_SIGNAL_EXPORT_PATH` | Yes | `/freqtrade/user_data/freqtrade_signals_karakana.csv` | Signal CSV produced continuously by Strategy322 and consumed by the shadow trader. |
| `KARAKANA_HISTORICAL_THRESHOLD_GOVERNOR_ENABLED` | Yes | `1` | Enables dynamic threshold overrides from Directional Strategy Health. |
| `KARAKANA_HISTORICAL_STRATEGY_HEALTH_PATH` | Yes when governor is enabled | `/freqtrade/user_data/reports/directional_strategy_health.csv` | Health CSV consumed by Strategy322 to adjust long/short Q-margin thresholds. |
| `KARAKANA_HISTORICAL_REQUIRE_ARMED` | Strongly recommended live | `1` | Blocks new entries until the health CSV has sufficient evidence. Exits remain allowed. |
| `KARAKANA_HISTORICAL_MIN_ARMED_ROWS` | Recommended | `256` | Minimum latest health-window row count required before entries can arm. Keep this aligned with `KARAKANA_HEALTH_WINDOW_SIZE`; threshold apply patches both. |
| `KARAKANA_HISTORICAL_MIN_ARMED_LONG_COUNT` | Recommended | `64` | Minimum long-side virtual trades required before entries can arm. |
| `KARAKANA_HISTORICAL_MIN_ARMED_SHORT_COUNT` | Recommended | `64` | Minimum short-side virtual trades required before entries can arm. |
| `KARAKANA_HISTORICAL_MIN_ARMED_REGIME_CONFIDENCE` | Recommended | `0.0` | Minimum latest regime confidence required before entries can arm. |
| `KARAKANA_HISTORICAL_MIN_LONG_Q_MARGIN` | Optional | unset when governor is enabled | Static long-entry Q-margin floor used when the governor does not override it. |
| `KARAKANA_HISTORICAL_MIN_SHORT_Q_MARGIN` | Optional | unset when governor is enabled | Static short-entry Q-margin floor used when the governor does not override it. |
| `KARAKANA_HISTORICAL_MIN_Q_MARGIN` | Optional legacy fallback | unset | Legacy symmetric fallback for long/short margins. Prefer directional variables. |

The compose template also declares Freqtrade convenience variables. They are not
read by the strategy directly, but they make the intended runtime contract clear.

| Variable | Required | Recommended value | Purpose |
| --- | --- | --- | --- |
| `FT_CONFIG` | Recommended | `/freqtrade/user_data/configbybit.json` | Freqtrade config path mirrored by the `freqtrade trade --config` argument. |
| `FT_DB_URL` | Recommended | `sqlite:////freqtrade/user_data/tradesv3bybit.sqlite` | External sqlite DB URL mirrored by `--db-url`. |
| `FT_LOG_FILE` | Recommended | `/freqtrade/user_data/logs/freqtrade.log` | Freqtrade log path mirrored by `--logfile`. |
| `FT_STRATEGY` | Recommended | `Strategy322sgo` | Strategy class name mirrored by `--strategy`. Change this when moving to a new versioned Freqtrade strategy. |
| `FT_STRATEGY_FILE` | Recommended | `Strategy322sgo.py` | Strategy file expected under `user_data/strategies/`. Usually this is `${FT_STRATEGY}.py`, but it is explicit so deployment can support renamed files. |
| `FT_USER_DATA_DIR` | Recommended | `/freqtrade/user_data` | Shared mounted Freqtrade user data directory. |

### Shadow Trader Service

The shadow trader converts live Strategy322 signal rows into virtual trades.
In the provided compose file these variables are mirrored by explicit CLI
arguments. If you change one, keep the matching CLI argument in sync unless you
also rewrite the command to expand the environment variable.

| Variable | Required | Recommended value | Purpose |
| --- | --- | --- | --- |
| `KARAKANA_SHADOW_SOURCE` | Yes | `/freqtrade/user_data/freqtrade_signals_karakana.csv` | Signal CSV produced by Strategy322. Must match `KARAKANA_SHADOW_SIGNAL_EXPORT_PATH`. |
| `KARAKANA_SHADOW_POLICY_ROOT` | Yes | `/freqtrade/user_data/karakana_policy/watch` | Directory containing `best_policy.pt` and `offline_preprocessing.json`, or `latest.json`. |
| `KARAKANA_SHADOW_OUTPUT_CSV` | Yes | `/freqtrade/user_data/reports/karakana_shadow_trade_history.csv` | Virtual trade history written by the shadow trader and consumed by shadow health. |
| `KARAKANA_SHADOW_STATE_PATH` | Yes | `/freqtrade/user_data/reports/karakana_shadow_trader_state.json` | Rolling cursor so the shadow trader resumes from the last processed signal row. |
| `KARAKANA_SHADOW_HORIZON_ROWS` | Recommended | `12` | Number of future signal rows used to compute virtual trade reward. |
| `KARAKANA_SHADOW_FEE_BPS` | Recommended | `0` | Fee deducted from virtual reward, in basis points. |
| `KARAKANA_SHADOW_LONG_THRESHOLD` | Recommended | `1.3` | Base long-side Q-margin admission threshold for virtual trades. |
| `KARAKANA_SHADOW_SHORT_THRESHOLD` | Recommended | `0.07` | Base short-side Q-margin admission threshold for virtual trades. |
| `KARAKANA_SHADOW_ADMISSION_MODE` | Recommended | `winner` | If both directions pass, keep only the strongest threshold-adjusted candidate. |
| `KARAKANA_SHADOW_POLL_SECONDS` | Recommended | `60` | Watch-loop polling interval. |

The underlying policy object also supports these generic environment variables,
but the shadow trader normally passes explicit thresholds and disables the
governor for virtual-trade generation.

| Variable | Required | Recommended value | Purpose |
| --- | --- | --- | --- |
| `KARAKANA_MIN_LONG_ACTION_MARGIN` | Optional | unset | Generic long action-margin default for `KarakanaOfflinePolicy`. |
| `KARAKANA_MIN_SHORT_ACTION_MARGIN` | Optional | unset | Generic short action-margin default for `KarakanaOfflinePolicy`. |
| `KARAKANA_MIN_ACTION_MARGIN` | Optional legacy fallback | unset | Legacy symmetric generic action-margin fallback. |
| `KARAKANA_THRESHOLD_GOVERNOR_ENABLED` | Optional | unset or `0` | Generic policy governor flag. Strategy322 uses the historical-prefixed governor variables instead. |
| `KARAKANA_STRATEGY_HEALTH_PATH` | Optional | unset | Generic policy health path. Strategy322 uses `KARAKANA_HISTORICAL_STRATEGY_HEALTH_PATH`. |

### Shadow Health Service

The shadow health service converts virtual trades into
`directional_strategy_health.csv`, which Strategy322 consumes for arming and
dynamic threshold governance. As with the shadow trader, the provided compose
file mirrors these variables through explicit CLI arguments.

| Variable | Required | Recommended value | Purpose |
| --- | --- | --- | --- |
| `KARAKANA_HEALTH_SOURCE` | Yes | `/freqtrade/user_data/reports/karakana_shadow_trade_history.csv` | Virtual trade history produced by the shadow trader. Must match `KARAKANA_SHADOW_OUTPUT_CSV`. |
| `KARAKANA_HEALTH_OUTPUT_CSV` | Yes | `/freqtrade/user_data/reports/directional_strategy_health.csv` | Health/governor CSV consumed by Strategy322. Must match `KARAKANA_HISTORICAL_STRATEGY_HEALTH_PATH`. |
| `KARAKANA_HEALTH_WINDOW_SIZE` | Recommended | `256` | Rolling virtual-trade window used to compute directional health. Keep aligned with `KARAKANA_HISTORICAL_MIN_ARMED_ROWS`; threshold apply patches both. |
| `KARAKANA_HEALTH_WINDOW_STEP` | Recommended | `128` | Step between health windows. Smaller values update more frequently. |
| `KARAKANA_HEALTH_BASE_LONG_THRESHOLD` | Recommended | `1.3` | Base long threshold before health-derived adjustments. Keep aligned with shadow long threshold. |
| `KARAKANA_HEALTH_BASE_SHORT_THRESHOLD` | Recommended | `0.07` | Base short threshold before health-derived adjustments. Keep aligned with shadow short threshold. |
| `KARAKANA_HEALTH_POLL_SECONDS` | Recommended | `60` | Watch-loop polling interval. |

The CLI also has optional tuning flags that are not exposed in the current
compose template: `--tracker-window`, `--ema-weight`, `--alpha-floor`,
`--v-panic`, `--horizon-floor`, and `--fragility-decay`. Use these only when
you are intentionally changing the strategy-health dynamics.

### Threshold Scheduler Service

The optional fourth service, `karakana-threshold-scheduler`, periodically runs
the live threshold sweep. By default it is conservative: it writes
recommendations but does not patch compose and does not restart sidecars unless
explicitly enabled.

| Variable | Required | Recommended value | Purpose |
| --- | --- | --- | --- |
| `KARAKANA_THRESHOLD_SCHEDULER_APPLY` | Recommended | `0` initially, `1` after validation | If `1`, viable recommendations patch the compose file. |
| `KARAKANA_THRESHOLD_SCHEDULER_RESTART_SIDECARS` | Recommended | `0` initially, `1` after validation | If `1`, restart `karakana-shadow-trader` and `karakana-shadow-health` after a successful patch. Requires Docker socket mount. |
| `KARAKANA_THRESHOLD_SCHEDULER_RUN_ON_START` | Recommended | `0` | If `1`, run once immediately when the scheduler container starts before sleeping. |
| `KARAKANA_THRESHOLD_SCHEDULER_MIN_SIGNAL_ROWS` | Recommended | `20000` | Skip safely until the signal CSV has at least this many rows. |
| `KARAKANA_THRESHOLD_SCHEDULER_MIN_NEW_ROWS` | Recommended | `25000` | Target new-row amount for adaptive interval selection. |
| `KARAKANA_THRESHOLD_SCHEDULER_TAIL_ROWS` | Recommended | `50000` | Latest signal rows used by the sweep. |
| `KARAKANA_THRESHOLD_SCHEDULER_DEFAULT_INTERVAL_SECONDS` | Recommended | `7200` | Default scheduler interval, two hours. |
| `KARAKANA_THRESHOLD_SCHEDULER_INTERVAL_SECONDS_VALUES` | Optional | `3600,7200,10800,21600` | Candidate intervals. The scheduler can adapt based on observed row growth. |
| `KARAKANA_THRESHOLD_SCHEDULER_LONG_RANGE` | Recommended | `1.0:3.0:0.1` | Long base threshold sweep grid. |
| `KARAKANA_THRESHOLD_SCHEDULER_SHORT_RANGE` | Recommended | `0.05:1.5:0.05` | Short base threshold sweep grid. |
| `KARAKANA_THRESHOLD_SCHEDULER_HEALTH_WINDOW_SIZES` | Recommended | `128,256,512,1024` | Candidate health window sizes. |
| `KARAKANA_THRESHOLD_SCHEDULER_HEALTH_WINDOW_STEPS` | Recommended | `32,64,128,256` | Candidate health window steps. |
| `KARAKANA_THRESHOLD_SCHEDULER_HEALTH_POLL_SECONDS_VALUES` | Recommended | `60` | Candidate shadow-health polling intervals. |
| `KARAKANA_THRESHOLD_SCHEDULER_MONITOR` | Recommended | `1` | If `1`, run the runtime CSV monitor at each scheduler cycle. |
| `KARAKANA_THRESHOLD_SCHEDULER_POLICY_RESET` | Recommended | `1` | If `1`, fingerprint `best_policy.pt` and `offline_preprocessing.json`; when they change, archive/reset policy-derived runtime artifacts. |
| `KARAKANA_THRESHOLD_SCHEDULER_POLICY_RESET_FORCE` | Optional | `0` | If `1`, force one reset on scheduler start/run. Set back to `0` after use. |
| `KARAKANA_THRESHOLD_SCHEDULER_POLICY_RESET_ON_FIRST_SEEN` | Optional | `0` | If `1`, reset policy-derived artifacts even when no prior fingerprint exists. Usually keep `0` to avoid wiping a new deployment accidentally. |
| `KARAKANA_RUNTIME_SIGNALS_MAX_ROWS` | Recommended | `250000` | Cap `user_data/freqtrade_signals_karakana.csv` after archiving. Set `0` to disable capping. |
| `KARAKANA_RUNTIME_SHADOW_MAX_ROWS` | Recommended | `100000` | Cap shadow trade history after archiving. Set `0` to disable capping. |
| `KARAKANA_RUNTIME_HEALTH_MAX_ROWS` | Recommended | `20000` | Cap directional health history after archiving. Set `0` to disable capping. |
| `KARAKANA_RUNTIME_COUNT_TAIL_ROWS` | Optional | `10000` | Tail rows used for action/side/status counts in the runtime monitor. |

Scheduler artifacts:

```text
user_data/reports/karakana_threshold_scheduler.log
user_data/reports/karakana_threshold_scheduler_state.json
user_data/reports/karakana_live_threshold_sweep.csv
user_data/reports/karakana_live_threshold_sweep.json
user_data/reports/karakana_runtime_status.json
user_data/reports/archive/*.csv.gz
```

Policy change behavior:

```text
preserved:
  user_data/freqtrade_signals_karakana.csv

archived then removed:
  user_data/reports/karakana_shadow_trade_history.csv
  user_data/reports/directional_strategy_health.csv

removed:
  user_data/reports/karakana_shadow_trader_state.json
  user_data/reports/karakana_shadow_trade_history_summary.json
```

This lets the shadow trader replay the existing signal CSV with the new policy
and rebuild health from policy-consistent virtual trades.

For a one-shot reset immediately after manually replacing policy artifacts:

```bash
make -f freqtrade-karakana-thresholds.mk karakana-threshold-scheduler \
  threshold_scheduler_once=1 \
  threshold_scheduler_policy_reset_force=1
```

If using the scheduler container instead, set
`KARAKANA_THRESHOLD_SCHEDULER_POLICY_RESET_FORCE=1`, recreate only
`karakana-threshold-scheduler`, then set it back to `0` after the reset is
recorded in `karakana_threshold_scheduler_state.json`.

The scheduler service mounts the Freqtrade root at `/work` and uses:

```text
/work/rl-trade-trainer/artifacts/karakana_analysis/threshold_scheduler.py
/work/rl-trade-trainer/artifacts/karakana_analysis/sweep_live_shadow_thresholds.py
/work/rl-trade-trainer/artifacts/karakana_analysis/monitor_karakana_runtime.py
```

If `KARAKANA_THRESHOLD_SCHEDULER_RESTART_SIDECARS=1`, it also needs:

```text
/var/run/docker.sock:/var/run/docker.sock
```

This allows the scheduler to restart only:

```text
karakana-shadow-trader
karakana-shadow-health
```

Do not enable sidecar restarts until recommendation-only mode has produced
sensible sweep artifacts.

## Runtime

The image is built from `freqtradeorg/freqtrade:2026.3` and adds:

- Karakana runtime package.
- CPU Torch runtime.
- `karakana-shadow-trader`.
- `karakana-shadow-health`.

It does not copy strategy/config/sqlite/policy files into the image.

The Dockerfile installs NumPy/Pandas explicitly, then installs Karakana with
`--no-deps`. This avoids mixed NumPy Python files and compiled extensions in
`/home/ftuser/.local`, which can otherwise produce errors such as:

```text
ImportError: cannot import name '_finfo_get_realdtype' from numpy._core._multiarray_umath
```

If this happens after changing dependency layers, rebuild without cache:

```bash
docker build --no-cache -f docker/Dockerfile.test_0626 -t moinonin/freqtrade-karakana:local .
```

The runtime loop is four processes/services sharing the same `user_data` mount:

```text
freqtrade
  writes user_data/freqtrade_signals_karakana.csv
  reads user_data/reports/directional_strategy_health.csv

karakana-shadow-trader
  reads user_data/freqtrade_signals_karakana.csv
  reads user_data/karakana_policy/watch/
  writes user_data/reports/karakana_shadow_trade_history.csv

karakana-shadow-health
  reads user_data/reports/karakana_shadow_trade_history.csv
  writes user_data/reports/directional_strategy_health.csv

karakana-threshold-scheduler
  reads signal, policy, health, and compose files
  writes threshold sweep reports and runtime status
  can patch compose and restart shadow sidecars when enabled
```

The active strategy file should be present at:

```text
user_data/strategies/<strategy-file>.py
```

Freqtrade can then discover it normally with:

```bash
freqtrade trade \
  --logfile /freqtrade/user_data/logs/freqtrade.log \
  --db-url sqlite:////freqtrade/user_data/tradesv3bybit.sqlite \
  --config /freqtrade/user_data/configbybit.json \
  --strategy "${FT_STRATEGY:-Strategy322sgo}"
```

## Safety Gate

For live dynamic thresholds, the active strategy should run with:

```bash
KARAKANA_HISTORICAL_THRESHOLD_GOVERNOR_ENABLED=1
KARAKANA_HISTORICAL_REQUIRE_ARMED=1
KARAKANA_HISTORICAL_STRATEGY_HEALTH_PATH=/freqtrade/user_data/reports/directional_strategy_health.csv
KARAKANA_SHADOW_SIGNAL_EXPORT_PATH=/freqtrade/user_data/freqtrade_signals_karakana.csv
```

With arming enabled, entries remain blocked until
`directional_strategy_health.csv` has enough evidence. Defaults are `256` rows,
`64` long samples, and `64` short samples. Row count and regime confidence are
global gates. Long and short sample counts should be enforced directionally by
the strategy: low long evidence should block long entries, not short entries,
and vice versa. Exits remain available.

## Frequent Base-Threshold Sweeps

The base thresholds should be treated as runtime calibration values, not fixed
constants. Use the live threshold sweep after the signal CSV has accumulated
enough recent rows. The sweep reads the current signal stream, evaluates the
mounted Karakana policy over a long/short threshold grid, evaluates candidate
shadow-health window sizes and steps, writes a report, and can optionally patch
the compose file. Poll seconds is treated as an operational cadence candidate;
it can be selected from a supplied list with an optional penalty, but it is not
a model-quality signal by itself.

From this repository:

```bash
make karakana-live-threshold-sweep
```

Outputs:

```text
user_data/reports/karakana_live_threshold_sweep.csv
user_data/reports/karakana_live_threshold_sweep.json
```

To patch the compose file from this repository:

```bash
make karakana-live-threshold-apply live_threshold_compose_file=custom-docker-compose.yml
```

For the external Freqtrade root, copy or include:

```text
docs/freqtrade-karakana-thresholds.mk
```

The external fragment runs the sweep inside
`moinonin/freqtrade-karakana:1.0.0` with `<freqtrade-root>` mounted at `/work`,
so it does not require Torch, Pandas, or Karakana to be installed on the host.
Then run from `<freqtrade-root>`:

```bash
make -f freqtrade-karakana-thresholds.mk karakana-live-threshold-sweep
make -f freqtrade-karakana-thresholds.mk karakana-live-threshold-apply
make -f freqtrade-karakana-thresholds.mk karakana-threshold-scheduler threshold_scheduler_once=1
make -f freqtrade-karakana-thresholds.mk restart-karakana-sidecars
```

Override the image if needed:

```bash
make -f freqtrade-karakana-thresholds.mk karakana-live-threshold-sweep \
  THRESHOLD_IMAGE=moinonin/freqtrade-karakana:1.0.1
```

If you include the fragment from the existing external `Makefile`, the commands
become plain `make karakana-live-threshold-sweep`,
`make karakana-live-threshold-apply`, and `make restart-karakana-sidecars`.

Useful overrides:

```bash
make -f freqtrade-karakana-thresholds.mk karakana-live-threshold-sweep \
  live_threshold_long_range=1.0:3.0:0.1 \
  live_threshold_short_range=0.05:1.5:0.05 \
  live_threshold_health_window_sizes=128,256,512,1024 \
  live_threshold_health_window_steps=32,64,128,256 \
  live_threshold_health_poll_seconds_values=30,60,120 \
  live_threshold_tail_rows=20000 \
  live_threshold_horizon_mode=pair
```

`live_threshold_horizon_mode=pair` is the recommended default for multi-pair
live streams. It computes virtual reward against a future row from the same
pair. Use `live_threshold_horizon_mode=row` only when you intentionally want to
match the older row-offset shadow-trader reward approximation.

When `karakana-live-threshold-apply` patches the compose file, it uses the
recommended long threshold, short threshold, health window size, health window
step, and health poll seconds unless explicit `live_threshold_apply_*` values
are supplied. It updates both the environment values and the mirrored CLI
arguments:

```text
KARAKANA_SHADOW_LONG_THRESHOLD
KARAKANA_SHADOW_SHORT_THRESHOLD
KARAKANA_HEALTH_BASE_LONG_THRESHOLD
KARAKANA_HEALTH_BASE_SHORT_THRESHOLD
--long-threshold
--short-threshold
--base-long-threshold
--base-short-threshold
```

It can also patch the shadow-health rolling-window settings:

```text
KARAKANA_HEALTH_WINDOW_SIZE
KARAKANA_HISTORICAL_MIN_ARMED_ROWS
KARAKANA_HEALTH_WINDOW_STEP
KARAKANA_HEALTH_POLL_SECONDS
--window-size
--window-step
--poll-seconds
```

Example, forcing the active 128-row / 32-step / 60-second cadence instead of
using the sweep recommendation:

```bash
make -f freqtrade-karakana-thresholds.mk karakana-live-threshold-apply \
  live_threshold_apply_health_window_size=128 \
  live_threshold_apply_health_window_step=32 \
  live_threshold_apply_health_poll_seconds=60
```

The patch creates a `.bak` copy of the compose file before writing changes.
Recreate `karakana-shadow-trader` and `karakana-shadow-health` after applying
new base thresholds. Freqtrade itself only needs recreation if you also changed
Strategy322 environment variables.

## For Freqtrade To Execute Properly You Need

```text
<freqtrade-root>/
  Makefile
  custom-docker-compose.yml
  freqtrade-karakana-thresholds.mk
  docker/Dockerfile.test_0626
  .dockerignore

  rl-trade-trainer/
    karakana/
    artifacts/karakana_analysis/
    docs/

  user_data/
    configbybit.json
    tradesv3bybit.sqlite
    strategies/
    karakana_policy/watch/
    reports/
    logs/
```

Required details:

- `custom-docker-compose.yml` must define the four services:
  `freqtrade`, `karakana-shadow-trader`, `karakana-shadow-health`, and
  `karakana-threshold-scheduler`.
- `user_data/strategies/` must contain the active strategy file declared by
  `FT_STRATEGY_FILE`, and the class name must match `FT_STRATEGY`.
- `user_data/configbybit.json` must be the Freqtrade config passed to
  `freqtrade trade --config`.
- `user_data/tradesv3bybit.sqlite` is the external Freqtrade trade database.
  It can be an existing DB or a writable path that Freqtrade can create.
- `user_data/karakana_policy/watch/` must contain the current Karakana policy
  export. At minimum it needs `best_policy.pt` and
  `offline_preprocessing.json`. If using rolling exports, keep `latest.json`
  there too.
- `user_data/reports/` must be writable. It receives signal CSVs, shadow trade
  history, directional health, threshold sweep reports, and scheduler state.
- `user_data/logs/` must be writable for the Freqtrade log.
- `rl-trade-trainer/karakana/` must include the runtime package used by the
  Docker image build and the sidecar imports.
- `rl-trade-trainer/artifacts/karakana_analysis/` must include the shadow,
  health, threshold sweep, and scheduler scripts.
- `freqtrade-karakana-thresholds.mk` is required only for manual host-side
  sweep/apply/restart commands.
- `/var/run/docker.sock:/var/run/docker.sock` is required only if
  `KARAKANA_THRESHOLD_SCHEDULER_RESTART_SIDECARS=1`.
