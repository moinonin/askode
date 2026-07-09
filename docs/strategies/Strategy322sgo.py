from datetime import datetime, timedelta, timezone
from typing import Optional, Any
import csv
import json
import os
import sys
from pathlib import Path

# Add the Karakana project root when running this strategy from the repository.
project_root = str(Path(__file__).resolve().parents[2])
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import numpy as np
import pandas as pd
import talib.abstract as ta
from pandas import DataFrame

from freqtrade.strategy import (
    IStrategy,
    DecimalParameter,
    IntParameter,
    merge_informative_pair,
    CategoricalParameter,
    stoploss_from_absolute
)
from freqtrade.persistence import Trade

import torch
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
logger.propagate = True
# Suppress warnings
import warnings
warnings.filterwarnings("ignore")

try:
    from karakana.streaming import StreamingAlphaMonitor
    from karakana.trainers.offline_trading import (
        ACTION_LABELS,
        OfflineTradingQPolicy,
    )
except (ImportError, ModuleNotFoundError):
    StreamingAlphaMonitor = None
    ACTION_LABELS = ("go_long", "go_short", "do_nothing")
    OfflineTradingQPolicy = None

KARAKANA_AVAILABLE = StreamingAlphaMonitor is not None and OfflineTradingQPolicy is not None

pd.set_option('future.no_silent_downcasting', True)


class Strategy322sgo(IStrategy):
    INTERFACE_VERSION = 3
    karakana_collapse_reasons = frozenset(
        {
            "short_karakana_structural_collapse",
            "long_karakana_structural_collapse",
            "short_karakana_collapse_horizon",
            "long_karakana_collapse_horizon",
        }
    )
    karakana_exit_reasons = karakana_collapse_reasons | {
        "short_karakana_warmup_unrealized_loss",
        "long_karakana_warmup_unrealized_loss",
        "short_karakana_degenerating",
        "long_karakana_degenerating",
    }
    karakana_tight_stop_reasons = frozenset(
        {
            "short_karakana_degenerating",
            "long_karakana_degenerating",
        }
    )

    timeframe = '1m'
    startup_candle_count: int = 50

    can_short = True
    
    use_custom_stoploss = True

    long_policy_lag = 7
    short_policy_lag = 10
    historical_feature_order = ("ask", "bid", "sma_compare", "candidate_is_short")
    historical_min_long_q_margin = float(
        os.getenv(
            "KARAKANA_HISTORICAL_MIN_LONG_Q_MARGIN",
            os.getenv("KARAKANA_HISTORICAL_MIN_Q_MARGIN", "0.08"),
        )
    )
    historical_min_short_q_margin = float(
        os.getenv(
            "KARAKANA_HISTORICAL_MIN_SHORT_Q_MARGIN",
            os.getenv("KARAKANA_HISTORICAL_MIN_Q_MARGIN", "6.25"),
        )
    )
    historical_min_q_margin = float(
        os.getenv("KARAKANA_HISTORICAL_MIN_Q_MARGIN", str(historical_min_short_q_margin))
    )
    historical_threshold_governor_enabled = os.getenv(
        "KARAKANA_HISTORICAL_THRESHOLD_GOVERNOR_ENABLED", "0"
    ).strip().lower() in {"1", "true", "yes", "on"}
    historical_strategy_health_path = os.getenv(
        "KARAKANA_HISTORICAL_STRATEGY_HEALTH_PATH",
        "user_data/reports/directional_strategy_health.csv",
    )
    shadow_signal_export_path = os.getenv(
        "KARAKANA_SHADOW_SIGNAL_EXPORT_PATH",
        "user_data/freqtrade_signals_karakana.csv",
    ).strip()
    historical_require_armed = os.getenv(
        "KARAKANA_HISTORICAL_REQUIRE_ARMED", "0"
    ).strip().lower() in {"1", "true", "yes", "on"}
    historical_min_armed_rows = int(os.getenv("KARAKANA_HISTORICAL_MIN_ARMED_ROWS", "128"))
    historical_min_armed_long_count = int(
        os.getenv("KARAKANA_HISTORICAL_MIN_ARMED_LONG_COUNT", "16")
    )
    historical_min_armed_short_count = int(
        os.getenv("KARAKANA_HISTORICAL_MIN_ARMED_SHORT_COUNT", "16")
    )
    historical_min_armed_regime_confidence = float(
        os.getenv("KARAKANA_HISTORICAL_MIN_ARMED_REGIME_CONFIDENCE", "0.0")
    )
    
    buy_long_bid_rl = CategoricalParameter(['go_long','go_short'], default= 'go_long', space='buy', optimize=False)
    buy_short_bid_rl = CategoricalParameter(['go_long','go_short'], default= 'go_short', space='buy', optimize=False)
    sell_pnl_upperband = DecimalParameter([0.01, 0.274], default=0.274, space='sell', optimize=True) # 0.076
    sell_pnl_midband = DecimalParameter([0.05, 0.207], default=0.193, space='sell', optimize=False)
    sell_stop_ratio = DecimalParameter([1, 5.1], default=5.057, space='sell', optimize=True) # 4.197
    sell_final_exit_time = IntParameter([360, 2900], default=2880, space='sell', optimize=False)
    # Stoploss hyperspace params:
    sell_short_final_fraction = DecimalParameter(0.0, 1.0, default= 0.003, space='sell', optimize=False)
    sell_long_final_fraction = DecimalParameter(0.001, 1.0, default= 0.496, space='sell', optimize=False)

    sell_long_loss_factor_two = DecimalParameter(0.61, 0.999, default= 0.994, space='sell', optimize=True)
    sell_short_loss_factor_two = DecimalParameter(1.01, 1.015, default= 1.014, space='sell', optimize=True)

    sell_long_tmax = DecimalParameter(15, 34560, default= 19290.724, space='sell', optimize=False)
    sell_short_tmax = DecimalParameter(15, 34560, default= 20383.598, space='sell', optimize=False)
    sell_Tmax_short = DecimalParameter(15, 34560, default= 7790.838, space='sell', optimize=False)
    sell_Tmax_long = DecimalParameter(15, 34560, default= 9426.723, space='sell', optimize=False)
    sell_long_custom_sl = DecimalParameter(0.0, 0.29, default= 0.235, space='sell', optimize=False)
    sell_short_custom_sl = DecimalParameter(0.0, 0.393, default= 0.274, space='sell', optimize=False)
    # SGO hyperopt settings
    sell_pnl_deadband = DecimalParameter([0.001, 0.01], default=0.002, space='sell', optimize=False)
    sell_proactive_pullback = DecimalParameter([0.001, 0.02], default=0.002, space='sell', optimize=False)
    sell_decline_candles = IntParameter([1, 5], default=2, space='sell', optimize=False)
    sell_monitor_chunk_size = IntParameter([2, 40], default=23, space='sell', optimize=False)
    sell_reversal_expiry_minutes = IntParameter([3, 60], default=15, space='sell', optimize=False)
    sell_same_direction_cooldown_minutes = IntParameter([3, 12960], default=2880, space='sell', optimize=False)
    sell_monitor_collapse_threshold = DecimalParameter([0.01, 1.0], default=0.259, space='sell', optimize=False)
    sell_monitor_horizon_threshold = IntParameter([1, 20], default=5, space='sell', optimize=False)
    sell_warmup_loss_floor = DecimalParameter([0.01, 1.0], default=0.015, space='sell', optimize=False)
    sell_monitor_safety_floor = DecimalParameter([0.001, 0.01], default=0.004, space='sell', optimize=False)
    
    # SGO open-trade monitor settings
    monitor_chunk_size = sell_monitor_chunk_size.value
    monitor_collapse_threshold = -sell_monitor_collapse_threshold.value  #-0.05
    monitor_safety_floor = sell_monitor_safety_floor.value #0.005
    pnl_deadband = sell_pnl_deadband.value
    proactive_pullback = sell_proactive_pullback.value
    decline_candles = sell_decline_candles.value
    warmup_loss_floor = -sell_warmup_loss_floor.value #-0.025
    fail_closed_on_sgo_error = False
    reversal_expiry_minutes = sell_reversal_expiry_minutes.value
    same_direction_cooldown_minutes = sell_same_direction_cooldown_minutes.value

    # Edge computation settings
    fast_ema_period = 12
    slow_ema_period = 36
    edge_scale = 20.0

    historical_checkpoint_path = os.getenv(
        "KARAKANA_HISTORICAL_CHECKPOINT",
        "examples/historical_trading/"
        "HistoricalTrading-v0_7fce2798-c191-4549-abb6-a57414c1fce6_best_policy.pt",
    )
    historical_preprocessing_path = os.getenv(
        "KARAKANA_HISTORICAL_PREPROCESSING",
        "examples/historical_trading/"
        "HistoricalTrading-v0_7fce2798-c191-4549-abb6-a57414c1fce6_offline_preprocessing.json",
    )
    # Compute ROI and stop losses
    take_pnl_ratio = sell_pnl_upperband.value / sell_stop_ratio.value
    '''
    minimal_roi = {"0": sell_pnl_upperband.value}
    '''
    minimal_roi = {"0": 0.105, "69": 0.064, "2880": 0.036, "12960": 0}

    stoploss = -sell_pnl_upperband.value #-0.15

    interval = float(timeframe.split('m')[0])

    @staticmethod
    def stop_loss_decay(final_fraction, T_max, t, SL_0: Optional [float] = None):
        # Calculate the decay constant k
        k = -np.log(final_fraction) / T_max
        
        # Return the stop-loss at time t, freeze decay after T_max, clamp t to T_max
        t_clamped = max(0, min(t, T_max))
        return SL_0 * np.exp(-k * t_clamped)
    def version(self) -> str:
        return "1.3.7"

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.exit_monitors = {}
        self._last_pushed = {}
        self.karakana_ready = False
        self.offline_policy = None
        self.state_mean = None
        self.state_scale = None
        self.action_labels = ACTION_LABELS
        self._karakana_exit_flags = {}
        self._trade_peak_pnl = {}
        self._trade_last_pnl = {}
        self._trade_decline_streak = {}
        self._pending_reversals = {}
        self._blocked_reentries = {}
        self._policy_load_attempted = False
        self._strategy_health_snapshot = None
        self._strategy_health_mtime = None
        self._shadow_signal_last_key = None

    def bot_start(self, **kwargs: Any) -> None:
        """
        Load the HistoricalTrading policy and its exact training normalization.
        """
        self.exit_monitors = {}
        self._last_pushed = {}
        self.karakana_ready = False
        self._karakana_exit_flags = {}
        self._trade_peak_pnl = {}
        self._trade_last_pnl = {}
        self._trade_decline_streak = {}
        self._pending_reversals = {}
        self._blocked_reentries = {}
        self._policy_load_attempted = False
        self._strategy_health_snapshot = None
        self._strategy_health_mtime = None
        self._shadow_signal_last_key = None
        self._load_historical_policy()

    @staticmethod
    def _resolve_artifact_path(configured_path: str) -> Optional[Path]:
        configured = Path(configured_path).expanduser()
        strategy_dir = Path(__file__).resolve().parent
        search_directories = [
            strategy_dir,
            strategy_dir / "historical_trading",
            Path.cwd() / "user_data" / "strategies",
            Path.cwd() / "user_data" / "strategies" / "historical_trading",
            Path.cwd() / "torchmodels",
            Path.cwd() / "user_data" / "torchmodels",
            Path.cwd() / "examples",
        ]
        candidates = [
            configured,
            Path.cwd() / configured,
            Path(project_root) / configured,
        ]
        candidates.extend(directory / configured.name for directory in search_directories)
        for candidate in candidates:
            if candidate.is_file():
                return candidate.resolve()

        patterns = (
            ("*HistoricalTrading*best_policy.pt", "*best_policy.pt")
            if configured.suffix == ".pt"
            else ("offline_preprocessing*.json", "offline_processing*.json")
        )
        discovered = [
            path
            for directory in search_directories
            if directory.is_dir()
            for pattern in patterns
            for path in directory.glob(pattern)
            if path.is_file()
        ]
        if discovered:
            return max(discovered, key=lambda path: path.stat().st_mtime).resolve()
        return None

    @staticmethod
    def _safe_margin(value: Any, default: float) -> float:
        try:
            margin = float(value)
        except (TypeError, ValueError):
            return default
        if not np.isfinite(margin) or margin < 0.0:
            return default
        return margin

    def _resolve_strategy_health_path(self) -> Path:
        configured = Path(self.historical_strategy_health_path).expanduser()
        if configured.is_absolute():
            return configured
        return Path.cwd() / configured

    def _refresh_strategy_health_snapshot(self) -> Optional[dict[str, Any]]:
        if not self.historical_threshold_governor_enabled:
            return None
        path = self._resolve_strategy_health_path()
        if not path.is_file():
            return None
        try:
            mtime = path.stat().st_mtime
            if self._strategy_health_mtime == mtime:
                return self._strategy_health_snapshot
            latest_row = None
            with path.open("r", encoding="utf-8", newline="") as handle:
                for row in csv.DictReader(handle):
                    latest_row = row
            if not latest_row:
                return None
            snapshot = dict(latest_row)
            snapshot["effective_long_threshold"] = self._safe_margin(
                snapshot.get("effective_long_threshold"),
                self.historical_min_long_q_margin,
            )
            snapshot["effective_short_threshold"] = self._safe_margin(
                snapshot.get("effective_short_threshold"),
                self.historical_min_short_q_margin,
            )
            snapshot["source_path"] = str(path)
            self._strategy_health_snapshot = snapshot
            self._strategy_health_mtime = mtime
            return snapshot
        except Exception as exc:
            logger.warning("[Karakana] Could not read strategy health snapshot: %s", exc)
            return self._strategy_health_snapshot

    def _historical_required_margin(self, candidate_is_short: int) -> float:
        snapshot = self._refresh_strategy_health_snapshot()
        if snapshot:
            key = "effective_short_threshold" if candidate_is_short else "effective_long_threshold"
            return float(snapshot[key])
        return (
            self.historical_min_short_q_margin
            if candidate_is_short
            else self.historical_min_long_q_margin
        )

    @staticmethod
    def _snapshot_int(snapshot: Optional[dict[str, Any]], key: str) -> int:
        if not snapshot:
            return 0
        try:
            return int(float(snapshot.get(key, 0)))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _snapshot_float(snapshot: Optional[dict[str, Any]], key: str) -> float:
        if not snapshot:
            return 0.0
        try:
            value = float(snapshot.get(key, 0.0))
        except (TypeError, ValueError):
            return 0.0
        return value if np.isfinite(value) else 0.0

    def _historical_trading_armed(self) -> tuple[bool, str]:
        if not self.historical_require_armed:
            return True, "arming_disabled"
        if not self.historical_threshold_governor_enabled:
            return False, "threshold_governor_disabled"

        snapshot = self._refresh_strategy_health_snapshot()
        if not snapshot:
            return False, "missing_strategy_health"

        rows = self._snapshot_int(snapshot, "rows")
        long_count = self._snapshot_int(snapshot, "long_count")
        short_count = self._snapshot_int(snapshot, "short_count")
        confidence = self._snapshot_float(snapshot, "regime_confidence")
        if rows < self.historical_min_armed_rows:
            return False, f"rows {rows} < {self.historical_min_armed_rows}"
        if confidence < self.historical_min_armed_regime_confidence:
            return (
                False,
                f"regime_confidence {confidence:.4f} < "
                f"{self.historical_min_armed_regime_confidence:.4f}",
            )
        return True, (
            f"armed rows={rows} long_count={long_count} short_count={short_count} "
            f"regime={snapshot.get('regime', '')} confidence={confidence:.4f}"
        )

    def _historical_side_armed(self, side: str) -> tuple[bool, str]:
        if not self.historical_require_armed:
            return True, "arming_disabled"
        snapshot = self._refresh_strategy_health_snapshot()
        if not snapshot:
            return False, "missing_strategy_health"
        if side == "long":
            count = self._snapshot_int(snapshot, "long_count")
            minimum = self.historical_min_armed_long_count
            key = "long_count"
        elif side == "short":
            count = self._snapshot_int(snapshot, "short_count")
            minimum = self.historical_min_armed_short_count
            key = "short_count"
        else:
            return False, f"unknown_side={side}"
        if count < minimum:
            return False, f"{key} {count} < {minimum}"
        return True, f"{key} {count} >= {minimum}"

    def _load_historical_policy(self) -> bool:
        if self.karakana_ready:
            return True
        if self._policy_load_attempted:
            return False
        self._policy_load_attempted = True
        if not KARAKANA_AVAILABLE:
            logger.error(
                "[Karakana] Imports unavailable. Ensure the Freqtrade image contains "
                "karakana.streaming and karakana.trainers.offline_trading."
            )
            return False

        torch.manual_seed(42)
        checkpoint_path = self._resolve_artifact_path(self.historical_checkpoint_path)
        preprocessing_path = self._resolve_artifact_path(self.historical_preprocessing_path)
        if checkpoint_path is None or preprocessing_path is None:
            logger.error(
                "[Karakana] HistoricalTrading artifacts not found. "
                "checkpoint=%r preprocessing=%r cwd=%s strategy_dir=%s. "
                "Set KARAKANA_HISTORICAL_CHECKPOINT and "
                "KARAKANA_HISTORICAL_PREPROCESSING to mounted absolute paths.",
                self.historical_checkpoint_path,
                self.historical_preprocessing_path,
                Path.cwd(),
                Path(__file__).resolve().parent,
            )
            return False

        try:
            preprocessing = json.loads(preprocessing_path.read_text(encoding="utf-8"))
            self.state_mean = np.asarray(preprocessing["means"], dtype=np.float32)
            self.state_scale = np.asarray(preprocessing["scales"], dtype=np.float32)
            self.action_labels = tuple(preprocessing.get("action_labels", ACTION_LABELS))
            feature_order = tuple(
                preprocessing.get(
                    "observation_layout",
                    preprocessing.get("feature_order", ()),
                )
            )
            if self.state_mean.shape != (4,) or self.state_scale.shape != (4,):
                raise ValueError("HistoricalTrading preprocessing must contain four means and scales")
            #print(f"RESOLVED PATH: {preprocessing_path}")
            #print(f"RESOLVED ORDER: {feature_order}")
            if np.any(self.state_scale <= 0) or not np.all(np.isfinite(self.state_scale)):
                raise ValueError("HistoricalTrading preprocessing scales must be finite and positive")
            if self.action_labels != tuple(ACTION_LABELS):
                raise ValueError(f"Unexpected action order: {self.action_labels}")
            #print(self.historical_feature_order)
            if feature_order not in (
                                ("state_0", "state_1", "state_2", "state_3"),
                                self.historical_feature_order,
                            ):
                                raise ValueError(
                                    "Unexpected HistoricalTrading-v0 feature order: "
                                    f"{feature_order}; expected {self.historical_feature_order}"
                                )
            if (
                not np.isfinite(self.historical_min_long_q_margin)
                or self.historical_min_long_q_margin < 0.0
                or not np.isfinite(self.historical_min_short_q_margin)
                or self.historical_min_short_q_margin < 0.0
            ):
                raise ValueError(
                    "Karakana historical Q margins must be finite and non-negative"
                )

            self.offline_policy = OfflineTradingQPolicy()
            try:
                state_dict = torch.load(checkpoint_path, map_location="cpu", weights_only=True)
            except TypeError:
                state_dict = torch.load(checkpoint_path, map_location="cpu")
            self.offline_policy.load_state_dict(state_dict)
            self.offline_policy.eval()
        except Exception as exc:
            logger.exception("[Karakana] Could not load HistoricalTrading artifacts: %s", exc)
            return False

        self.karakana_ready = True
        logger.warning(
            "[Karakana] Loaded HistoricalTrading-v0 policy checkpoint=%s preprocessing=%s "
            "features=%s timeframe=%s long_lag=%s short_lag=%s "
            "min_long_q_margin=%.4f min_short_q_margin=%.4f "
            "threshold_governor=%s strategy_health_path=%s shadow_signal_export=%s "
            "require_armed=%s min_armed_rows=%s min_armed_long_count=%s "
            "min_armed_short_count=%s",
            checkpoint_path,
            preprocessing_path,
            self.historical_feature_order,
            self.timeframe,
            self.long_policy_lag,
            self.short_policy_lag,
            self.historical_min_long_q_margin,
            self.historical_min_short_q_margin,
            self.historical_threshold_governor_enabled,
            self._resolve_strategy_health_path(),
            self.shadow_signal_export_path or "disabled",
            self.historical_require_armed,
            self.historical_min_armed_rows,
            self.historical_min_armed_long_count,
            self.historical_min_armed_short_count,
        )
        return True

    def _historical_inference(
        self,
        ask: float,
        bid: float,
        sma_compare: float,
        candidate_is_short: int,
    ) -> tuple[Optional[str], Optional[list[float]], Optional[float]]:
        if not self.karakana_ready and not self._load_historical_policy():
            return None, None, None
        if self.offline_policy is None:
            return None, None, None
        if candidate_is_short not in (0, 1):
            logger.error(
                "[Karakana] candidate_is_short must be 0 or 1, received %r",
                candidate_is_short,
            )
            return None, None, None
        state = np.asarray(
            [float(ask), float(bid), sma_compare, candidate_is_short],
            dtype=np.float32,
        )
        if not np.all(np.isfinite(state)):
            return None, None, None
        normalized = (state - self.state_mean) / self.state_scale
        with torch.inference_mode():
            q_values = self.offline_policy(
                torch.from_numpy(normalized).unsqueeze(0)
            )[0]
        do_nothing_idx = self.action_labels.index("do_nothing")
        directional_action = "go_short" if candidate_is_short else "go_long"
        directional_idx = self.action_labels.index(directional_action)
        directional_q = float(q_values[directional_idx].item())
        do_nothing_q = float(q_values[do_nothing_idx].item())
        q_margin = directional_q - do_nothing_q
        required_margin = self._historical_required_margin(candidate_is_short)
        action = (
            directional_action
            if q_margin >= required_margin
            else "do_nothing"
        )
        return action, [float(value) for value in q_values.tolist()], q_margin

    def _export_shadow_signal_row(self, dataframe: DataFrame, pair: str) -> None:
        if not self.shadow_signal_export_path or dataframe.empty:
            return
        row = dataframe.iloc[-1]
        if "date" in dataframe.columns:
            candle_time = str(row.get("date"))
        else:
            candle_time = str(dataframe.index[-1])
        dedupe_key = (pair, candle_time)
        if self._shadow_signal_last_key == dedupe_key:
            return
        self._shadow_signal_last_key = dedupe_key
        path = Path(self.shadow_signal_export_path).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        path.parent.mkdir(parents=True, exist_ok=True)
        output = {
            "date": candle_time,
            "pair": pair,
            "ask": float(row.get("ask", np.nan)),
            "bid": float(row.get("bid", np.nan)),
            "sma-compare": float(row.get("sma-compare", np.nan)),
            "mid-price": float(row.get("mid-price", row.get("close", np.nan))),
            "reward-price": float(row.get("close", np.nan)),
            "close": float(row.get("close", np.nan)),
            "long-q-margin": float(row.get("long-q-margin", np.nan)),
            "short-q-margin": float(row.get("short-q-margin", np.nan)),
            "long-bid-rl": str(row.get("long-bid-rl", "")),
            "short-bid-rl": str(row.get("short-bid-rl", "")),
        }
        write_header = not path.exists() or path.stat().st_size == 0
        with path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(output))
            if write_header:
                writer.writeheader()
            writer.writerow(output)

    def informative_pairs(self):
        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, '1m') for pair in pairs]
        informative_pairs += [("BTC/USDC:USDC", "1m")]
        return informative_pairs

    # --- Indicator Population ---
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        if self.dp is None:
            return dataframe

        pair = metadata['pair']
        if self.timeframe == '1m':
            inf_tf = '1m'
            informative = self.dp.get_pair_dataframe(pair=pair, timeframe=inf_tf)
            dataframe = merge_informative_pair(dataframe, informative, self.timeframe, inf_tf, ffill=True)

        # Primary technical indicators for RL models
        dataframe['sma-05'] = ta.SMA(dataframe, timeperiod=5)
        dataframe['sma-07'] = ta.SMA(dataframe, timeperiod=7)
        dataframe['sma-25'] = ta.SMA(dataframe, timeperiod=25)

        dataframe['sma-trend-flag'] = (
            (dataframe['sma-07'] > dataframe['sma-05']) &
            (dataframe['sma-25'] > dataframe['sma-07'])
        ).astype(int)

        # Volume‑weighted ask/bid approximation
        denom = dataframe['close'] + dataframe['open']
        denom = denom.replace(0, 0.00000001)
        dataframe['ask'] = dataframe['close'] * dataframe['volume'] / denom
        dataframe['bid'] = dataframe['open'] * dataframe['volume'] / denom
        dataframe['mid-price'] = (dataframe['bid'] + dataframe['ask']) / 2.0
        dataframe['spread'] = dataframe['ask'] - dataframe['bid']
        bid_sma = dataframe['bid'].rolling(window=20, min_periods=1).mean()
        safe_bid_sma = bid_sma.replace(0, np.nan)
        dataframe['sma-compare'] = (
            (dataframe['bid'] - bid_sma) / safe_bid_sma
        ).replace([np.inf, -np.inf], np.nan).fillna(0.0)
        dataframe = dataframe.ffill()

        # EMA indicators for SGO edge/gating
        dataframe["ema_fast"] = dataframe["close"].ewm(span=self.fast_ema_period, adjust=False).mean()
        dataframe["ema_slow"] = dataframe["close"].ewm(span=self.slow_ema_period, adjust=False).mean()
        dataframe["sgo_edge"] = (dataframe["ema_fast"] - dataframe["ema_slow"]) / dataframe["close"]

        # --- RL Model Application (Optimized) ---
        is_live = self.dp.runmode in ('live', 'dry_run')
        
        policy_ready = self.karakana_ready or self._load_historical_policy()
        fallback_action = 'do_nothing' if policy_ready else 'policy_unavailable'
        dataframe['long-bid-rl'] = fallback_action
        dataframe['short-bid-rl'] = fallback_action
        
        ask_vals = dataframe['ask'].values
        bid_vals = dataframe['bid'].values
        sma_vals = dataframe['sma-compare'].values
        
        if is_live:
            start_idx = max(0, len(dataframe) - 3)
        else:
            start_idx = 0
            
        long_rl_out = [fallback_action] * len(dataframe)
        short_rl_out = [fallback_action] * len(dataframe)
        long_q_out: list[Optional[list[float]]] = [None] * len(dataframe)
        short_q_out: list[Optional[list[float]]] = [None] * len(dataframe)
        long_margin_out = np.full(len(dataframe), np.nan, dtype=np.float32)
        short_margin_out = np.full(len(dataframe), np.nan, dtype=np.float32)
        
        if policy_ready:
            for i in range(start_idx, len(dataframe)):
                l_idx = i - self.long_policy_lag
                if l_idx >= 0:
                    long_action, long_q, long_margin = self._historical_inference(
                        ask_vals[l_idx], bid_vals[l_idx], sma_vals[l_idx], 0
                    )
                    long_rl_out[i] = long_action or 'inference_error'
                    long_q_out[i] = long_q
                    if long_margin is not None:
                        long_margin_out[i] = long_margin

                s_idx = i - self.short_policy_lag
                if s_idx >= 0:
                    short_action, short_q, short_margin = self._historical_inference(
                        ask_vals[s_idx], bid_vals[s_idx], sma_vals[s_idx], 1
                    )
                    short_rl_out[i] = short_action or 'inference_error'
                    short_q_out[i] = short_q
                    if short_margin is not None:
                        short_margin_out[i] = short_margin
            if long_q_out[-1] is not None and short_q_out[-1] is not None:
                l_idx = len(dataframe) - 1 - self.long_policy_lag
                s_idx = len(dataframe) - 1 - self.short_policy_lag
                logger.info(
                    "long_state=%r short_state=%r q_delta=%r",
                    [
                        ask_vals[l_idx],
                        bid_vals[l_idx],
                        sma_vals[l_idx],
                        0,
                    ],
                    [
                        ask_vals[s_idx],
                        bid_vals[s_idx],
                        sma_vals[s_idx],
                        1,
                    ],
                    np.asarray(long_q_out[-1]) - np.asarray(short_q_out[-1]),
                )
        
        dataframe['long-bid-rl'] = long_rl_out
        dataframe['short-bid-rl'] = short_rl_out
        dataframe['long-q-values'] = long_q_out
        dataframe['short-q-values'] = short_q_out
        dataframe['long-q-margin'] = long_margin_out
        dataframe['short-q-margin'] = short_margin_out
        self._export_shadow_signal_row(dataframe, pair)
        logger.info(
            "[Karakana RL OUT] pair=%s ready=%s\n%s",
            pair,
            policy_ready,
            dataframe[
                ['mid-price', 'spread', 'sma-compare', 'long-bid-rl', 'long-q-margin',
                 'long-q-values', 'short-bid-rl', 'short-q-margin',
                 'short-q-values']
            ].tail(5).to_string(index=False, justify='right')
        )
        return dataframe

    # --- Entry Trend ---
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        pair = metadata['pair']
        candle_time = self._latest_candle_time(dataframe)
        self._expire_pending_reversals(candle_time)
        dataframe['enter_long'] = 0
        dataframe['enter_short'] = 0
        dataframe['enter_tag'] = None
        long_required_margin = self._historical_required_margin(0)
        short_required_margin = self._historical_required_margin(1)
        armed, arm_reason = self._historical_trading_armed()
        if not armed:
            logger.warning(
                "[Karakana ARMING] Blocking entries for %s: %s "
                "health_path=%s signal_export=%s",
                pair,
                arm_reason,
                self._resolve_strategy_health_path(),
                self.shadow_signal_export_path or "disabled",
            )
            return dataframe

        long_candidate = (
            (dataframe['long-bid-rl'] == self.buy_long_bid_rl.value)
            & (dataframe['long-q-margin'] >= long_required_margin)
            & (dataframe['volume'] > 0)
        )
        short_candidate = (
            (dataframe['short-bid-rl'] == self.buy_short_bid_rl.value)
            & (dataframe['short-q-margin'] >= short_required_margin)
            & (dataframe['volume'] > 0)
        )
        long_side_armed, long_side_reason = self._historical_side_armed("long")
        short_side_armed, short_side_reason = self._historical_side_armed("short")
        if not long_side_armed:
            long_candidate &= False
        if not short_side_armed:
            short_candidate &= False

        conflict = long_candidate & short_candidate
        long_candidate &= ~conflict | (
            dataframe['long-q-margin'] > dataframe['short-q-margin']
        )
        short_candidate &= ~conflict | (
            dataframe['short-q-margin'] > dataframe['long-q-margin']
        )

        # Candidate direction is an input context. Only matching, sufficiently
        # confident actions become entries; a conflict keeps the larger margin.

        dataframe.loc[
            long_candidate,
            ['enter_long', 'enter_tag']
        ] = (1, 'rl_long_entry')


        dataframe.loc[
            short_candidate,
            ['enter_short', 'enter_tag']
        ] = (1, 'rl_short_entry')

        logger.info(
            "[Karakana ENTRY OUT] pair=%s effective_long_q_margin=%.4f "
            "effective_short_q_margin=%.4f threshold_governor=%s conflicts=%s\n%s",
            pair,
            long_required_margin,
            short_required_margin,
            self.historical_threshold_governor_enabled,
            int(conflict.sum()),
            dataframe[
                ['long-bid-rl', 'long-q-margin', 'short-bid-rl',
                'short-q-margin', 'enter_long', 'enter_short', 'enter_tag']
            ].tail(10).to_string(index=False, justify='right'),
        )
        if not long_side_armed or not short_side_armed:
            logger.info(
                "[Karakana SIDE ARMING] pair=%s long_armed=%s (%s) short_armed=%s (%s)",
                pair,
                long_side_armed,
                long_side_reason,
                short_side_armed,
                short_side_reason,
            )
        # A pending reversal gets priority over all normal whitelist entries.
        # Do not pop it here: dataframe signals are only proposals. The reversal
        # is cleared only after its entry fills or after expiry.
        if self._has_pending_reversal(pair):
            dataframe.loc[dataframe.index[-1], ['enter_long', 'enter_short', 'enter_tag']] = (0, 0, None)
            reverse_side = self._pending_reversal_side(pair)
            if reverse_side is None:
                return dataframe
            self._unlock_pair_for_reversal(pair)
            if reverse_side == "long":
                dataframe.loc[dataframe.index[-1], "enter_long"] = 1
                dataframe.loc[dataframe.index[-1], "enter_short"] = 0
                dataframe.loc[dataframe.index[-1], "enter_tag"] = "sgo_reversal_long"
                logger.info(f"[SGO REVERSAL] Injected LONG entry for {pair} tag=sgo_reversal_long")
            elif reverse_side == "short":
                dataframe.loc[dataframe.index[-1], "enter_short"] = 1
                dataframe.loc[dataframe.index[-1], "enter_long"] = 0
                dataframe.loc[dataframe.index[-1], "enter_tag"] = "sgo_reversal_short"
                logger.info(f"[SGO REVERSAL] Injected SHORT entry for {pair} tag=sgo_reversal_short")

        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        return dataframe

    # --- Pre-Trade Entry Gating Filter (SGO Shield 1) ---
    def confirm_trade_entry(
        self,
        pair: str,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        current_time: datetime,
        entry_tag: str | None,
        side: str,
        **kwargs: Any,
    ) -> bool:
        self._expire_pending_reversals(current_time)
        self._expire_blocked_reentries(current_time)

        armed, arm_reason = self._historical_trading_armed()
        if not armed:
            logger.warning(
                "[Karakana ARMING] Confirm-entry blocked for %s side=%s tag=%s: %s",
                pair,
                side,
                entry_tag,
                arm_reason,
            )
            return False

        if self._is_reversal_entry(pair, entry_tag, side):
            self._unlock_pair_for_reversal(pair)
            logger.info(f"[SGO REVERSAL] Confirming forced {side} reversal entry for {pair}.")
            return True

        if self._has_pending_reversal(pair):
            logger.info(
                f"[SGO REVERSAL] Blocking normal entry for {pair} side={side}; "
                f"pending reversal={self._pending_reversal_summary()}."
            )
            return False

        if self._is_same_direction_blocked(pair, side):
            logger.info(
                f"[SGO COOLDOWN] Blocking same-direction re-entry for {pair} side={side}; "
                f"cooldown={self._blocked_reentries.get((pair, side))}."
            )
            return False

        if not self.karakana_ready:
            return not self.fail_closed_on_sgo_error
        return True

    def _latest_edge(self, pair: str) -> float:
        if not hasattr(self, "dp") or self.dp is None:
            return 0.0
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        if dataframe is None or dataframe.empty or "sgo_edge" not in dataframe:
            return 0.0
        value = dataframe.iloc[-1]["sgo_edge"]
        return 0.0 if value != value else float(value)

    # --- Real-Time Exit Monitor (SGO Shield 2) ---
    def _evaluate_karakana_exit(
        self,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        pnl: float,
    ) -> str | None:
        if not KARAKANA_AVAILABLE or StreamingAlphaMonitor is None:
            return None

        monitor = self.exit_monitors.setdefault(
            str(trade.id),
            StreamingAlphaMonitor(
                chunk_size=self.monitor_chunk_size,
                collapse_threshold=self.monitor_collapse_threshold,
                safety_floor=self.monitor_safety_floor,
            ),
        )

        # Timeframe Lock: Only push a new score once per candle close
        trade_id = str(trade.id)
        timeframe_minutes = 15
        if hasattr(self, "timeframe") and self.timeframe:
            tf = self.timeframe.lower()
            if tf.endswith("m"):
                try:
                    timeframe_minutes = int(tf[:-1])
                except ValueError:
                    pass
            elif tf.endswith("h"):
                try:
                    timeframe_minutes = int(tf[:-1]) * 60
                except ValueError:
                    pass

        last_push = self._last_pushed.get(trade_id)
        should_push = False
        if last_push is None:
            should_push = True
        else:
            elapsed = (current_time - last_push).total_seconds()
            if elapsed >= (timeframe_minutes * 60) - 5: # 5 seconds buffer
                should_push = True

        if should_push:
            previous_peak = self._trade_peak_pnl.get(trade_id, pnl)
            peak_pnl = max(previous_peak, pnl)
            previous_pnl = self._trade_last_pnl.get(trade_id, pnl)
            decline_streak = (
                self._trade_decline_streak.get(trade_id, 0) + 1
                if pnl < previous_pnl
                else 0
            )
            pullback = peak_pnl - pnl
            self._trade_peak_pnl[trade_id] = peak_pnl
            self._trade_last_pnl[trade_id] = pnl
            self._trade_decline_streak[trade_id] = decline_streak

            # Score deterioration from the best open-trade gain, not only
            # absolute losses.
            score = 1.0 if pullback < self.pnl_deadband else -1.0
            self._last_pushed[trade_id] = current_time
            monitor.push(score)
            if (
                peak_pnl > 0.0
                and pullback >= self.proactive_pullback
                and decline_streak >= int(self.decline_candles)
            ):
                logger.info(
                    f"[Karakana DEGENERATION] trade={trade.id} peak={peak_pnl:.6f} "
                    f"pnl={pnl:.6f} pullback={pullback:.6f} "
                    f"decline_candles={decline_streak}."
                )
                return "short_karakana_degenerating" if trade.is_short else "long_karakana_degenerating"

        if monitor.in_warmup:
            if pnl <= self.warmup_loss_floor:
                self.exit_monitors.pop(trade_id, None)
                self._last_pushed.pop(trade_id, None)
                return "short_karakana_warmup_unrealized_loss" if trade.is_short else "long_karakana_warmup_unrealized_loss"
            return None

        if monitor.should_stop():
            self.exit_monitors.pop(trade_id, None)
            self._last_pushed.pop(trade_id, None)
            return "short_karakana_structural_collapse" if trade.is_short else "long_karakana_structural_collapse"

        horizon = monitor.current_horizon
        horizon_threshold = int(self.sell_monitor_horizon_threshold.value)
        if 0.0 < horizon <= horizon_threshold:
            self.exit_monitors.pop(str(trade.id), None)
            self._last_pushed.pop(str(trade.id), None)
            logger.info(
                f"[Karakana HORIZON] Proactive degeneration for trade={trade.id}: "
                f"H={horizon:.2f} chunks, threshold={horizon_threshold}."
            )
            return "short_karakana_collapse_horizon" if trade.is_short else "long_karakana_collapse_horizon"

        return None

    def custom_exit(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs: Any,
    ) -> str | None:
        # Monitor every open-trade loop. A Karakana flag is cached, but only a
        # later Freqtrade ROI proposal is allowed to execute it.
        if str(trade.id) in self._karakana_exit_flags:
            return None
        reason = self._evaluate_karakana_exit(
            trade,
            current_time,
            current_rate,
            current_profit,
        )
        if reason:
            self._karakana_exit_flags[str(trade.id)] = reason
        return None

    def custom_stoploss(
        self,
        pair: str,
        trade: Trade,
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        after_fill: bool = False,
        **kwargs: Any,
    ) -> Optional[float]:
        # Make sure you have the longest interval first - these conditions are evaluated from top to bottom.
        '''
        long_timediff = ((current_time - timedelta(minutes=self.sell_long_tmax.value)) - trade.open_date_utc).total_seconds()/60
        short_timediff = ((current_time - timedelta(minutes=self.sell_short_tmax.value)) - trade.open_date_utc).total_seconds()/60

        long_disc_time = self.interval * (long_timediff // self.interval)
        short_disc_time = self.interval * (short_timediff // self.interval)

        long_sl0 = self.sell_long_custom_sl.value # * trade.initial_stop_loss_pct
        short_sl0 = self.sell_short_custom_sl.value #* trade.initial_stop_loss_pct

        short_stop = self.stop_loss_decay(self.sell_short_final_fraction.value, self.sell_Tmax_short.value, t=short_disc_time, SL_0=short_sl0)
        long_stop = self.stop_loss_decay(self.sell_long_final_fraction.value, self.sell_Tmax_long.value, t=long_disc_time, SL_0=long_sl0)
        

        if trade.is_short:
            min_profit = self.sell_short_loss_factor_two.value - 1
        else:
            min_profit = 1 - self.sell_long_loss_factor_two.value
        
        can_set_absolute_sl = current_profit > min_profit
        '''

        short_stop_price = max(current_rate * (self.sell_short_loss_factor_two.value), current_rate)
        long_stop_price = min(current_rate * (self.sell_long_loss_factor_two.value), current_rate)

        karakana_reason = self._karakana_exit_flags.get(str(trade.id))

        if karakana_reason not in self.karakana_tight_stop_reasons:
            #return -short_stop if trade.is_short else -long_stop
            return None
        logger.info(
            "[Karakana STOPLOSS] Tightening %s trade=%s side=%s reason=%s "
            "by 50%% from current_rate=%.8f profit=%.6f.",
            pair,
            getattr(trade, "id", None),
            "short" if getattr(trade, "is_short", False) else "long",
            karakana_reason,
            current_rate,
            current_profit,
        )
        #return self.take_pnl_ratio
        return (
            stoploss_from_absolute(short_stop_price, current_rate, is_short=trade.is_short) if trade.is_short
            else stoploss_from_absolute(long_stop_price, current_rate, is_short=trade.is_short)
        )
        

    def confirm_trade_exit(
        self,
        pair: str,
        trade: Trade,
        order_type: str,
        amount: float,
        rate: float,
        time_in_force: str,
        exit_reason: str,
        current_time: datetime,
        **kwargs: Any,
    ) -> bool:
        normalized_exit_reason = str(exit_reason or "")
        if normalized_exit_reason.startswith("roi"):
            trade_id = str(trade.id)
            karakana_reason = self._karakana_exit_flags.get(trade_id)
            if not karakana_reason:
                pnl = self._signed_open_trade_return(trade, rate)
                karakana_reason = self._evaluate_karakana_exit(
                    trade,
                    current_time,
                    rate,
                    pnl,
                )
                if karakana_reason:
                    self._karakana_exit_flags[trade_id] = karakana_reason
            if karakana_reason:
                logger.info(
                    f"[Karakana ROI GATING] Allowing ROI exit for {pair} "
                    f"after degeneration flag {karakana_reason}."
                )
                return True
            return False

        if normalized_exit_reason in self.karakana_exit_reasons:
            return True

        return True

    def order_filled(self, pair: str, trade: Trade, order: Any, current_time: datetime, **kwargs) -> None:
        """
        Callback triggered when any order is filled.
        Schedules same-pair reversal after confirmed SGO collapse exits and
        clears pending reversal after the reversal entry actually fills.
        """
        entry_tag = getattr(trade, "enter_tag", None)
        if entry_tag in ("sgo_reversal_long", "sgo_reversal_short"):
            pending = self._pending_reversals.get(pair)
            if pending and pending.get("side") == ("long" if entry_tag.endswith("_long") else "short"):
                self._pending_reversals.pop(pair, None)
                logger.info(f"[SGO REVERSAL] Reversal entry filled for {pair}; clearing pending reversal.")

        # Only react to Karakana-related exits or ROI exits allowed after a
        # Karakana degeneration flag.
        order_side = self._order_side(order)
        exit_reason = str(getattr(trade, "exit_reason", None) or "")
        trade_is_short = bool(getattr(trade, "is_short", False))
        is_exit_order = order_side == ('buy' if trade_is_short else 'sell')

        karakana_reason = (
            self._karakana_exit_flags.pop(str(trade.id), None)
            if is_exit_order
            else None
        )

        is_collapse_exit = (
            exit_reason in self.karakana_collapse_reasons
            or karakana_reason in self.karakana_collapse_reasons
        )
        is_karakana_exit = (
            exit_reason in self.karakana_exit_reasons
            or karakana_reason in self.karakana_exit_reasons
        )

        if not is_exit_order:
            return

        # Exit state is cleared only after a confirmed fill. Clearing it in
        # confirm_trade_exit would lose monitoring if the order were cancelled.
        self._clear_trade_monitor_state(trade)
        if not is_karakana_exit:
            return

        exited_side = "short" if trade_is_short else "long"
        effective_reason = karakana_reason or exit_reason or "karakana_degenerating"
        self._block_same_direction_reentry(pair, exited_side, current_time, effective_reason)

        if not is_collapse_exit:
            return

        # Determine reverse direction
        reverse_side = "long" if trade_is_short else "short"

        self._pending_reversals[pair] = {
            "side": reverse_side,
            "created_at": self._normalize_reversal_time(current_time),
            "reason": effective_reason,
            "trade_id": getattr(trade, "id", None),
        }
        self._unlock_pair_for_reversal(pair)
        logger.info(
            f"[SGO REVERSAL] Exit filled for {pair} due to {exit_reason}. "
            f"Scheduling same-pair {reverse_side} reversal until {self._reversal_expiry(current_time)}."
        )

    def _clear_trade_monitor_state(self, trade: Trade) -> None:
        trade_id = str(trade.id)
        self.exit_monitors.pop(trade_id, None)
        self._last_pushed.pop(trade_id, None)
        self._karakana_exit_flags.pop(trade_id, None)
        self._trade_peak_pnl.pop(trade_id, None)
        self._trade_last_pnl.pop(trade_id, None)
        self._trade_decline_streak.pop(trade_id, None)

    def _latest_candle_time(self, dataframe: DataFrame) -> datetime:
        if dataframe is None or dataframe.empty:
            return datetime.now(timezone.utc)
        value = dataframe.index[-1]
        if isinstance(value, pd.Timestamp):
            return self._normalize_reversal_time(value.to_pydatetime())
        if isinstance(value, datetime):
            return self._normalize_reversal_time(value)
        return datetime.now(timezone.utc)

    def _reversal_expiry(self, created_at: datetime) -> datetime:
        return self._normalize_reversal_time(created_at) + timedelta(minutes=int(self.reversal_expiry_minutes))

    def _expire_pending_reversals(self, now: datetime) -> None:
        now = self._normalize_reversal_time(now)
        expired = [
            pair for pair, pending in self._pending_reversals.items()
            if now >= self._reversal_expiry(pending["created_at"])
        ]
        for pair in expired:
            pending = self._pending_reversals.pop(pair, None)
            logger.info(f"[SGO REVERSAL] Expired pending reversal for {pair}: {pending}")

    @staticmethod
    def _normalize_reversal_time(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value
        return value.astimezone(timezone.utc).replace(tzinfo=None)

    def _has_pending_reversal(self, pair: str | None = None) -> bool:
        if pair is None:
            return bool(self._pending_reversals)
        return pair in self._pending_reversals

    def _block_same_direction_reentry(self, pair: str, side: str, now: datetime, reason: str) -> None:
        now = self._normalize_reversal_time(now)
        expires_at = now + timedelta(minutes=int(self.same_direction_cooldown_minutes))
        self._blocked_reentries[(pair, side)] = {
            "expires_at": expires_at,
            "reason": reason,
        }
        self._lock_pair_side_for_cooldown(pair, side, expires_at, reason)
        logger.info(
            f"[SGO COOLDOWN] Blocking {pair} {side} re-entry until {expires_at} after {reason}."
        )

    def _expire_blocked_reentries(self, now: datetime) -> None:
        now = self._normalize_reversal_time(now)
        expired = [
            key for key, payload in self._blocked_reentries.items()
            if now >= self._normalize_reversal_time(payload["expires_at"])
        ]
        for key in expired:
            payload = self._blocked_reentries.pop(key, None)
            logger.info(f"[SGO COOLDOWN] Expired same-direction re-entry block for {key}: {payload}")

    def _is_same_direction_blocked(self, pair: str, side: str) -> bool:
        return (pair, side) in self._blocked_reentries

    def _pending_reversal_side(self, pair: str) -> Optional[str]:
        pending = self._pending_reversals.get(pair)
        return str(pending.get("side")) if pending else None

    def _is_reversal_entry(self, pair: str, entry_tag: str | None, side: str) -> bool:
        expected_side = self._pending_reversal_side(pair)
        if expected_side is None or expected_side != side:
            return False
        return entry_tag == f"sgo_reversal_{side}"

    def _pending_reversal_summary(self) -> str:
        return ", ".join(
            f"{pair}:{pending.get('side')}({pending.get('reason')})"
            for pair, pending in self._pending_reversals.items()
        )

    def _unlock_pair_for_reversal(self, pair: str) -> None:
        unlock_pair = getattr(self, "unlock_pair", None)
        if not callable(unlock_pair):
            return
        try:
            unlock_pair(pair)
            logger.info(f"[SGO REVERSAL] Unlocked pair lock for forced reversal on {pair}.")
        except Exception as exc:
            logger.warning(f"[SGO REVERSAL] Could not unlock pair lock for {pair}: {exc}")

    def _lock_pair_side_for_cooldown(self, pair: str, side: str, until: datetime, reason: str) -> None:
        lock_pair = getattr(self, "lock_pair", None)
        if not callable(lock_pair):
            return
        lock_reason = f"sgo_same_direction_cooldown:{side}:{reason}"
        try:
            lock_pair(pair, until=until, reason=lock_reason, side=side)
            logger.info(f"[SGO COOLDOWN] Added side-specific pair lock for {pair} side={side}.")
        except TypeError:
            logger.info(
                f"[SGO COOLDOWN] Freqtrade lock_pair does not support side-specific locks; "
                f"using internal {pair} {side} cooldown only."
            )
        except Exception as exc:
            logger.warning(f"[SGO COOLDOWN] Could not add pair lock for {pair} side={side}: {exc}")

    @staticmethod
    def _order_side(order: Any) -> Optional[str]:
        if isinstance(order, dict):
            value = order.get("side") or order.get("ft_order_side")
        else:
            value = getattr(order, "side", None) or getattr(order, "ft_order_side", None)
        return str(value).lower() if value is not None else None

    @staticmethod
    def _signed_open_trade_return(trade: Trade, current_rate: float) -> float:
        calculate_profit = getattr(trade, "calc_profit_ratio", None)
        if callable(calculate_profit):
            return float(calculate_profit(current_rate))
        open_rate = float(trade.open_rate)
        if getattr(trade, "is_short", False):
            return (open_rate - current_rate) / open_rate
        return (current_rate - open_rate) / open_rate
