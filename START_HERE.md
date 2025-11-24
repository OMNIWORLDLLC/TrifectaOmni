# 🚀 TrifectaOmni - ONE-CLICK LIVE DEMO

## ⚡ QUICK START (60 Seconds to Live Trading Demo)

```bash
./build_and_run_demo.sh
```

That's it! The system will:
1. ✅ Install all dependencies automatically
2. ✅ Build the complete system
3. ✅ Launch live streaming demo
4. ✅ Open dashboard in your browser

---

## 🎯 What This Demo Does

### Real-Time AI Trading System (Shadow Mode)
- **Streams LIVE market data** from Yahoo Finance (AAPL, MSFT, GOOGL, TSLA, NVDA, SPY)
- **AI Predictions** using LSTM + Transformer models
- **Fibonacci-based signals** with confidence scoring
- **Risk management** and position tracking
- **Beautiful web dashboard** with real-time updates
- **Shadow mode** - No real trades, zero risk!

### Updates Every 60 Seconds
- Fresh market prices
- New AI predictions
- Trading signals
- Portfolio metrics

---

## 📊 Live Dashboard

Access at: **http://localhost:8080**

### Features:
- 📈 **Portfolio Performance** - Real-time P&L tracking
- 🎯 **6 Symbol Cards** - Each with live prices, predictions, and signals
- 📊 **Interactive Charts** - Portfolio growth and signal distribution
- 📡 **Activity Feed** - Live stream of all trading decisions
- 💰 **Metrics** - Win rate, Sharpe ratio, position tracking

---

## 🛠️ System Requirements

### Automatic Installation Handles:
- ✅ Python 3.8+
- ✅ System packages (build tools, etc.)
- ✅ All Python dependencies (PyTorch, TensorFlow, etc.)
- ✅ Redis (optional, for caching)
- ✅ Node.js packages (for dashboard)

### Supported Platforms:
- Ubuntu/Debian Linux
- macOS
- Other Linux distributions (with minor adjustments)

---

## 📖 How to Use

### Method 1: One-Click Launch (Recommended)
```bash
chmod +x build_and_run_demo.sh
./build_and_run_demo.sh
```

### Method 2: Step-by-Step
```bash
# 1. Install everything
chmod +x one_click_install.sh
./one_click_install.sh

# 2. Activate environment
source venv/bin/activate

# 3. Run demo
python3 live_demo.py
```

### Method 3: Quick Launch (After Installation)
```bash
source venv/bin/activate
python3 live_demo.py
```

---

## 🎮 What You'll See

### Terminal Output
```
🚀 TrifectaOmni Live Demo Starting...
====================================================================
📊 Tracking symbols: AAPL, MSFT, GOOGL, TSLA, NVDA, SPY
🔄 Update interval: 60 seconds
💰 Initial capital: $100,000
🛡️  Mode: SHADOW (No real executions)

🌐 Dashboard: http://localhost:8080
📡 WebSocket: ws://localhost:8080/ws
====================================================================

INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8080
```

### Web Dashboard
- **Green "Live" indicator** - System is streaming
- **Symbol cards updating** - Prices, predictions, signals
- **Portfolio value changing** - Based on shadow trades
- **Activity feed scrolling** - Live trading decisions
- **Charts animating** - Performance visualization

---

## 🧪 Verify Installation

Before running, test the setup:
```bash
python3 test_demo_setup.py
```

Expected output:
```
✅ ALL TESTS PASSED! Ready to run the live demo.
```

---

## 🎨 Dashboard Features Explained

### 1. Portfolio Metrics (Top)
- **Portfolio Value** - Total virtual capital
- **Cash Available** - Unallocated funds
- **Unrealized P&L** - Open position profits
- **Realized P&L** - Closed trade profits
- **Total Signals** - All decisions made
- **Win Rate** - Percentage of profitable trades

### 2. Charts (Middle)
- **Portfolio Performance** - Value over time
- **Signal Distribution** - Buy/Sell/Hold breakdown

### 3. Symbol Cards (Grid)
Each card shows:
- Current price (live updates)
- AI prediction direction & confidence
- Visual prediction bar (green=bullish, red=bearish)
- Trading signal (BUY/SELL/HOLD badge)

### 4. Activity Feed (Bottom)
Live scrolling feed of:
- New signals generated
- Shadow trades executed
- Price milestones
- System events

---

## ⚙️ Configuration

### Default Settings
- **Symbols**: AAPL, MSFT, GOOGL, TSLA, NVDA, SPY
- **Update Frequency**: 60 seconds
- **Initial Capital**: $100,000
- **Risk per Trade**: 2% of portfolio
- **Max Positions**: 5 concurrent

### Customize
Edit `config/live_demo_config.yaml`:
```yaml
data:
  symbols: [AAPL, AMZN, TSLA]  # Change symbols
  update_interval: 30           # Faster updates

execution:
  initial_capital: 50000        # Different capital
  risk_per_trade: 0.01          # More conservative
```

---

## 🔍 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                   WEB DASHBOARD                          │
│              (Real-time WebSocket Updates)               │
└─────────────────────────────────────────────────────────┘
                           ▲
                           │
┌─────────────────────────────────────────────────────────┐
│                  LIVE DEMO ORCHESTRATOR                  │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Data Feed    │→ │ AI Predictor │→ │ Signal Gen   │  │
│  │ (YFinance)   │  │ (LSTM+Trans) │  │ (Fibonacci)  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│           │                │                │            │
│           ▼                ▼                ▼            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Risk Manager │→ │ Decision Gov │→ │ Shadow OMS   │  │
│  │              │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                           ▲
                           │
┌─────────────────────────────────────────────────────────┐
│              REAL MARKET DATA (Yahoo Finance)            │
└─────────────────────────────────────────────────────────┘
```

---

## 📝 Demo Capabilities

### What It DOES:
✅ Fetches real, live market data
✅ Runs actual AI predictions
✅ Calculates genuine Fibonacci levels
✅ Generates real trading signals
✅ Tracks virtual portfolio accurately
✅ Shows realistic P&L calculations
✅ Demonstrates full system integration

### What It DOESN'T Do:
❌ Connect to real brokers
❌ Execute actual trades
❌ Risk real money
❌ Require API keys (basic mode)
❌ Need paid subscriptions

---

## 🚨 Troubleshooting

### Port 8080 Already in Use?
```bash
# Kill process on port 8080
lsof -ti:8080 | xargs kill -9
```

### Module Import Errors?
```bash
# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt
```

### Dashboard Won't Load?
1. Check demo is running: `ps aux | grep live_demo`
2. Check logs: `tail -f logs/live_demo.log`
3. Try different browser
4. Clear browser cache

### No Data Updating?
- Check internet connection (needs Yahoo Finance access)
- Market might be closed (updates only during trading hours)
- Check logs for API errors

---

## 📊 Performance Tips

### Faster Updates
Edit `config/live_demo_config.yaml`:
```yaml
data:
  update_interval: 30  # Update every 30 seconds
```

### More Symbols
```yaml
data:
  symbols: [AAPL, MSFT, GOOGL, TSLA, NVDA, SPY, AMZN, META, NFLX]
```

### Different Prediction Horizon
```yaml
prediction:
  horizon: 10  # Shorter-term predictions
```

---

## 🎓 Learning from the Demo

### Observe:
1. **How AI predictions compare to actual price movements**
2. **When Fibonacci signals trigger vs when they don't**
3. **How risk management limits position sizes**
4. **The relationship between confidence and accuracy**
5. **Portfolio performance over time**

### Experiment:
1. Change configuration parameters
2. Add more symbols
3. Adjust risk settings
4. Modify prediction thresholds
5. Watch how system responds

### Extend:
1. Add your own indicators
2. Create custom prediction models
3. Implement new signal strategies
4. Build additional visualizations
5. Integrate other data sources

---

## 📚 Documentation

- **Full Documentation**: See `LIVE_DEMO_README.md`
- **Installation Guide**: See `one_click_install.sh`
- **API Reference**: http://localhost:8080/docs (when running)
- **Logs**: `logs/live_demo.log`

---

## 🎯 Next Steps

After running the demo:

1. **Watch it run** for 10-15 minutes to see multiple update cycles
2. **Check the metrics** - Are predictions accurate? Is P&L positive?
3. **Review the logs** to understand decision-making
4. **Customize configuration** to your preferences
5. **Extend the system** with your own ideas

---

## ⚡ Quick Commands Reference

```bash
# Install and run (first time)
./build_and_run_demo.sh

# Run again (after installation)
source venv/bin/activate
python3 live_demo.py

# Test setup
python3 test_demo_setup.py

# Check status
curl http://localhost:8080/api/status

# View logs
tail -f logs/live_demo.log

# Stop demo
Ctrl+C (in terminal running demo)
```

---

## 🎉 Success Checklist

✅ Demo is working when you see:
- [ ] Terminal shows "Started server process"
- [ ] Dashboard loads at http://localhost:8080
- [ ] Status indicator shows "Live" (green dot)
- [ ] Symbol prices are displayed
- [ ] Prices update every ~60 seconds
- [ ] Predictions appear in symbol cards
- [ ] Activity feed shows events
- [ ] Portfolio value is tracking

---

## 🆘 Need Help?

### Check These First:
1. `logs/live_demo.log` - Detailed error messages
2. `python3 test_demo_setup.py` - Verify installation
3. `curl localhost:8080/api/status` - Check if server running

### Common Issues:
- **Import errors** → Run `./one_click_install.sh`
- **Port conflicts** → Kill process on 8080
- **No updates** → Check internet, market hours
- **Slow performance** → Reduce symbol count or update frequency

---

## 📜 Credits

Built with:
- **FastAPI** - Modern web framework
- **PyTorch** - Deep learning
- **TensorFlow** - Machine learning
- **Chart.js** - Visualizations
- **Yahoo Finance** - Market data

---

## 🔒 Safety Notice

**This is a DEMO system running in SHADOW MODE:**
- ✅ Safe to run - no real trading
- ✅ No financial risk
- ✅ Educational purpose only
- ⚠️ Not financial advice
- ⚠️ Past performance doesn't guarantee future results

---

## 🚀 Launch Now!

```bash
./build_and_run_demo.sh
```

**Dashboard:** http://localhost:8080

**Watch real AI trading in action!** 📈🤖

---

*Built with ❤️ for the TrifectaOmni Project*
*Version 1.0 - Live Demo Edition*
