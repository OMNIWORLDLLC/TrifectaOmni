# TrifectaOmni - Quick Start

## Installation

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
