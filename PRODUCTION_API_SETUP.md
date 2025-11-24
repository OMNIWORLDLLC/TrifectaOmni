# 🚀 Production Real-Time Scanner - API Setup Guide

This guide explains how to configure **real API endpoints** for the production scanner instead of using delayed Yahoo Finance data.

---

## 📡 Available Data Sources

### 1️⃣ **MetaTrader 5 (MT5)** - Forex Real-Time Data
**Best for:** Spot Forex trading with institutional-grade data

**What you get:**
- Real-time bid/ask prices (millisecond updates)
- Full order book depth
- Historical tick data
- No delays, direct broker feed

**Setup:**
1. Open account with MT5-compatible broker (IC Markets, Pepperstone, etc.)
2. Download MT5 terminal: https://www.metatrader5.com/
3. Get your login credentials (Login, Server, Password)
4. Add to `.env`:
```bash
MT5_LOGIN=12345678
MT5_SERVER=ICMarkets-Demo
MT5_PASSWORD=your_password
```

**Cost:** Free with broker account (demo or live)

---

### 2️⃣ **CCXT** - Cryptocurrency Exchange Data
**Best for:** Cross-exchange arbitrage with 100+ exchanges

**What you get:**
- Real-time prices from Binance, Kraken, Coinbase, etc.
- Unified API across all exchanges
- Order book depth, trade history
- WebSocket streaming support

**Setup:**
1. Install CCXT:
```bash
pip install ccxt
```

2. No API keys needed for public market data!
3. For trading, add exchange API keys to `.env`:
```bash
BINANCE_API_KEY=your_key
BINANCE_SECRET=your_secret
```

**Cost:** Free for market data, trading requires exchange account

---

### 3️⃣ **DEX/Blockchain RPC** - On-Chain Arbitrage
**Best for:** Cross-chain and DEX arbitrage

**What you get:**
- Real-time on-chain prices
- DEX liquidity pool data
- Gas price estimates
- MEV opportunities

**Setup:**
1. Get RPC endpoint (Infura, Alchemy, QuickNode):
   - Infura: https://infura.io/
   - Alchemy: https://www.alchemy.com/
   - QuickNode: https://www.quicknode.com/

2. Add to `.env`:
```bash
DEX_RPC=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
DEX_PRIVKEY=your_wallet_private_key  # ⚠️ NEVER SHARE!
MEV_RELAY_URL=https://your-mev-relay
```

**Cost:** Free tier available (Infura: 100k req/day)

---

### 4️⃣ **Pocket Option API** - Binary Options Signals
**Best for:** 60-second binary options trading

**What you get:**
- Real-time binary signals
- Win probability estimates
- Payout ratios
- Market sentiment data

**Setup:**
1. Create Pocket Option account: https://po.trade/
2. Get API token from dashboard
3. Add to `.env`:
```bash
POCKET_TOKEN=your_api_token
POCKET_BASE_URL=https://api.po.trade
```

**Cost:** Requires funded account

---

## 🔧 Complete `.env` Configuration

Create a `.env` file in the project root:

```bash
# =============================================================================
# PRODUCTION API CONFIGURATION
# =============================================================================

# -------------------------
# MetaTrader 5 (Forex)
# -------------------------
MT5_LOGIN=your_mt5_login
MT5_SERVER=your_mt5_server
MT5_PASSWORD=your_mt5_password

# -------------------------
# Binary Options Platform
# -------------------------
POCKET_TOKEN=your_pocket_token
POCKET_BASE_URL=https://api.po.trade

# -------------------------
# DEX/Blockchain
# -------------------------
DEX_RPC=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
DEX_PRIVKEY=your_private_key  # ⚠️ Keep secure!
MEV_RELAY_URL=https://your-mev-relay

# -------------------------
# Exchange API Keys (Optional - for trading)
# -------------------------
BINANCE_API_KEY=your_binance_key
BINANCE_SECRET=your_binance_secret

KRAKEN_API_KEY=your_kraken_key
KRAKEN_SECRET=your_kraken_secret

# -------------------------
# System Configuration
# -------------------------
OMNI_LOG_DIR=runtime/logs
SEQ_MODEL_ONNX=models/sequence_model.onnx

# -------------------------
# Safety Limits
# -------------------------
MAX_DAILY_LOSS=100.0
MAX_DAILY_TRADES=50
MAX_LOSS_STREAK=5
```

---

## 🚀 Running Production Scanner

### Option 1: YFinance Demo (Free, Delayed)
```bash
python realtime_multi_asset_demo.py
```
- Uses Yahoo Finance (free)
- ~60 second delay
- Good for testing/learning
- No API keys required

### Option 2: Production Scanner (Real-Time)
```bash
python realtime_multi_asset_demo_production.py
```
- Uses configured APIs from `.env`
- Real-time data (<1s latency)
- Production-grade reliability
- Requires API configuration

---

## 📊 Data Comparison

| Feature | YFinance (Demo) | Production APIs |
|---------|----------------|-----------------|
| **Latency** | ~60 seconds | <1 second |
| **Forex Data** | Limited pairs | All MT5 pairs |
| **Crypto Exchanges** | 1 (aggregated) | 100+ via CCXT |
| **Binary Options** | Simulated | Real signals |
| **Cost** | Free | Free-Paid |
| **Reliability** | Good | Excellent |
| **Rate Limits** | 2000 req/hour | Varies by provider |

---

## 🎯 Recommended Setup for Each Use Case

### 📚 **Learning/Testing**
```bash
# Use demo scanner - no configuration needed
python realtime_multi_asset_demo.py
```

### 💹 **Forex Trading Focus**
```bash
# Configure MT5 only
MT5_LOGIN=xxx
MT5_SERVER=xxx
MT5_PASSWORD=xxx

python realtime_multi_asset_demo_production.py
```

### 🪙 **Crypto Arbitrage Focus**
```bash
# Install CCXT (no keys needed for market data)
pip install ccxt

python realtime_multi_asset_demo_production.py
```

### ⚡ **Binary Options Focus**
```bash
# Configure Pocket Option
POCKET_TOKEN=xxx

python realtime_multi_asset_demo_production.py
```

### 🔥 **Full System (All Assets)**
```bash
# Configure all APIs
MT5_LOGIN=xxx
MT5_SERVER=xxx
MT5_PASSWORD=xxx
POCKET_TOKEN=xxx
DEX_RPC=xxx

pip install ccxt

python realtime_multi_asset_demo_production.py
```

---

## 🔐 Security Best Practices

### ⚠️ **NEVER:**
- Commit `.env` to Git
- Share private keys publicly
- Use production keys in testing
- Store keys in code

### ✅ **ALWAYS:**
- Use `.env.example` for templates
- Add `.env` to `.gitignore`
- Use demo/testnet for testing
- Rotate keys regularly
- Use environment variables in production

---

## 🧪 Testing Your Configuration

After setting up your `.env`, test each component:

```bash
# Test MT5 connection
python -c "
import MetaTrader5 as MT5
import os
from dotenv import load_dotenv

load_dotenv()
MT5.initialize(
    login=int(os.getenv('MT5_LOGIN')),
    server=os.getenv('MT5_SERVER'),
    password=os.getenv('MT5_PASSWORD')
)
print('MT5:', 'Connected' if MT5.terminal_info() else 'Failed')
MT5.shutdown()
"

# Test CCXT
python -c "
import ccxt
exchange = ccxt.binance()
ticker = exchange.fetch_ticker('BTC/USDT')
print('CCXT:', 'Working' if ticker else 'Failed')
"

# Test DEX RPC
python -c "
from web3 import Web3
import os
from dotenv import load_dotenv

load_dotenv()
w3 = Web3(Web3.HTTPProvider(os.getenv('DEX_RPC')))
print('DEX RPC:', 'Connected' if w3.is_connected() else 'Failed')
"
```

---

## 📈 Performance Metrics

**Demo Scanner (YFinance):**
- Update frequency: 30-60 seconds
- API calls: ~100/hour
- Cost: $0

**Production Scanner (Real APIs):**
- Update frequency: <1 second
- API calls: ~1000+/hour
- Cost: $0-50/month (depends on tier)

---

## 🆘 Troubleshooting

### MT5 Connection Failed
- Verify credentials in `.env`
- Check MT5 terminal is installed
- Ensure broker allows API access
- Try demo account first

### CCXT Errors
- Install: `pip install ccxt`
- Check exchange is supported: `ccxt.exchanges`
- Verify symbol format: `BTC/USDT` not `BTCUSDT`

### RPC Connection Issues
- Test RPC URL in browser
- Check API key/project ID
- Verify network (mainnet vs testnet)
- Check request limits

### Rate Limiting
- Add delays between requests
- Use WebSocket instead of REST
- Upgrade to higher API tier
- Implement request caching

---

## 📞 Support Resources

- **MT5 Documentation:** https://www.mql5.com/en/docs
- **CCXT Manual:** https://docs.ccxt.com/
- **Infura Docs:** https://docs.infura.io/
- **Alchemy Docs:** https://docs.alchemy.com/
- **Pocket Option:** https://po.trade/help

---

## ✅ Quick Start Checklist

- [ ] Copy `.env.example` to `.env`
- [ ] Configure at least one data source (MT5, CCXT, DEX, or Pocket)
- [ ] Install required packages (`pip install ccxt python-dotenv aiohttp`)
- [ ] Test configuration with test scripts above
- [ ] Run production scanner: `python realtime_multi_asset_demo_production.py`
- [ ] Open dashboard: http://localhost:8080
- [ ] Verify "API CONNECTION STATUS" shows green checkmarks

---

**Status:** 🟢 Production-ready with real API integration

**Last Updated:** November 24, 2025
