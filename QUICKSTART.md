# TrifectaOmni - Quick Start

[![Status](https://img.shields.io/badge/Status-Ready%20to%20Run-brightgreen)](STATUS.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](requirements.txt)

## 🎯 Repository Status: ✅ READY TO RUN

This repository is **fully functional** and **ready for immediate use**. All components are implemented, tested, and documented.

---

## 🚀 Fastest Start (3 Commands)

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

## 📦 Installation Methods

### Method 1: Quick Test (Recommended First)

Perfect for testing the system immediately:

```bash
git clone https://github.com/OMNIWORLDLLC/TrifectaOmni.git
cd TrifectaOmni
pip install -r requirements.txt
python examples/shadow_mode_example.py
```

**No configuration needed!** Shadow mode works out of the box.

### Method 2: One-Click Installation

```bash
# Clone the repository
git clone https://github.com/OMNIWORLDLLC/TrifectaOmni.git
cd TrifectaOmni

# Test prerequisites (optional but recommended)
bash scripts/test-install.sh

# One-click installation with shadow mode testing
./full-system-install.sh
```

This will automatically:
1. Install all dependencies and create virtual environment
2. Build and compile the system
3. Wire up configuration and validate connectivity
4. Deploy in shadow mode for testing

## Manual Installation

If you prefer to install manually:

```bash
# Clone the repository
git clone https://github.com/OMNIWORLDLLC/TrifectaOmni.git
cd TrifectaOmni

# Install dependencies
pip install -r requirements.txt
```

## Run Shadow Mode Example

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
