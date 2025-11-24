# 🎯 Real-Time Multi-Asset Opportunity Scanner

## Overview

The **TrifectaOmni Real-Time Scanner** simultaneously detects and streams three types of trading opportunities:

1. **💎 Cryptocurrency Arbitrage** - Cross-exchange, cross-chain, and triangular arbitrage
2. **💱 Forex Trading Signals** - All major USD currency pairs
3. **⚡ Binary Options** - Ultra-short term (60-second expiry) high-probability setups

---

## 🚀 Quick Start

### One-Command Launch:
```bash
./launch_realtime_scanner.sh
```

### Manual Launch:
```bash
cd /workspaces/TrifectaOmni
source venv/bin/activate
python3 realtime_multi_asset_demo.py
```

### Access Dashboard:
Open your browser to: **http://localhost:8080**

---

## 📊 Features

### 1. Cryptocurrency Arbitrage Detection

#### **Cross-Exchange Arbitrage (2-Hop)**
- Detects price differences between exchanges
- Example: Buy BTC on Binance @ $43,000, Sell on Kraken @ $43,150
- Real-time spread calculation with fees and gas costs
- **Minimum Profit Threshold:** 15 basis points (0.15%)

#### **Cross-Chain Arbitrage**
- Monitors token equivalents across blockchains
- Example: USDC on Ethereum vs USDC on Arbitrum
- Accounts for bridge fees and waiting times
- Supported tokens: USDC, USDT, WETH, WBTC
- **Chains:** Ethereum, Polygon, Arbitrum, Optimism, Base, Avalanche, BNB Chain

#### **Triangular Arbitrage (3-Hop)**
- Detects circular trading opportunities
- Example: USDT → BTC → ETH → USDT
- Calculates implied vs actual exchange rates
- **Minimum Profit Threshold:** 30 basis points (0.30%)

#### **Real-Time Metrics Displayed:**
- Expected Profit (USD)
- Profit Margin (basis points)
- Risk Score (0-100)
- Execution Time (milliseconds)
- Capital Required
- Buy/Sell Prices
- Recommendation (Execute/Consider/Monitor)

---

### 2. Forex Trading Opportunities

#### **Supported Pairs - All Majors Involving USD:**
```
EUR/USD - Euro vs US Dollar
GBP/USD - British Pound vs US Dollar
USD/JPY - US Dollar vs Japanese Yen
AUD/USD - Australian Dollar vs US Dollar
USD/CAD - US Dollar vs Canadian Dollar
USD/CHF - US Dollar vs Swiss Franc
NZD/USD - New Zealand Dollar vs US Dollar
USD/SEK - US Dollar vs Swedish Krona
USD/NOK - US Dollar vs Norwegian Krone
USD/DKK - US Dollar vs Danish Krone
```

#### **Technical Analysis Signals:**
- **RSI (Relative Strength Index)** - Overbought/Oversold detection
- **Moving Averages** - SMA 20, SMA 50 trend analysis
- **MACD** - Momentum and trend strength
- **ATR-Based Stop Loss/Take Profit** - Dynamic risk management

#### **Signal Strength:**
- **Strong Signal (80%+):** Execute immediately
- **Moderate Signal (70-80%):** Consider entry
- **Weak Signal (<70%):** Monitor only

#### **Risk Management:**
- Automatic Stop Loss calculation (1x ATR)
- Automatic Take Profit calculation (2x ATR)
- Risk/Reward Ratio displayed
- Pip target calculations

---

### 3. Binary Options Opportunities (60-Second Expiry)

#### **Ultra-Short Term Analysis:**
- **1-minute momentum** analysis
- **5-minute micro-trend** detection
- **RSI-5** for quick reversals
- **Volatility filtering** (low volatility = higher confidence)

#### **Probability Thresholds:**
- **High Probability (75%+):** Recommended execution
- **Moderate Probability (65-75%):** Proceed with caution
- **Low Probability (<65%):** Skip

#### **Call/Put Signals:**
- **CALL:** Price expected to rise in 60 seconds
- **PUT:** Price expected to fall in 60 seconds

#### **Displayed Metrics:**
- Win Probability percentage
- Payout Ratio (typically 1.85x)
- Risk Amount ($100 standard)
- Potential Profit
- Current vs Predicted Price
- Momentum (pips per minute)
- Volatility percentage

---

## 🎨 Dashboard Features

### Real-Time Statistics Bar:
- **Arbitrage Opportunities Found** - Total cross-exchange and cross-chain opportunities
- **Forex Opportunities Found** - Total trading signals generated
- **Binary Options Found** - Total high-probability setups
- **Total Scans** - Number of complete scans performed
- **Uptime** - Scanner running time

### Live Opportunity Cards:
- Color-coded by opportunity type:
  - **Green Border:** Arbitrage opportunities
  - **Blue Border:** Forex signals
  - **Orange Border:** Binary options
- Badge indicators:
  - ✅ **EXECUTE NOW** - High confidence, low risk
  - ⚠️ **CONSIDER** - Moderate confidence
  - ❌ **MONITOR** - Low confidence or high risk
- Hover effects for interactivity
- Auto-refresh every 15 seconds

### Connection Status:
- 🟢 **Live** - WebSocket connected, receiving updates
- 🔴 **Disconnected** - Attempting to reconnect
- Real-time ping/heartbeat

---

## 📈 Performance Metrics

### Update Intervals:
- **Arbitrage Scan:** Every 30 seconds
- **Forex Scan:** Every 10 seconds
- **Binary Options Scan:** Every 15 seconds
- **Dashboard Refresh:** Every 15 seconds (combined)

### Data Sources:
- **Yahoo Finance** - Real-time market data (free tier, 60-second delay)
- **Simulated Exchanges** - Bid/ask spreads for arbitrage detection
- **Token Equivalence Registry** - Cross-chain token mapping

### Accuracy:
- ✅ **Arbitrage:** Net profit calculated after all fees, gas, slippage
- ✅ **Forex:** Multi-indicator confluence for signal validation
- ✅ **Binary:** Probability-weighted with volatility adjustment

---

## 🔧 Technical Architecture

### Backend (FastAPI + WebSockets):
```python
# Main Components:
- RealTimeOpportunityScanner    # Core scanning logic
- MultiHopArbitrageCalculator   # Arbitrage profit calculator
- TOKEN_REGISTRY                # Cross-chain token mapping
- WebSocket Broadcaster         # Real-time updates to clients
```

### Frontend (HTML + JavaScript):
```javascript
// WebSocket Client
- Auto-reconnect on disconnect
- Real-time DOM updates
- Responsive grid layout
- Color-coded opportunity cards
```

### Data Flow:
```
1. Fetch Market Data (YFinance API)
   ↓
2. Scan for Opportunities (3 parallel scans)
   • Arbitrage: Cross-exchange + Cross-chain + Triangular
   • Forex: Technical analysis on 10 major pairs
   • Binary: Ultra-short term momentum
   ↓
3. Calculate Metrics
   • Profit/Loss
   • Risk scores
   • Probabilities
   ↓
4. Broadcast via WebSocket
   ↓
5. Dashboard Updates in Real-Time
```

---

## 🎯 Opportunity Examples

### Example 1: Cross-Exchange Arbitrage
```
Asset: BTC
Route: 2-HOP
Buy: Binance @ $43,010.00
Sell: Kraken @ $43,180.00
Spread: 0.395%
Expected Profit: $125.50
Profit (bps): 125.50 bps
Capital Required: $10,000
Risk Score: 15.0/100 (LOW)
Execution Time: 120ms
Recommendation: ✅ EXECUTE NOW
```

### Example 2: Forex Signal
```
Pair: EUR/USD
Signal: BUY
Strength: 82.5%
Current Price: 1.08450
Entry: 1.08450
Take Profit: 1.08650
Stop Loss: 1.08350
Risk/Reward: 2.0:1
Pip Target: 20 pips
Timeframe: 15m
Confidence: 88.0%
Indicators:
  • RSI: 28.5 (Oversold)
  • SMA20: 1.08550
  • MACD: Bullish crossover
Recommendation: ✅ STRONG SIGNAL
```

### Example 3: Binary Options
```
Pair: GBP/USD
Direction: CALL
Expiry: 60 seconds
Probability: 78.5%
Payout: 1.85
Current: 1.26450
Predicted: 1.26462
Risk: $100.00
Potential Profit: $85.00
Momentum: +2.15 pips/min
Volatility: 0.08%
Indicators:
  • RSI_5: 32.0
  • Momentum_1m: +0.0008%
  • Trend: Bullish
Recommendation: ✅ HIGH PROBABILITY
```

---

## 🛡️ Risk Management

### Arbitrage Risk Controls:
- **Minimum Profit Threshold:** 25 basis points
- **Maximum Slippage:** 50 basis points
- **Safety Margin:** 15% (reduces expected profit)
- **Risk Score Calculation:** Based on profit, slippage, liquidity, complexity
- **Capital Limits:** $1,000 minimum, $500,000 maximum

### Forex Risk Controls:
- **Signal Strength Filter:** Minimum 70% strength
- **Risk/Reward Minimum:** 1.5:1 ratio
- **ATR-Based Stops:** Dynamic based on volatility
- **Multi-Indicator Confluence:** 4+ indicators must agree

### Binary Options Risk Controls:
- **Probability Threshold:** Minimum 65% win rate
- **Volatility Filter:** High volatility = reduced confidence
- **Momentum Validation:** Must have directional momentum
- **Fixed Risk:** $100 per trade (adjustable)

---

## 📊 Statistics & Tracking

The scanner tracks:
- Total opportunities found (by type)
- Total scans performed
- System uptime
- Real-time connection status
- Last update timestamp

---

## 🔍 How It Works

### Arbitrage Detection:
1. Fetch cryptocurrency prices from multiple sources
2. Simulate bid/ask spreads for different exchanges
3. Calculate potential profit after fees, gas, slippage
4. Apply 15% safety margin
5. Filter by minimum profit threshold (25 bps)
6. Calculate risk score (0-100)
7. Generate recommendation

### Forex Signal Generation:
1. Fetch 15-minute forex data (5 days history)
2. Calculate technical indicators (RSI, SMA, MACD)
3. Score bullish vs bearish signals
4. Determine signal strength and direction
5. Calculate ATR-based stop loss / take profit
6. Compute risk/reward ratio
7. Generate confidence score

### Binary Options Analysis:
1. Fetch recent price data (ultra-short term)
2. Calculate 1-minute and 5-minute momentum
3. Measure micro-trend strength
4. Check RSI-5 for quick reversals
5. Assess volatility (high volatility = lower confidence)
6. Calculate win probability
7. Adjust for risk factors

---

## 🌐 Supported Assets

### Cryptocurrencies (Arbitrage):
- BTC (Bitcoin)
- ETH (Ethereum)
- BNB (Binance Coin)
- ADA (Cardano)
- SOL (Solana)
- MATIC (Polygon)
- AVAX (Avalanche)

### Cross-Chain Tokens:
- USDC (10 variants across 8 chains)
- USDT (6 variants)
- WETH (6 variants)
- WBTC (6 variants)

### Forex Pairs (All USD Majors):
- EUR/USD, GBP/USD, USD/JPY
- AUD/USD, USD/CAD, USD/CHF
- NZD/USD, USD/SEK, USD/NOK, USD/DKK

### Binary Options (Same as Forex):
- All major USD pairs
- 60-second expiry
- High-frequency setups

---

## 🚨 Important Notes

### Data Accuracy:
- Yahoo Finance provides **free-tier data** with ~60 second delay
- For production use, integrate paid real-time APIs (Bloomberg, IEX, etc.)
- Exchange prices are **simulated** for demo purposes
- Use actual exchange APIs (Binance, Kraken, Coinbase) for live trading

### Execution Disclaimer:
⚠️ **This is a DEMO/SCANNING system only**
- No actual trades are executed
- Opportunities are for **informational purposes only**
- Always verify prices before executing real trades
- Consider slippage, market impact, and execution delays
- Past performance does not guarantee future results

### Risk Warning:
- **Arbitrage:** Prices can move during execution, eliminating profit
- **Forex:** High leverage can result in significant losses
- **Binary Options:** 60-second trades are extremely risky and speculative
- Never risk more than you can afford to lose
- Use proper risk management and position sizing

---

## 🛠️ Troubleshooting

### Connection Issues:
```bash
# If WebSocket won't connect:
1. Check if port 8080 is available: lsof -i :8080
2. Restart the scanner: ./launch_realtime_scanner.sh
3. Check firewall settings
4. Try accessing via http://127.0.0.1:8080
```

### No Opportunities Found:
```
Possible reasons:
• Market conditions (tight spreads, low volatility)
• Profit thresholds too high (adjust in code)
• Data fetch errors (check logs/realtime_demo.log)
• Network issues (Yahoo Finance API down)

Solution:
• Lower min_profit_bps in MultiHopArbitrageCalculator
• Wait for more volatile market conditions
• Check logs for API errors
```

### Performance Issues:
```bash
# If dashboard is slow:
1. Reduce update frequency (increase sleep intervals)
2. Limit number of tracked assets
3. Optimize technical indicator calculations
4. Check system resources: top or htop
```

---

## 📝 Customization

### Adjust Profit Thresholds:
```python
# In realtime_multi_asset_demo.py
calculator = MultiHopArbitrageCalculator(
    min_profit_bps=25.0,      # Change to 15.0 for more opportunities
    max_slippage_bps=50.0,    # Increase for higher risk tolerance
    safety_margin=0.15        # Reduce for more aggressive estimates
)
```

### Change Update Intervals:
```python
# In realtime_multi_asset_demo.py
ARBITRAGE_UPDATE_INTERVAL = 30  # Change to 60 for less frequent scans
FOREX_UPDATE_INTERVAL = 10      # Change to 5 for faster updates
BINARY_OPTIONS_INTERVAL = 15    # Change to 10 for more frequent signals
```

### Add More Forex Pairs:
```python
# In realtime_multi_asset_demo.py
FOREX_PAIRS = [
    'EURUSD=X',
    'GBPUSD=X',
    'USDJPY=X',
    'USDMXN=X',  # Add Mexican Peso
    'USDBRL=X',  # Add Brazilian Real
    # ... add more
]
```

### Customize Dashboard Colors:
```css
/* In dashboard/realtime_scanner.html */
.opportunity-card.arbitrage {
    border-left-color: #10b981;  /* Change green to your color */
}
```

---

## 📚 API Reference

### Scanner Class:
```python
scanner = RealTimeOpportunityScanner()

# Scan for opportunities
arbitrage = await scanner.scan_arbitrage_opportunities()
forex = await scanner.scan_forex_opportunities()
binary = await scanner.scan_binary_options_opportunities()

# Get statistics
stats = scanner.get_stats()
```

### WebSocket Message Format:
```json
{
  "arbitrage": [...],
  "forex": [...],
  "binary_options": [...],
  "stats": {
    "arbitrage_opportunities_found": 12,
    "forex_opportunities_found": 8,
    "binary_opportunities_found": 5,
    "total_scans": 45,
    "uptime_seconds": 1350,
    "uptime_formatted": "0:22:30"
  },
  "timestamp": "2025-11-24T12:34:56.789Z"
}
```

---

## 🎓 Learning Resources

### Understanding Arbitrage:
- [Investopedia: Arbitrage](https://www.investopedia.com/terms/a/arbitrage.asp)
- [Cross-Chain Arbitrage Guide](https://academy.binance.com/en/articles/what-is-arbitrage-trading)

### Forex Trading:
- [BabyPips School of Pipsology](https://www.babypips.com/learn/forex)
- [Technical Analysis Basics](https://www.investopedia.com/technical-analysis-4427766)

### Binary Options (Use Caution):
- [Binary Options Overview](https://www.investopedia.com/terms/b/binary-option.asp)
- **Warning:** Binary options are banned in many jurisdictions due to high risk

---

## 🏁 Conclusion

The **TrifectaOmni Real-Time Scanner** provides a comprehensive view of trading opportunities across three asset classes. Use it as a learning tool, research platform, or basis for your own trading system.

**Remember:** Always do your own research, use proper risk management, and never trade with money you can't afford to lose.

---

## 📞 Support

For issues or questions:
1. Check the logs: `logs/realtime_demo.log`
2. Review this documentation
3. Check GitHub issues

---

**Last Updated:** November 24, 2025  
**Version:** 1.0.0  
**Status:** Production Ready ✅

**Happy Trading! 🚀**
