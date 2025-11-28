# 🎯 EXECUTION LOGIC - ALL 3 ENGINES

## Complete Technical Reference for Binary Options, Spot Forex, and Flashloan Arbitrage

**Status:** 🟢 Production-Ready  
**Last Updated:** November 28, 2025

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Engine 1: Binary Options Execution](#engine-1-binary-options-execution)
3. [Engine 2: Spot Forex Execution](#engine-2-spot-forex-execution)
4. [Engine 3: Flashloan Arbitrage Execution](#engine-3-flashloan-arbitrage-execution)
5. [Common Execution Flow](#common-execution-flow)
6. [Decision Governor Logic](#decision-governor-logic)
7. [Safety & Risk Management](#safety--risk-management)
8. [Code Reference Summary](#code-reference-summary)

---

## System Overview

The Omni-Trifecta Quant Engine operates **three distinct execution engines**, each optimized for its specific market domain:

| Engine | Market Domain | Trade Type | Duration | Key Characteristics |
|--------|---------------|------------|----------|---------------------|
| **Binary** | Binary Options | CALL/PUT | 60s - 5min | Fixed expiry, binary outcome |
| **Spot** | Forex Markets | BUY/SELL | Minutes - Hours | TP/SL management, position sizing |
| **Arbitrage** | DEX/CEX | Multi-hop routes | Milliseconds | Flashloans, cross-chain |

### Execution Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TICK STREAM / PRICE FEED                          │
│         (MT5, Binance WebSocket, DEX RPC, YFinance)                 │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   OMNI RUNTIME (orchestration.py)                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  1. SafetyManager.can_trade() - Pre-trade safety check        │  │
│  │  2. MasterGovernorX100.decide() - Intelligence processing    │  │
│  │  3. RealTimeExecutionHub.execute() - Engine dispatch          │  │
│  │  4. OmniLogger.log_trade() - Audit trail                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────────┘
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│    BINARY     │ │     SPOT      │ │   ARBITRAGE   │
│   EXECUTOR    │ │   EXECUTOR    │ │   EXECUTOR    │
│               │ │               │ │               │
│ CALL/PUT      │ │ BUY/SELL      │ │ 2/3/4-HOP     │
│ Fixed Expiry  │ │ TP/SL Mgmt    │ │ Flashloans    │
└───────────────┘ └───────────────┘ └───────────────┘
```

---

## Engine 1: Binary Options Execution

### Purpose
Execute short-duration directional speculation trades with fixed expiry times and binary outcomes (win/loss).

### Execution Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  BINARY OPTIONS EXECUTION FLOW                                       │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Signal Generation
├── BinaryFibonacciEngine.analyze()
│   ├── Calculate Fibonacci retracement levels
│   ├── Check if price is near 0.382 or 0.618 level
│   ├── Determine momentum direction (last 10 prices)
│   └── Output: {signal: 'CALL'/'PUT', confidence: 0.0-1.0}

Step 2: Governor Enhancement
├── MasterGovernorX100._enhance_binary_decision()
│   ├── LadderRiskAI.next_stake(balance, last_win)
│   │   ├── Win: Reset to base_stake
│   │   └── Loss: Multiply stake by 2.0 (up to max_stake)
│   ├── Set direction from direction_prob
│   │   ├── prob > 0.5 → CALL
│   │   └── prob ≤ 0.5 → PUT
│   └── Set expiry (default 300 seconds)

Step 3: Execution
├── BinaryExecutor.execute(decision, ctx)
│   ├── Extract: symbol, direction, stake, expiry
│   ├── If api_client available:
│   │   └── api_client.place_trade(symbol, direction, stake, expiry)
│   └── Return: {success, trade_id, pnl, mode}

Step 4: Shadow Mode Alternative
└── ShadowExecutionHub.execute()
    ├── Simulate 60% win rate
    ├── Win: pnl = stake * 0.8 (80% payout)
    └── Loss: pnl = -stake
```

### Key Components

#### BinaryFibonacciEngine (fibonacci/engines.py)

```python
class BinaryFibonacciEngine:
    """Fibonacci-based signal generator for binary options."""
    
    def analyze(self, price_series, high, low, atr) -> Dict:
        """
        Analyze market for binary option entry.
        
        Logic:
        1. Calculate Fibonacci levels (0.236, 0.382, 0.500, 0.618, 0.786, 1.0)
        2. Create ATR-adjusted zones around each level
        3. If price within 0.382 or 0.618 zone:
           - Check momentum (current vs 10 periods ago)
           - Positive momentum → CALL signal
           - Negative momentum → PUT signal
        4. Return signal with confidence (0.7 for key levels)
        """
```

#### LadderRiskAI (decision/rl_agents.py)

```python
class LadderRiskAI:
    """Ladder-based position sizing for binary options."""
    
    def __init__(self, base_stake=1.0, max_stake=100.0, multiplier=2.0):
        self.current_stake = base_stake
        self.win_streak = 0
        self.loss_streak = 0
    
    def next_stake(self, balance, last_win) -> float:
        """
        Calculate next stake based on last result.
        
        Logic:
        - Win: Reset to base_stake, increment win_streak
        - Loss: Multiply stake by 2.0, increment loss_streak
        - Apply limits:
          - Cap at max_stake
          - Cap at 10% of balance
        """
```

#### BinaryExecutor (execution/executors.py)

```python
class BinaryExecutor(ExecutorBase):
    """Binary options executor."""
    
    def execute(self, decision, ctx) -> Dict:
        """
        Execute binary option trade.
        
        Parameters:
        - symbol: Trading pair (e.g., 'EURUSD')
        - direction: 'CALL' or 'PUT'
        - stake: Amount to risk
        - expiry: Duration in seconds
        
        Production Integration:
        - PocketOption API
        - IQ Option API
        - Deriv/Binary.com API
        """
```

### Decision Output Format

```python
binary_decision = {
    "engine_type": "binary",
    "direction_prob": 0.65,          # Probability from sequence model
    "direction": "CALL",             # or "PUT"
    "stake": 5.0,                    # Calculated by LadderRiskAI
    "expiry": 300,                   # 5 minutes
    "symbol": "EURUSD",
    "regime_state": RegimeState(...),
    "fib_block": {
        "signal": "CALL",
        "confidence": 0.7,
        "fib_levels": {...}
    }
}
```

---

## Engine 2: Spot Forex Execution

### Purpose
Execute trend-following and mean-reversion trades in the forex market with take-profit and stop-loss management.

### Execution Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  SPOT FOREX EXECUTION FLOW                                           │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Signal Generation
├── SpotFibonacciEngine.analyze()
│   ├── Calculate Fibonacci retracement levels
│   ├── Calculate Fibonacci extension targets
│   ├── Check for 61.8% (golden ratio) retracement
│   ├── If trend_strength > 0.5 AND price at golden ratio:
│   │   ├── Uptrend (high > low) → BUY
│   │   └── Downtrend (low > high) → SELL
│   └── Output: {signal, confidence, entry, tp_targets, fib_retracements}

Step 2: Governor Enhancement
├── MasterGovernorX100._enhance_spot_decision()
│   ├── SpotTPRotator.choose_tp(fib_extensions, atr, trend_strength)
│   │   ├── trend_strength > 0.8 → Use 1.618 extension
│   │   ├── trend_strength > 0.6 → Use 1.414 extension
│   │   └── Otherwise → Use 1.272 extension
│   ├── Set SL = ATR * 1.5
│   ├── Set volume = 0.01 (micro lot)
│   └── Set direction from direction_prob
│       ├── prob > 0.5 → BUY
│       └── prob ≤ 0.5 → SELL

Step 3: Execution
├── MT5SpotExecutor.execute(decision, ctx)
│   ├── Extract: symbol, direction, volume, tp, sl
│   ├── If mt5_bridge available:
│   │   └── mt5_bridge.send_order(symbol, direction, volume, tp, sl)
│   └── Return: {success, order_id, pnl, mode}

Step 4: Shadow Mode Alternative
└── ShadowExecutionHub.execute()
    ├── Simulate Gaussian distribution around TP
    └── pnl = random.gauss(0, tp * 0.5)
```

### Key Components

#### SpotFibonacciEngine (fibonacci/engines.py)

```python
class SpotFibonacciEngine:
    """Fibonacci-based signal generator for spot forex trading."""
    
    def analyze(self, price_series, high, low, atr, trend_strength) -> Dict:
        """
        Analyze market for spot forex entry.
        
        Logic:
        1. Calculate Fibonacci retracements:
           - 0.0, 0.236, 0.382, 0.500, 0.618, 0.786, 1.0
        2. Calculate Fibonacci extensions:
           - 1.272, 1.414, 1.618, 2.0, 2.618
        3. Create ATR-adjusted zone around 0.618 level
        4. If trend_strength > 0.5 AND price in golden zone:
           - Generate signal with confidence = 0.8 * trend_strength
        5. Return signal with TP targets from extensions
        """
```

#### SpotTPRotator (decision/rl_agents.py)

```python
class SpotTPRotator:
    """Take-profit selector for spot forex trades."""
    
    def choose_tp(self, fib_extensions, atr, trend_strength) -> float:
        """
        Choose take-profit level based on trend strength.
        
        Logic:
        - Very strong trend (> 0.8): Use 1.618 extension (larger target)
        - Strong trend (> 0.6): Use 1.414 extension
        - Moderate trend: Use 1.272 extension (conservative)
        - Fallback if no extensions: ATR * 3.0
        """
```

#### MT5SpotExecutor (execution/executors.py)

```python
class MT5SpotExecutor(ExecutorBase):
    """MT5 spot forex executor."""
    
    def execute(self, decision, ctx) -> Dict:
        """
        Execute spot forex trade.
        
        Parameters:
        - symbol: Currency pair (e.g., 'EURUSD')
        - direction: 'BUY' or 'SELL'
        - volume: Position size in lots
        - tp: Take-profit price level
        - sl: Stop-loss price level
        
        Production Integration:
        - MetaTrader 5 terminal
        - OANDA REST API
        - Alpaca API
        - CCXT for exchange trading
        """
```

#### ForexExecutor (execution/executors.py)

```python
class ForexExecutor(ExecutorBase):
    """Forex trade executor for paper trading."""
    
    async def execute_paper_trade(self, pair, signal, entry_price,
                                   take_profit, stop_loss, size) -> Dict:
        """
        Execute paper forex trade.
        
        Simulation Logic:
        - Calculate risk = abs(entry_price - stop_loss)
        - Calculate reward = abs(take_profit - entry_price)
        - Win probability = 60%
        - Win: pnl = size * (reward / entry_price)
        - Loss: pnl = -size * (risk / entry_price)
        """
```

### Decision Output Format

```python
spot_decision = {
    "engine_type": "spot",
    "direction_prob": 0.72,          # Probability from sequence model
    "direction": "BUY",              # or "SELL"
    "volume": 0.01,                  # Micro lot
    "tp": 0.0050,                    # Take-profit in price units
    "sl": 0.0015,                    # Stop-loss (ATR * 1.5)
    "symbol": "EURUSD",
    "regime_state": RegimeState(...),
    "fib_block": {
        "signal": "BUY",
        "confidence": 0.64,          # 0.8 * trend_strength
        "entry": 1.0850,
        "tp_targets": {
            "1.272": 1.0890,
            "1.414": 1.0920,
            "1.618": 1.0960
        }
    }
}
```

---

## Engine 3: Flashloan Arbitrage Execution

### Purpose
Execute intra-block inefficiency exploitation through multi-hop arbitrage routes across DEXes and CEXes, optionally using flashloans for capital efficiency.

### Execution Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│  FLASHLOAN ARBITRAGE EXECUTION FLOW                                  │
└─────────────────────────────────────────────────────────────────────┘

Step 1: Timing Signal Generation
├── ArbitrageFibonacciTiming.analyze()
│   ├── Calculate volatility statistics
│   ├── Check for volatility compression (< 61.8% of mean)
│   │   └── Compression → READY signal (potential expansion)
│   ├── Check for high volatility (> mean + std)
│   │   └── High vol → EXECUTE signal (opportunity window)
│   └── Output: {timing: 'READY'/'EXECUTE'/'WAIT', confidence}

Step 2: Governor Enhancement
├── MasterGovernorX100._enhance_arbitrage_decision()
│   ├── ArbitrageRLAgent.choose_best_route(candidate_routes)
│   │   ├── Initialize scores for new routes
│   │   └── Select route with highest historical score
│   ├── Set route_id (e.g., 'uniswap_v3', 'sushiswap')
│   └── Set amount from context

Step 3: Route Calculation
├── MultiHopArbitrageCalculator.calculate_*_arbitrage()
│   ├── 2-HOP: A → B → A (cross-exchange)
│   │   ├── Buy on Exchange 1 (apply fee + slippage)
│   │   ├── Sell on Exchange 2 (apply fee + slippage)
│   │   ├── Subtract gas costs
│   │   └── Calculate net profit in bps
│   ├── 3-HOP: A → B → C → A (triangular)
│   │   ├── Step 1: USDT → BTC (fee + slippage)
│   │   ├── Step 2: BTC → ETH (fee + slippage)
│   │   ├── Step 3: ETH → USDT (fee + slippage)
│   │   ├── Subtract gas costs
│   │   └── Calculate net profit in bps
│   └── 4-HOP: A → B → C → D → A (rectangular)
│       ├── Execute 4 sequential swaps
│       ├── Use Decimal precision for calculations
│       └── Calculate net profit with safety margin

Step 4: Risk Assessment
├── MultiHopArbitrageCalculator.calculate_risk_reward_ratio()
│   ├── Calculate potential reward
│   ├── Calculate risks:
│   │   ├── Slippage risk (2x worst case)
│   │   ├── Fee risk (1.5x expected)
│   │   ├── Gas risk (2x for spikes)
│   │   ├── Liquidity risk (1% capital)
│   │   └── Execution risk (time-dependent)
│   ├── Calculate risk/reward ratio
│   ├── Estimate profit probability
│   ├── Calculate expected value
│   └── Calculate Kelly fraction for sizing

Step 5: Execution
├── ArbitrageExecutor.execute(decision, ctx)
│   ├── If route_id in route_registry:
│   │   ├── Get execution function
│   │   └── Execute with amount and context
│   └── Return: {success, route, pnl, mode}

Step 6: Shadow Mode Alternative
└── ShadowExecutionHub.execute()
    └── pnl = random.uniform(0, 0.01) * capital
```

### Key Components

#### ArbitrageFibonacciTiming (fibonacci/engines.py)

```python
class ArbitrageFibonacciTiming:
    """Fibonacci-based timing for arbitrage opportunities."""
    
    def analyze(self, dex_vol, volatility_score) -> Dict:
        """
        Analyze timing for arbitrage execution.
        
        Logic:
        1. Calculate volatility mean and std
        2. Set compression threshold = mean * 0.618
        3. If volatility < compression threshold:
           - Return READY signal (expansion incoming)
        4. If volatility > mean + std:
           - Return EXECUTE signal (opportunity window)
        5. Otherwise WAIT
        """
```

#### MultiHopArbitrageCalculator (execution/arbitrage_calculator.py)

```python
class MultiHopArbitrageCalculator:
    """Calculate multi-hop arbitrage opportunities with risk analysis."""
    
    def __init__(self, min_profit_bps=30.0, max_slippage_bps=50.0, safety_margin=0.20):
        """
        Initialize with thresholds:
        - min_profit_bps: Minimum 0.30% profit required
        - max_slippage_bps: Maximum 0.50% slippage acceptable
        - safety_margin: 20% safety buffer on calculations
        """
    
    def calculate_2hop_arbitrage(self, pair1, pair2, capital) -> Optional[ArbitrageRoute]:
        """
        Calculate 2-hop arbitrage profit.
        
        Path: Currency A → Currency B → Currency A
        Example: USDT → BTC → USDT
        
        Steps:
        1. Buy on Exchange 1
           - Apply trading fee
           - Calculate slippage based on trade size
           - Convert to target currency
        2. Sell on Exchange 2
           - Apply trading fee
           - Calculate slippage
           - Convert back to quote currency
        3. Subtract gas costs
        4. Calculate gross profit and profit in bps
        5. Apply safety margin
        6. Return None if below min_profit_bps
        """
    
    def calculate_3hop_arbitrage(self, pair1, pair2, pair3, capital) -> Optional[ArbitrageRoute]:
        """
        Calculate triangular arbitrage profit.
        
        Path: A → B → C → A
        Example: USDT → BTC → ETH → USDT
        """
    
    def calculate_4hop_arbitrage(self, pair1, pair2, pair3, pair4, capital) -> Optional[ArbitrageRoute]:
        """
        Calculate rectangular arbitrage profit.
        
        Path: A → B → C → D → A
        Example: USDT → BTC → ETH → BNB → USDT
        
        Uses Decimal precision for 18-digit accuracy.
        """
```

#### ArbitrageRLAgent (decision/rl_agents.py)

```python
class ArbitrageRLAgent:
    """RL agent for arbitrage route selection."""
    
    def __init__(self, learning_rate=0.1):
        self.route_scores: Dict[str, float] = {}
    
    def choose_best_route(self, candidate_routes) -> str:
        """
        Choose best arbitrage route based on historical performance.
        
        Logic:
        - Initialize score = 0.0 for new routes
        - Select route with highest historical score
        """
    
    def update_route(self, route_id, reward):
        """
        Update route score based on execution result.
        
        Uses exponential moving average:
        new_score = (1 - α) * old_score + α * reward
        """
    
    def evaluate_opportunity(self, order_proposal) -> Dict:
        """
        Evaluate arbitrage opportunity.
        
        Criteria:
        - Expected profit >= 0.5% of capital
        - Risk score <= 75/100
        """
```

#### Cross-Chain Token Equivalence (execution/token_equivalence.py)

```python
class TokenEquivalenceRegistry:
    """Registry for cross-chain token mapping."""
    
    def find_cross_chain_arbitrage(self, token_group, prices) -> List[Dict]:
        """
        Find cross-chain arbitrage opportunities.
        
        Compares token prices across:
        - Ethereum, Polygon, Arbitrum, Optimism
        - Base, Avalanche, BNB Chain, Fantom
        
        Returns opportunities where price diff > 0.1%
        """

class ChainId(Enum):
    """Supported blockchain networks."""
    ETHEREUM = 1
    POLYGON = 137
    ARBITRUM = 42161
    OPTIMISM = 10
    BASE = 8453
    AVALANCHE = 43114
    BNB_CHAIN = 56
    FANTOM = 250

class RouteType(Enum):
    """Arbitrage route types."""
    TWO_HOP = 2      # A → B → A
    THREE_HOP = 3    # A → B → C → A (triangular)
    FOUR_HOP = 4     # A → B → C → D → A (rectangular)
```

### Decision Output Format

```python
arbitrage_decision = {
    "engine_type": "arbitrage",
    "direction_prob": 0.55,          # Not primary factor for arb
    "route_id": "uniswap_v3",        # Selected by ArbitrageRLAgent
    "amount": 10000.0,               # Capital to deploy
    "symbol": "BTC",
    "regime_state": RegimeState(...),
    "fib_block": {
        "timing": "EXECUTE",
        "confidence": 0.9,
        "reason": "high_volatility"
    }
}
```

### Arbitrage Route Data Structure

```python
@dataclass
class ArbitrageRoute:
    route_type: RouteType           # TWO_HOP, THREE_HOP, FOUR_HOP
    pairs: List[TradingPair]        # Trading pairs in the route
    path: List[str]                 # Token path ['USDT', 'BTC', 'ETH', 'USDT']
    expected_profit: float          # USD profit
    expected_profit_bps: float      # Profit in basis points
    risk_score: float               # 0-100, lower is better
    execution_time_ms: float        # Estimated execution time
    total_fees: float               # Trading fees in USD
    total_gas: float                # Gas costs in USD
    slippage_estimate: float        # Expected slippage
    min_capital_required: float     # Minimum capital
    max_capital_recommended: float  # Max capital (10% of liquidity)
```

---

## Common Execution Flow

### 1. OmniRuntime.on_tick() - Entry Point

```python
def on_tick(self, price_window, swings, fx_vol, bin_vol, dex_vol, balance, ctx):
    """
    Handle a new price tick and make trading decision.
    
    Flow:
    1. MasterGovernorX100.decide() → Get decision with engine_type
    2. DecisionAuditTrail.log_decision() → Record for audit
    3. RealTimeExecutionHub.execute() → Dispatch to appropriate engine
    4. Return execution result
    """
```

### 2. MasterGovernorX100.decide() - Intelligence Hub

```python
def decide(self, price_window, swings, fx_vol, bin_vol, dex_vol, balance, ctx):
    """
    Make trading decision based on all available intelligence.
    
    Flow:
    1. Sequence Model Predictions:
       - dir_prob = seq_model.predict_direction(price_window)
       - vol_est = seq_model.predict_volatility(price_window)
    
    2. Regime State Construction:
       - trend_strength = |last - first| / (std + ε)
       - mean_reversion_score = 1 - trend_strength
       - state = RegimeState(vol_score, trend_strength, mean_reversion)
    
    3. Engine Selection via RegimeSwitchingRL:
       - High volatility (vol_score > 1.5) → "binary"
       - Strong trend (trend_strength > 0.7) → "spot"
       - Mean reversion (mr_score > 0.7) → "arbitrage"
       - Q-learning bias from historical performance
    
    4. Fibonacci Intelligence:
       - enriched = MasterFibonacciGovernor.evaluate_market()
       - Includes: clusters, wave_state, patterns, volatility_score
    
    5. Engine-Specific Enhancement:
       - Binary: LadderRiskAI stake calculation
       - Spot: SpotTPRotator TP selection
       - Arbitrage: ArbitrageRLAgent route selection
    
    6. Return complete decision envelope
    """
```

### 3. RealTimeExecutionHub.execute() - Dispatch

```python
def execute(self, decision, ctx):
    """
    Execute trade via appropriate executor.
    
    Routing Logic:
    - engine_type == "binary" → BinaryExecutor.execute()
    - engine_type == "spot" → MT5SpotExecutor.execute()
    - engine_type == "arbitrage" → ArbitrageExecutor.execute()
    
    Post-Execution:
    - Update OMS if available
    - Track position and P&L
    """
```

---

## Decision Governor Logic

### RegimeSwitchingRL - Engine Selection

```python
class RegimeSwitchingRL:
    """Q-learning for regime-based engine selection."""
    
    ENGINES = ["binary", "spot", "arbitrage"]
    
    def choose_engine(self, state: RegimeState) -> str:
        """
        Select trading engine based on market regime.
        
        Algorithm:
        1. Discretize state into buckets for Q-table lookup
        2. Apply epsilon-greedy exploration (10% random)
        3. Apply heuristic biases:
           - High volatility → +0.2 to binary Q-value
           - Strong trend → +0.2 to spot Q-value
           - Mean reversion → +0.2 to arbitrage Q-value
        4. Select engine with highest Q-value
        """
    
    def update(self, state, engine, reward, next_state):
        """
        Q-learning update rule.
        
        Q(s,a) ← Q(s,a) + α[R + γ·max(Q(s',a')) - Q(s,a)]
        
        Parameters:
        - α (learning_rate) = 0.1
        - γ (discount) = 0.9
        """
```

### State Discretization

```python
@dataclass
class RegimeState:
    vol_score: float           # Volatility estimate
    trend_strength: float      # 0.0-1.0
    mean_reversion_score: float  # 1.0 - trend_strength
    
    def to_key(self) -> str:
        """Convert to Q-table key with 6 buckets per dimension."""
        vol_bucket = int(self.vol_score * 10) // 2      # 0-5
        trend_bucket = int(self.trend_strength * 10) // 2  # 0-5
        mr_bucket = int(self.mean_reversion_score * 10) // 2  # 0-5
        return f"v{vol_bucket}_t{trend_bucket}_m{mr_bucket}"
```

---

## Safety & Risk Management

### SafetyManager - Pre-Trade Checks

```python
class SafetyManager:
    """Enforce risk limits and cooldown periods."""
    
    def __init__(self,
                 max_daily_loss=100.0,      # Max loss before cooldown
                 max_daily_trades=50,       # Max trades per day
                 max_loss_streak=5,         # Max consecutive losses
                 cooldown_duration=3600):   # 1 hour cooldown
    
    def can_trade(self) -> bool:
        """
        Check if trading is allowed.
        
        Blocks trading if:
        1. In cooldown period
        2. Daily trade limit reached
        3. Daily loss limit exceeded
        4. Loss streak limit reached
        
        Resets counters at midnight.
        """
    
    def register_trade(self, pnl):
        """
        Track trade result and trigger cooldown if needed.
        
        Updates:
        - trades_count += 1
        - daily_pnl += pnl
        - loss_streak (reset on win, increment on loss)
        
        Triggers cooldown if any limit exceeded.
        """
    
    def check_trade_approval(self, asset, size, direction, portfolio_value):
        """
        Detailed trade approval with risk level.
        
        Checks:
        - Not in cooldown
        - Not at daily limits
        - Position size <= 25% of portfolio
        
        Returns:
        - approved: bool
        - reason: str
        - risk_level: 'LOW', 'MEDIUM', 'HIGH', 'BLOCKED'
        """
```

### DeploymentChecklist - Environment Validation

```python
class DeploymentChecklist:
    """Verify deployment readiness before live trading."""
    
    def verify(self) -> Dict:
        """
        Check all critical configuration.
        
        Validates:
        - MT5 credentials configured
        - Binary options API token present
        - DEX RPC and private key set
        - Log directory accessible
        - ONNX model file exists (optional)
        
        Returns aggregate all_passed status.
        """
```

---

## Code Reference Summary

### File Locations

| Component | File Path |
|-----------|-----------|
| **Master Governor** | `omni_trifecta/decision/master_governor.py` |
| **RL Agents** | `omni_trifecta/decision/rl_agents.py` |
| **Executors** | `omni_trifecta/execution/executors.py` |
| **Brokers** | `omni_trifecta/execution/brokers.py` |
| **Arbitrage Calculator** | `omni_trifecta/execution/arbitrage_calculator.py` |
| **Token Equivalence** | `omni_trifecta/execution/token_equivalence.py` |
| **Order Management** | `omni_trifecta/execution/oms.py` |
| **Fibonacci Engines** | `omni_trifecta/fibonacci/engines.py` |
| **Fibonacci Governor** | `omni_trifecta/fibonacci/master_governor.py` |
| **Runtime Orchestration** | `omni_trifecta/runtime/orchestration.py` |
| **Safety Managers** | `omni_trifecta/safety/managers.py` |

### Key Classes Per Engine

| Engine | Decision | Signal | Execution |
|--------|----------|--------|-----------|
| **Binary** | LadderRiskAI | BinaryFibonacciEngine | BinaryExecutor |
| **Spot** | SpotTPRotator | SpotFibonacciEngine | MT5SpotExecutor, ForexExecutor |
| **Arbitrage** | ArbitrageRLAgent | ArbitrageFibonacciTiming | ArbitrageExecutor |

### Enum Reference

| Enum | Location | Values |
|------|----------|--------|
| **RouteType** | arbitrage_calculator.py | TWO_HOP, THREE_HOP, FOUR_HOP |
| **OrderType** | oms.py | MARKET, LIMIT, STOP, STOP_LIMIT |
| **OrderSide** | oms.py | BUY, SELL, LONG, SHORT |
| **OrderStatus** | oms.py | PENDING, OPEN, FILLED, PARTIAL, CANCELLED, REJECTED, EXPIRED |
| **ChainId** | token_equivalence.py | ETHEREUM(1), POLYGON(137), ARBITRUM(42161), etc. |
| **TokenType** | token_equivalence.py | NATIVE, BRIDGED, WRAPPED, LIQUID_STAKING, SYNTHETIC |

---

## Execution Mode Comparison

| Aspect | Binary | Spot | Arbitrage |
|--------|--------|------|-----------|
| **Trade Duration** | 60s-5min | Minutes-Hours | Milliseconds |
| **Outcome** | Binary (Win/Loss) | Gradual P&L | Atomic profit |
| **Position Sizing** | LadderRiskAI | Fixed volume | Kelly Criterion |
| **Signal Source** | Fibonacci zones | Golden ratio | Volatility timing |
| **Risk Management** | Loss streak limits | TP/SL levels | Gas + slippage |
| **Capital Usage** | Full stake at risk | Margin-based | Flashloan leverage |
| **Broker Integration** | PocketOption API | MT5/OANDA/Alpaca | DEX/Web3 |

---

## Quick Start Example

```python
from omni_trifecta.decision.master_governor import MasterGovernorX100
from omni_trifecta.execution.executors import RealTimeExecutionHub, ShadowExecutionHub
from omni_trifecta.safety.managers import SafetyManager

# Initialize components
governor = MasterGovernorX100(base_stake=1.0, max_stake=50.0)
execution_hub = ShadowExecutionHub()  # Or RealTimeExecutionHub for live
safety_manager = SafetyManager(max_daily_loss=100, max_loss_streak=5)

# Prepare data
price_window = [1.0850, 1.0852, 1.0848, ...]  # 256 recent prices
swings = [(0, 1.0800, 'low'), (50, 1.0900, 'high'), ...]
fx_vol = [0.0012, 0.0015, ...]
bin_vol = [0.0010, 0.0012, ...]
dex_vol = [0.0014, 0.0018, ...]
balance = 1000.0

# Check safety
if safety_manager.can_trade():
    # Make decision
    decision = governor.decide(
        price_window=price_window,
        swings=swings,
        fx_vol=fx_vol,
        bin_vol=bin_vol,
        dex_vol=dex_vol,
        balance=balance,
        ctx={"symbol": "EURUSD", "timestamp": datetime.now()}
    )
    
    # Execute trade
    result = execution_hub.execute(decision, ctx={})
    
    # Process result
    print(f"Engine: {decision['engine_type']}")
    print(f"Success: {result['success']}")
    print(f"PnL: ${result['pnl']:.2f}")
    
    # Register with safety manager
    safety_manager.register_trade(result['pnl'])
```

---

**Document Version:** 1.0  
**Covers:** All 3 execution engines with complete logic flow  
**Status:** ✅ Production-Ready Reference
