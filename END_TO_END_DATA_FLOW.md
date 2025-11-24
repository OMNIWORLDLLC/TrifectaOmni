# 🔄 TrifectaOmni - Complete End-to-End Data Flow

## System Architecture: From Data Intake to Trade Execution

```
┌───────────────────────────────────────────────────────────────────────────┐
│                         LAYER 1: DATA INTAKE                              │
│                   (Real-time market data from APIs)                       │
└───────────────────────────────────────────────────────────────────────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     │               │               │
                     ▼               ▼               ▼
        ┌─────────────────┐ ┌─────────────┐ ┌──────────────────┐
        │  MT5 Forex API  │ │  CCXT Crypto│ │ Pocket Options   │
        │  (MetaTrader 5) │ │  + DEX RPC  │ │  Binary Signals  │
        │                 │ │             │ │                  │
        │  • 7 G7 pairs   │ │ • 7 pairs   │ │  • 60s signals   │
        │  • <100ms tick  │ │ • 4 exchanges│ │  • Probability   │
        │  • Bid/Ask      │ │ • Cross-ex   │ │  • CALL/PUT      │
        └────────┬────────┘ └──────┬──────┘ └────────┬─────────┘
                 │                 │                  │
                 └─────────────────┼──────────────────┘
                                   │
                                   ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                   LAYER 2: DATA PROVIDER LAYER                            │
│              (ProductionDataProvider - API Orchestration)                 │
└───────────────────────────────────────────────────────────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌─────────────────┐    ┌────────────────────┐    ┌──────────────────┐
│get_forex_price  │    │get_crypto_price    │    │get_binary_signals│
│_mt5()           │    │_ccxt()             │    │_pocket()         │
│                 │    │                    │    │                  │
│Returns:         │    │Returns:            │    │Returns:          │
│ {               │    │ {                  │    │ [{               │
│  'bid': 1.0843, │    │  'bid': 43010.0,   │    │  'pair': 'EUR/..│
│  'ask': 1.0845, │    │  'ask': 43020.0,   │    │  'direction': ..│
│  'last': 1.0844,│    │  'last': 43015.0,  │    │  'probability':.│
│  'spread': 0.0002│    │  'volume': 1250.3  │    │  'expiry': '60s'│
│  'timestamp': ..│    │  'timestamp': ..   │    │ }]               │
│ }               │    │ }                  │    │                  │
└────────┬────────┘    └──────────┬─────────┘    └────────┬─────────┘
         │                        │                       │
         └────────────────────────┼───────────────────────┘
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                   LAYER 3: SCANNER LAYER                                  │
│          (RealTimeProductionScanner - Opportunity Detection)              │
└───────────────────────────────────────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌───────────────────┐  ┌───────────────────┐  ┌─────────────────────┐
│scan_arbitrage     │  │scan_forex         │  │scan_binary          │
│_opportunities()   │  │_opportunities()   │  │_opportunities()     │
│                   │  │                   │  │                     │
│For each crypto:   │  │For each forex:    │  │For each signal:     │
│1. Fetch prices    │  │1. Fetch MT5 tick  │  │1. Get Pocket signal │
│   from 4 exchanges│  │2. Get 100 bars    │  │2. Calculate prob    │
│2. Calculate spread│  │   (M15 timeframe) │  │3. Assess risk/reward│
│3. Check > 0.25%   │  │3. Calculate RSI   │  │4. Check >= 65% prob │
│4. Estimate fees   │  │4. Calculate SMA   │  │5. Create opportunity│
│5. Calculate PnL   │  │   (20 & 50)       │  │                     │
│6. Create opp      │  │5. Calculate ATR   │  │                     │
│                   │  │6. Generate signal │  │                     │
│                   │  │   (BUY if RSI<30) │  │                     │
│                   │  │7. Calculate TP/SL │  │                     │
│                   │  │8. Create opp      │  │                     │
└────────┬──────────┘  └─────────┬─────────┘  └──────────┬──────────┘
         │                       │                       │
         │ opportunity = {       │ opportunity = {       │ opportunity = {
         │  'type': 'ARBITRAGE', │  'type': 'FOREX',     │  'type': 'BINARY',
         │  'route_type': '2HOP',│  'pair': 'EUR/USD',   │  'pair': 'EUR/USD',
         │  'asset': 'BTC',      │  'signal': 'BUY',     │  'direction': 'CALL',
         │  'buy_exchange': ..   │  'strength': 85.0,    │  'probability': 75.0,
         │  'sell_exchange': ..  │  'entry': 1.0850,     │  'risk_amount': 100,
         │  'expected_profit':.. │  'take_profit': 1.09, │  'potential_profit':85,
         │  'risk_score': 15.0,  │  'stop_loss': 1.0825, │  'expiry': '60s',
         │  'recommendation': .. │  'risk_reward': 2.0,  │  'recommendation': ..
         │ }                     │  'recommendation': .. │ }
         │                       │ }                     │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                   LAYER 4: OPPORTUNITY STORAGE                            │
│                  (In-memory lists sorted by profit)                       │
└───────────────────────────────────────────────────────────────────────────┘
                                 │
         scanner.arbitrage_opportunities = [opp1, opp2, ...] (top 10)
         scanner.forex_opportunities = [opp1, opp2, ...] (top 10)
         scanner.binary_opportunities = [opp1, opp2, ...] (top 10)
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                   LAYER 5: BROADCAST LAYER                                │
│              (WebSocket streaming to dashboard clients)                   │
└───────────────────────────────────────────────────────────────────────────┘
                                 │
                Every 10 seconds, broadcast to all WS clients:
                {
                  'arbitrage': [...opportunities...],
                  'forex': [...opportunities...],
                  'binary': [...opportunities...],
                  'stats': {scanner stats},
                  'timestamp': '...'
                }
                                 │
                                 ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                   LAYER 6: DECISION LAYER                                 │
│          (Master Governor + RL Agents + Risk Manager + AI)                │
└───────────────────────────────────────────────────────────────────────────┘
                                 │
        When user clicks "EXECUTE" on dashboard (or auto-execute enabled):
                                 │
                 ┌───────────────┼───────────────┐
                 │               │               │
                 ▼               ▼               ▼
    ┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
    │ ARBITRAGE PATH   │ │  FOREX PATH  │ │   BINARY PATH    │
    └──────────────────┘ └──────────────┘ └──────────────────┘

═══════════════════════════════════════════════════════════════════════════
                         ARBITRAGE EXECUTION PATH
═══════════════════════════════════════════════════════════════════════════

Input: opportunity = {
  'type': 'ARBITRAGE_CROSS_EXCHANGE',
  'route_type': '2-HOP',
  'asset': 'BTC',
  'buy_exchange': 'Binance',
  'sell_exchange': 'Kraken',
  'expected_profit': 125.50,
  'capital': 10000.0
}

Step 1: SCANNER.execute_paper_trade_arbitrage(opportunity)
        └─> Creates order_proposal:
            {
              'type': 'arbitrage',
              'route': '2-HOP',
              'asset': 'BTC',
              'capital': 10000.0,
              'expected_profit': 125.50
            }

Step 2: RL AGENT EVALUATION
        └─> arb_rl_agent.evaluate_opportunity(order_proposal)
            • Checks historical performance for similar routes
            • Assesses market conditions
            • Returns: {'action': 'execute' | 'skip', 'confidence': 0.85}
            
        IF action == 'skip':
            └─> Return None (abort execution)

Step 3: RISK MANAGER APPROVAL
        └─> risk_manager.check_trade_approval(
              asset='BTC',
              size=10000.0,
              direction='long',
              current_portfolio_value=oms.get_portfolio_value()
            )
            
            Checks:
            • Position size < max_position_size (20% of portfolio)
            • Daily loss < max_daily_loss ($5000)
            • No active cooldown period
            • Loss streak < max_loss_streak (5)
            
            Returns: {'approved': True/False, 'reason': '...'}
            
        IF NOT approved:
            └─> Return None (abort execution)

Step 4: ARBITRAGE EXECUTOR
        └─> arbitrage_executor.execute_paper_trade(
              route='2-HOP',
              asset='BTC',
              capital=10000.0,
              expected_profit=125.50,
              buy_exchange='Binance',
              sell_exchange='Kraken'
            )
            
            Paper Mode Simulation:
            • Simulates buy on Binance at ask price
            • Simulates sell on Kraken at bid price
            • Applies random variance (85-100% of expected profit)
            • Calculates fees and slippage
            
            Returns:
            {
              'success': True,
              'execution_id': 'ARB_12345',
              'route': '2-HOP',
              'asset': 'BTC',
              'capital': 10000.0,
              'pnl': 106.25,  # Actual profit after fees
              'buy_exchange': 'Binance',
              'sell_exchange': 'Kraken',
              'mode': 'paper'
            }

Step 5: OMS UPDATE
        └─> oms.update_capital(pnl=106.25)
            • Updates portfolio value
            • Records trade in history
            • Updates paper trading stats

Step 6: STATISTICS UPDATE
        └─> scanner.paper_trades['arbitrage']:
            {
              'count': += 1,
              'pnl': += 106.25,
              'wins': += 1 if pnl > 0 else 0
            }

Step 7: RL AGENT LEARNING
        └─> arb_rl_agent.update(
              state=market_state,
              action='execute',
              reward=106.25,
              next_state=new_market_state
            )
            • Updates Q-table based on outcome
            • Improves future decision making

═══════════════════════════════════════════════════════════════════════════
                            FOREX EXECUTION PATH
═══════════════════════════════════════════════════════════════════════════

Input: opportunity = {
  'type': 'FOREX',
  'pair': 'EUR/USD',
  'signal': 'BUY',
  'strength': 85.0,
  'entry': 1.0850,
  'take_profit': 1.0900,
  'stop_loss': 1.0825,
  'risk_reward': 2.0
}

Step 1: SCANNER.execute_paper_trade_forex(opportunity)
        └─> Creates order_proposal:
            {
              'type': 'forex',
              'pair': 'EUR/USD',
              'signal': 'BUY',
              'entry_price': 1.0850,
              'take_profit': 1.0900,
              'stop_loss': 1.0825,
              'size': 10000.0  # Standard lot
            }

Step 2: AI PREDICTOR ENSEMBLE
        └─> Prepare features from MT5 historical data:
            • Last 50 close prices
            • RSI, SMA, ATR values
            • Volume data
            
        └─> lstm_predictor.predict(features)
            • Returns: direction_prob = 0.72
            
        └─> transformer_predictor.predict(features)
            • Returns: direction_prob = 0.68
            
        └─> ensemble_confidence = (0.72 + 0.68) / 2 = 0.70

Step 3: RL AGENT EVALUATION
        └─> forex_rl_agent.evaluate_opportunity({
              ...order_proposal,
              'ai_confidence': 0.70
            })
            
            • Considers AI confidence
            • Checks signal strength (85.0)
            • Assesses risk/reward ratio (2.0)
            • Returns: {'action': 'execute', 'confidence': 0.80}
            
        IF action == 'hold':
            └─> Return None (abort execution)

Step 4: RISK MANAGER APPROVAL
        └─> risk_manager.check_trade_approval(
              asset='EUR/USD',
              size=10000.0,
              direction='long',  # BUY signal
              current_portfolio_value=oms.get_portfolio_value()
            )
            
        IF NOT approved:
            └─> Return None (abort execution)

Step 5: FOREX EXECUTOR
        └─> forex_executor.execute_paper_trade(
              pair='EUR/USD',
              signal='BUY',
              entry_price=1.0850,
              take_profit=1.0900,
              stop_loss=1.0825,
              size=10000.0
            )
            
            Paper Mode Simulation:
            • Calculates risk = |entry - stop_loss| = 0.0025
            • Calculates reward = |take_profit - entry| = 0.0050
            • Simulates outcome: 60% win probability
            • If WIN: pnl = size * (reward / entry) = 10000 * (0.005/1.085) = $46.08
            • If LOSS: pnl = -size * (risk / entry) = -10000 * (0.0025/1.085) = -$23.04
            
            Returns:
            {
              'success': True,
              'execution_id': 'FX_54321',
              'pair': 'EUR/USD',
              'signal': 'BUY',
              'entry': 1.0850,
              'size': 10000.0,
              'pnl': 46.08,  # Assuming win
              'outcome': 'WIN',
              'mode': 'paper'
            }

Step 6: OMS ORDER TRACKING
        └─> Creates Order object:
            Order(
              order_id='FX_54321',
              symbol='EUR/USD',
              side=OrderSide.BUY,  # Mapped from 'BUY' signal
              order_type=OrderType.MARKET,
              quantity=10000.0,
              price=1.0850,
              status=OrderStatus.FILLED,  # Paper mode: instant fill
              take_profit=1.0900,
              stop_loss=1.0825
            )
            
        └─> oms.submit_order(order)
            • Tracks order in OMS
            • Updates positions
            • Calculates P&L

Step 7: STATISTICS UPDATE
        └─> scanner.paper_trades['forex']:
            {
              'count': += 1,
              'pnl': += 46.08,
              'wins': += 1
            }

Step 8: RL AGENT LEARNING
        └─> forex_rl_agent.update(
              state=market_state,
              action='execute',
              reward=46.08
            )

═══════════════════════════════════════════════════════════════════════════
                           BINARY OPTIONS PATH
═══════════════════════════════════════════════════════════════════════════

Input: opportunity = {
  'type': 'BINARY_OPTIONS',
  'pair': 'EUR/USD',
  'direction': 'CALL',
  'probability': 75.0,
  'risk_amount': 100.0,
  'potential_profit': 85.0,
  'expiry': '60s'
}

Step 1: SCANNER.execute_paper_trade_binary(opportunity)
        └─> Creates order_proposal:
            {
              'type': 'binary_options',
              'pair': 'EUR/USD',
              'direction': 'CALL',
              'expiry': '60s',
              'risk_amount': 100.0,
              'potential_profit': 85.0,
              'probability': 75.0
            }

Step 2: RISK MANAGER APPROVAL
        └─> risk_manager.check_trade_approval(
              asset='EUR/USD',
              size=100.0,  # Risk amount
              direction='long' if CALL else 'short',
              current_portfolio_value=oms.get_portfolio_value()
            )
            
        IF NOT approved:
            └─> Return None (abort execution)

Step 3: DIRECT EXECUTION (No separate BinaryExecutor in this flow)
        └─> Simulate binary outcome:
            • win_probability = opportunity['probability'] / 100 = 0.75
            • random_roll = random.random()
            • win = (random_roll < win_probability)
            
            If WIN:
              └─> pnl = +potential_profit = +85.0
            If LOSS:
              └─> pnl = -risk_amount = -100.0
            
            Returns:
            {
              'success': True,
              'execution_id': f"BINARY_{timestamp}",
              'pair': 'EUR/USD',
              'direction': 'CALL',
              'risk_amount': 100.0,
              'pnl': 85.0 or -100.0,
              'outcome': 'WIN' or 'LOSS',
              'mode': 'paper'
            }

Step 4: OMS UPDATE
        └─> oms.update_capital(pnl)
            • Immediate P&L (binary options settle instantly)
            • No order tracking needed (instant expiry)

Step 5: STATISTICS UPDATE
        └─> scanner.paper_trades['binary']:
            {
              'count': += 1,
              'pnl': += 85.0 (or -100.0),
              'wins': += 1 if win else 0
            }

═══════════════════════════════════════════════════════════════════════════
                      LAYER 7: RESULT AGGREGATION
═══════════════════════════════════════════════════════════════════════════

After each execution:

1. Trade History Update:
   scanner.trade_history.append({
     'timestamp': datetime.now(),
     'type': 'arbitrage' | 'forex' | 'binary',
     'opportunity': {...},
     'execution_result': {...},
     'pnl': float,
     'success': bool
   })

2. Portfolio Update:
   oms.capital = initial_capital + sum(all_pnls)
   oms.positions = [active positions]
   oms.orders = [order history]

3. Performance Metrics:
   • Total trades: sum of all trade counts
   • Total P&L: sum of all pnls
   • Win rate: wins / total_trades
   • Sharpe ratio: risk-adjusted returns
   • Max drawdown: largest peak-to-trough decline

4. Dashboard Update:
   • Broadcast updated stats via WebSocket
   • Show latest trade in real-time
   • Update portfolio value chart
   • Display win/loss indicators

═══════════════════════════════════════════════════════════════════════════
                      DATA STRUCTURES AT EACH LAYER
═══════════════════════════════════════════════════════════════════════════

LAYER 1 (Raw API Data):
  MT5: Tick object (bid, ask, time, volume)
  CCXT: Ticker dict (bid, ask, last, volume, timestamp)
  Pocket: Signal list (pair, direction, probability, expiry)

LAYER 2 (Normalized Price Data):
  {
    'bid': float,
    'ask': float,
    'last': float,
    'spread': float,
    'volume': float,
    'timestamp': int
  }

LAYER 3 (Opportunity Object):
  {
    'type': 'ARBITRAGE' | 'FOREX' | 'BINARY_OPTIONS',
    'asset' | 'pair': str,
    'signal' | 'direction': str,
    'expected_profit' | 'strength' | 'probability': float,
    'recommendation': 'EXECUTE' | 'CONSIDER' | 'SKIP',
    'risk_score' | 'risk_reward': float,
    ...engine-specific fields...
    'timestamp': str
  }

LAYER 4 (Stored Opportunities):
  scanner.arbitrage_opportunities: List[Dict] (sorted by expected_profit)
  scanner.forex_opportunities: List[Dict] (sorted by strength)
  scanner.binary_opportunities: List[Dict] (sorted by probability)

LAYER 5 (WebSocket Broadcast):
  {
    'arbitrage': List[Dict],
    'forex': List[Dict],
    'binary': List[Dict],
    'stats': {
      'arbitrage_count': int,
      'forex_count': int,
      'binary_count': int,
      'total_scans': int,
      'uptime_seconds': int,
      'portfolio_value': float,
      'paper_trades': {...}
    },
    'timestamp': str
  }

LAYER 6 (Decision Objects):
  Order Proposal:
    {
      'type': str,
      'asset' | 'pair': str,
      'signal' | 'direction': str,
      'size' | 'capital': float,
      ...
    }
  
  RL Agent Decision:
    {
      'action': 'execute' | 'skip' | 'hold',
      'confidence': float
    }
  
  Risk Check:
    {
      'approved': bool,
      'reason': str
    }

LAYER 7 (Execution Result):
  {
    'success': bool,
    'execution_id': str,
    'type': str,
    'pnl': float,
    'mode': 'paper' | 'live',
    ...engine-specific fields...
  }

═══════════════════════════════════════════════════════════════════════════
                      ENUM ROUTING THROUGHOUT SYSTEM
═══════════════════════════════════════════════════════════════════════════

Opportunity Type (String-based) → Executor Routing:
  'ARBITRAGE*' → ArbitrageExecutor
  'FOREX' → ForexExecutor
  'BINARY*' → Direct execution (or BinaryExecutor)

RouteType Enum → Arbitrage Strategy:
  RouteType.TWO_HOP → Cross-exchange arbitrage
  RouteType.THREE_HOP → Triangular arbitrage
  RouteType.CROSS_CHAIN → Bridge/DEX arbitrage

OrderSide Enum → Trade Direction:
  'BUY' signal → OrderSide.BUY
  'SELL' signal → OrderSide.SELL
  'CALL' binary → equivalent to 'long'
  'PUT' binary → equivalent to 'short'

OrderType Enum → Execution Type:
  Default: OrderType.MARKET (immediate execution)
  TP/SL orders: OrderType.LIMIT

OrderStatus Enum → Order Lifecycle:
  OrderStatus.PENDING → Order created
  OrderStatus.OPEN → Order submitted
  OrderStatus.FILLED → Order executed
  OrderStatus.CANCELLED → Order cancelled
  OrderStatus.REJECTED → Order rejected

ChainId Enum → Cross-chain Routing:
  ChainId.ETHEREUM → Ethereum mainnet
  ChainId.POLYGON → Polygon network
  ChainId.ARBITRUM → Arbitrum L2

TokenType Enum → Token Classification:
  TokenType.NATIVE → Original token
  TokenType.BRIDGED → Bridged token
  TokenType.WRAPPED → Wrapped token

═══════════════════════════════════════════════════════════════════════════
                      TIMING & PERFORMANCE METRICS
═══════════════════════════════════════════════════════════════════════════

PRODUCTION MODE LATENCIES:

Data Intake (Layer 1):
  • MT5 tick data: <100ms
  • CCXT exchange data: 200-500ms per exchange
  • DEX RPC call: 100-300ms
  • Pocket API: 500-1000ms

Scanner Processing (Layer 3):
  • Arbitrage scan (7 pairs × 4 exchanges): ~3-5 seconds
  • Forex scan (7 pairs + TA): ~2-3 seconds
  • Binary scan: ~1 second
  • Total scan cycle: ~5-8 seconds

Decision Layer (Layer 6):
  • RL Agent evaluation: <10ms
  • Risk Manager check: <5ms
  • AI Predictor (LSTM+Transformer): 50-100ms
  • Total decision time: ~100-150ms

Execution Layer:
  • Paper trade simulation: <10ms
  • OMS update: <5ms
  • Statistics update: <5ms
  • Total execution time: ~20ms

End-to-End Latency:
  • From opportunity detection to execution: ~5-8 seconds (dominated by scanning)
  • From decision trigger to execution complete: ~150ms

WebSocket Broadcast:
  • Every 10 seconds
  • Payload size: ~50-100KB JSON
  • Client update latency: <50ms

═══════════════════════════════════════════════════════════════════════════
                      CONCURRENCY & ASYNC FLOWS
═══════════════════════════════════════════════════════════════════════════

Parallel Scanning:
  asyncio.gather(
    scan_arbitrage_opportunities(),  # Independent
    scan_forex_opportunities(),       # Independent
    scan_binary_opportunities()       # Independent
  )
  → All three scans run concurrently
  → Results populate separate opportunity lists

Periodic Tasks (Background):
  1. periodic_scanning() 
     └─> Runs every min(30s, 5s, 10s) = 5 seconds
     └─> Calls scan_all_assets() → asyncio.gather()
  
  2. broadcast_opportunities()
     └─> Runs every 10 seconds
     └─> Sends JSON to all WebSocket clients
     └─> Non-blocking (fire-and-forget)

Sequential Execution Flow:
  execute_paper_trade_arbitrage() is ASYNC but runs sequentially:
    1. Create order proposal
    2. await RL agent evaluation
    3. Check risk manager (sync)
    4. await executor.execute_paper_trade()
    5. Update OMS (sync)
    6. Update stats (sync)
  
  Cannot parallelize because each step depends on previous step's result

═══════════════════════════════════════════════════════════════════════════
                      ERROR HANDLING & RESILIENCE
═══════════════════════════════════════════════════════════════════════════

API Connection Failures:
  • MT5 not available → Skip forex scanning, log warning
  • CCXT import error → Skip crypto scanning
  • DEX RPC timeout → Skip on-chain arbitrage
  • Pocket API error → Skip binary scanning
  
  System continues with available data sources

Execution Failures:
  • RL Agent returns 'skip' → Abort gracefully, no trade
  • Risk Manager rejects → Abort gracefully, log reason
  • Executor returns success=False → Log error, no P&L update
  • Paper trade always succeeds (simulation)

Safety Mechanisms:
  • Max daily loss limit: Trading stops if breached
  • Max daily trades: Cooldown after limit
  • Loss streak detection: Cooldown after 5 consecutive losses
  • Position size limits: No single trade > 20% of portfolio

Cooldown Period:
  • Duration: 3600 seconds (1 hour)
  • Triggered by: Daily loss, trade limit, loss streak
  • Effect: can_trade() returns False
  • Resume: Automatic after cooldown expires

═══════════════════════════════════════════════════════════════════════════
                      SUMMARY: COMPLETE DATA JOURNEY
═══════════════════════════════════════════════════════════════════════════

1. RAW DATA (Layer 1)
   └─> MT5/CCXT/Pocket APIs fetch real-time prices
   
2. NORMALIZED DATA (Layer 2)
   └─> ProductionDataProvider formats to standard structure
   
3. OPPORTUNITY DETECTION (Layer 3)
   └─> Scanner calculates spreads, signals, probabilities
   └─> Creates opportunity objects with recommendations
   
4. STORAGE & SORTING (Layer 4)
   └─> Top 10 opportunities per engine type
   └─> Sorted by profit/strength/probability
   
5. BROADCAST (Layer 5)
   └─> WebSocket streams to dashboard every 10s
   └─> Users see live opportunities
   
6. DECISION (Layer 6)
   └─> User clicks "Execute" OR auto-execute enabled
   └─> RL Agent evaluates → Risk Manager approves
   └─> AI Predictors provide confidence
   
7. EXECUTION (Layer 6 continued)
   └─> Route to appropriate executor based on type
   └─> Executor simulates (paper) or places real order (live)
   └─> Returns execution result with P&L
   
8. POST-EXECUTION (Layer 7)
   └─> OMS updates portfolio
   └─> Statistics updated
   └─> RL Agents learn from outcome
   └─> Dashboard shows results

LOOP CONTINUES:
  └─> Scanner fetches new data
  └─> New opportunities detected
  └─> Broadcast to clients
  └─> Await next execution
  └─> Repeat ∞

═══════════════════════════════════════════════════════════════════════════

**Status:** ✅ Complete end-to-end data flow mapped
**Mode:** Paper trading (simulation) by default
**Live Trading:** Requires broker API configuration + live execution methods
**Last Updated:** November 24, 2025
