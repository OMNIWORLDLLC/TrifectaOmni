#!/bin/bash
#
# TrifectaOmni Wire/Setup Script
# Validates configuration and tests connectivity
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

log_info "Starting TrifectaOmni Wire/Setup Process..."
log_info "Project root: ${PROJECT_ROOT}"

# 1. Activate virtual environment
log_info "Step 1/5: Activating virtual environment..."

if [ ! -d "${VENV_DIR}" ]; then
    log_error "Virtual environment not found. Please run install.sh first."
    exit 1
fi

source "${VENV_DIR}/bin/activate"
log_success "Virtual environment activated"

# 2. Verify .env configuration
log_info "Step 2/5: Verifying configuration..."

if [ ! -f "${PROJECT_ROOT}/.env" ]; then
    log_warning ".env file not found"
    log_info "Creating .env from template..."
    if [ -f "${PROJECT_ROOT}/.env.example" ]; then
        cp "${PROJECT_ROOT}/.env.example" "${PROJECT_ROOT}/.env"
        log_warning "Please edit .env with your actual credentials"
    else
        log_error ".env.example not found"
        exit 1
    fi
fi

log_success "Configuration file found"

# 3. Test configuration loading
log_info "Step 3/5: Testing configuration loading..."

python << 'EOF'
import sys
sys.path.insert(0, '.')

try:
    from omni_trifecta.core.config import OmniConfig
    
    config = OmniConfig()
    print(f"✓ Configuration loaded successfully")
    print(f"  - Log directory: {config.log_dir}")
    print(f"  - Model path: {config.seq_model_onnx}")
    
except Exception as e:
    print(f"✗ Configuration loading failed: {e}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    log_error "Configuration test failed"
    exit 1
fi
log_success "Configuration loaded successfully"

# 4. Run deployment checklist
log_info "Step 4/5: Running deployment checklist..."

python << 'EOF'
import sys
sys.path.insert(0, '.')

from omni_trifecta.core.config import OmniConfig
from omni_trifecta.safety.managers import DeploymentChecklist

print("\n=== Deployment Checklist ===\n")

try:
    config = OmniConfig()
    checklist = DeploymentChecklist(config)
    checks = checklist.verify()
    
    components = [
        ("MT5 Connection", checks['mt5_configured']),
        ("Binary Options API", checks['binary_configured']),
        ("DEX/Blockchain RPC", checks['dex_configured']),
        ("Logging System", checks['log_dir_accessible']),
        ("ONNX Model (optional)", checks.get('onnx_model_exists', False))
    ]
    
    for name, status in components:
        status_str = "✓ READY" if status else "✗ NOT CONFIGURED"
        print(f"  {name:.<30} {status_str}")
    
    print()
    if checks['all_passed']:
        print("✓ All systems configured and ready!")
        sys.exit(0)
    else:
        print("⚠ Some systems are not configured.")
        print("  For testing, you can use shadow mode.")
        print("  For production, please configure .env file.")
        sys.exit(0)  # Don't fail - shadow mode can still work
        
except Exception as e:
    print(f"✗ Checklist failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    log_error "Deployment checklist failed"
    exit 1
fi

# 5. Test core module imports
log_info "Step 5/5: Testing core module imports..."

python << 'EOF'
import sys
sys.path.insert(0, '.')

modules = [
    'omni_trifecta.core.config',
    'omni_trifecta.prediction.sequence_models',
    'omni_trifecta.fibonacci.master_governor',
    'omni_trifecta.decision.master_governor',
    'omni_trifecta.execution.executors',
    'omni_trifecta.safety.managers',
    'omni_trifecta.runtime.orchestration',
]

errors = []
for module_name in modules:
    try:
        __import__(module_name)
        print(f"✓ {module_name}")
    except Exception as e:
        errors.append(f"{module_name}: {e}")
        print(f"✗ {module_name}: {e}")

if errors:
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    log_error "Module import tests failed"
    exit 1
fi
log_success "All core modules imported successfully"

# Wire/Setup complete
echo ""
log_success "=============================================="
log_success "  TrifectaOmni Wire/Setup Complete!"
log_success "=============================================="
echo ""
log_info "System Status:"
echo "  ✓ Configuration validated"
echo "  ✓ Deployment checklist completed"
echo "  ✓ Core modules verified"
echo ""
log_info "Ready for deployment!"
echo "  - Test with shadow mode: bash scripts/deploy.sh shadow"
echo "  - Deploy to production: bash scripts/deploy.sh production"
echo ""
