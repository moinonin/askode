# Freqtrade RL-Karakana Strategy Specification

**Version:** 1.0  
**Status:** Active Development  
**Environment:** Freqtrade (Dry-run / Live) — 1m timeframe  
**Policy Source:** Karakana Offline-RL (OfflineTradingQPolicy)  
**Last Updated:** 2025-07-05

---

## 1. Overview

### 1.1 Purpose
This document specifies a high-frequency, reinforcement-learning-driven directional trading strategy for Freqtrade operating on 1-minute candles. The strategy combines a pre-trained offline Q-learning policy (Karakana OfflineTradingQPolicy) with a multi-layer, real-time risk management framework (Karakana SGO / StreamingAlphaMonitor) and post-exit reversal logic (SGO Shield).

### 1.2 Objectives
- Capture high-confidence directional entries via a learned Q-policy distilled from historical 1m microstructure
- Hold winning trades by gating fixed-ROI exits behind a real-time health monitor (ROI gating)
- Detect early structural deterioration (pullbacks, decline streaks, horizon collapse) and exit before large drawdowns
- Automatically schedule counter-directional reversal entries after structural collapse with a same-direction cooldown
- Dynamically adapt entry thresholds via an external health governor CSV

### 1.3 Scope
- **Timeframe:** 1m candles (live); 1m historical for training
- **Direction:** Long & Short (hedge mode compatible)
- **Asset Class:** Liquid crypto perpetuals / spot (sufficient 1m volume)
- **Deployment:** Freqtrade dry-run → dry-run live → live (per exchange API limits)

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        FREQTRADE STRATEGY                           │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐   ┌──────────────────────────────────────┐   │
│  │  RL Entry Policy │   │      Karakana SGO Monitor            │   │
│  │  (OfflineTrading │   │  (StreamingAlphaMonitor per trade)   │   │
│  │   QPolicy)       │   │  - Peak PnL tracking                 │   │
│  │  - 4 features    │   │  - Pullback / deadband scoring       │   │
│  │  - 3 actions     │   │  - Sliding-window collapse detect    │   │
│  │  - Q-margin gate │   │  - Early-exit triggers               │   │
│  └────────┬─────────┘   └───────────────┬──────────────────────┘   │
│           │                              │                          │
│           ▼                              ▼                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    EXIT & RISK LAYER                          │   │
│  │  ┌──────────────┐  ┌─────────────────┐  ┌────────────────┐   │
│  │  │ Decaying SL  │  │ Tightened SL on │  │ ROI Gate (ROI  │   │
│  │  │ (exp decay)  │  │ degeneration    │  │ gated by SGO)  │   │
│  │  └──────────────┘  └─────────────────┘  └────────────────┘   │
│  └──────────────────────────────────────────────────────────────┘   │
│           │                              │                          │
│           ▼                              ▼                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                  POST-EXIT LOGIC (SGO Shield 1)              │   │
│  │  - Structural collapse → schedule counter-direction reversal │   │
│  │  - Reversal valid for N minutes (reversal_expiry_minutes)    │   │
│  │  - Same-direction cooldown (same_direction_cooldown_minutes) │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Entry Signal — RL Policy

### 3.1 Policy Definition
- **Class:** `karakana.agents.offline_rl_trading.OfflineTradingQPolicy`
- **Training:** Offline Q-learning on historical 1m candles (Karakana framework)
- **Actions:** `{0: go_long, 1: go_short, 2: do_nothing}`
- **Observation Space (4 features, normalised):**

| Index | Feature | Description |
|-------|---------|-------------|
| 0 | `ask` | Volume-weighted ask price approximation |
| 1 | `bid` | Volume-weighted bid price approximation |
| 2 | `sma_compare` | `(bid - SMA20(bid)) / SMA20(bid)` — distance from 20-period SMA |
| 3 | `candidate_is_short` | Binary flag: 1 = evaluating short, 0 = evaluating long |

### 3.2 Inference Pipeline
1. **Lagged Evaluation** — Policy evaluated on candle `t - lag` where `lag_long = 7`, `lag_short = 10` (avoids look-ahead bias)
2. **Q-Margin Calculation** — `Q_margin = Q(directional_action) - Q(do_nothing)`
3. **Threshold Gate** — Entry allowed iff:
   - `Q_margin > effective_threshold` (long or short, from governor CSV or env var)
   - `argmax(Q) == directional_action` (model agrees with side)
4. **Conflict Resolution** — If both long and short pass on same candle, higher `Q_margin` wins
5. **Entry Tags** — `rl_long_entry` / `rl_short_entry`

### 3.3 Adaptive Threshold Governor (Optional)
- **Source:** CSV at `historical_strategy_health_path`
- **Columns:** `effective_long_threshold`, `effective_short_threshold`, (plus health metrics)
- **Activation:** `historical_threshold_governor_enabled = 1` (env var)
- **Behaviour:** Thresholds read from latest CSV row on each candle; allows external process to tighten/loosen entry criteria based on recent strategy health

### 3.4 Shadow Mode
- **Export path:** `KARAKANA_SHADOW_SIGNAL_EXPORT_PATH`, defaulting to `user_data/freqtrade_signals_karakana.csv`
- **Signal columns:** `date`, `pair`, `ask`, `bid`, `sma-compare`, `mid-price`, `close`, `long-q-margin`, `short-q-margin`, `long-bid-rl`, `short-bid-rl`
- **Runtime sidecars:** `karakana-shadow-trader --watch` and `karakana-shadow-health --watch`
- **Purpose:** Build virtual trade evidence continuously, then update `directional_strategy_health.csv` for adaptive thresholds and the arming gate.

---

## 4. Exit & Risk Management

### 4.1 Layer 1 — Exponential Decaying Stop-Loss (Baseline)
- **Initial SL:** `stoploss = -sell_pnl_upperband.value` (e.g., -10.5%)
- **Decay Function:** `SL(t) = SL₀ × exp(-k × t)`
  - `t` = trade age in minutes (clamped to `T_max = stoploss_decay_max_minutes`)
  - `k = -ln(final_fraction) / T_max` where `final_fraction = stoploss_decay_final_fraction`
- **Floor:** After `T_max`, stop holds at `SL₀ × final_fraction`
- **Intent:** Wide initial room → progressive risk reduction as trade ages without profit

### 4.2 Layer 2 — Karakana SGO Monitor (StreamingAlphaMonitor)
**Per-trade stateful monitor** instantiated on entry, updated each candle.

#### 4.2.1 Core Metrics (per update)
- `peak_pnl` — maximum unrealised PnL observed
- `pullback = peak_pnl - current_pnl`
- `score = +1` if `pullback ≤ pnl_deadband` else `-1`
- `decline_streak` — consecutive candles with `score = -1`
- `horizon` — internal stability metric (decays on negative scores)

#### 4.2.2 Early-Exit Triggers
| Trigger | Condition | Exit Reason Tag |
|---------|-----------|-----------------|
| Warmup Loss Floor | `current_pnl < warmup_loss_floor` AND `n_observations < warmup_periods` | `*_karakana_warmup_unrealized_loss` |
| Proactive Degeneration | `peak_pnl > 0` AND `pullback > proactive_pullback_threshold` AND `decline_streak ≥ decline_candles` | `*_karakana_degenerating` |
| Horizon Collapse | `horizon < horizon_threshold` | `*_karakana_collapse_horizon` |
| Structural Collapse | Sliding window (`chunk_size`) negative-score ratio ≥ `collapse_threshold` | `*_karakana_structural_collapse` |

*Prefix `long_` or `short_` per trade direction.*

#### 4.2.3 ROI Gate (Critical Mechanism)
- `custom_exit()` **only sets a flag** (`karakana_exit_reason`) — does **not** issue exit order
- `confirm_trade_exit()` intercepts Freqtrade's native ROI exit:
  - **Rejects** ROI exit if **no** Karakana flag is set (trade stays open)
  - **Allows** ROI exit **only** when a Karakana flag exists (health-deterioration confirmed)
- **Result:** Healthy trades ignore fixed ROI tables; unhealthy trades exit at next ROI checkpoint

### 4.3 Layer 3 — Tightened Stop on Degeneration
- **Trigger:** Active Karakana reason ∈ `karakana_tight_stop_reasons` (degeneration-type reasons)
- **Action:** `custom_stoploss()` overrides decaying SL with absolute price:
  - **Short:** `stop_price = current_rate × sell_short_loss_factor_two` (factor > 1.0)
  - **Long:** `stop_price = current_rate × sell_long_loss_factor_two` (factor < 1.0)
- **Effect:** Immediate hard stop near current price, cutting degeneration fast

---

## 5. Post-Exit Logic — SGO Shield 1 (Reversal & Cooldown)

### 5.1 Structural Collapse → Scheduled Reversal
- **Trigger:** Exit reason ∈ `karakana_collapse_reasons` (structural collapse variants)
- **Action:** `schedule_reversal(pair, opposite_direction, expiry_minutes=reversal_expiry_minutes)`
- **State:** `pending_reversals[pair] = {direction, expiry_ts}`

### 5.2 Reversal Execution
- On next entry signal for `pair`:
  - If pending reversal exists and not expired → **force entry** in reversal direction
  - Entry tag: `sgo_reversal_long` / `sgo_reversal_short`
  - `confirm_trade_entry()` **unconditionally approves** reversal entries (bypasses RL gate)
- On fill: `pending_reversals[pair]` cleared

### 5.3 Same-Direction Cooldown
- **Trigger:** Same structural collapse exit
- **Action:** `cooldowns[pair][collapsed_direction] = now + same_direction_cooldown_minutes`
- **Effect:** Blocks any **normal** RL entry in same direction until expiry
- **Note:** Reversal entries (opposite direction) are **not** blocked by cooldown

---

## 6. Configuration Reference

### 6.1 Environment Variables (Strategy Parameters)
| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `min_qmargin_long` | float | `0.05` | Min Q-margin for long entry (fallback) |
| `min_qmargin_short` | float | `0.05` | Min Q-margin for short entry (fallback) |
| `lag_long_candles` | int | `7` | Evaluation lag for long signals |
| `lag_short_candles` | int | `10` | Evaluation lag for short signals |
| `stoploss` | float | `-0.105` | Initial stop-loss (negative) |
| `stoploss_decay_max_minutes` | int | `120` | `T_max` for exponential decay |
| `stoploss_decay_final_fraction` | float | `0.2` | Floor fraction of initial SL |
| `sell_pnl_upperband` | float | `0.105` | Initial SL magnitude (positive) |
| `pnl_deadband` | float | `0.003` | Pullback deadband for +1 score |
| `warmup_periods` | int | `10` | Min observations before collapse detection |
| `warmup_loss_floor` | float | `-0.015` | Early-exit loss floor during warmup |
| `proactive_pullback_threshold` | float | `0.008` | Pullback trigger for degeneration |
| `decline_candles` | int | `3` | Consecutive negative candles for degeneration |
| `horizon_threshold` | float | `0.3` | Horizon collapse threshold |
| `chunk_size` | int | `20` | Sliding window for collapse detection |
| `collapse_threshold` | float | `0.65` | Negative-score ratio for structural collapse |
| `sell_long_loss_factor_two` | float | `0.995` | Tight SL factor for long degeneration |
| `sell_short_loss_factor_two` | float | `1.005` | Tight SL factor for short degeneration |
| `karakana_tight_stop_reasons` | csv | `degenerating` | Substring match for tight-SL activation |
| `karakana_collapse_reasons` | csv | `structural_collapse,collapse_horizon` | Substring match for reversal scheduling |
| `reversal_expiry_minutes` | int | `30` | Validity window for scheduled reversal |
| `same_direction_cooldown_minutes` | int | `60` | Cooldown on collapsed direction |
| `historical_strategy_health_path` | str | `""` | Path to governor CSV (empty = disabled) |
| `historical_threshold_governor_enabled` | int | `0` | Enable governor (1/0) |
| `KARAKANA_SHADOW_SIGNAL_EXPORT_PATH` | str | `user_data/freqtrade_signals_karakana.csv` | Export path for live shadow signal rows. |
| `KARAKANA_HISTORICAL_REQUIRE_ARMED` | int | `0` | If `1`, block entries until Directional Strategy Health has enough rows and long/short support. |

### 6.2 Freqtrade Strategy Interface
| Method | Purpose |
|--------|---------|
| `populate_indicators` | Compute bid/ask/SMA features; run policy inference (lagged); write shadow CSV |
| `populate_entry_trend` | Set `enter_long`/`enter_short` + tags; inject forced reversals |
| `populate_exit_trend` | Not used (exits via custom logic) |
| `custom_stoploss` | Exponential decay + degeneration override |
| `custom_exit` | Run SGO monitor; set Karakana flags only |
| `confirm_trade_exit` | ROI gate — allow exit only if Karakana flag set |
| `confirm_trade_entry` | Approve reversals unconditionally; block cooldown direction |

### 6.3 Internal State (Persisted via `strategy._state`)
| Key | Type | Description |
|-----|------|-------------|
| `karakana_monitors` | `dict[str, StreamingAlphaMonitor]` | Per-trade monitor instances |
| `karakana_exit_reasons` | `dict[str, str]` | Active exit reason per trade |
| `pending_reversals` | `dict[str, dict]` | Scheduled reversals with expiry |
| `cooldowns` | `dict[str, dict[direction, datetime]]` | Same-direction cooldowns |
| `policy` | `OfflineTradingQPolicy` | Loaded RL policy (loaded once in `__init__`) |

---

## 7. Operational Modes

| Mode | Description |
|------|-------------|
| **Dry-run (Backtest)** | Full history replay; shadow CSV exported for analysis |
| **Dry-run (Live)** | Real-time candles, paper orders; SGO monitor active; shadow CSV optional |
| **Live** | Real capital; all layers active; governor CSV hot-reloaded each candle |

---

## 8. Observability & Diagnostics

| Artifact | Location | Purpose |
|----------|----------|---------|
| `freqtrade_signals_karakana.csv` | `user_data/freqtrade_signals_karakana.csv` | Live signal stream consumed by `karakana-shadow-trader`. |
| `karakana_shadow_trade_history.csv` | `user_data/reports/karakana_shadow_trade_history.csv` | Virtual trades generated from the signal stream. |
| Freqtrade `trade_history` | DB / `trades.json` | Entry/exit tags, PnL, exit reasons |
| Strategy logs | `logs/freqtrade.log` | `custom_exit` reasons, reversal scheduling, cooldown events |
| Governor CSV | `historical_strategy_health_path` | External threshold tuning feedback loop |

---

## 9. Deployment Checklist

- [ ] Policy file (`policy.zip` or equivalent) placed at configured path
- [ ] Governor CSV path configured (or governor disabled)
- [ ] Exchange API keys configured (dry-run → live progression)
- [ ] Pairlist configured for liquid 1m markets
- [ ] `max_open_trades` set per risk budget
- [ ] `stake_amount` / `stake_currency` configured
- [ ] Dry-run backtest ≥ 30 days with positive expectancy
- [ ] Dry-run live ≥ 7 days with signal quality review (shadow CSV)
- [ ] Governor CSV pipeline operational (if enabled)
- [ ] Alerting on: structural collapse frequency, reversal fill rate, cooldown activation rate

---

## 10. Assumptions & Constraints

| Assumption | Risk if Violated |
|------------|------------------|
| 1m candles available with < 2s latency | Look-ahead bias / stale signals |
| Policy trained on same exchange/symbol distribution | Distribution shift → degraded Q-values |
| Sufficient liquidity for market exits at stop prices | Slippage > expected loss factors |
| Governor CSV updated at ≤ 1m cadence (if enabled) | Stale thresholds → over/under trading |
| Freqtrade `process_only_new_candles = True` | Duplicate candle processing → duplicate signals |

---

## 11. Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-07-05 | — | Initial specification from implementation |

---

*End of Specification*
