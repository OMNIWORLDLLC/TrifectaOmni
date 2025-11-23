# Production Deployment Guide

## System Overview

The Omni-Trifecta Quant Engine is a production-ready, multi-asset trading system supporting:

- **Forex Trading** (Oanda, Forex.com, MT5)
- **Cryptocurrency** (100+ exchanges via CCXT, Binance, Coinbase)
- **Stocks** (Alpaca, Interactive Brokers via CCXT)
- **Binary Options** (Pocket Option, IQ Option)
- **DEX/Arbitrage** (Uniswap, PancakeSwap, Flashloans)

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Run Shadow Mode Test

```bash
python examples/shadow_mode_example.py
```

### 4. Run Advanced Integration

```bash
python examples/advanced_integration_example.py
```

## Production Deployment

### Architecture Components

1. **Data Layer** - Real-time price feeds from multiple sources
2. **Intelligence Layer** - Technical analysis, ML models, pattern recognition
3. **Decision Layer** - Regime switching, Fibonacci analysis, RL optimization
4. **Execution Layer** - Order management, broker integrations
5. **Risk Layer** - Position sizing, portfolio management, safety limits
6. **Learning Layer** - Performance tracking, RL training, model updates

### Component Initialization

```python
from omni_trifecta.core.config import OmniConfig
from omni_trifecta.core.configurations import get_config, merge_configs
from omni_trifecta.data.price_feeds import create_price_feed
from omni_trifecta.execution.brokers import create_broker_bridge
from omni_trifecta.decision.master_governor import MasterGovernorX100
from omni_trifecta.execution.executors import RealTimeExecutionHub
from omni_trifecta.execution.oms import OrderManagementSystem
from omni_trifecta.safety.advanced_risk import DynamicPositionSizer, RiskParameters
from omni_trifecta.safety.managers import SafetyManager

# Load configuration
config = OmniConfig()
trading_config = get_config('balanced')

# Initialize components
governor = MasterGovernorX100(base_stake=100.0, max_stake=1000.0)
oms = OrderManagementSystem()
position_sizer = DynamicPositionSizer(RiskParameters())
safety_manager = SafetyManager(
    max_daily_loss=500.0,
    max_daily_trades=50,
    max_loss_streak=5
)

# Setup data feed
price_feed = create_price_feed(
    source='binance',
    symbol='BTC/USDT',
    config={}
)

# Setup broker
broker = create_broker_bridge(
    broker_type='ccxt',
    config={
        'exchange_id': 'binance',
        'api_key': 'YOUR_KEY',
        'api_secret': 'YOUR_SECRET',
        'testnet': True
    }
)
```

### Forex Trading Setup (Oanda)

```python
# Configure Oanda broker
broker = create_broker_bridge(
    broker_type='oanda',
    config={
        'api_key': 'YOUR_OANDA_API_KEY',
        'account_id': 'YOUR_ACCOUNT_ID',
        'practice': True  # Use practice account
    }
)

# Configure price feed
price_feed = create_price_feed(
    source='oanda',
    symbol='EUR_USD',
    config={
        'api_key': 'YOUR_OANDA_API_KEY',
        'account_id': 'YOUR_ACCOUNT_ID',
        'practice': True
    }
)
```

### Cryptocurrency Trading Setup (Binance)

```python
# Configure Binance via CCXT
broker = create_broker_bridge(
    broker_type='ccxt',
    config={
        'exchange_id': 'binance',
        'api_key': 'YOUR_BINANCE_API_KEY',
        'api_secret': 'YOUR_BINANCE_SECRET',
        'testnet': True  # Use testnet first
    }
)

# Configure price feed
price_feed = create_price_feed(
    source='ccxt',
    symbol='BTC/USDT',
    config={
        'exchange_id': 'binance',
        'poll_interval': 1.0
    }
)
```

### Stock Trading Setup (Alpaca)

```python
# Configure Alpaca broker
broker = create_broker_bridge(
    broker_type='alpaca',
    config={
        'api_key': 'YOUR_ALPACA_API_KEY',
        'api_secret': 'YOUR_ALPACA_SECRET',
        'paper': True  # Use paper trading
    }
)

# Configure price feed
price_feed = create_price_feed(
    source='alpaca',
    symbol='AAPL',
    config={
        'api_key': 'YOUR_ALPACA_API_KEY',
        'api_secret': 'YOUR_ALPACA_SECRET',
        'feed_type': 'iex'
    }
)
```

## Risk Management

### Position Sizing

The system uses multiple methods:

1. **Fixed Fractional** - Risk fixed % of capital per trade
2. **Kelly Criterion** - Optimal f based on win rate and R:R
3. **Volatility-Adjusted** - Scale positions by ATR/volatility
4. **Portfolio Heat** - Limit total portfolio risk exposure

```python
from omni_trifecta.safety.advanced_risk import (
    DynamicPositionSizer,
    RiskParameters,
    PortfolioHeatMap
)

risk_params = RiskParameters(
    max_position_size=0.2,        # Max 20% per position
    max_portfolio_risk=0.05,      # Max 5% total risk
    max_position_risk=0.02,       # Max 2% risk per trade
    max_correlation_exposure=0.5, # Max 50% correlated positions
    max_leverage=2.0              # Max 2x leverage
)

position_sizer = DynamicPositionSizer(risk_params)
heat_map = PortfolioHeatMap(max_heat=0.1)

# Calculate position size
size = position_sizer.calculate_position_size(
    symbol='BTC/USDT',
    account_balance=10000.0,
    current_price=45000.0,
    volatility=500.0,  # ATR or volatility measure
    confidence=0.7,    # Signal confidence
    current_positions={'ETH/USDT': 0.5}
)
```

### Safety Limits

```python
from omni_trifecta.safety.managers import SafetyManager

safety = SafetyManager(
    max_daily_loss=500.0,      # Max $500 loss per day
    max_daily_trades=50,       # Max 50 trades per day
    max_loss_streak=5          # Stop after 5 consecutive losses
)

# Check before trading
if safety.can_trade():
    # Execute trade
    result = execute_trade()
    safety.register_trade(result['pnl'])
```

## Advanced Features

### Technical Indicators

```python
from omni_trifecta.utils.advanced_indicators import (
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    analyze_market_structure,
    detect_chart_patterns
)

# Calculate indicators
rsi = calculate_rsi(prices, period=14)
macd, signal, hist = calculate_macd(prices)
upper, middle, lower = calculate_bollinger_bands(prices)

# Market structure analysis
structure = analyze_market_structure(
    prices, high_prices, low_prices, volume
)
print(f"Trend: {structure.trend}")
print(f"Strength: {structure.strength}")
print(f"Support: {structure.support_levels}")
print(f"Resistance: {structure.resistance_levels}")

# Pattern detection
patterns = detect_chart_patterns(prices)
for pattern in patterns:
    print(f"{pattern['pattern']}: {pattern['direction']} ({pattern['confidence']})")
```

### Order Management

```python
from omni_trifecta.execution.oms import OrderManagementSystem, OrderType

oms = OrderManagementSystem()

# Create order
order = oms.create_order(
    symbol='BTC/USDT',
    side='BUY',
    order_type=OrderType.MARKET,
    quantity=0.1,
    metadata={'strategy': 'momentum', 'confidence': 0.8}
)

# Fill order
oms.fill_order(order.order_id, fill_price=45000.0, fill_quantity=0.1)

# Get position
position = oms.get_position('BTC/USDT')
print(f"Position: {position.quantity} @ ${position.entry_price}")
print(f"Unrealized P&L: ${position.unrealized_pnl}")

# Portfolio summary
summary = oms.get_portfolio_summary()
print(f"Total P&L: ${summary['total_pnl']}")
print(f"Open Positions: {summary['open_positions']}")
```

## Monitoring & Logging

### Log Files

All logs are saved to `runtime/logs/`:

- `ticks.jsonl` - All price ticks
- `trades.jsonl` - All trade executions
- `events.jsonl` - System events
- `decision_audit.jsonl` - Decision trail
- `performance.jsonl` - Performance metrics

### Performance Metrics

```python
from omni_trifecta.runtime.logging import PerformanceRecorder

perf_recorder = PerformanceRecorder(config.log_dir)

# Record metrics
perf_recorder.record_metrics(
    balance=balance,
    equity_curve=[balance],
    engine_stats=governor.regime_rl.get_stats(),
    safety_status=safety_manager.get_status()
)
```

## Production Checklist

### Pre-Deployment

- [ ] Test in shadow mode for 7+ days
- [ ] Verify all API credentials
- [ ] Test broker connectivity
- [ ] Configure safety limits
- [ ] Set up monitoring/alerting
- [ ] Review risk parameters
- [ ] Test emergency shutdown

### Deployment

- [ ] Start with minimal capital
- [ ] Use testnet/paper trading first
- [ ] Monitor first 100 trades closely
- [ ] Review logs daily
- [ ] Adjust parameters as needed
- [ ] Scale gradually

### Post-Deployment

- [ ] Daily performance review
- [ ] Weekly risk analysis
- [ ] Monthly strategy optimization
- [ ] Quarterly model retraining
- [ ] Continuous monitoring

## Troubleshooting

### Common Issues

**API Connection Errors**
- Verify credentials in `.env`
- Check IP whitelist on broker
- Ensure sufficient API rate limits

**Position Sizing Issues**
- Review risk parameters
- Check account balance
- Verify volatility calculations

**Safety Cooldown Triggered**
- Review loss streak
- Check daily loss limits
- Analyze trade quality

### Emergency Shutdown

```python
from omni_trifecta.safety.managers import EmergencyShutdownController

shutdown = EmergencyShutdownController()

# Trigger shutdown
shutdown.trigger_shutdown(reason="Manual intervention")

# Close all positions
for symbol in oms.positions:
    position = oms.get_position(symbol)
    broker.close_position(symbol)
```

## Support & Resources

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: See README.md for architecture details
- **Examples**: Check `examples/` directory for more samples
- **Configuration**: See `omni_trifecta/core/configurations.py` for templates

## Security Best Practices

1. **API Keys**
   - Store in `.env` file (never commit to git)
   - Use read-only keys when possible
   - Rotate keys regularly
   - Use IP whitelisting

2. **Private Keys** (Web3)
   - Use hardware wallet for production
   - Never expose in code
   - Use environment variables only

3. **Network Security**
   - Use VPN for trading
   - Enable 2FA on all accounts
   - Monitor for unauthorized access

4. **Capital Management**
   - Start with small amounts
   - Never risk more than you can afford
   - Keep emergency reserves
   - Use stop losses

## Disclaimer

This is a sophisticated trading system. Trading involves substantial risk of loss. Past performance does not guarantee future results. Always:

- Test thoroughly in shadow/paper mode
- Start with minimal capital
- Monitor continuously
- Use appropriate risk management
- Understand all strategies before deployment

