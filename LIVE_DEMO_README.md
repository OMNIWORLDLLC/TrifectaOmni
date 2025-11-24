# 🚀 TrifectaOmni Live Demo - Quick Start Guide

## One-Click Install, Build & Run

This demo showcases TrifectaOmni's AI-powered trading system with **real-time market data** streaming, predictions, and decision-making in **shadow mode** (no real trades executed).

---

## ⚡ Quick Start (One Command)

### Option 1: Install & Run Everything
```bash
chmod +x build_and_run_demo.sh
./build_and_run_demo.sh
```

This single script will:
- ✅ Install all system dependencies
- ✅ Create Python virtual environment
- ✅ Install all Python packages
- ✅ Configure the system
- ✅ Launch the live demo
- ✅ Open the dashboard in your browser

### Option 2: Manual Installation (If Needed)
```bash
# 1. Run installation only
chmod +x one_click_install.sh
./one_click_install.sh

# 2. Launch the demo
source venv/bin/activate
python3 live_demo.py
```

---

## 🎯 What You'll See

### Live Dashboard (http://localhost:8080)
The dashboard displays in real-time:

1. **Portfolio Metrics**
   - Portfolio value with P&L
   - Cash available
   - Unrealized & realized P&L
   - Win rate and Sharpe ratio

2. **Real-Time Charts**
   - Portfolio performance over time
   - Signal distribution (Buy/Sell/Hold)

3. **Symbol Cards (AAPL, MSFT, GOOGL, TSLA, NVDA, SPY)**
   - Current price (live updates every 60s)
   - AI predictions (LSTM + Transformer ensemble)
   - Trading signals with confidence levels
   - Visual prediction bars

4. **Activity Feed**
   - Live stream of all trading signals
   - Timestamps and signal strengths
   - Execution confirmations (shadow mode)

---

## 🛡️ Shadow Mode Features

**No Real Trades Executed** - All trading happens in simulation:
- ✅ Real market data from Yahoo Finance
- ✅ Actual AI predictions on live data
- ✅ Real Fibonacci level calculations
- ✅ Genuine risk management decisions
- ❌ No real broker connections
- ❌ No real money at risk
- ✅ Perfect for testing and demonstration

**Initial Virtual Capital:** $100,000

---

## 🏗️ System Architecture

### Data Pipeline
```
Yahoo Finance → Data Feed → Feature Engineering → AI Models → Predictions
```

### Decision Pipeline
```
Predictions → Fibonacci Analysis → Risk Manager → Signal Generation → Shadow OMS
```

### Components Running:
1. **Unified Data Feed** - Fetches real-time market data
2. **LSTM Predictor** - Neural network for price prediction
3. **Transformer Predictor** - Advanced sequence model
4. **Fibonacci Engine** - Calculates support/resistance levels
5. **Master Governor** - Makes trading decisions
6. **Risk Manager** - Enforces position limits
7. **Shadow OMS** - Simulates order execution
8. **WebSocket Server** - Streams updates to dashboard

---

## 📊 Tracked Symbols

- **AAPL** - Apple Inc.
- **MSFT** - Microsoft Corporation
- **GOOGL** - Alphabet Inc.
- **TSLA** - Tesla Inc.
- **NVDA** - NVIDIA Corporation
- **SPY** - S&P 500 ETF

All symbols update every **60 seconds** with fresh market data.

---

## 🔧 Configuration

### Default Configuration (`config/live_demo_config.yaml`)
```yaml
system:
  mode: shadow
  log_level: INFO

data:
  symbols: [AAPL, MSFT, GOOGL, TSLA, NVDA, SPY]
  update_interval: 60  # seconds

prediction:
  models: [lstm, transformer]
  confidence_threshold: 0.6

execution:
  initial_capital: 100000
  risk_per_trade: 0.02
  max_positions: 5
```

### Customization
Edit the config file to:
- Change tracked symbols
- Adjust update frequency
- Modify risk parameters
- Change initial capital

---

## 🎮 Usage

### Starting the Demo
```bash
./build_and_run_demo.sh
```

### Accessing the Dashboard
Open your browser to: **http://localhost:8080**

The dashboard will automatically connect via WebSocket and start displaying real-time updates.

### Monitoring
- **Dashboard**: Real-time visual interface
- **Logs**: `logs/live_demo.log`
- **Terminal**: Live status updates

### Stopping the Demo
Press `Ctrl+C` in the terminal running the demo.

---

## 🧪 Testing & Verification

### Check Installation
```bash
source venv/bin/activate
python3 verify_installation.py
```

### Check API Endpoints
```bash
# System status
curl http://localhost:8080/api/status

# Trade history
curl http://localhost:8080/api/history
```

### Check WebSocket
```bash
# Install wscat if needed
npm install -g wscat

# Connect to WebSocket
wscat -c ws://localhost:8080/ws
```

---

## 📈 Performance Metrics

The system tracks and displays:
- **Total Signals Generated** - All buy/sell/hold decisions
- **Win Rate** - Percentage of profitable trades
- **Sharpe Ratio** - Risk-adjusted returns
- **Portfolio Value** - Current total value
- **Realized P&L** - Closed position profits/losses
- **Unrealized P&L** - Open position profits/losses

---

## 🔍 How It Works

### 1. Data Collection (Every 60s)
- Fetches latest 1-minute bars from Yahoo Finance
- Calculates technical indicators (RSI, MACD, Bollinger Bands)
- Normalizes features for AI models

### 2. Prediction Generation
- **LSTM Model**: Analyzes momentum and trends
- **Transformer Model**: Considers volatility and patterns
- **Ensemble**: Combines both predictions with confidence scoring

### 3. Signal Generation
- Compares predictions with Fibonacci levels
- Checks near support (buy opportunities) or resistance (sell signals)
- Applies confidence thresholds (>60%)
- Calculates signal strength

### 4. Risk Management
- Validates against position limits
- Checks portfolio exposure
- Ensures adequate cash for trades
- Applies stop-loss logic

### 5. Shadow Execution
- Simulates order placement
- Tracks position costs and sizes
- Calculates P&L in real-time
- Updates portfolio metrics

### 6. Dashboard Updates
- Broadcasts via WebSocket
- Updates charts and cards
- Logs activity feed
- Maintains connection health

---

## 🚨 Troubleshooting

### Port 8080 Already in Use
```bash
# Find and kill process using port 8080
lsof -ti:8080 | xargs kill -9

# Or change port in live_demo.py
```

### Redis Not Running
```bash
# Start Redis (Ubuntu/Debian)
sudo systemctl start redis-server

# Start Redis (macOS)
brew services start redis

# Or run without Redis (caching disabled)
```

### Import Errors
```bash
# Reinstall packages
source venv/bin/activate
pip install --upgrade -r requirements.txt
pip install -e .
```

### WebSocket Connection Failed
- Check firewall settings
- Ensure demo is running: `ps aux | grep live_demo.py`
- Check logs: `tail -f logs/live_demo.log`

---

## 📁 Project Structure

```
TrifectaOmni/
├── build_and_run_demo.sh      # One-click launcher ⭐
├── one_click_install.sh        # Installation script
├── live_demo.py                # Main demo application
├── dashboard/
│   └── index.html              # Web interface
├── config/
│   └── live_demo_config.yaml   # Configuration
├── logs/
│   └── live_demo.log           # Application logs
├── omni_trifecta/              # Core package
│   ├── data/                   # Data feeds
│   ├── prediction/             # AI models
│   ├── decision/               # Decision engine
│   ├── execution/              # Order management
│   ├── fibonacci/              # Fibonacci analysis
│   └── safety/                 # Risk management
└── requirements.txt            # Python dependencies
```

---

## 🎯 Next Steps

After running the demo:

1. **Observe the System** - Watch predictions and signals in real-time
2. **Analyze Performance** - Check win rate and P&L metrics
3. **Customize Configuration** - Adjust symbols and parameters
4. **Review Logs** - Understand decision-making process
5. **Extend Functionality** - Add new models or indicators

---

## ⚠️ Important Notes

- **Educational Purpose**: This demo is for learning and testing
- **No Real Trading**: All executions are simulated
- **Market Data**: Free tier from Yahoo Finance (delayed possible)
- **API Limits**: Respect rate limits (60s updates safe)
- **Resource Usage**: Moderate CPU/memory for AI models

---

## 🆘 Support

### Issues?
1. Check `logs/live_demo.log` for errors
2. Verify all packages installed: `pip list`
3. Ensure Redis running: `redis-cli ping`
4. Test port availability: `nc -zv localhost 8080`

### Need Help?
- Review configuration in `config/live_demo_config.yaml`
- Check system status: `curl localhost:8080/api/status`
- Restart demo: `./build_and_run_demo.sh`

---

## 🎉 Success Indicators

✅ Demo is working if you see:
- Dashboard loads at http://localhost:8080
- "Live" status indicator is green
- Symbol prices updating every 60 seconds
- Predictions appearing in symbol cards
- Activity feed showing signals
- Portfolio value tracking changes

---

## 📜 License

See main project LICENSE file.

---

**Happy Demo Running! 🚀📈**

Built with ❤️ by the TrifectaOmni Team
