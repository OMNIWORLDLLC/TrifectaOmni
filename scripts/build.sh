#!/bin/bash
#
# TrifectaOmni Build Script
# Validates and prepares the system for deployment
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

log_info "Starting TrifectaOmni Build Process..."
log_info "Project root: ${PROJECT_ROOT}"

# 1. Check if virtual environment exists
log_info "Step 1/5: Checking virtual environment..."

if [ ! -d "${VENV_DIR}" ]; then
    log_error "Virtual environment not found. Please run install.sh first."
    exit 1
fi

source "${VENV_DIR}/bin/activate"
log_success "Virtual environment activated"

# 2. Verify Python environment
log_info "Step 2/5: Verifying Python environment..."

PYTHON_VERSION=$(python --version | cut -d' ' -f2)
log_info "Python version: ${PYTHON_VERSION}"

# Check critical modules
python << 'EOF'
import sys
import importlib.util

critical_modules = [
    'numpy',
    'pandas', 
    'sklearn',
    'onnxruntime',
    'omni_trifecta'
]

missing = []
for module in critical_modules:
    if importlib.util.find_spec(module) is None:
        missing.append(module)
        print(f"✗ {module} not found")
    else:
        print(f"✓ {module} found")

if missing:
    print(f"\nMissing modules: {', '.join(missing)}")
    sys.exit(1)
EOF

if [ $? -ne 0 ]; then
    log_error "Missing critical Python modules. Please run install.sh"
    exit 1
fi
log_success "All critical modules present"

# 3. Compile Python modules (bytecode)
log_info "Step 3/5: Compiling Python modules..."

python -m compileall "${PROJECT_ROOT}/omni_trifecta" -q
log_success "Python modules compiled"

# 4. Validate package structure
log_info "Step 4/5: Validating package structure..."

REQUIRED_DIRS=(
    "omni_trifecta/core"
    "omni_trifecta/data"
    "omni_trifecta/prediction"
    "omni_trifecta/fibonacci"
    "omni_trifecta/decision"
    "omni_trifecta/execution"
    "omni_trifecta/safety"
    "omni_trifecta/learning"
    "omni_trifecta/runtime"
    "omni_trifecta/utils"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ ! -d "${PROJECT_ROOT}/${dir}" ]; then
        log_error "Required directory not found: ${dir}"
        exit 1
    fi
done
log_success "Package structure validated"

# 5. Run pre-flight system checks
log_info "Step 5/5: Running pre-flight checks..."

python << 'EOF'
import sys
sys.path.insert(0, '.')

from omni_trifecta.core.config import OmniConfig
from omni_trifecta.safety.managers import DeploymentChecklist

print("\n=== Pre-flight System Checks ===\n")

try:
    config = OmniConfig()
    print("✓ Configuration loaded successfully")
    
    checklist = DeploymentChecklist(config)
    checks = checklist.verify()
    
    print(f"\nMT5 Configured: {'✓' if checks['mt5_configured'] else '✗'}")
    print(f"Binary API Configured: {'✓' if checks['binary_configured'] else '✗'}")
    print(f"DEX Configured: {'✓' if checks['dex_configured'] else '✗'}")
    print(f"Logging System: {'✓' if checks['log_dir_accessible'] else '✗'}")
    print(f"ONNX Model: {'✓' if checks.get('onnx_model_exists', False) else '✗ (optional)'}")
    
    if not checks['all_passed']:
        print("\n⚠ Some checks failed. Please configure .env file for production deployment.")
        print("   For testing, you can use shadow mode without configuration.")
    else:
        print("\n✓ All systems ready for production deployment!")
        
except Exception as e:
    print(f"✗ Error during pre-flight checks: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

log_success "Build process completed successfully"

echo ""
log_info "Build Summary:"
echo "  - Python environment: OK"
echo "  - Module compilation: OK"
echo "  - Package structure: OK"
echo "  - Pre-flight checks: Completed"
echo ""
log_info "System is ready for deployment."
echo "  - For shadow mode testing: bash scripts/deploy.sh shadow"
echo "  - For production deployment: bash scripts/deploy.sh production"
echo ""
