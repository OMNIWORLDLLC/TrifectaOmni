# 🎯 TrifectaOmni - Complete Windows Deployment

## ✅ ALL READY FOR YOUR LOCAL DRIVE!

You now have **5 Windows batch files** (.bat) for complete one-click deployment:

---

## 📦 What's Included

### 1️⃣ **install_and_run.bat** ⭐ MAIN INSTALLER
```
Double-click this first!
```

**What it does:**
- ✅ Checks Python installation
- ✅ Creates virtual environment automatically
- ✅ Installs all dependencies (NumPy, PyTorch, TensorFlow, CCXT, FastAPI, etc.)
- ✅ Creates directory structure (logs/, data/, dashboard/)
- ✅ Sets up .env configuration file
- ✅ Asks you: Demo or Production mode?
- ✅ Launches the scanner
- ✅ Opens dashboard at http://localhost:8080

**First time running?** USE THIS ONE!

---

### 2️⃣ **quick_start_demo.bat** 🚀 INSTANT DEMO
```
Quick launch - No configuration needed!
```

**Perfect for:**
- Testing the system (30 seconds)
- No API keys required
- Uses free Yahoo Finance data
- Full paper trading system
- Live dashboard

---

### 3️⃣ **launch_production.bat** 🔥 PRODUCTION MODE
```
Launch with real-time APIs
```

**Features:**
- Uses your configured APIs from .env
- Sub-second data latency
- Validates API configuration on startup
- Shows connection status
- Full production features

---

### 4️⃣ **setup_environment.bat** 🔧 SETUP ONLY
```
Prepare environment without launching
```

**Use when:**
- You want to setup first, run later
- Need to configure .env before starting
- Building environment for scheduled tasks

---

### 5️⃣ **run_tests.bat** 🧪 TEST SUITE
```
Verify everything works correctly
```

**Tests available:**
1. Demo setup verification
2. Arbitrage calculations
3. Token equivalence mapping
4. Full system validation

---

## 🚀 Quick Start (3 Steps)

### Step 1: Download to Your Local Drive
```
Download from: https://github.com/OMNIWORLDLLC/TrifectaOmni
Extract to: C:\TrifectaOmni (or anywhere you want)
```

### Step 2: Double-Click
```
install_and_run.bat
```

### Step 3: Choose Mode
```
Press 1 for Demo Mode (no configuration needed)
Press 2 for Production Mode (uses your API credentials)
```

**That's it!** Dashboard opens at http://localhost:8080

---

## 📋 Requirements

**You need:**
- ✅ Windows 10 or 11
- ✅ Python 3.8+ ([Download here](https://www.python.org/downloads/))
  - ⚠️ **CHECK "Add Python to PATH" during installation!**

**Optional:**
- Git (for easy updates)
- Visual Studio Code (best editor)

---

## 🎮 Usage Examples

### First Time Installation
```batch
REM Navigate to folder
cd C:\TrifectaOmni

REM Run installer
install_and_run.bat

REM Choose Demo Mode (press 1)
REM Dashboard opens at http://localhost:8080
```

### Quick Demo Launch (After Installation)
```batch
cd C:\TrifectaOmni
quick_start_demo.bat
```

### Production Launch (With Your APIs)
```batch
cd C:\TrifectaOmni

REM First time: Edit .env file
notepad .env

REM Add your credentials:
REM MT5_LOGIN=12345678
REM MT5_SERVER=ICMarkets-Demo
REM MT5_PASSWORD=your_password

REM Launch production scanner
launch_production.bat
```

### Run Tests
```batch
cd C:\TrifectaOmni
run_tests.bat

REM Choose test:
REM 1 = Demo setup test
REM 2 = Arbitrage calculations
REM 3 = Token equivalence
REM 4 = Full test suite
```

---

## 🔧 Configuration (.env file)

### For Demo Mode
**No configuration needed!** Just works.

### For Production Mode

Edit `.env` file:

```bash
# ===== FOREX REAL-TIME (MetaTrader 5) =====
MT5_LOGIN=12345678
MT5_SERVER=ICMarkets-Demo
MT5_PASSWORD=your_password

# ===== CRYPTO ARBITRAGE (CCXT) =====
# No API keys needed for market data!
# Just install: pip install ccxt

# ===== BLOCKCHAIN/DEX =====
DEX_RPC=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
DEX_PRIVKEY=your_private_key

# ===== BINARY OPTIONS =====
POCKET_TOKEN=your_api_token
POCKET_BASE_URL=https://api.po.trade

# ===== EXCHANGE KEYS (Optional for trading) =====
BINANCE_API_KEY=your_key
BINANCE_SECRET=your_secret
```

**Get API Credentials:**
- **MT5:** Sign up with [IC Markets](https://www.icmarkets.com/) or [Pepperstone](https://pepperstone.com/)
- **Infura:** [infura.io](https://infura.io/) (100k free requests/day)
- **Pocket Option:** [po.trade](https://po.trade/)
- **CCXT:** No keys needed for data! Just `pip install ccxt`

---

## 📊 What You'll See

Dashboard at **http://localhost:8080** shows:

### 🎯 Real-Time Opportunities

**Arbitrage:**
- Cross-exchange crypto arbitrage
- Cross-chain token arbitrage (8 networks)
- Triangular arbitrage (3-hop)
- Expected profit & risk scores

**Forex:**
- 7 major USD pairs (EUR, GBP, JPY, AUD, CAD, CHF, NZD)
- Technical analysis signals
- Entry/exit points
- Risk/reward ratios

**Binary Options:**
- 60-second predictions
- Win probability estimates
- Payout ratios
- Market momentum

### 📈 System Stats
- Paper trades executed
- Win rate & PnL
- Portfolio value ($100k starting capital)
- API connection status
- Active positions

---

## 🛠️ Troubleshooting

### "Python is not recognized"
```
Solution: Reinstall Python, CHECK "Add Python to PATH"
Download: https://www.python.org/downloads/
```

### Port 8080 already in use
```batch
netstat -ano | findstr :8080
taskkill /PID <PID> /F
```

### Module not found
```batch
venv\Scripts\activate
pip install -r requirements.txt
```

### Virtual environment issues
```batch
rmdir /s /q venv
install_and_run.bat
```

---

## 💡 Pro Tips

### Run in Background
```batch
start /B launch_production.bat
```

### Auto-Start on Windows Boot
1. Press `Win + R`
2. Type: `shell:startup`
3. Create shortcut to `launch_production.bat`

### View Logs
```batch
notepad logs\realtime_production.log
```

### Update from GitHub
```batch
git pull origin main
pip install -r requirements.txt --upgrade
```

---

## 📁 File Structure

```
C:\TrifectaOmni\
│
├── 📜 install_and_run.bat          ⭐ MAIN (USE THIS FIRST!)
├── 📜 quick_start_demo.bat         🚀 Quick demo
├── 📜 launch_production.bat        🔥 Production
├── 📜 setup_environment.bat        🔧 Setup only
├── 📜 run_tests.bat                🧪 Tests
│
├── 📄 WINDOWS_QUICKSTART.md        📖 Complete guide
├── 📄 .env                          🔑 Your API credentials
├── 📄 .env.example                  📋 Configuration template
│
├── 🐍 realtime_multi_asset_demo.py              (Demo scanner)
├── 🐍 realtime_multi_asset_demo_production.py   (Production scanner)
│
├── 📁 omni_trifecta/               Core system
├── 📁 dashboard/                   Web UI
├── 📁 logs/                        Log files
└── 📁 venv/                        Python environment (auto-created)
```

---

## ✅ Quick Checklist

- [ ] Windows 10/11
- [ ] Python 3.8+ installed (with PATH)
- [ ] Downloaded TrifectaOmni to local drive
- [ ] Double-clicked `install_and_run.bat`
- [ ] Chose Demo or Production mode
- [ ] Dashboard opened at http://localhost:8080
- [ ] Seeing live opportunities! 🎉

---

## 🎯 System Features

**All 3 Execution Engines Active:**
1. **ARBITRAGE Engine** - Cross-exchange, cross-chain, triangular
2. **FOREX Engine** - Technical analysis, MT5 integration
3. **BINARY Engine** - Ultra-short momentum analysis

**Integrated Components:**
- Order Management System (OMS)
- Risk Manager
- Master Decision Governor
- RL Agents (Arbitrage + Forex)
- AI Predictors (LSTM + Transformer)
- Fibonacci Resonance Engine
- Paper Trading System ($100k capital)

**Multi-Chain Support:**
- 8 blockchain networks
- 30+ DEX routers
- 50+ token mappings
- Bridge detection
- MEV protection

---

## 🚀 You're All Set!

**To start right now:**

1. Open folder where you downloaded TrifectaOmni
2. Double-click: **install_and_run.bat**
3. Press **1** for Demo Mode
4. Watch dashboard at **http://localhost:8080**

**Need production features?**
- Edit `.env` with your API credentials
- Run `launch_production.bat`

---

## 📞 Support

**Documentation:**
- `WINDOWS_QUICKSTART.md` - Complete Windows guide
- `PRODUCTION_API_SETUP.md` - API configuration
- `DATA_SOURCES_COMPARISON.md` - Demo vs Production

**GitHub:**
- Issues: [github.com/OMNIWORLDLLC/TrifectaOmni/issues](https://github.com/OMNIWORLDLLC/TrifectaOmni/issues)
- Repository: [github.com/OMNIWORLDLLC/TrifectaOmni](https://github.com/OMNIWORLDLLC/TrifectaOmni)

---

**Status:** 🟢 **Windows Deployment Complete & Ready**

**Last Updated:** November 24, 2025

---

# 🎉 READY TO RUN ON YOUR LOCAL DRIVE!

Just **double-click** `install_and_run.bat` and you're live in 60 seconds! 🚀
