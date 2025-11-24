# 📚 Quick Installation Reference

## 🚀 Installation Commands

### One-Click Full Installation
```bash
git clone https://github.com/OMNIWORLDLLC/TrifectaOmni.git && cd TrifectaOmni && ./full-system-install.sh
```

### Mode-Specific Installation
```bash
# Shadow mode (testing, default)
./full-system-install.sh shadow

# Production mode (live trading)
./full-system-install.sh production

# Service mode (systemd service)
./full-system-install.sh service
```

### Quick Test (Minimal)
```bash
git clone https://github.com/OMNIWORLDLLC/TrifectaOmni.git
cd TrifectaOmni
pip install -r requirements.txt
python examples/shadow_mode_example.py
```

---

## 📊 Installation Phases

| Phase | Duration | What Happens |
|-------|----------|--------------|
| **1. Installation** | 60-90s | Dependencies, venv, packages |
| **2. Build** | 10-15s | Compilation, validation |
| **3. Wire** | 5-10s | Configuration, connectivity |
| **4. Deploy** | 30-60s | System launch and demo |
| **Total** | **~2-3 min** | **Complete working system** |

---

## 🎯 After Installation

### Activate Environment
```bash
source activate.sh
```

### Run Examples
```bash
# Shadow mode (no risk)
python examples/shadow_mode_example.py

# Production ready (requires .env config)
python examples/production_ready_example.py

# Advanced integration
python examples/advanced_integration_example.py
```

### Check Logs
```bash
# View trade history
cat runtime/logs/trades.jsonl

# View price ticks
cat runtime/logs/ticks.jsonl

# View system events
cat runtime/logs/events.jsonl
```

### Verify Installation
```bash
python verify_installation.py
```

---

## 📁 Project Structure

```
TrifectaOmni/
├── 📂 omni_trifecta/        Main package (10 modules)
├── 📂 examples/             Usage examples (3 files)
├── 📂 scripts/              Installation scripts (4 scripts)
├── 📂 runtime/logs/         System logs
├── 📂 models/               ML models (ONNX)
├── 📂 venv/                 Virtual environment
├── 🔧 full-system-install.sh One-click installer
├── 📄 requirements.txt      Python dependencies
├── 📄 .env                  Configuration (auto-generated)
└── 📚 Documentation         README, QUICKSTART, SETUP, etc.
```

---

## 🛠️ Component Scripts

| Script | Purpose |
|--------|---------|
| `scripts/install.sh` | Install dependencies + venv |
| `scripts/build.sh` | Build and compile system |
| `scripts/wire.sh` | Configure and validate |
| `scripts/deploy.sh` | Deploy in selected mode |
| `full-system-install.sh` | **Orchestrates all of above** |

---

## 🔧 Configuration Files

| File | Purpose | Required? |
|------|---------|-----------|
| `.env` | API credentials & settings | For production |
| `.env.example` | Template for .env | Reference |
| `requirements.txt` | Python dependencies | Yes |

---

## 📖 Documentation Files

| File | Description |
|------|-------------|
| **ONE-CLICK-INSTALL.md** | Complete one-click guide |
| **QUICKSTART.md** | Quick start instructions |
| **SETUP.md** | Detailed configuration |
| **README.md** | Full architecture docs |
| **STATUS.md** | System readiness status |
| **INSTALL-REFERENCE.md** | This quick reference |

---

## ⚡ Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Permission denied | `chmod +x full-system-install.sh` |
| Python not found | Install Python 3.10+ |
| Package errors | `pip install --upgrade pip` |
| Import errors | `source activate.sh` |

---

## 🎮 Deployment Modes

### Shadow Mode (Default)
- ✅ No API credentials needed
- ✅ Simulated trading
- ✅ Zero risk
- ✅ Perfect for testing

### Production Mode
- ⚠️ Requires API credentials in .env
- ⚠️ Real trading with real money
- ⚠️ Use after thorough testing
- ⚠️ Safety manager always active

### Service Mode
- 🔧 Creates systemd service
- 🔧 For 24/7 operation
- 🔧 VPS/server deployment
- 🔧 Provides install commands

---

## 🚀 Next Steps

1. **Test**: Run shadow mode
2. **Configure**: Edit .env with credentials
3. **Validate**: Test with minimal capital
4. **Scale**: Gradually increase position sizes
5. **Monitor**: Watch logs and performance

---

## 📞 Support

- **Documentation**: See all .md files in root
- **Examples**: Check examples/ directory
- **Logs**: Review runtime/logs/ for details
- **Issues**: Open GitHub issue for bugs

---

**Quick Links:**
- [ONE-CLICK-INSTALL.md](ONE-CLICK-INSTALL.md) - Detailed installation guide
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [SETUP.md](SETUP.md) - Full setup documentation
- [README.md](README.md) - Architecture overview
