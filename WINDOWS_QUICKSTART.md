# 🪟 TrifectaOmni - Windows Quick Start Guide

Complete one-click installation and launch system for Windows.

---

## 🚀 Ultra-Quick Start (30 Seconds)

**Just double-click:**
```
install_and_run.bat
```

That's it! Choose Demo or Production mode when prompted.

---

## 📦 What You Get

Five Windows batch files for complete control:

### 1️⃣ **install_and_run.bat** - All-in-One Installer ⭐ RECOMMENDED
```batch
install_and_run.bat
```
**Does everything:**
- ✅ Checks Python installation
- ✅ Creates virtual environment
- ✅ Installs all dependencies
- ✅ Sets up directory structure
- ✅ Creates configuration files
- ✅ Launches scanner (your choice: Demo or Production)

**First time?** Use this one!

---

### 2️⃣ **quick_start_demo.bat** - Instant Demo (No Config)
```batch
quick_start_demo.bat
```
**Perfect for:**
- Testing the system
- Learning how it works
- No API keys required
- Uses free Yahoo Finance data

**Ready in:** 10 seconds

---

### 3️⃣ **launch_production.bat** - Real-Time Production
```batch
launch_production.bat
```
**For serious trading:**
- Uses your real API endpoints
- Sub-second data latency
- Full production features
- Requires `.env` configuration

---

### 4️⃣ **setup_environment.bat** - Setup Only (No Launch)
```batch
setup_environment.bat
```
**Use when:**
- You want to prepare environment first
- You'll launch manually later
- You need to edit config before running

---

### 5️⃣ **run_tests.bat** - Verify Everything Works
```batch
run_tests.bat
```
**Test suites:**
- Demo setup verification
- Arbitrage calculations
- Token equivalence mapping
- Full system validation

---

## 📋 Prerequisites

### Required:
- **Windows 10/11**
- **Python 3.8+** - Download from [python.org](https://www.python.org/downloads/)
  - ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation!

### Optional:
- **Git** - For easy updates ([git-scm.com](https://git-scm.com/download/win))
- **Visual Studio Code** - Best editor ([code.visualstudio.com](https://code.visualstudio.com/))

---

## 🎯 Step-by-Step First Run

### Option A: Complete Beginner (Recommended)

1. **Download the project:**
   - Click green "Code" button on GitHub
   - Download ZIP
   - Extract to `C:\TrifectaOmni`

2. **Double-click:**
   ```
   install_and_run.bat
   ```

3. **Choose Demo Mode** when prompted (press `1`)

4. **Open browser:**
   ```
   http://localhost:8080
   ```

**Done!** 🎉

---

### Option B: Advanced User (Production APIs)

1. **Clone repository:**
   ```bash
   git clone https://github.com/OMNIWORLDLLC/TrifectaOmni.git
   cd TrifectaOmni
   ```

2. **Run installer:**
   ```batch
   install_and_run.bat
   ```

3. **Choose Production Mode** (press `2`)

4. **Edit `.env` file** with your API credentials:
   ```batch
   notepad .env
   ```
   
   Add your credentials:
   - MT5: Login, Server, Password (for forex)
   - DEX: RPC endpoint (for blockchain)
   - Pocket: API token (for binary options)
   - CCXT: No keys needed! (for crypto arbitrage)

5. **Run again:**
   ```batch
   launch_production.bat
   ```

6. **Dashboard:**
   ```
   http://localhost:8080
   ```

---

## 🔧 Configuration Guide

### Demo Mode (No Configuration)
**Just works!** No setup needed.
- Uses Yahoo Finance (free)
- ~60 second data delay
- Perfect for testing

### Production Mode (Real-Time)

**Create/Edit `.env` file:**

```bash
# Forex Real-Time (MetaTrader 5)
MT5_LOGIN=12345678
MT5_SERVER=ICMarkets-Demo
MT5_PASSWORD=your_password

# Crypto Arbitrage (CCXT - No keys needed!)
# Just install: pip install ccxt

# Blockchain/DEX
DEX_RPC=https://mainnet.infura.io/v3/YOUR_PROJECT_ID

# Binary Options
POCKET_TOKEN=your_api_token
POCKET_BASE_URL=https://api.po.trade
```

**Get API Credentials:**
- **MT5 (Forex):** Sign up with broker ([IC Markets](https://www.icmarkets.com/), [Pepperstone](https://pepperstone.com/))
- **Infura (Blockchain):** [infura.io](https://infura.io/) - 100k free requests/day
- **Pocket Option:** [po.trade](https://po.trade/)
- **CCXT (Crypto):** No keys needed for market data!

---

## 📊 What You'll See

Once running, open **http://localhost:8080** for:

### Real-Time Dashboard

**1. Arbitrage Opportunities**
- Cross-exchange crypto arbitrage
- Cross-chain token arbitrage
- Triangular arbitrage
- Expected profit calculations
- Risk scores

**2. Forex Trading Signals**
- 7 major USD pairs
- Technical analysis
- Entry/exit points
- Take profit / Stop loss
- Risk/reward ratios

**3. Binary Options**
- 60-second predictions
- Win probability
- Payout ratios
- Market momentum

**4. System Stats**
- Paper trades executed
- Win rate & PnL
- Portfolio value
- API connection status

---

## 🛠️ Troubleshooting

### "Python is not recognized"
**Solution:**
1. Reinstall Python from [python.org](https://www.python.org/downloads/)
2. ✅ Check "Add Python to PATH" during installation
3. Restart computer

### "pip is not recognized"
**Solution:**
```batch
python -m ensurepip --default-pip
python -m pip install --upgrade pip
```

### "Port 8080 already in use"
**Solution:**
```batch
# Find process using port 8080
netstat -ano | findstr :8080

# Kill process (replace PID with actual number)
taskkill /PID <PID> /F
```

### "Module not found"
**Solution:**
```batch
venv\Scripts\activate
pip install -r requirements.txt
```

### Virtual environment issues
**Solution:**
```batch
# Delete and recreate
rmdir /s /q venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## 🎮 Common Commands

### Start Demo
```batch
quick_start_demo.bat
```

### Start Production
```batch
launch_production.bat
```

### Run Tests
```batch
run_tests.bat
```

### Setup Only
```batch
setup_environment.bat
```

### Update from Git
```batch
git pull origin main
pip install -r requirements.txt --upgrade
```

### Manual Launch (Advanced)
```batch
venv\Scripts\activate
python realtime_multi_asset_demo.py          # Demo
python realtime_multi_asset_demo_production.py  # Production
```

---

## 📁 Directory Structure

```
TrifectaOmni/
│
├── 📜 install_and_run.bat          ← Main installer (USE THIS FIRST!)
├── 📜 quick_start_demo.bat         ← Quick demo launch
├── 📜 launch_production.bat        ← Production launch
├── 📜 setup_environment.bat        ← Setup only
├── 📜 run_tests.bat                ← Test suite
│
├── 📄 .env                          ← Your API credentials (create from .env.example)
├── 📄 .env.example                  ← Configuration template
├── 📄 requirements.txt              ← Python dependencies
│
├── 🐍 realtime_multi_asset_demo.py              ← Demo scanner
├── 🐍 realtime_multi_asset_demo_production.py   ← Production scanner
│
├── 📁 omni_trifecta/               ← Core system
│   ├── execution/                   ← Trading execution
│   ├── decision/                    ← AI decision making
│   ├── prediction/                  ← ML models
│   ├── safety/                      ← Risk management
│   └── fibonacci/                   ← Fibonacci engine
│
├── 📁 dashboard/                   ← Web UI
├── 📁 logs/                        ← Log files
└── 📁 venv/                        ← Python environment (auto-created)
```

---

## 💡 Pro Tips

### Background Mode
Run scanner in background:
```batch
start /B launch_production.bat
```

### Auto-Start on Boot
1. Press `Win + R`
2. Type: `shell:startup`
3. Create shortcut to `launch_production.bat`

### Multiple Instances
Run on different ports (edit script):
```python
# Change in script:
uvicorn.run(app, host="0.0.0.0", port=8081)  # or 8082, 8083...
```

### View Logs
```batch
# Real-time log viewing
powershell Get-Content logs\realtime_production.log -Wait -Tail 50
```

---

## 🔒 Security

### API Keys
- ✅ **NEVER** commit `.env` to Git
- ✅ `.env` is in `.gitignore` (safe)
- ✅ Use demo/testnet accounts for testing
- ✅ Rotate keys regularly

### Private Keys
- ⚠️ **NEVER** share `DEX_PRIVKEY`
- ⚠️ Use separate wallet for trading
- ⚠️ Start with small amounts

---

## 🆘 Getting Help

1. **Check logs:**
   ```batch
   notepad logs\realtime_production.log
   ```

2. **Run tests:**
   ```batch
   run_tests.bat
   ```

3. **Verify setup:**
   ```batch
   python test_demo_setup.py
   ```

4. **GitHub Issues:**
   [github.com/OMNIWORLDLLC/TrifectaOmni/issues](https://github.com/OMNIWORLDLLC/TrifectaOmni/issues)

---

## ✅ Quick Checklist

- [ ] Python 3.8+ installed (with PATH)
- [ ] Downloaded/cloned TrifectaOmni
- [ ] Run `install_and_run.bat`
- [ ] Choose Demo or Production mode
- [ ] Open http://localhost:8080
- [ ] See live opportunities!

---

## 🎯 What's Next?

**After successful launch:**

1. **Watch the dashboard** - See live opportunities
2. **Configure production APIs** - For real-time data
3. **Review paper trades** - Check execution results
4. **Customize settings** - Edit `.env` file
5. **Run tests** - Verify all components

---

**Ready?** Double-click `install_and_run.bat` and you're live in 60 seconds! 🚀

**Status:** 🟢 Windows-ready with one-click deployment

**Last Updated:** November 24, 2025
