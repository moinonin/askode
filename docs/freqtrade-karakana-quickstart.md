# Freqtrade Karakana Quickstart

This is the operator guide for running the Freqtrade + Karakana stack day to
day. It assumes a separate Freqtrade root directory that contains this repo as
`rl-trade-trainer/`.

Use `docs/freqtrade-karakana-deployment.md` as the detailed reference. Use this
file when you just need to run, check, and maintain the system.

## Mental Model

Four containers run together:

```text
freqtrade
  Runs the strategy.
  Writes user_data/freqtrade_signals_karakana.csv.
  Reads user_data/reports/directional_strategy_health.csv.

karakana-shadow-trader
  Replays signal rows as virtual trades with the current Karakana policy.
  Writes user_data/reports/karakana_shadow_trade_history.csv.

karakana-shadow-health
  Converts virtual trades into directional health and dynamic thresholds.
  Writes user_data/reports/directional_strategy_health.csv.

karakana-threshold-scheduler
  Periodically sweeps thresholds, monitors CSV sizes, detects policy changes,
  and optionally patches/restarts the shadow sidecars.
```

Runtime files live on the host under `user_data/`. Recreating containers does
not delete these files.

## One-Time Setup

From this repo, copy these files into the external Freqtrade root:

```text
docs/Dockerfile.test_0626            -> <freqtrade-root>/docker/Dockerfile.test_0626
docs/template-docker-ignore          -> <freqtrade-root>/.dockerignore
docs/docker-compose.yml              -> <freqtrade-root>/custom-docker-compose.yml
docs/freqtrade-root-Makefile         -> <freqtrade-root>/Makefile
docs/freqtrade-karakana-thresholds.mk -> <freqtrade-root>/freqtrade-karakana-thresholds.mk
```

The external Freqtrade root must contain:

```text
<freqtrade-root>/
  custom-docker-compose.yml
  Makefile
  freqtrade-karakana-thresholds.mk
  docker/Dockerfile.test_0626
  .dockerignore
  rl-trade-trainer/
  user_data/
```

Minimum required `user_data/` files:

```text
user_data/configbybit.json
user_data/strategies/<strategy-file>.py
user_data/karakana_policy/watch/best_policy.pt
user_data/karakana_policy/watch/offline_preprocessing.json
user_data/reports/
user_data/logs/
```

In `custom-docker-compose.yml`, confirm the active strategy:

```yaml
- FT_STRATEGY=Strategy322sgo
- FT_STRATEGY_FILE=Strategy322sgo.py
```

For a new strategy version, change only those two values, for example:

```yaml
- FT_STRATEGY=Strategy323sgo
- FT_STRATEGY_FILE=Strategy323sgo.py
```

## Build The Image

Build only when Dockerfile, Python dependencies, or Karakana runtime code
changed.

For the current AMD64 runtime:

```bash
cd <freqtrade-root>
docker buildx build --platform=linux/amd64 \
  -f docker/Dockerfile.test_0626 \
  -t moinonin/freqtrade-karakana:1.0.0 \
  --load .
```

If you push to a registry instead:

```bash
docker buildx build --cache-to=type=inline --platform=linux/amd64 \
  -f docker/Dockerfile.test_0626 \
  -t moinonin/freqtrade-karakana:1.0.0 \
  --push .
```

You do not need to rebuild for strategy edits, policy artifacts, compose env
changes, sqlite changes, or report CSV changes because those are mounted from
`user_data/`.

## Start

From `<freqtrade-root>`:

```bash
make start-cluster
```

Follow useful logs without scheduler noise:

```bash
make logs-cluster
```

Or start and immediately follow logs:

```bash
make start-cluster-logs
```

## Daily Check

Run this once or twice a day:

```bash
make daily-check
```

Look for:

```text
All containers Up/healthy.
freqtrade_signals_karakana.csv row count increasing.
karakana_shadow_trade_history.csv row count increasing.
directional_strategy_health.csv has recent rows.
karakana_runtime_status.json exists and has no obvious missing files.
```

If you want raw commands:

```bash
docker compose -f custom-docker-compose.yml ps
wc -l user_data/freqtrade_signals_karakana.csv \
  user_data/reports/karakana_shadow_trade_history.csv \
  user_data/reports/directional_strategy_health.csv
tail -n 3 user_data/reports/directional_strategy_health.csv
python3 -m json.tool user_data/reports/karakana_runtime_status.json | tail -n 80
```

## Read Logs

Normal logs:

```bash
make logs-cluster
```

Only Freqtrade:

```bash
docker compose -f custom-docker-compose.yml logs -f freqtrade
```

Only Karakana sidecars:

```bash
docker compose -f custom-docker-compose.yml logs -f karakana-shadow-trader karakana-shadow-health
```

Scheduler audit log:

```bash
tail -n 100 user_data/reports/karakana_threshold_scheduler.log
```

## Arming And Entry Blocking

`KARAKANA_HISTORICAL_REQUIRE_ARMED=1` means entries are blocked until health has
enough evidence. Exits still work.

Global checks:

```text
rows >= KARAKANA_HISTORICAL_MIN_ARMED_ROWS
regime_confidence >= KARAKANA_HISTORICAL_MIN_ARMED_REGIME_CONFIDENCE
```

Directional checks:

```text
long entries require long_count >= KARAKANA_HISTORICAL_MIN_ARMED_LONG_COUNT
short entries require short_count >= KARAKANA_HISTORICAL_MIN_ARMED_SHORT_COUNT
```

A low `long_count` should not block shorts, and a low `short_count` should not
block longs.

If logs show:

```text
rows 256 < 1024
```

then `KARAKANA_HISTORICAL_MIN_ARMED_ROWS` is not aligned with
`KARAKANA_HEALTH_WINDOW_SIZE`. Set them to the same value and recreate
Freqtrade:

```bash
docker compose -f custom-docker-compose.yml up -d --force-recreate freqtrade
```

## Threshold Sweeps

Manual recommendation only:

```bash
make -f freqtrade-karakana-thresholds.mk karakana-live-threshold-sweep
```

Apply the latest recommendation manually:

```bash
make -f freqtrade-karakana-thresholds.mk karakana-live-threshold-apply
docker compose -f custom-docker-compose.yml up -d --force-recreate \
  karakana-shadow-trader karakana-shadow-health
```

The apply command patches:

```text
KARAKANA_SHADOW_LONG_THRESHOLD
KARAKANA_SHADOW_SHORT_THRESHOLD
KARAKANA_HEALTH_BASE_LONG_THRESHOLD
KARAKANA_HEALTH_BASE_SHORT_THRESHOLD
KARAKANA_HEALTH_WINDOW_SIZE
KARAKANA_HEALTH_WINDOW_STEP
KARAKANA_HEALTH_POLL_SECONDS
KARAKANA_HISTORICAL_MIN_ARMED_ROWS
matching CLI arguments
```

If `KARAKANA_HISTORICAL_MIN_ARMED_ROWS` changed, also recreate Freqtrade:

```bash
docker compose -f custom-docker-compose.yml up -d --force-recreate freqtrade
```

## Automatic Threshold Apply

The scheduler can apply recommendations and restart shadow sidecars
automatically. In `custom-docker-compose.yml`:

```yaml
- KARAKANA_THRESHOLD_SCHEDULER_APPLY=1
- KARAKANA_THRESHOLD_SCHEDULER_RESTART_SIDECARS=1
```

Then recreate only the scheduler:

```bash
docker compose -f custom-docker-compose.yml up -d --force-recreate karakana-threshold-scheduler
```

This requires the Docker socket mount:

```yaml
- /var/run/docker.sock:/var/run/docker.sock
```

The scheduler restarts:

```text
karakana-shadow-trader
karakana-shadow-health
```

It does not restart Freqtrade unless you do it manually.

## Policy Artifact Changes

Policy artifacts:

```text
user_data/karakana_policy/watch/best_policy.pt
user_data/karakana_policy/watch/offline_preprocessing.json
```

When these change, old shadow trades and old health are no longer comparable.
The scheduler fingerprints the policy artifacts and can reset policy-derived
files.

Manual forced reset after replacing policy artifacts:

```bash
make -f freqtrade-karakana-thresholds.mk karakana-threshold-scheduler \
  threshold_scheduler_once=1 \
  threshold_scheduler_policy_reset_force=1
```

Then recreate policy consumers:

```bash
docker compose -f custom-docker-compose.yml up -d --force-recreate \
  freqtrade karakana-shadow-trader karakana-shadow-health karakana-threshold-scheduler
```

Preserved:

```text
user_data/freqtrade_signals_karakana.csv
```

Archived then removed:

```text
user_data/reports/karakana_shadow_trade_history.csv
user_data/reports/directional_strategy_health.csv
```

Removed:

```text
user_data/reports/karakana_shadow_trader_state.json
user_data/reports/karakana_shadow_trade_history_summary.json
```

## CSV Growth

The runtime monitor writes:

```text
user_data/reports/karakana_runtime_status.json
```

Default active CSV caps:

```text
signals:       250000 rows
shadow trades: 100000 rows
health:         20000 rows
```

Before capping, it archives to:

```text
user_data/reports/archive/*.csv.gz
```

Run monitor manually:

```bash
make -f freqtrade-karakana-thresholds.mk karakana-runtime-monitor
```

## Restart Rules

Use this after compose env changes or strategy file changes:

```bash
docker compose -f custom-docker-compose.yml up -d --force-recreate freqtrade
```

Use this after threshold changes:

```bash
docker compose -f custom-docker-compose.yml up -d --force-recreate \
  karakana-shadow-trader karakana-shadow-health
```

Use this after scheduler env changes:

```bash
docker compose -f custom-docker-compose.yml up -d --force-recreate karakana-threshold-scheduler
```

Use this only when you want every service recreated:

```bash
make restart-cluster
```

## Stop

Preferred:

```bash
docker compose -f custom-docker-compose.yml down
```

If you are using the root Makefile:

```bash
make stop-cluster
```

`down` or container recreation does not delete `user_data/`.

## Common Problems

`No module named karakana.evx`

```text
Use a Karakana build where karakana.metrics treats EVX as optional. Current
runtime does not need EVX for HistoricalTrading-v0.
```

`missing_strategy_health`

```text
Shadow health has not produced directional_strategy_health.csv yet.
Check karakana-shadow-trader and karakana-shadow-health logs.
```

`long_count 0 < 64`

```text
Long entries are blocked. Shorts can still trade if short_count passes and the
strategy has side-specific arming logic.
```

`short_count 0 < 64`

```text
Short entries are blocked. Longs can still trade if long_count passes.
```

`rows 256 < 1024`

```text
Set KARAKANA_HISTORICAL_MIN_ARMED_ROWS to match KARAKANA_HEALTH_WINDOW_SIZE.
Then recreate Freqtrade.
```

Docker build copies huge files:

```text
Check that docs/template-docker-ignore was copied to <freqtrade-root>/.dockerignore.
The filename must be exactly .dockerignore.
```

Scheduler floods the terminal:

```text
Run compose detached and follow selected logs:
make start-cluster
make logs-cluster
```

