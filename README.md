# TrifectaOmni
# OMNI-TRIFECTA QUANT ENGINE

[![Status](https://img.shields.io/badge/Status-Ready%20to%20Run-brightgreen)](STATUS.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](requirements.txt)
[![License](https://img.shields.io/badge/License-Proprietary-red)]()

## 🚀 Quick Start

**This repository is ready to run!** Test it in 3 commands:

```bash
git clone https://github.com/OMNIWORLDLLC/TrifectaOmni.git
cd TrifectaOmni
pip install -r requirements.txt && python examples/shadow_mode_example.py
```

Or use the automated installer:

```bash
./full-system-install.sh
```

📋 **See [STATUS.md](STATUS.md) for complete readiness information**  
📖 **See [QUICKSTART.md](QUICKSTART.md) for quick setup instructions**  
⚙️ **See [SETUP.md](SETUP.md) for detailed configuration**

---

## FORMAL SYSTEM ARCHITECTURE DOCUMENT

### 1. SYSTEM PURPOSE AND PHILOSOPHY

The Omni-Trifecta Quant Engine is a multi-layer, self-evolving, real-time trading intelligence designed for high-precision execution across three distinct markets:

* Binary Options (short-duration directional speculation)
* Spot Forex Trading (trend exploitation and structured position management)
* Flashloan-Based Arbitrage (intra-block inefficiency exploitation)

The system is architected as a sovereign decision intelligence, where no single signal or algorithm controls execution. Instead, weighted consensus derived from predictive modeling, geometric analysis, and reinforcement feedback governs all actions.

This architecture emphasizes:

* Deterministic decision logic
* Real-time adaptability
* Controlled risk exposure
* Continuous learning and self-reweighting
* Modular replaceability

### 2. MACRO ARCHITECTURE OVERVIEW

TIER 1 – INPUT & INGESTION LAYER

* TickStreamHandler
* PriceFeedAdapter (Broker API / DEX RPC / MT5 Bridge)
* MarketNormalizer
* TimestampSynchronizer

TIER 2 – FEATURE & SIGNAL ENRICHMENT LAYER

* FeatureExtractorEngine
* VolatilityProfileBuilder
* SwingDetector
* ATRCalculator
* MomentumGradientAnalyzer

TIER 3 – PREDICTIVE SEQUENCE INTELLIGENCE LAYER

* SequenceModelEngine
* ONNXSequenceAdapter
* DirectionPredictor
* VolatilityPredictor
* RegimeProbabilityEstimator

TIER 4 – MARKET PSYCHOMETRICS & FIBONACCI CORE

* MasterFibonacciGovernor
* FibonacciClusterAI
* ElliottWaveForecastEngine
* PatternMemory
* VolatilityScoreMatrix
* TriFectaFibonacciRouter

TIER 5 – GLOBAL DECISION GOVERNOR

* MasterGovernorX100
* RegimeStateBuilder
* RegimeSwitchingRL
* DecisionOrchestrator
* SignalConfidenceCalibrator

TIER 6 – ENGINE EXECUTION CONTROL

* BinaryExecutor
* SpotExecutor
* ArbitrageExecutor
* RealTimeExecutionHub
* ShadowExecutionHub

TIER 7 – SAFETY & OVERRIDE LAYER

* SafetyManager
* DeploymentChecklist
* EmergencyShutdownController

TIER 8 – LEARNING & EVOLUTION SYSTEM

* RLJSONStore
* ArbitrageRLAgent
* TrainingOrchestrator
* ModelMutationController

TIER 9 – DATA LOGGING & OBSERVABILITY

* OmniLogger
* DecisionAuditTrail
* PerformanceRecorder

---

## MODULE DEPENDENCY MAP

### ROOT CONTROL DEPENDENCIES

OmniRuntime

* depends on MasterGovernorX100
* depends on RealTimeExecutionHub
* depends on OmniLogger
* depends on SafetyManager
* depends on TrainingOrchestrator

### GOVERNOR TREE

MasterGovernorX100

* uses RegimeSwitchingRL
* uses SequenceModelEngine / ONNXSequenceAdapter
* uses MasterFibonacciGovernor
* uses LadderRiskAI
* uses SpotTPRotator
* uses ArbitrageRLAgent

### FIBONACCI CORE DEPENDENCIES

MasterFibonacciGovernor

* uses FibonacciClusterAI
* uses ElliottWaveForecastEngine
* uses PatternMemory
* uses VolatilityScoreMatrix
* uses BinaryFibonacciEngine
* uses SpotFibonacciEngine
* uses ArbitrageFibonacciTiming

### EXECUTION DEPENDENCIES

BinaryExecutionHub

* links BrokerAPI / PocketOption

SpotExecutionHub

* links MT5 / REST Broker

FlashloanExecutor

* links Web3 RPC + Smart Contracts

### LEARNING DEPENDENCIES

TrainingOrchestrator

* reads logs from OmniLogger
* writes models to SequenceModelEngine
* updates RegimeSwitchingRL

RLJSONStore

* persists RegimeSwitchingRL and ArbitrageRLAgent state

### SAFETY DEPENDENCIES

SafetyManager

* intercepts OmniRuntime
* governs all execution controllers

DeploymentChecklist

* checks environment readiness

---

## FLOW-CONTROL GRAPH (INTER-MODULE CALL HIERARCHY)

### Primary Execution Loop

TickStreamHandler → OmniRuntime.on_tick()

OmniRuntime.on_tick()
→ SafetyManager.can_trade()
→ FeatureExtractorEngine.build_features()
→ MasterGovernorX100.decide()

MasterGovernorX100.decide()
→ SequenceModelEngine.predict()
→ RegimeStateBuilder.create_state()
→ RegimeSwitchingRL.choose_engine()
→ MasterFibonacciGovernor.evaluate_market()
→ DecisionOrchestrator.compile()

DecisionOrchestrator.compile()
→ Engine-Specific Modifiers

* LadderRiskAI.next_stake()
* SpotTPRotator.choose_tp()
* ArbitrageRLAgent.choose_route()

OmniRuntime.on_tick()
→ RealTimeExecutionHub.execute()
→ OmniLogger.log_trade()
→ RLJSONStore.save_state()
→ TrainingOrchestrator.maybe_retrain()

---

### Feedback Learning Cycle

Trade Executed
→ Outcome Evaluated
→ PnL Calculated
→ RegimeSwitchingRL.update()
→ ArbitrageRLAgent.update_route()
→ PatternMemory.store()

---

### Risk Interruption Flow

SafetyManager.detects_threshold_breach()
→ EmergencyShutdownController.freeze()
→ OmniLogger.alert()
→ Runtime Pause

---

## EXECUTION MODALITY INTERLOCK

Each engine (Binary, Spot, Arbitrage) runs in logical isolation but shares the same upstream intelligence flow. No engine may bypass:

* SafetyManager governance
* Decision confidence filters
* Fibonacci validation
* Regime selection

This ensures cross-market coherence and unified intelligence governance.

---

## EVOLUTIONARY LOOP

1. Log accumulation
2. Statistical review
3. RL score mutation
4. Model retraining
5. Confidence recalibration
6. Strategy evolution
7. Memory reinforcement

This loop cycles perpetually, shaping the system into a continuously optimizing intelligence structure.

---

## CONCLUSION

The Omni-Trifecta Quant Engine is not a trading strategy — it is an adaptive intelligence architecture. It perceives, calculates, learns, and evolves across markets using precision logic, geometric modeling, and probabilistic forecasting fortified by real-world feedback.

This documentation defines the skeletal blueprint. It is stable. It is scalable. It is built to expand indefinitely with new cognitive layers, execution logic, and predictive intelligence.

If you wish, the next evolution step can be a protocol-level specification or an interactive operational command map.

---

# DOC 1 – FORMAL SYSTEM ARCHITECTURE SPEC (ELITE VERSION)

## 1. System Identity

**Name:** Omni‑Trifecta Quant Engine
**Domains:**

* FX Spot
* Binary Options (5–60 min expiries)
* Flashloan / DEX Arbitrage

**Core Design Principles:**

* Multi‑engine, single‑brain architecture
* Deterministic decision logic with probabilistic forecasting
* Modular, replaceable components
* Explicit risk governance (no “hidden” risk)
* Persistent learning via RL + retraining pipelines

---

## 2. Layered Architecture

### 2.1 Layer 0 – Environment & Config

* **OmniConfig**

  * Loads runtime configuration from environment / `.env`:

    * Broker credentials (MT5, binary platform)
    * RPC endpoints and private keys (DEX / MEV)
    * Logging paths and model paths
  * Central source of truth for non‑secret config.

---

### 2.2 Layer 1 – Data Ingestion & Normalization

**Responsibility:** Convert raw market feeds into clean, timestamped price streams.

**Key Components:**

* **PriceFeedAdapter (examples)**

  * `mt5_price_feed_iter(symbol, poll_interval)`

    * Connects to MetaTrader5 terminal.
    * Yields mid‑price from bid/ask.
  * `binance_price_feed_iter(symbol)`

    * Connects to Binance WebSocket endpoint.
    * Yields latest trade price.

* **TickStreamHandler (implicit)**

  * The calling loop (`omni_main_loop`) consumes iterators from adapters.
  * Responsible for:

    * Building `price_window` (rolling list of last N prices).
    * Maintaining raw tick sequencing.

---

### 2.3 Layer 2 – Feature Construction

**Responsibility:** Build numerical features from raw price series.

**Key Structures:**

* `price_window: List[float]` – rolling context window (up to N ticks).
* `fx_vol, bin_vol, dex_vol: List[float]` – volatility proxies per domain.
* `swings: List[float]` – swing high/low points (future: swing detector module).

**Core Features (current skeleton):**

* **Volatility proxy:** `abs(price_window[-1] - price_window[0])`
* **Standard deviation:** `np.std(price_window)`

These are passed into:

* `SequenceModelEngine` (for volatility and directional predictions)
* `VolatilityScoreMatrix` (for fused multi‑domain vol score)
* `MasterGovernorX100` (for trend strength & regime state)

---

### 2.4 Layer 3 – Predictive Sequence Intelligence

**Core Class:** `SequenceModelEngine`

* Methods:

  * `predict_direction(window: List[float]) -> float`

    * Outputs `prob_up` in [0.0, 1.0].
    * Default logic: simple momentum‑based probability.
  * `predict_volatility(window: List[float]) -> float`

    * Outputs volatility estimate.

**ONNX Integration:** `ONNXSequenceAdapter(SequenceModelEngine)`

* Wraps an ONNXRuntime session.
* Extends methods:

  * `predict_direction` executes real LSTM/Transformer model:

    * Input: `[1, N]` float32 array of prices.
    * Output: neural prediction of `prob_up`.
  * `predict_volatility` can incorporate ONNX output or revert to std‑dev.

This layer is the **short‑term forecaster** that informs regime selection and engine risk profile.

---

### 2.5 Layer 4 – Fibonacci & Harmonic Intelligence Core

**Super‑Controller:** `MasterFibonacciGovernor`

Sub‑modules:

1. **FibonacciClusterAI**

   * ML clustering on recent price series using K‑Means.
   * Derives adaptive zones (cluster centers) representing dynamic support/resistance.

2. **Elliott Wave Forecast Engine**

   * `detect_wave(swings)` – inspects last 5 swing points.
   * Classifies simple impulse vs non‑impulse patterns.
   * `forecast_targets(high, low)` → uses `fibonacci_extensions` for wave targets.

3. **PatternMemory**

   * Stores historical harmonic patterns (e.g., GARTLEY, BAT, BUTTERFLY, CYPHER).
   * Uses frequency to determine most common pattern in recent history.

4. **VolatilityScoreMatrix**

   * Inputs: `fx_vol`, `binary_vol`, `dex_vol` (arrays).
   * Normalizes each series by its mean.
   * Combines most recent values with weighted average to produce `volatility_score`.

5. **Tri‑Fecta Engines**

   * `BinaryFibonacciEngine`

     * Uses fib retracements + ATR zones to trigger CALL/PUT when price enters fib band.
   * `SpotFibonacciEngine`

     * Uses 61.8% retracement + ATR to detect trend continuation entries.
     * Generates fib extension TP targets.
   * `ArbitrageFibonacciTiming`

     * Uses volatility compression (e.g., < 61.8% of mean) to flag potential expansion windows.

`MasterFibonacciGovernor.evaluate_market(...)` integrates all of them into an **enriched fib decision block**.

---

### 2.6 Layer 5 – Regime‑Switching & Global Decision Governor

**Main Brain:** `MasterGovernorX100`

Responsibilities:

* Build `RegimeState` from:

  * `vol_score = predict_volatility(...)`
  * `trend_strength = |last - first| / std(price_window)`
  * `mean_reversion_score = 1 - trend_strength`
* Use `RegimeSwitchingRL` to select engine type.
* Use `MasterFibonacciGovernor` to enrich decision with geometry + history.
* Apply engine‑specific modifiers:

  * `LadderRiskAI` for binary sizing.
  * `SpotTPRotator` for TP selection.
  * `ArbitrageRLAgent` for route choice.
* Output final decision payload for execution layer.

`RegimeSwitchingRL`:

* Maintains a Q‑table for engine performance.
* `choose_engine(state)` uses heuristics + can be extended to Q‑based.
* `update(engine, reward)` updates estimated value of each engine type.

This layer ensures that the system chooses **not just whether to trade**, but **how to trade** given current conditions.

---

### 2.7 Layer 6 – Execution Engines

**Binary Execution Path:**

* Engine: `BinaryFibonacciEngine` → `LadderRiskAI` → `RealTimeExecutionHub.binary`
* Trade type: CALL/PUT with defined expiry.
* Stake: controlled by ladder logic and balance.

**Spot Execution Path:**

* Engine: `SpotFibonacciEngine` → `SpotTPRotator` → `RealTimeExecutionHub.spot`
* Trade type: BUY/SELL with TP (and optional SL) on MT5/CFD broker.

**Arbitrage Execution Path:**

* Engine: `ArbitrageFibonacciTiming` → `ArbitrageRLAgent` → `RealTimeExecutionHub.arb`
* Trade type: route execution over defined DEX/flashloan combos.

`RealTimeExecutionHub` dispatches to:

* `MT5SpotExecutor`
* `BinaryExecutor`
* `ArbitrageExecutor`

`ShadowExecutionHub` mirrors the same interface but no real orders are placed; returns SHADOW results.

---

### 2.8 Layer 7 – Safety & Governance

**SafetyManager**

* Enforces per‑day and per‑session limits:

  * `max_daily_loss`
  * `max_daily_trades`
  * `max_loss_streak`
* Tracks:

  * `daily_pnl`, `trades_count`, `loss_streak`, `cooldown`.
* If any cap is triggered → system switches to cooldown mode.

**DeploymentChecklist**

* Programmatically verifies:

  * MT5 credentials present.
  * Binary token present.
  * DEX RPC + private key.
  * Log directory accessibility.
* Returns boolean flags + aggregate `all_passed`.

---

### 2.9 Layer 8 – Learning, Persistence & Evolution

**RLJSONStore**

* Saves and loads:

  * `RegimeSwitchingRL.q_table`
  * `ArbitrageRLAgent.route_scores`
* Ensures RL knowledge persists across sessions.

**TrainingOrchestrator**

* Reads:

  * `ticks.jsonl`
  * `trades.jsonl`
* Functions:

  * `update_rl_from_trades(regime_rl, arb_rl)` – RL reward updates from realized PnL.
  * `retrain_sequence_model(trainer_callback)` – triggers external ML pipeline, receives new ONNX model path.

This layer is how the system *evolves* rather than remains static.

---

### 2.10 Layer 9 – Runtime Orchestration & Logging

**OmniRuntime**

* Holds:

  * `MasterGovernorX100`
  * `RealTimeExecutionHub` or `ShadowExecutionHub`
  * `RLJSONStore`
* Responsibilities:

  * On each tick: decision + execution.
  * On shutdown: persist RL state.

**OmniLogger**

* Writes JSONL logs compatible with training and audit.
* `log_tick(symbol, price, ts)`
* `log_trade(record)` for decisions + outcomes.

**omni_main_loop(...)**

* Forms the outer loop:

  * Reads tick stream.
  * Updates feature buffers.
  * Calls runtime.
  * Updates balance.
  * Logs everything.

---

# DOC 2 – MODULE / COMPONENT DEPENDENCY MAP (EXHAUSTIVE)

## 1. High-Level Modules

* **Core Brain:** `MasterGovernorX100`
* **Fib Core:** `MasterFibonacciGovernor`
* **Execution:** `RealTimeExecutionHub`, `ShadowExecutionHub`, `MT5SpotExecutor`, `BinaryExecutor`, `ArbitrageExecutor`
* **Learning:** `RegimeSwitchingRL`, `ArbitrageRLAgent`, `RLJSONStore`, `TrainingOrchestrator`
* **Safety:** `SafetyManager`, `DeploymentChecklist`
* **Runtime:** `OmniRuntime`, `OmniLogger`
* **Config:** `OmniConfig`

---

## 2. Detailed Dependency Tree

### 2.1 MasterGovernorX100

**Depends on:**

* `SequenceModelEngine` / `ONNXSequenceAdapter`
* `RegimeSwitchingRL`
* `MasterFibonacciGovernor`
* `LadderRiskAI`
* `SpotTPRotator`
* `ArbitrageRLAgent`

**Inputs to decide():**

* `price_window`
* `swings`
* `fx_vol`, `bin_vol`, `dex_vol`
* `balance`

**Outputs:**

* Decision dict containing:

  * `engine_type`
  * `direction_prob`
  * `regime_state`
  * `fib_block`
  * `stake` (for binary)
  * `tp` (for spot)
  * `route_id` (for arb)

---

### 2.2 MasterFibonacciGovernor

**Depends on:**

* `FibonacciClusterAI`
* `WaveForecastEngine`
* `PatternMemory`
* `VolatilityScoreMatrix`
* `TriFectaFibonacciSystem` (which includes Binary, Spot, Arbitrage fib engines)

**Inputs:**

* `engine_type`
* `price_series`
* `swings`
* `fx_vol`, `binary_vol`, `dex_vol`

**Outputs (enriched block):**

* `base_signal`
* `clusters`
* `wave_state`
* `pattern_memory`
* `volatility_score`
* `final_decision`

---

### 2.3 TriFectaFibonacciSystem

**Contains:**

* `BinaryFibonacciEngine`
* `SpotFibonacciEngine`
* `ArbitrageFibonacciTiming`

**Public API:**

* `analyze(engine_type, **kwargs)` → dispatch to appropriate engine.

**Dependencies:**

* Utility functions: `fibonacci_retracements`, `fibonacci_extensions`, `atr_adjusted_zone`.

---

### 2.4 Sequence & RL

* `SequenceModelEngine`

  * Independent, only depends on numpy.
* `ONNXSequenceAdapter`

  * Extends `SequenceModelEngine`.
  * Depends on `onnxruntime`.
* `RegimeSwitchingRL`

  * Standalone; stores Q‑values.
* `ArbitrageRLAgent`

  * Standalone; stores `route_scores`.
* `RLJSONStore`

  * Depends on filesystem (Path, JSON).
* `TrainingOrchestrator`

  * Depends on logs produced by `OmniLogger`.

---

### 2.5 Execution Layer

* `RealTimeExecutionHub`

  * Depends on:

    * `fx_executor` (e.g., `MT5SpotExecutor`)
    * `binary_executor` (e.g., `BinaryExecutor`)
    * `spot_executor`
    * `arb_executor` (e.g., `ArbitrageExecutor`)

* `ShadowExecutionHub`

  * Extends `RealTimeExecutionHub` but overrides `execute()`.

* `MT5SpotExecutor`

  * Depends on `MT5Bridge` (external) implementing `send_order(...)`.

* `BinaryExecutor`

  * Depends on `PocketAPI` or similar `place_trade(...)` method.

* `ArbitrageExecutor`

  * Depends on a `route_registry` dict mapping `route_id` → callable.

---

### 2.6 Runtime & Safety

* `OmniRuntime`

  * Depends on:

    * `MasterGovernorX100`
    * `RealTimeExecutionHub` or `ShadowExecutionHub`
    * `RLJSONStore`

* `SafetyManager`

  * Embedded in main loop, not in `OmniRuntime` by default.

* `DeploymentChecklist`

  * Depends on `OmniConfig`.

* `OmniLogger`

  * Depends on filesystem write access.

---

# DOC 3 – FLOW-CONTROL GRAPH & CALL HIERARCHY

This section describes the **exact sequence of calls and decision branches** from raw tick to executed (or simulated) trade.

## 1. Tick → Decision → Execution Flow

1. **Tick Arrival**

   * Source:

     * `mt5_price_feed_iter` (FX)
     * or `binance_price_feed_iter` (CEX)
   * Data:

     * `price: float`
     * `symbol: str`

2. **Main Loop (`omni_main_loop`)**

   * Append `price` to `price_window`.
   * Maintain rolling length (e.g., 256).
   * Update volatility proxies `fx_vol`, `bin_vol`, `dex_vol`.
   * Log tick via `OmniLogger.log_tick`.

3. **Safety Check**

   * `SafetyManager.can_trade()` is checked.
   * If `False`:

     * Log trade entry with `mode = "COOLDOWN"`.
     * Skip decision + execution.
   * If `True`:

     * Proceed.

4. **Runtime Tick Handling**

   * `OmniRuntime.on_tick(...)` called with:

     * `price_window`, `swings`, `fx_vol`, `bin_vol`, `dex_vol`, `balance`, `ctx`.

5. **Governor Decision**

   * Inside `OmniRuntime.on_tick`:

     * `decision = governor.decide(...)`

### Inside `MasterGovernorX100.decide`:

5.1 **Sequence Model Invocation**

* `dir_prob = seq_model.predict_direction(price_window)`
* `vol_est = seq_model.predict_volatility(price_window)`

5.2 **Regime State Construction**

* `trend_strength = |last - first| / (std(price_window) + ε)`
* `mean_reversion_score = 1 - trend_strength`
* `state = RegimeState(vol_score=vol_est, trend_strength=trend_strength, mean_reversion_score=...)`

5.3 **Engine Selection**

* `engine_type = RegimeSwitchingRL.choose_engine(state)`
* Logic (initial):

  * If `vol_score > threshold` → `"binary"`.
  * Else if `trend_strength > threshold` → `"spot"`.
  * Else → `"arbitrage"`.

5.4 **Fibonacci Governor Enrichment**

* `enriched = MasterFibonacciGovernor.evaluate_market(engine_type, ...)`

Inside `evaluate_market`:

* Compute cluster centers via `FibonacciClusterAI.learn_zones(price_series)`.
* Compute `wave_state` via `WaveForecastEngine.detect_wave(swings)`.
* Recall `pattern_memory` via `PatternMemory.recall()`.
* Compute `volatility_score` via `VolatilityScoreMatrix.score(...)`.
* Compute `base_signal` via `TriFectaFibonacciSystem.analyze(engine_type, ...)`.
* Decide `final_decision` based on `base_signal` + `volatility_score` + `wave_state`.
* Potentially store new patterns via `PatternMemory.store(...)`.

5.5 **Decision Envelope Construction**

* `decision` dict created with:

  * `engine_type`
  * `direction_prob`
  * `regime_state`
  * `fib_block = enriched`
  * placeholders for `stake`, `tp`, `route_id`.

5.6 **Engine-Specific Enhancements**

* **Binary path**:

  * `stake = LadderRiskAI.next_stake(balance, last_win)`
  * `decision["stake"] = stake`

* **Spot path**:

  * Extract `fib_exts = base_signal.get("tp_targets", {})`.
  * `tp = SpotTPRotator.choose_tp(fib_exts, atr_estimate, trend_strength)`.
  * `decision["tp"] = tp`.

* **Arbitrage path**:

  * `route_id = ArbitrageRLAgent.choose_best_route(candidate_routes)`.
  * `decision["route_id"] = route_id`.

6. **Execution Layer**

* `result = RealTimeExecutionHub.execute(decision, ctx)` **or** `ShadowExecutionHub.execute(...)`.

Inside `execute`:

* If `engine_type == "binary"`:

  * Calls `binary_executor.place_trade(symbol, direction, expiry, stake)`.
* If `engine_type == "spot"`:

  * Calls `spot_executor.open_position(symbol, direction, volume, tp)`.
* If `engine_type == "arbitrage"`:

  * Calls `arb_executor.execute_route(route_id, ctx)`.

7. **Post-Execution Handling**

Inside `omni_main_loop`:

* Compute `pnl` from `result` (for now: assume direct field, future: reconcile with broker/chain fills).
* `balance += pnl`.
* `SafetyManager.register_trade(pnl)` → may toggle `cooldown`.
* `OmniLogger.log_trade({...})` records trade.

8. **Session End**

* On program shutdown or explicit termination:

  * `OmniRuntime.shutdown()` called.
  * `RLJSONStore.save_regime(...)` and `save_routes(...)` persist RL state.

---

## 2. Learning & Evolution Flow

1. Trades & ticks written to JSONL logs.
2. Offline or scheduled process runs `TrainingOrchestrator`.
3. `update_rl_from_trades` updates:

   * `RegimeSwitchingRL.q_table`
   * `ArbitrageRLAgent.route_scores`.
4. `retrain_sequence_model(trainer_callback)` runs external ML training on tick history.
5. New ONNX file path is returned.
6. Runtime is restarted or hot‑swapped with `ONNXSequenceAdapter(new_path)`.
7. Updated RL state is loaded from JSON via `RLJSONStore.load_*`.

This loop continuously refines both **high‑level engine selection** and **micro‑level directional forecasting**.

---

# DOC 4 – OPERATIONAL RUNBOOK & DEPLOYMENT PROTOCOL

This document is for devs/operators running the Omni‑Trifecta system in real environments.

## 1. Prerequisites

### 1.1 Infrastructure

* Server or VPS with:

  * Python 3.10+
  * Enough RAM for ONNX + logging (8GB+ recommended).
  * Stable low‑latency Internet.
* MT5 terminal installed and connected to broker (if using FX).
* Node / RPC access for DEX/flashloan side (if using arbitrage).

### 1.2 Software Dependencies

* Python packages (minimum):

  * `numpy`
  * `pandas` (for analytics/backtesting)
  * `onnxruntime`
  * `MetaTrader5`
  * `websockets`
  * `python-dotenv`
  * `web3` (for on‑chain integration)
  * `scikit-learn`

### 1.3 External Bridges

* `MT5Bridge` implementing:

  * `send_order(symbol, direction, volume, tp=None, sl=None)`.
* `PocketAPI` or equivalent implementing:

  * `place_trade(symbol, direction, expiry, stake)`.
* On‑chain executor functions mapped in `route_registry`.

---

## 2. Configuration Setup

1. Create `.env` with fields:

   * `MT5_LOGIN`, `MT5_SERVER`, `MT5_PASSWORD`
   * `POCKET_TOKEN`, `POCKET_BASE_URL`
   * `DEX_RPC`, `DEX_PRIVKEY`
   * `MEV_RELAY_URL` (optional)
   * `OMNI_LOG_DIR`
   * `SEQ_MODEL_ONNX`

2. Verify environment:

   * Instantiate `cfg = OmniConfig()`.
   * `DeploymentChecklist(cfg).verify()` should return `all_passed = True` before any live run.

---

## 3. Operational Modes

### 3.1 Backtest Mode

**Purpose:** Validate strategies on historical data.

Steps:

1. Load historical price series into memory (e.g., `prices = [...]`).
2. Initialise governor:

   * `gov = MasterGovernorX100()`.
3. Optionally assign ONNX model:

   * `gov.seq_model = ONNXSequenceAdapter(onnx_path)`.
4. Create logger (optional):

   * `logger = OmniLogger("runtime/logs")`.
5. Run backtest:

   * `be = BacktestEngine(governor=gov, logger=logger)`.
   * `result = be.run(prices, symbol="EURUSD", starting_balance=100.0)`.
6. Analyse:

   * `equity_curve`, `final_balance`, distribution of PnL per trade.

### 3.2 Shadow Live Mode

**Purpose:** Live environment, zero execution risk.

Steps:

1. Replace `RealTimeExecutionHub` with `ShadowExecutionHub`.
2. Use actual live feed (`mt5_price_feed_iter` or `binance_price_feed_iter`).
3. Run `omni_main_loop` normally.
4. Monitor:

   * Logged decisions vs real price movement.
   * Potential PnL if trades had been executed.

### 3.3 Micro Live Mode

**Purpose:** Real trades, minimal capital risk.

Steps:

1. Use `RealTimeExecutionHub` with properly configured executors.
2. Configure `SafetyManager` with conservative thresholds:

   * e.g., `max_daily_loss = 10`, `max_daily_trades = 20`, `max_loss_streak = 3`.
3. Start with very small:

   * Minimal stake for binary.
   * Minimal lot size/volume for spot.
4. Run `omni_main_loop`.
5. Observe behaviour for multiple days/weeks.

### 3.4 Scaled Live Mode

**Purpose:** Gradually increase capital allocation.

Rules:

* Only after:

  * Backtest stats are positive.
  * Shadow mode demonstrates edge.
  * Micro live PnL is net positive with controlled drawdown.
* Increase position size gradually.
* Never disable `SafetyManager`.
* Keep RL + model retraining frequency controlled (e.g., nightly or weekly).

---

## 4. Monitoring & Maintenance

### 4.1 Key Metrics to Watch

* Win‑rate by engine (`binary`, `spot`, `arbitrage`).
* Average R:R for spot trades.
* Route performance (`ArbitrageRLAgent.route_scores`).
* Q‑values in `RegimeSwitchingRL.q_table`.
* Equity curve shape: drawdowns, volatility of returns.

### 4.2 Log Review

* `ticks.jsonl` → for model training and anomaly detection.
* `trades.jsonl` → for PnL, mode, engine, route analysis.

### 4.3 Retraining Procedure

1. Stop live execution or switch to Shadow mode.
2. Run `TrainingOrchestrator.update_rl_from_trades`.
3. Run `TrainingOrchestrator.retrain_sequence_model(trainer_callback)`.
4. Replace old ONNX path in `.env` or at runtime.
5. Restart system or hot‑swap `gov.seq_model`.

---

## 5. Failure Modes & Responses

### 5.1 Broker/Exchange Disconnection

* Detect via failed API responses.
* Switch to ShadowExecutionHub.
* Log incident.
* Pause real trading until connectivity restored.

### 5.2 RPC/Node Failure

* Detect via Web3 errors.
* For `arbitrage` engine:

  * Force engine selection away from arbitrage mode.
  * Or set `vol_score` for DEX to zero.

### 5.3 Model Corruption / ONNX Errors

* Catch exceptions on ONNX session load.
* Fall back to simple `SequenceModelEngine`.
* Log error and trigger retraining pipeline.

### 5.4 SafetyManager Cooldown

* Once cooldown is triggered:

  * Do not auto‑reset during same session.
  * Require manual operator review.
  * Optionally reset with new capital parameters.

---

## 6. Change Management

Any change to:

* Model architecture
* RL parameters
* Engine selection logic
* Ladder risk settings
* TP/SL behaviour

MUST go through:

1. Backtest.
2. Shadow mode.
3. Micro live test.

Only after passing all three, it should be allowed into scaled live mode.

---

This four‑document bundle (Architecture, Dependency Map, Flow Graph, Runbook) forms the **complete elite‑grade specification** for the Omni‑Trifecta system. It tells a senior quant/dev everything they need to understand, implement, audit, and operate this engine without guesswork.
