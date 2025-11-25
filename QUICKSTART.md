# TrifectaOmni - Quick Start

[![Status](https://img.shields.io/badge/Status-Ready%20to%20Run-brightgreen)](STATUS.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](requirements.txt)

## 🎯 Repository Status: ✅ READY TO RUN

This repository is **fully functional** and **ready for immediate use**. All components are implemented, tested, and documented.

---

## 🚀 ONE-CLICK FULL SYSTEM INSTALLATION

**The absolute fastest way to get everything running:**

```bash
git clone https://github.com/OMNIWORLDLLC/TrifectaOmni.git
cd TrifectaOmni
./full-system-install.sh
```

**That's it!** This single command will:
- ✅ Install all dependencies and create virtual environment
- ✅ Build and compile the entire system
- ✅ Wire up configuration and validate connectivity
- ✅ Deploy and run in shadow mode with live testing

**Expected output:** Complete system setup in ~2-3 minutes, followed by successful shadow mode trading demonstration.

---

## 🎯 Alternative Quick Start Methods

### Method 1: Super Quick Test (3 Commands)

Test the system immediately without any configuration:

```bash
git clone https://github.com/OMNIWORLDLLC/TrifectaOmni.git
cd TrifectaOmni
pip install -r requirements.txt && python examples/shadow_mode_example.py
```

**Expected output:** The system will run successfully, showing trading decisions and performance metrics.

---

## ✅ Verify Installation

After cloning, verify everything is ready:

```bash
python verify_installation.py
```

This will check:
- ✓ Python version
- ✓ Required packages
- ✓ Module imports
- ✓ Directory structure
- ✓ Configuration files
- ✓ Example scripts

---

### Method 2: Verify Installation

After cloning, verify everything is ready:

```bash
python verify_installation.py
```

This will check:
- ✓ Python version
- ✓ Required packages
- ✓ Module imports
- ✓ Directory structure
- ✓ Configuration files
- ✓ Example scripts

---

## 📦 Full System Installation Modes

The `full-system-install.sh` script supports multiple deployment modes:

### Shadow Mode (Default - Recommended)
```bash
./full-system-install.sh shadow
# or just
./full-system-install.sh
```
**Best for:** Testing and learning the system without any risk

### Production Mode
```bash
./full-system-install.sh production
```
**Best for:** Live trading with real money (requires API credentials in .env)

### Service Mode
```bash
./full-system-install.sh service
```
**Best for:** Installing as a systemd service for 24/7 operation

---

## 🔧 Manual Installation

## 🔧 Manual Installation

If you prefer step-by-step installation:

```bash
# 1. Clone the repository
git clone https://github.com/OMNIWORLDLLC/TrifectaOmni.git
cd TrifectaOmni

# 2. Install dependencies
bash scripts/install.sh

# 3. Build the system
bash scripts/build.sh

# 4. Wire configuration
bash scripts/wire.sh

# 5. Deploy
bash scripts/deploy.sh shadow
```

---

## 📊 What Happens During Installation

### Phase 1: Installation (60-90 seconds)
- Creates Python virtual environment
- Installs all required packages (numpy, pandas, scikit-learn, onnxruntime, web3, etc.)
- Creates directory structure (runtime/logs, models, data, backups)
- Sets up environment configuration from .env.example
- Verifies all imports work correctly

### Phase 2: Build (10-15 seconds)
- Compiles Python bytecode for faster execution
- Validates package structure
- Runs pre-flight system checks
- Verifies all 10 core modules are ready

### Phase 3: Wire & Configuration (5-10 seconds)
- Validates configuration loading
- Tests all component imports
- Runs deployment checklist
- Confirms system readiness

### Phase 4: Deployment (30-60 seconds)
- Launches the system in selected mode
- Runs shadow trading simulation (default)
- Generates performance metrics
- Saves complete logs

**Total Time: ~2-3 minutes for complete system setup**

---

## 🎮 Using the System

### Run Shadow Mode Example

Test the system with simulated trading:

```bash
python examples/shadow_mode_example.py
```

This will:
- Generate 500 synthetic price ticks
- Run the complete trading system
- Output performance metrics
- Save logs to `runtime/logs/`

## Documentation

- **SETUP.md** - Complete setup and usage guide
- **README.md** - Full architecture documentation
- **.env.example** - Configuration template

## Key Features

✅ **Multi-Engine Trading**: Binary Options, Spot Forex, Arbitrage  
✅ **Fibonacci Intelligence**: ML-based clustering + Elliott Wave analysis  
✅ **Regime Switching**: Q-learning for optimal engine selection  
✅ **Safety Management**: Risk limits, cooldowns, emergency shutdown  
✅ **RL Learning**: Continuous improvement via reinforcement learning  
✅ **Shadow Mode**: Risk-free testing and validation  

## Architecture

9-Layer system:
1. Configuration & Data Ingestion
2. Feature Extraction
3. Predictive Models (ONNX support)
4. Fibonacci & Harmonic Intelligence
5. Decision Making (Regime Switching RL)
6. Execution Engines
7. Safety & Risk Management
8. Learning & Evolution
9. Runtime & Logging

## Support

See SETUP.md for detailed documentation and troubleshooting.
