# TrifectaOmni Installation & Deployment Scripts

This directory contains the complete automation scripts for TrifectaOmni system operations.

## Quick Start

### One-Command Full System Setup

For a complete end-to-end setup and deployment:

```bash
# From project root
./full-system-install.sh
```

This will automatically:
1. Install all dependencies
2. Build the system
3. Configure and wire everything
4. Deploy in shadow mode for testing

### Deployment Modes

```bash
# Shadow mode (testing, no real trades)
./full-system-install.sh shadow

# Production mode (real trading)
./full-system-install.sh production

# Service installation (systemd)
./full-system-install.sh service
```

## Individual Scripts

If you need to run phases individually:

### 1. Install (`install.sh`)

Sets up the complete environment:

```bash
bash scripts/install.sh
```

**What it does:**
- Checks Python prerequisites (Python 3.8+)
- Creates Python virtual environment
- Installs all dependencies from requirements.txt
- Creates necessary directory structure
- Sets up .env configuration file
- Creates activation helper script
- Verifies all imports

**Output:**
- Virtual environment at `venv/`
- Configuration file at `.env`
- Activation script at `activate.sh`

### 2. Build (`build.sh`)

Validates and prepares the system:

```bash
bash scripts/build.sh
```

**What it does:**
- Validates virtual environment
- Verifies Python modules
- Compiles Python bytecode
- Validates package structure
- Runs pre-flight system checks

**Requirements:**
- Must run after `install.sh`
- Virtual environment must exist

### 3. Wire (`wire.sh`)

Configures and tests connectivity:

```bash
bash scripts/wire.sh
```

**What it does:**
- Tests configuration loading
- Runs deployment checklist
- Validates API connectivity (if configured)
- Tests core module imports
- Verifies system readiness

**Output:**
- Configuration validation report
- Connectivity status for:
  - MT5 connection
  - Binary options API
  - DEX/Blockchain RPC
  - Logging system

### 4. Deploy (`deploy.sh`)

Deploys the system in specified mode:

```bash
# Shadow mode (recommended for testing)
bash scripts/deploy.sh shadow

# Production mode (real trading)
bash scripts/deploy.sh production

# Service installation
bash scripts/deploy.sh service
```

**Modes:**

**Shadow Mode:**
- Simulated trading
- No real money at risk
- Full system testing
- Performance metrics
- Log generation

**Production Mode:**
- Real trading with real money
- Requires configured .env
- Safety manager active
- Real-time execution

**Service Mode:**
- Creates systemd service configuration
- Enables automatic startup
- Log rotation
- Crash recovery

### 5. Test Install (`test-install.sh`)

Comprehensive test suite for validating the one-click installation process:

```bash
bash scripts/test-install.sh
```

**What it tests:**
1. Script existence and executability
2. Help message display
3. Prerequisite scripts presence
4. Python version compatibility (>=3.8)
5. requirements.txt validity
6. .env.example template
7. Package structure integrity
8. Example files presence
9. Documentation files
10. Script mode validation
11. Existing installation functionality
12. Script phases structure (4 phases)
13. Error handling mechanisms
14. Logging functions
15. Production mode safety confirmations

**When to use:**
- Before running the full installation
- After making changes to installation scripts
- As part of CI/CD validation
- To troubleshoot installation issues

**Expected Output:**
- Test summary showing passed/failed tests
- Detailed results for each test
- Pass/fail verdict with guidance

## Full System Workflow

### First Time Setup

```bash
# 1. Clone the repository (if not already done)
git clone https://github.com/OMNIWORLDLLC/TrifectaOmni.git
cd TrifectaOmni

# 2. Run full system install (shadow mode)
./full-system-install.sh shadow

# 3. Review the results
ls -la runtime/logs/
```

### Testing Configuration

```bash
# Test with shadow mode
./full-system-install.sh shadow

# Review logs
tail -f runtime/logs/trades.jsonl
```

### Production Deployment

```bash
# 1. Edit configuration
nano .env

# 2. Run wire script to validate
bash scripts/wire.sh

# 3. Deploy to production
./full-system-install.sh production
```

### Service Installation

```bash
# 1. Complete setup and testing
./full-system-install.sh shadow

# 2. Install as service
./full-system-install.sh service

# 3. Follow the displayed commands to enable service
sudo cp /tmp/trifecta-omni.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trifecta-omni
sudo systemctl start trifecta-omni

# 4. Monitor service
sudo systemctl status trifecta-omni
journalctl -u trifecta-omni -f
```

## Manual Environment Activation

If you need to activate the environment manually:

```bash
# Activate virtual environment
source activate.sh

# Or directly
source venv/bin/activate
export PYTHONPATH="${PWD}:${PYTHONPATH}"
```

## Directory Structure Created

After running the installation, you'll have:

```
TrifectaOmni/
├── venv/                    # Python virtual environment
├── runtime/
│   └── logs/               # System logs
│       ├── ticks.jsonl     # Price tick data
│       ├── trades.jsonl    # Trade history
│       └── rl_state/       # RL state persistence
├── models/                 # ONNX models directory
├── data/
│   └── cache/             # Data cache
├── backups/               # System backups
├── .env                   # Configuration (from .env.example)
└── activate.sh           # Environment activation script
```

## Troubleshooting

### Pre-Installation Validation

Before installation, run the test suite to identify potential issues:

```bash
# Run comprehensive tests
bash scripts/test-install.sh

# If all tests pass, proceed with installation
./full-system-install.sh shadow
```

### Installation Issues

**Problem:** Unsure if system is ready for installation
```bash
# Run test suite to validate prerequisites
bash scripts/test-install.sh
```

**Problem:** Python version too old
```bash
# Check Python version
python3 --version

# Must be Python 3.8 or higher
# Update Python if needed
```

**Problem:** pip install fails
```bash
# Update pip
python3 -m pip install --upgrade pip

# Retry installation
bash scripts/install.sh
```

### Build Issues

**Problem:** Module not found
```bash
# Activate environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Wire/Configuration Issues

**Problem:** Configuration not valid
```bash
# Check .env file
cat .env

# Copy from example if needed
cp .env.example .env
nano .env
```

**Problem:** API connectivity failed
- For testing: Use shadow mode (doesn't require API credentials)
- For production: Verify credentials in .env file

### Deployment Issues

**Problem:** Production deployment blocked
- Ensure .env is configured with valid credentials
- Run `bash scripts/wire.sh` to verify configuration
- Use shadow mode for testing first

## Script Options

### Environment Variables

You can set these before running scripts:

```bash
# Custom virtual environment location
export VENV_DIR="/path/to/custom/venv"

# Non-interactive mode (use defaults)
export TRIFECTA_AUTO=1

# Run scripts
./full-system-install.sh
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Deploy TrifectaOmni

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Test installation prerequisites
        run: bash scripts/test-install.sh
      - name: Run full system install
        run: ./full-system-install.sh shadow
```

### Pre-Deployment Testing

Always test before deploying:

```bash
# 1. Run test suite
bash scripts/test-install.sh

# 2. If tests pass, run shadow mode
./full-system-install.sh shadow

# 3. Review results before production
tail -f runtime/logs/trades.jsonl
```

## Security Notes

- Never commit `.env` file to version control
- Keep API credentials secure
- Use shadow mode for testing
- Review all configurations before production deployment
- Monitor logs for suspicious activity

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review main documentation: `../SETUP.md`
3. Check examples: `../examples/`
4. Open an issue on GitHub

## License

See LICENSE file in project root.
