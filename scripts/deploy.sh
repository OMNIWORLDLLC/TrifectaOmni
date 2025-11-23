#!/bin/bash
#
# TrifectaOmni Deployment Script
# Deploys the system in shadow or production mode
#

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${PROJECT_ROOT}/venv"

# Deployment mode (shadow or production)
MODE="${1:-shadow}"

# Logging
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Usage
show_usage() {
    echo "Usage: $0 [mode]"
    echo ""
    echo "Modes:"
    echo "  shadow      - Deploy in shadow mode (simulated trading, no real trades)"
    echo "  production  - Deploy in production mode (real trading)"
    echo "  service     - Install as systemd service"
    echo ""
    echo "Examples:"
    echo "  $0 shadow"
    echo "  $0 production"
    echo "  $0 service"
    exit 1
}

log_info "Starting TrifectaOmni Deployment..."
log_info "Project root: ${PROJECT_ROOT}"
log_info "Deployment mode: ${MODE}"

# Validate mode
if [[ ! "$MODE" =~ ^(shadow|production|service)$ ]]; then
    log_error "Invalid deployment mode: ${MODE}"
    show_usage
fi

# 1. Activate virtual environment
log_info "Step 1/4: Activating virtual environment..."

if [ ! -d "${VENV_DIR}" ]; then
    log_error "Virtual environment not found. Please run install.sh first."
    exit 1
fi

source "${VENV_DIR}/bin/activate"
log_success "Virtual environment activated"

# 2. Pre-deployment checks
log_info "Step 2/4: Running pre-deployment checks..."

if [ "$MODE" == "production" ]; then
    log_warning "Production mode requires valid API credentials in .env"
    
    python << 'EOF'
import sys
sys.path.insert(0, '.')

from omni_trifecta.core.config import OmniConfig
from omni_trifecta.safety.managers import DeploymentChecklist

config = OmniConfig()
checklist = DeploymentChecklist(config)
checks = checklist.verify()

if not checks['all_passed']:
    print("\n✗ Production deployment blocked: Not all systems are configured")
    print("  Please configure .env file with valid credentials")
    print("  Or use shadow mode for testing: bash scripts/deploy.sh shadow")
    sys.exit(1)
else:
    print("\n✓ All systems ready for production deployment")
EOF
    
    if [ $? -ne 0 ]; then
        log_error "Pre-deployment checks failed for production mode"
        exit 1
    fi
fi

log_success "Pre-deployment checks passed"

# 3. Deploy based on mode
log_info "Step 3/4: Deploying in ${MODE} mode..."

case "$MODE" in
    shadow)
        log_info "Running shadow mode example..."
        python "${PROJECT_ROOT}/examples/shadow_mode_example.py"
        ;;
        
    production)
        log_warning "⚠️  PRODUCTION MODE - REAL TRADING ⚠️"
        log_warning "This will execute real trades with real money!"
        
        # Skip confirmation in auto mode
        if [ -z "$TRIFECTA_AUTO" ]; then
            read -p "Are you sure you want to continue? (yes/NO): " -r
            echo
            if [[ ! $REPLY =~ ^yes$ ]]; then
                log_info "Production deployment cancelled"
                exit 0
            fi
        else
            log_warning "Auto mode: Production deployment confirmed"
        fi
        
        log_info "Starting production deployment..."
        python "${PROJECT_ROOT}/examples/production_ready_example.py"
        ;;
        
    service)
        log_info "Installing as systemd service..."
        
        # Create systemd service file
        SERVICE_FILE="/tmp/trifecta-omni.service"
        
        cat > "$SERVICE_FILE" << EOF
[Unit]
Description=TrifectaOmni Trading System
After=network.target

[Service]
Type=simple
User=$(whoami)
WorkingDirectory=${PROJECT_ROOT}
Environment="PYTHONPATH=${PROJECT_ROOT}"
ExecStart=${VENV_DIR}/bin/python ${PROJECT_ROOT}/examples/production_ready_example.py
Restart=on-failure
RestartSec=30
StandardOutput=append:${PROJECT_ROOT}/runtime/logs/service.log
StandardError=append:${PROJECT_ROOT}/runtime/logs/service-error.log

[Install]
WantedBy=multi-user.target
EOF
        
        log_info "Service file created at ${SERVICE_FILE}"
        log_info "To install the service, run as root:"
        echo ""
        echo "  sudo cp ${SERVICE_FILE} /etc/systemd/system/"
        echo "  sudo systemctl daemon-reload"
        echo "  sudo systemctl enable trifecta-omni"
        echo "  sudo systemctl start trifecta-omni"
        echo "  sudo systemctl status trifecta-omni"
        echo ""
        log_success "Service configuration created"
        ;;
esac

# 4. Post-deployment information
log_info "Step 4/4: Post-deployment information..."

echo ""
log_success "=============================================="
log_success "  TrifectaOmni Deployment Complete!"
log_success "=============================================="
echo ""

case "$MODE" in
    shadow)
        log_info "Shadow mode deployment completed"
        echo "  - Check logs: ${PROJECT_ROOT}/runtime/logs/"
        echo "  - Review trades.jsonl for trade history"
        echo "  - Review performance.jsonl for metrics"
        ;;
        
    production)
        log_info "Production deployment completed"
        echo "  - Monitor logs: tail -f ${PROJECT_ROOT}/runtime/logs/trades.jsonl"
        echo "  - Safety Manager is active"
        echo "  - Emergency stop: Ctrl+C"
        ;;
        
    service)
        log_info "Service configuration created"
        echo "  - Install with commands shown above"
        echo "  - Service logs: journalctl -u trifecta-omni -f"
        ;;
esac

echo ""
log_info "For support, see SETUP.md or README.md"
echo ""
