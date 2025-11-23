# TrifectaOmni - Setup and Usage Guide

## Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/OMNIWORLDLLC/TrifectaOmni.git
cd TrifectaOmni
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your credentials and settings
```

### Running the System

#### Shadow Mode (Recommended for Testing)

Run the system in shadow mode with simulated trades:

```bash
python examples/shadow_mode_example.py
```

This will:
- Generate synthetic price data
- Run the full trading system without real trades
- Output performance metrics and statistics
- Save logs to `runtime/logs/`

#### Live Mode

**⚠️ WARNING: Only use live mode after thorough testing in shadow mode!**

See the architecture documentation in README.md for details on configuring live trading with:
- MetaTrader 5 for spot forex
- Binary options platforms
- DEX/blockchain for arbitrage

## Architecture Overview

The Omni-Trifecta Quant Engine consists of 9 layers:

1. **Layer 0-1**: Configuration & Data Ingestion
2. **Layer 2-3**: Feature Extraction & Predictive Models
3. **Layer 4**: Fibonacci & Harmonic Intelligence
4. **Layer 5**: Regime Switching & Decision Making
5. **Layer 6**: Execution Engines
6. **Layer 7**: Safety & Risk Management
7. **Layer 8**: Learning & Evolution
8. **Layer 9**: Runtime & Logging

## Key Components

### MasterGovernorX100
The main decision-making brain that coordinates:
- Sequence models for prediction
- Regime switching RL for engine selection
- Fibonacci intelligence for market analysis
- Engine-specific modifiers (ladder risk, TP rotation, route selection)

### Execution Modes

**Binary Options**: Short-duration directional trades with adaptive position sizing

**Spot Forex**: Trend-following trades with Fibonacci-based TP/SL levels

**Arbitrage**: DEX/flashloan opportunities timed by volatility analysis

### Safety Manager

Enforces:
- Maximum daily loss limits
- Maximum trade count limits
- Loss streak protection
- Automatic cooldown periods

## Project Structure

```
TrifectaOmni/
├── omni_trifecta/          # Main package
│   ├── core/               # Configuration
│   ├── data/               # Price feeds
│   ├── prediction/         # Sequence models
│   ├── fibonacci/          # Fibonacci intelligence
│   ├── decision/           # Decision making & RL
│   ├── execution/          # Trade executors
│   ├── safety/             # Risk management
│   ├── learning/           # Persistence & training
│   ├── runtime/            # Main loop & logging
│   └── utils/              # Technical indicators
├── examples/               # Usage examples
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # Architecture documentation
```

## Configuration

Edit `.env` with your settings:

### MT5 Configuration
```
MT5_LOGIN=your_login
MT5_SERVER=your_server
MT5_PASSWORD=your_password
```

### Binary Options
```
POCKET_TOKEN=your_token
POCKET_BASE_URL=https://api.po.trade
```

### DEX/Blockchain
```
DEX_RPC=https://your-rpc
DEX_PRIVKEY=your_private_key
```

### Safety Limits
```
MAX_DAILY_LOSS=100.0
MAX_DAILY_TRADES=50
MAX_LOSS_STREAK=5
```

## Logs and Output

The system generates several log files in `runtime/logs/`:

- `ticks.jsonl`: All price ticks
- `trades.jsonl`: All trade executions
- `events.jsonl`: System events
- `decision_audit.jsonl`: Complete decision trail
- `performance.jsonl`: Performance metrics

## Development

### Adding a New Feature

1. Identify the appropriate layer (see architecture in README.md)
2. Implement the component following existing patterns
3. Test in shadow mode
4. Update this guide

### Testing

Run the shadow mode example to test changes:

```bash
python examples/shadow_mode_example.py
```

### Monitoring

Monitor system performance via:
- Log files in `runtime/logs/`
- Performance summary at end of session
- Real-time console output during execution

## Advanced Usage

### Custom ONNX Models

1. Train your sequence model
2. Export to ONNX format
3. Update `.env` with model path:
   ```
   SEQ_MODEL_ONNX=models/my_model.onnx
   ```
4. The system will automatically use your model

### RL Training

The system continuously learns via:
- Regime switching RL (engine selection)
- Arbitrage route scoring
- Automatic persistence between sessions

State is saved to `runtime/logs/rl_state/`:
- `regime_rl.json`: Regime Q-table
- `arb_routes.json`: Route scores

## Safety First

- Always start with shadow mode
- Test extensively before live trading
- Monitor safety manager status
- Never disable safety limits in production
- Keep adequate capital reserves

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Review architecture documentation in README.md
- Check example scripts in `examples/`

## License

See LICENSE file for details.

---

**Disclaimer**: This is a sophisticated trading system. Use at your own risk. Past performance does not guarantee future results. Always test thoroughly in shadow mode before live trading.
