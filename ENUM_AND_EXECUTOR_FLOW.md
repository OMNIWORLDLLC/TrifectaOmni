# 🔄 Enum and Executor Flow - Complete System Reference

## Overview

This document explicitly clarifies how **enums drive routing** from **Scanner → Decision → Executor** throughout the TrifectaOmni system.

---

## 📊 System Architecture: Enum-Driven Routing

```
┌─────────────────┐
│  SCANNER        │  Detects opportunities
│  (Data Layer)   │  ↓ Creates opportunity dict with 'type' enum
└────────┬────────┘
         │
         │ opportunity = {'type': 'ARBITRAGE', ...}
         ↓
┌─────────────────┐
│  GOVERNOR       │  Evaluates using enum routing
│  (Decision)     │  ↓ Routes based on opportunity['type']
└────────┬────────┘
         │
         │ if type == 'ARBITRAGE': → ArbitrageExecutor
         │ if type == 'FOREX': → ForexExecutor
         │ if type == 'BINARY': → (Direct execution)
         ↓
┌─────────────────┐
│  EXECUTOR       │  Executes trade
│  (Execution)    │  ↓ Uses OrderType/OrderSide enums
└─────────────────┘
```

---

## 🎯 Core Enums in the System

### 1. **Opportunity Type** (String-based, not formal Enum)

**Location:** Scanner opportunity dictionaries

**Purpose:** Routes opportunities to appropriate executors

```python
# Defined in: realtime_multi_asset_demo.py

OPPORTUNITY_TYPES = {
    'ARBITRAGE': ArbitrageExecutor,
    'ARBITRAGE_CROSS_EXCHANGE': ArbitrageExecutor,
    'ARBITRAGE_CROSS_CHAIN': ArbitrageExecutor,
    'ARBITRAGE_TRIANGULAR': ArbitrageExecutor,
    'FOREX': ForexExecutor,
    'BINARY': BinaryExecutor,  # Direct execution
    'BINARY_OPTIONS': BinaryExecutor
}
```

**Usage in Scanner:**
```python
# Arbitrage opportunity
opportunity = {
    'type': 'ARBITRAGE_CROSS_EXCHANGE',  # ← Routing key
    'asset': 'BTC',
    'buy_exchange': 'Binance',
    'sell_exchange': 'Kraken',
    'expected_profit': 125.50
}

# Forex opportunity
opportunity = {
    'type': 'FOREX',  # ← Routing key
    'pair': 'EUR/USD',
    'signal': 'BUY',
    'entry_price': 1.0850
}

# Binary opportunity
opportunity = {
    'type': 'BINARY_OPTIONS',  # ← Routing key
    'pair': 'EUR/USD',
    'direction': 'CALL',
    'expiry': '60s'
}
```

---

### 2. **RouteType Enum** (Arbitrage-specific)

**Location:** `omni_trifecta/execution/arbitrage_calculator.py`

**Purpose:** Classifies multi-hop arbitrage routes

```python
from enum import Enum

class RouteType(Enum):
    """Multi-hop arbitrage route types."""
    TWO_HOP = "2-hop"          # A → B → A
    THREE_HOP = "3-hop"        # A → B → C → A (triangular)
    FOUR_HOP = "4-hop"         # A → B → C → D → A (rectangular)
    CROSS_CHAIN = "cross-chain"  # Same asset, different blockchains
```

**Usage in Arbitrage Calculator:**
```python
from omni_trifecta.execution.arbitrage_calculator import RouteType, ArbitrageRoute

# 2-hop route
route = ArbitrageRoute(
    route_type=RouteType.TWO_HOP,  # ← Enum usage
    path=['Binance', 'BTC/USDT', 'Kraken'],
    expected_profit=125.50
)

# 3-hop triangular route
route = ArbitrageRoute(
    route_type=RouteType.THREE_HOP,  # ← Enum usage
    path=['USDT', 'BTC', 'ETH', 'USDT'],
    expected_profit=45.20
)

# Cross-chain bridge route
route = ArbitrageRoute(
    route_type=RouteType.CROSS_CHAIN,  # ← Enum usage
    path=['Ethereum-USDC', 'Bridge', 'Polygon-USDC'],
    expected_profit=15.00
)
```

**Enum Reference in Executor:**
```python
# ArbitrageExecutor uses RouteType to determine execution strategy
if route.route_type == RouteType.TWO_HOP:
    # Execute cross-exchange arbitrage
    await execute_cross_exchange(route)
elif route.route_type == RouteType.THREE_HOP:
    # Execute triangular arbitrage
    await execute_triangular(route)
elif route.route_type == RouteType.CROSS_CHAIN:
    # Execute cross-chain arbitrage
    await execute_bridge(route)
```

---

### 3. **OrderType Enum** (OMS)

**Location:** `omni_trifecta/execution/oms.py`

**Purpose:** Specifies order execution type

```python
from enum import Enum

class OrderType(Enum):
    """Order type for trade execution."""
    MARKET = "market"          # Immediate execution at current price
    LIMIT = "limit"            # Execute at specific price or better
    STOP = "stop"              # Trigger at stop price
    STOP_LIMIT = "stop_limit"  # Combo: stop + limit
```

**Usage in Order Creation:**
```python
from omni_trifecta.execution.oms import Order, OrderType, OrderSide

# Market order (immediate execution)
order = Order(
    order_id="ORD_001",
    symbol="BTC/USDT",
    side=OrderSide.BUY,
    order_type=OrderType.MARKET,  # ← Enum usage
    quantity=0.5
)

# Limit order (specific price)
order = Order(
    order_id="ORD_002",
    symbol="EUR/USD",
    side=OrderSide.SELL,
    order_type=OrderType.LIMIT,  # ← Enum usage
    quantity=10000.0,
    price=1.0850
)

# Stop-loss order
order = Order(
    order_id="ORD_003",
    symbol="BTC/USDT",
    side=OrderSide.SELL,
    order_type=OrderType.STOP,  # ← Enum usage
    quantity=0.5,
    stop_price=42000.0
)
```

---

### 4. **OrderSide Enum** (OMS)

**Location:** `omni_trifecta/execution/oms.py`

**Purpose:** Specifies trade direction

```python
from enum import Enum

class OrderSide(Enum):
    """Order side for trade direction."""
    BUY = "buy"      # Long position, acquire asset
    SELL = "sell"    # Short position, sell asset
    LONG = "long"    # Alias for BUY
    SHORT = "short"  # Alias for SELL
```

**Usage in Forex Executor:**
```python
from omni_trifecta.execution.oms import OrderSide

# Forex BUY signal
if forex_signal == 'BUY':
    order_side = OrderSide.BUY  # ← Enum usage
elif forex_signal == 'SELL':
    order_side = OrderSide.SELL  # ← Enum usage

# Create order with enum
order = Order(
    symbol="EUR/USD",
    side=order_side,  # ← Enum instance
    order_type=OrderType.MARKET,
    quantity=10000.0
)
```

---

### 5. **OrderStatus Enum** (OMS)

**Location:** `omni_trifecta/execution/oms.py`

**Purpose:** Tracks order lifecycle

```python
from enum import Enum

class OrderStatus(Enum):
    """Order execution status."""
    PENDING = "pending"        # Created, not submitted
    OPEN = "open"             # Submitted to market
    FILLED = "filled"         # Completely executed
    PARTIAL = "partial"       # Partially executed
    CANCELLED = "cancelled"   # User cancelled
    REJECTED = "rejected"     # Broker/exchange rejected
    EXPIRED = "expired"       # Time-limited order expired
```

**Usage in OMS:**
```python
# Order lifecycle
order.status = OrderStatus.PENDING  # Initial state

# Submit to broker
order.status = OrderStatus.OPEN  # Waiting for execution

# Partial fill
if order.filled_quantity < order.quantity:
    order.status = OrderStatus.PARTIAL

# Complete fill
if order.filled_quantity == order.quantity:
    order.status = OrderStatus.FILLED

# Track status transitions
if order.status == OrderStatus.FILLED:
    # Update P&L
    position.realized_pnl += calculate_pnl(order)
```

---

### 6. **ChainId Enum** (Token Equivalence)

**Location:** `omni_trifecta/execution/token_equivalence.py`

**Purpose:** Identifies blockchain networks

```python
from enum import Enum

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
```

**Usage in Cross-Chain Arbitrage:**
```python
from omni_trifecta.execution.token_equivalence import ChainId, TOKEN_REGISTRY

# Get token on specific chain
eth_usdc = TOKEN_REGISTRY.get_token(
    chain_id=ChainId.ETHEREUM.value,  # ← Enum value
    address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
)

polygon_usdc = TOKEN_REGISTRY.get_token(
    chain_id=ChainId.POLYGON.value,  # ← Enum value
    address="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
)

# Detect cross-chain arbitrage
if eth_usdc.base_value_usd != polygon_usdc.base_value_usd:
    opportunity = {
        'type': 'ARBITRAGE_CROSS_CHAIN',
        'source_chain': ChainId.ETHEREUM.name,  # ← Enum name
        'target_chain': ChainId.POLYGON.name,
        'asset': 'USDC'
    }
```

---

### 7. **TokenType Enum** (Token Equivalence)

**Location:** `omni_trifecta/execution/token_equivalence.py`

**Purpose:** Classifies token variants

```python
from enum import Enum

class TokenType(Enum):
    """Token variant classification."""
    NATIVE = "native"                  # Original token on home chain
    BRIDGED = "bridged"                # Bridged from another chain
    WRAPPED = "wrapped"                # Wrapped variant (WETH, WBTC)
    LIQUID_STAKING = "liquid_staking"  # Staked derivative (stETH)
    SYNTHETIC = "synthetic"            # Synthetic asset
```

**Usage in Bridge Arbitrage:**
```python
from omni_trifecta.execution.token_equivalence import TokenType

# Native USDC (Circle-issued)
native_usdc = TokenInfo(
    symbol="USDC",
    token_type=TokenType.NATIVE,  # ← Enum usage
    chain_id=ChainId.ETHEREUM.value
)

# Bridged USDC.e (from bridge)
bridged_usdc = TokenInfo(
    symbol="USDC.e",
    token_type=TokenType.BRIDGED,  # ← Enum usage
    chain_id=ChainId.POLYGON.value
)

# Detect native vs bridged arbitrage
if native_usdc.token_type == TokenType.NATIVE and \
   bridged_usdc.token_type == TokenType.BRIDGED:
    # Check price difference
    if abs(native_price - bridged_price) > bridge_fee:
        opportunity = {
            'type': 'ARBITRAGE_CROSS_CHAIN',
            'variant': 'native_vs_bridged',
            'profit': native_price - bridged_price - bridge_fee
        }
```

---

## 🔄 Complete Flow: Scanner → Executor

### Flow 1: Arbitrage Detection and Execution

```python
# ============================================================================
# STEP 1: Scanner detects arbitrage opportunity
# ============================================================================
# File: realtime_multi_asset_demo.py - scan_arbitrage_opportunities()

opportunity = {
    'type': 'ARBITRAGE_CROSS_EXCHANGE',  # ← Type routing key
    'route_type': '2-HOP',                # ← RouteType reference
    'asset': 'BTC',
    'buy_exchange': 'Binance',
    'sell_exchange': 'Kraken',
    'buy_price': 43010.0,
    'sell_price': 43180.0,
    'expected_profit': 125.50,
    'risk_score': 15.0,
    'recommendation': 'EXECUTE'
}

# ============================================================================
# STEP 2: Governor evaluates opportunity
# ============================================================================
# File: realtime_multi_asset_demo.py - execute_paper_trade_arbitrage()

async def execute_paper_trade_arbitrage(opportunity: Dict[str, Any]):
    # Create order proposal
    order_proposal = {
        'type': 'arbitrage',  # ← Type determines executor
        'route': opportunity['route_type'],  # ← RouteType
        'asset': opportunity['asset'],
        'capital': 10000.0,
        'expected_profit': float(opportunity['expected_profit'])
    }
    
    # RL Agent evaluates
    rl_decision = arbitrage_rl_agent.evaluate_opportunity(order_proposal)
    if rl_decision['action'] == 'skip':
        return None
    
    # Risk Manager approval
    risk_check = risk_manager.check_trade_approval(
        asset=order_proposal['asset'],
        size=order_proposal['capital'],
        direction='long',  # ← Maps to OrderSide.LONG
        current_portfolio_value=oms.get_portfolio_value()
    )
    if not risk_check['approved']:
        return None
    
    # ============================================================================
    # STEP 3: Route to ArbitrageExecutor based on type
    # ============================================================================
    
    # Execute via ArbitrageExecutor
    execution_result = await arbitrage_executor.execute_paper_trade(
        route=opportunity['route_type'],  # ← RouteType determines strategy
        asset=opportunity['asset'],
        capital=order_proposal['capital'],
        expected_profit=order_proposal['expected_profit'],
        buy_exchange=opportunity.get('buy_exchange'),
        sell_exchange=opportunity.get('sell_exchange')
    )
    
    return execution_result
```

### Flow 2: Forex Signal and Execution

```python
# ============================================================================
# STEP 1: Scanner detects forex opportunity
# ============================================================================
# File: realtime_multi_asset_demo.py - scan_forex_opportunities()

opportunity = {
    'type': 'FOREX',  # ← Type routing key
    'pair': 'EUR/USD',
    'signal': 'BUY',  # ← Maps to OrderSide.BUY
    'strength': 85.0,
    'entry_price': 1.0850,
    'take_profit': 1.0900,
    'stop_loss': 1.0825,
    'risk_reward_ratio': 2.0,
    'recommendation': 'EXECUTE'
}

# ============================================================================
# STEP 2: Governor evaluates
# ============================================================================
# File: realtime_multi_asset_demo.py - execute_paper_trade_forex()

async def execute_paper_trade_forex(opportunity: Dict[str, Any]):
    # Create order proposal
    order_proposal = {
        'type': 'forex',  # ← Type determines executor
        'pair': opportunity['pair'],
        'signal': opportunity['signal'],  # ← OrderSide mapping
        'entry_price': float(opportunity['entry_price']),
        'take_profit': float(opportunity['take_profit']),
        'stop_loss': float(opportunity['stop_loss']),
        'size': 10000.0
    }
    
    # AI Predictors analyze
    prediction_features = _prepare_forex_features(opportunity)
    lstm_prediction = lstm_predictor.predict(prediction_features)
    transformer_prediction = transformer_predictor.predict(prediction_features)
    ensemble_confidence = (lstm_prediction + transformer_prediction) / 2
    
    # RL Agent evaluates
    rl_decision = forex_rl_agent.evaluate_opportunity({
        **order_proposal,
        'ai_confidence': ensemble_confidence
    })
    if rl_decision['action'] == 'hold':
        return None
    
    # Risk Manager approval
    risk_check = risk_manager.check_trade_approval(
        asset=order_proposal['pair'],
        size=order_proposal['size'],
        direction='long' if order_proposal['signal'] == 'BUY' else 'short',  # ← OrderSide
        current_portfolio_value=oms.get_portfolio_value()
    )
    if not risk_check['approved']:
        return None
    
    # ============================================================================
    # STEP 3: Route to ForexExecutor based on type
    # ============================================================================
    
    # Execute via ForexExecutor
    execution_result = await forex_executor.execute_paper_trade(
        pair=order_proposal['pair'],
        signal=order_proposal['signal'],  # ← Converted to OrderSide internally
        entry_price=order_proposal['entry_price'],
        take_profit=order_proposal['take_profit'],
        stop_loss=order_proposal['stop_loss'],
        size=order_proposal['size']
    )
    
    return execution_result
```

### Flow 3: Binary Options Execution

```python
# ============================================================================
# STEP 1: Scanner detects binary opportunity
# ============================================================================
# File: realtime_multi_asset_demo.py - scan_binary_opportunities()

opportunity = {
    'type': 'BINARY_OPTIONS',  # ← Type routing key
    'pair': 'EUR/USD',
    'direction': 'CALL',  # ← Binary direction (not OrderSide)
    'expiry': '60s',
    'probability': 75.0,
    'risk_amount': 100.0,
    'potential_profit': 85.0,
    'recommendation': 'EXECUTE'
}

# ============================================================================
# STEP 2: Governor evaluates and executes directly
# ============================================================================
# File: realtime_multi_asset_demo.py - execute_paper_trade_binary()

async def execute_paper_trade_binary(opportunity: Dict[str, Any]):
    # Binary options use direct execution (no OMS orders)
    
    order_proposal = {
        'type': 'binary_options',  # ← Type determines flow
        'pair': opportunity['pair'],
        'direction': opportunity['direction'],  # CALL or PUT (not OrderSide)
        'expiry': opportunity['expiry'],
        'risk_amount': float(opportunity['risk_amount']),
        'potential_profit': float(opportunity['potential_profit']),
        'probability': float(opportunity['probability'])
    }
    
    # Risk Manager approval
    risk_check = risk_manager.check_trade_approval(
        asset=order_proposal['pair'],
        size=order_proposal['risk_amount'],
        direction='long' if order_proposal['direction'] == 'CALL' else 'short',
        current_portfolio_value=oms.get_portfolio_value()
    )
    if not risk_check['approved']:
        return None
    
    # ============================================================================
    # STEP 3: Direct execution (no separate executor class)
    # ============================================================================
    
    # Simulate binary outcome
    win = random.random() < (order_proposal['probability'] / 100)
    
    if win:
        pnl = order_proposal['potential_profit']
    else:
        pnl = -order_proposal['risk_amount']
    
    execution_result = {
        'success': True,
        'execution_id': f"BINARY_{datetime.now().timestamp()}",
        'pnl': pnl,
        'outcome': 'WIN' if win else 'LOSS'
    }
    
    return execution_result
```

---

## 📋 Enum Usage Summary Table

| Enum | Location | Purpose | Used By | Values |
|------|----------|---------|---------|--------|
| **RouteType** | `arbitrage_calculator.py` | Arbitrage route classification | ArbitrageCalculator, ArbitrageExecutor | TWO_HOP, THREE_HOP, FOUR_HOP, CROSS_CHAIN |
| **OrderType** | `oms.py` | Order execution type | OMS, All Executors | MARKET, LIMIT, STOP, STOP_LIMIT |
| **OrderSide** | `oms.py` | Trade direction | OMS, ForexExecutor, ArbitrageExecutor | BUY, SELL, LONG, SHORT |
| **OrderStatus** | `oms.py` | Order lifecycle tracking | OMS | PENDING, OPEN, FILLED, PARTIAL, CANCELLED, REJECTED, EXPIRED |
| **ChainId** | `token_equivalence.py` | Blockchain network ID | Token Registry, Cross-Chain Arbitrage | ETHEREUM(1), POLYGON(137), ARBITRUM(42161), etc. |
| **TokenType** | `token_equivalence.py` | Token variant classification | Token Registry, Bridge Arbitrage | NATIVE, BRIDGED, WRAPPED, LIQUID_STAKING, SYNTHETIC |

---

## 🎯 Key Routing Logic

### Type-Based Routing (Scanner → Executor)

```python
# In broadcast_opportunities() function:

if arbitrage_opps:
    best_arb = max(arbitrage_opps, key=lambda x: ...)
    if best_arb.get('recommendation') == '✅ EXECUTE NOW':
        # TYPE = 'ARBITRAGE*' → ArbitrageExecutor
        await scanner.execute_paper_trade_arbitrage(best_arb)

if forex_opps:
    best_forex = max(forex_opps, key=lambda x: ...)
    if best_forex.get('recommendation') == '✅ STRONG SIGNAL':
        # TYPE = 'FOREX' → ForexExecutor
        await scanner.execute_paper_trade_forex(best_forex)

if binary_opps:
    best_binary = max(binary_opps, key=lambda x: ...)
    if best_binary.get('recommendation') == '✅ HIGH PROBABILITY':
        # TYPE = 'BINARY*' → Direct execution
        await scanner.execute_paper_trade_binary(best_binary)
```

### RouteType-Based Strategy Selection

```python
# In ArbitrageExecutor:

if route == '2-HOP':
    # Cross-exchange arbitrage
    # Buy on Exchange A, sell on Exchange B
    strategy = execute_cross_exchange_arbitrage
elif route == '3-HOP':
    # Triangular arbitrage
    # A → B → C → A
    strategy = execute_triangular_arbitrage
elif route == 'CROSS-CHAIN' or route == 'BRIDGE':
    # Cross-chain bridge arbitrage
    # Ethereum-USDC → Polygon-USDC
    strategy = execute_bridge_arbitrage
```

### OrderSide Mapping

```python
# Signal to OrderSide conversion:

if signal == 'BUY':
    order_side = OrderSide.BUY
elif signal == 'SELL':
    order_side = OrderSide.SELL

# Binary direction mapping:
if direction == 'CALL':
    # Equivalent to OrderSide.LONG
    equivalent_side = 'long'
elif direction == 'PUT':
    # Equivalent to OrderSide.SHORT
    equivalent_side = 'short'
```

---

## ✅ Verification Checklist

**Enum Definitions:**
- ✅ `RouteType` - Defined in `arbitrage_calculator.py`
- ✅ `OrderType` - Defined in `oms.py`
- ✅ `OrderSide` - Defined in `oms.py`
- ✅ `OrderStatus` - Defined in `oms.py`
- ✅ `ChainId` - Defined in `token_equivalence.py`
- ✅ `TokenType` - Defined in `token_equivalence.py`

**Enum Usage:**
- ✅ Scanner creates opportunity dicts with 'type' string
- ✅ Governor routes based on opportunity['type']
- ✅ Executors use RouteType for strategy selection
- ✅ OMS uses OrderType, OrderSide, OrderStatus
- ✅ Token Registry uses ChainId and TokenType

**Flow Verification:**
- ✅ Scanner → opportunity['type'] → Governor → Executor
- ✅ RouteType → execution strategy selection
- ✅ OrderSide → trade direction
- ✅ OrderStatus → lifecycle tracking
- ✅ ChainId → blockchain routing
- ✅ TokenType → variant arbitrage detection

---

**Status:** 🟢 Enum system fully documented and verified

**Last Updated:** November 24, 2025
