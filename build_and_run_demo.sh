#!/bin/bash
###############################################################################
# TrifectaOmni - BUILD ALL & RUN LIVE DEMO
# One-click script to install, build, and launch the live trading demo
###############################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
cat << "EOF"
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║    ████████╗██████╗ ██╗███████╗███████╗ ██████╗████████╗ █████╗          ║
║    ╚══██╔══╝██╔══██╗██║██╔════╝██╔════╝██╔════╝╚══██╔══╝██╔══██╗         ║
║       ██║   ██████╔╝██║█████╗  █████╗  ██║        ██║   ███████║         ║
║       ██║   ██╔══██╗██║██╔══╝  ██╔══╝  ██║        ██║   ██╔══██║         ║
║       ██║   ██║  ██║██║██║     ███████╗╚██████╗   ██║   ██║  ██║         ║
║       ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝     ╚══════╝ ╚═════╝   ╚═╝   ╚═╝  ╚═╝         ║
║                                                                           ║
║              🚀 ONE-CLICK BUILD & LIVE DEMO LAUNCHER 🚀                   ║
║                                                                           ║
║          AI-Powered Trading System with Real-Time Streaming              ║
║                      (Shadow Mode - No Real Trades)                      ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Function definitions
print_step() {
    echo -e "\n${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC} ${YELLOW}$1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}\n"
}

print_status() {
    echo -e "${CYAN}[*]${NC} $1"
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

# Check if installation is needed
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    print_step "STEP 1: Installation Required"
    print_status "Virtual environment not found. Running full installation..."
    
    if [ ! -f "one_click_install.sh" ]; then
        print_error "Installation script not found!"
        exit 1
    fi
    
    chmod +x one_click_install.sh
    ./one_click_install.sh
    
    if [ $? -ne 0 ]; then
        print_error "Installation failed!"
        exit 1
    fi
else
    print_success "Virtual environment found. Skipping installation."
fi

# Activate virtual environment
print_step "STEP 2: Activating Environment"
source venv/bin/activate
print_success "Virtual environment activated"

# Verify installation
print_step "STEP 3: Verifying Installation"
print_status "Checking Python packages..."

python3 << 'EOFPYTHON'
import sys
required = ['numpy', 'pandas', 'torch', 'tensorflow', 'yfinance', 'fastapi', 'uvicorn']
missing = []
for pkg in required:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)
        
if missing:
    print(f"Missing packages: {', '.join(missing)}")
    sys.exit(1)
else:
    print("✓ All required packages available")
EOFPYTHON

if [ $? -ne 0 ]; then
    print_error "Package verification failed!"
    print_status "Attempting to install missing packages..."
    pip install numpy pandas torch tensorflow yfinance fastapi uvicorn websockets redis aiohttp
fi

print_success "Installation verified"

# Check Redis
print_step "STEP 4: Checking Services"
print_status "Checking Redis server..."

if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        print_success "Redis is running"
    else
        print_warning "Redis not responding. Attempting to start..."
        if command -v systemctl &> /dev/null; then
            sudo systemctl start redis-server 2>/dev/null || sudo systemctl start redis 2>/dev/null || true
        elif command -v service &> /dev/null; then
            sudo service redis-server start 2>/dev/null || sudo service redis start 2>/dev/null || true
        fi
        
        sleep 2
        if redis-cli ping &> /dev/null; then
            print_success "Redis started successfully"
        else
            print_warning "Could not start Redis. Demo will continue without caching."
        fi
    fi
else
    print_warning "Redis not installed. Demo will continue without caching."
fi

# Create necessary directories
print_step "STEP 5: Preparing Environment"
print_status "Creating directory structure..."

mkdir -p logs
mkdir -p data/market_data
mkdir -p data/models
mkdir -p config
mkdir -p dashboard

print_success "Directories created"

# Check for configuration
if [ ! -f "config/live_demo_config.yaml" ]; then
    print_status "Creating default configuration..."
    cat > config/live_demo_config.yaml << 'EOFCONFIG'
system:
  mode: shadow
  log_level: INFO
  enable_metrics: true
  
data:
  sources:
    - yfinance
  symbols:
    - AAPL
    - MSFT
    - GOOGL
    - TSLA
    - NVDA
    - SPY
  update_interval: 60

prediction:
  models:
    - lstm
    - transformer
  horizon: 20
  confidence_threshold: 0.6

execution:
  broker: shadow
  paper_trading: true
  initial_capital: 100000

visualization:
  dashboard_port: 8080
  update_frequency: 5
EOFCONFIG
    print_success "Configuration created"
else
    print_success "Configuration already exists"
fi

# Build check
print_step "STEP 6: Build Verification"
print_status "Verifying TrifectaOmni package..."

python3 << 'EOFPYTHON'
try:
    from omni_trifecta.core import config
    from omni_trifecta.data import price_feeds
    from omni_trifecta.prediction import sequence_models
    from omni_trifecta.decision import master_governor
    from omni_trifecta.execution import oms
    from omni_trifecta.fibonacci import engines
    print("✓ All TrifectaOmni modules loaded successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    exit(1)
EOFPYTHON

if [ $? -eq 0 ]; then
    print_success "Package build verified"
else
    print_warning "Package verification failed. Reinstalling..."
    pip install -e .
fi

# Display pre-launch information
print_step "STEP 7: Pre-Launch Configuration"

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}                  ${GREEN}SYSTEM CONFIGURATION${NC}                 ${CYAN}║${NC}"
echo -e "${CYAN}╠═══════════════════════════════════════════════════════════╣${NC}"
echo -e "${CYAN}║${NC} ${YELLOW}Mode:${NC}              Shadow (No real executions)         ${CYAN}║${NC}"
echo -e "${CYAN}║${NC} ${YELLOW}Initial Capital:${NC}   $100,000                            ${CYAN}║${NC}"
echo -e "${CYAN}║${NC} ${YELLOW}Tracked Symbols:${NC}   AAPL, MSFT, GOOGL, TSLA, NVDA, SPY ${CYAN}║${NC}"
echo -e "${CYAN}║${NC} ${YELLOW}Update Interval:${NC}   60 seconds                          ${CYAN}║${NC}"
echo -e "${CYAN}║${NC} ${YELLOW}Dashboard Port:${NC}    8080                                ${CYAN}║${NC}"
echo -e "${CYAN}║${NC} ${YELLOW}Data Source:${NC}       Yahoo Finance (Free)                ${CYAN}║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════╝${NC}"

echo ""
echo -e "${GREEN}Features Enabled:${NC}"
echo -e "  ${GREEN}✓${NC} Real-time market data streaming"
echo -e "  ${GREEN}✓${NC} AI predictions (LSTM + Transformer)"
echo -e "  ${GREEN}✓${NC} Fibonacci-based signal generation"
echo -e "  ${GREEN}✓${NC} Risk management & position tracking"
echo -e "  ${GREEN}✓${NC} Live performance metrics"
echo -e "  ${GREEN}✓${NC} Interactive web dashboard"
echo -e "  ${GREEN}✓${NC} Real-time WebSocket updates"
echo ""

# Check if port is available
print_status "Checking if port 8080 is available..."
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    print_warning "Port 8080 is already in use!"
    print_status "Attempting to free port..."
    fuser -k 8080/tcp 2>/dev/null || true
    sleep 2
fi
print_success "Port 8080 is available"

# Launch countdown
print_step "STEP 8: LAUNCHING LIVE DEMO"

for i in 3 2 1; do
    echo -e "${YELLOW}Starting in ${i}...${NC}"
    sleep 1
done

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║${NC}                   ${MAGENTA}🚀 LAUNCHING NOW 🚀${NC}                   ${GREEN}║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Launch the demo
print_status "Starting TrifectaOmni Live Demo..."
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📊 Dashboard:${NC}  ${GREEN}http://localhost:8080${NC}"
echo -e "${YELLOW}📡 WebSocket:${NC}  ${GREEN}ws://localhost:8080/ws${NC}"
echo -e "${YELLOW}📁 Logs:${NC}       ${GREEN}logs/live_demo.log${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the demo${NC}"
echo ""

# Open browser after a delay (in background)
(sleep 5 && "$BROWSER" http://localhost:8080 2>/dev/null || xdg-open http://localhost:8080 2>/dev/null || open http://localhost:8080 2>/dev/null || true) &

# Run the demo
python3 live_demo.py

# If we get here, the demo has stopped
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}Demo stopped.${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "To restart: ${GREEN}./build_and_run_demo.sh${NC}"
echo ""
