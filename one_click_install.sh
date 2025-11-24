#!/bin/bash
###############################################################################
# TrifectaOmni - ONE CLICK INSTALLER
# Installs all dependencies, sets up environment, and prepares for live demo
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           TRIFECTA OMNI - ONE CLICK INSTALLER                ║
║                                                               ║
║     AI-Powered Trading System with Live Demo Capabilities    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Function to print status messages
print_status() {
    echo -e "${BLUE}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_warning "Please do not run as root. Run as regular user."
    exit 1
fi

# Detect OS
print_status "Detecting operating system..."
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
    print_success "Detected: $PRETTY_NAME"
else
    print_error "Cannot detect OS version"
    exit 1
fi

# Update system packages
print_status "Updating system packages..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update -qq
    print_success "System packages updated"
elif command -v yum &> /dev/null; then
    sudo yum update -y -q
    print_success "System packages updated"
fi

# Install system dependencies
print_status "Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get install -y -qq \
        python3 \
        python3-pip \
        python3-venv \
        python3-dev \
        build-essential \
        git \
        curl \
        wget \
        libssl-dev \
        libffi-dev \
        libhdf5-dev \
        libblas-dev \
        liblapack-dev \
        gfortran \
        pkg-config \
        redis-server \
        nodejs \
        npm \
        > /dev/null 2>&1
    print_success "System dependencies installed"
elif command -v yum &> /dev/null; then
    sudo yum install -y -q \
        python3 \
        python3-pip \
        python3-devel \
        gcc \
        gcc-c++ \
        make \
        git \
        curl \
        wget \
        openssl-devel \
        libffi-devel \
        hdf5-devel \
        blas-devel \
        lapack-devel \
        redis \
        nodejs \
        npm \
        > /dev/null 2>&1
    print_success "System dependencies installed"
fi

# Start Redis if not running
print_status "Starting Redis server..."
if command -v systemctl &> /dev/null; then
    sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis 2>/dev/null || true
    sudo systemctl enable redis-server 2>/dev/null || sudo systemctl enable redis 2>/dev/null || true
elif command -v service &> /dev/null; then
    sudo service redis-server start 2>/dev/null || sudo service redis start 2>/dev/null || true
fi
print_success "Redis server started"

# Create virtual environment
print_status "Creating Python virtual environment..."
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists. Removing..."
    rm -rf venv
fi
python3 -m venv venv
source venv/bin/activate
print_success "Virtual environment created and activated"

# Upgrade pip and essential tools
print_status "Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel --quiet
print_success "Pip and build tools upgraded"

# Install Python dependencies
print_status "Installing Python dependencies (this may take a few minutes)..."
pip install --upgrade pip
pip install numpy==1.24.3
pip install pandas==2.0.3
pip install scikit-learn==1.3.0
pip install torch==2.0.1
pip install tensorflow==2.13.0
pip install ta-lib || print_warning "TA-Lib failed, using alternative indicators"
pip install yfinance==0.2.28
pip install alpaca-py==0.10.0
pip install ccxt==4.0.0
pip install websockets==11.0.3
pip install fastapi==0.103.0
pip install uvicorn==0.23.2
pip install pydantic==2.3.0
pip install python-dotenv==1.0.0
pip install redis==5.0.0
pip install aioredis==2.0.1
pip install gymnasium==0.29.1
pip install stable-baselines3==2.1.0
pip install plotly==5.17.0
pip install dash==2.13.0
pip install pyyaml==6.0.1
pip install requests==2.31.0
pip install aiohttp==3.8.5
pip install psutil==5.9.5

print_success "All Python dependencies installed"

# Install the package in development mode
print_status "Installing TrifectaOmni package..."
pip install -e . --quiet
print_success "TrifectaOmni package installed"

# Create necessary directories
print_status "Creating directory structure..."
mkdir -p logs
mkdir -p data/market_data
mkdir -p data/models
mkdir -p data/backtest_results
mkdir -p config
mkdir -p dashboard/static
mkdir -p dashboard/templates
print_success "Directory structure created"

# Create default configuration file
print_status "Creating default configuration..."
cat > config/live_demo_config.yaml << 'EOFCONFIG'
# TrifectaOmni Live Demo Configuration
system:
  mode: shadow  # shadow mode - no real executions
  log_level: INFO
  enable_metrics: true
  
data:
  sources:
    - yfinance
    - alpaca
  symbols:
    - AAPL
    - MSFT
    - GOOGL
    - TSLA
    - NVDA
    - SPY
  timeframes:
    - 1m
    - 5m
    - 15m
  update_interval: 60  # seconds

prediction:
  models:
    - lstm
    - transformer
  horizon: 20  # prediction steps ahead
  confidence_threshold: 0.6

decision:
  strategy: adaptive_fibonacci
  risk_per_trade: 0.02
  max_positions: 5
  
execution:
  broker: shadow  # No real executions
  paper_trading: true
  initial_capital: 100000
  
visualization:
  dashboard_port: 8080
  update_frequency: 5  # seconds
  chart_history: 500  # data points

redis:
  host: localhost
  port: 6379
  db: 0
EOFCONFIG
print_success "Default configuration created"

# Create environment template
print_status "Creating environment template..."
cat > .env.template << 'EOFENV'
# TrifectaOmni Environment Configuration
# Copy this to .env and fill in your API keys

# Alpaca API (for market data - free tier available)
ALPACA_API_KEY=your_alpaca_api_key_here
ALPACA_SECRET_KEY=your_alpaca_secret_key_here
ALPACA_BASE_URL=https://paper-api.alpaca.markets

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# System Configuration
LOG_LEVEL=INFO
DEMO_MODE=true
SHADOW_MODE=true
EOFENV

if [ ! -f .env ]; then
    cp .env.template .env
    print_success "Environment template created (.env.template and .env)"
else
    print_warning ".env already exists, not overwriting"
fi

# Install Node.js dependencies for dashboard
print_status "Installing dashboard dependencies..."
cd dashboard 2>/dev/null || mkdir -p dashboard
npm init -y --silent 2>/dev/null || true
npm install --silent express socket.io chart.js plotly.js 2>/dev/null || true
cd ..
print_success "Dashboard dependencies installed"

# Create launch script
print_status "Creating launch script..."
cat > launch_demo.sh << 'EOFLAUNCH'
#!/bin/bash
# Launch TrifectaOmni Live Demo

source venv/bin/activate
python live_demo.py
EOFLAUNCH
chmod +x launch_demo.sh
print_success "Launch script created"

# Run verification
print_status "Running installation verification..."
python << 'EOFPYTHON'
import sys
import importlib

print("\n" + "="*60)
print("VERIFYING INSTALLATION")
print("="*60)

required_packages = [
    'numpy', 'pandas', 'sklearn', 'torch', 'tensorflow',
    'yfinance', 'ccxt', 'websockets', 'fastapi', 'uvicorn',
    'redis', 'gymnasium', 'plotly', 'yaml', 'requests'
]

failed = []
for package in required_packages:
    try:
        if package == 'sklearn':
            importlib.import_module('sklearn')
        elif package == 'yaml':
            importlib.import_module('yaml')
        else:
            importlib.import_module(package)
        print(f"✓ {package:20} OK")
    except ImportError as e:
        print(f"✗ {package:20} FAILED")
        failed.append(package)

print("="*60)
if failed:
    print(f"❌ {len(failed)} packages failed to import: {', '.join(failed)}")
    sys.exit(1)
else:
    print("✅ All packages imported successfully!")
    print("="*60)
EOFPYTHON

print_success "Verification complete"

# Print final instructions
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}║           🎉 INSTALLATION COMPLETE! 🎉                        ║${NC}"
echo -e "${GREEN}║                                                               ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo -e "  1️⃣  ${BLUE}Activate environment:${NC}"
echo -e "     source venv/bin/activate"
echo ""
echo -e "  2️⃣  ${BLUE}(Optional) Configure API keys in .env${NC}"
echo -e "     nano .env"
echo ""
echo -e "  3️⃣  ${BLUE}Launch the live demo:${NC}"
echo -e "     ./launch_demo.sh"
echo ""
echo -e "  OR run the all-in-one build and launch:"
echo -e "     ${GREEN}./build_and_run_demo.sh${NC}"
echo ""
echo -e "${YELLOW}📊 Dashboard will be available at:${NC} ${GREEN}http://localhost:8080${NC}"
echo ""
echo -e "${BLUE}System Features:${NC}"
echo -e "  ✓ Real-time market data streaming"
echo -e "  ✓ AI-powered predictions (LSTM + Transformer)"
echo -e "  ✓ Fibonacci-based decision making"
echo -e "  ✓ Shadow mode (NO real trades)"
echo -e "  ✓ Live performance metrics"
echo -e "  ✓ Interactive web dashboard"
echo ""
echo -e "${GREEN}Happy Trading! 🚀${NC}"
echo ""
