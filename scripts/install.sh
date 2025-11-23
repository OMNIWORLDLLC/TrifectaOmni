#!/bin/bash
#
# TrifectaOmni Installation Script
# This script handles the complete installation of the TrifectaOmni trading system
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

# Check if running with bash
if [ -z "$BASH_VERSION" ]; then
    log_error "This script must be run with bash"
    exit 1
fi

log_info "Starting TrifectaOmni Installation..."
log_info "Project root: ${PROJECT_ROOT}"

# 1. Check system prerequisites
log_info "Step 1/7: Checking system prerequisites..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    log_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
log_success "Python ${PYTHON_VERSION} found"

# Check pip
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    log_error "pip is not installed. Please install pip3."
    exit 1
fi
log_success "pip found"

# Check git
if ! command -v git &> /dev/null; then
    log_warning "git is not installed. Version control features may be limited."
else
    log_success "git found"
fi

# 2. Create/activate virtual environment
log_info "Step 2/7: Setting up Python virtual environment..."

if [ -d "${VENV_DIR}" ]; then
    log_warning "Virtual environment already exists at ${VENV_DIR}"
    # Auto mode - don't prompt if TRIFECTA_AUTO is set
    if [ -z "$TRIFECTA_AUTO" ]; then
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log_info "Removing existing virtual environment..."
            rm -rf "${VENV_DIR}"
        else
            log_info "Using existing virtual environment"
        fi
    else
        log_info "Using existing virtual environment (auto mode)"
    fi
fi

if [ ! -d "${VENV_DIR}" ]; then
    log_info "Creating virtual environment..."
    python3 -m venv "${VENV_DIR}"
    log_success "Virtual environment created"
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source "${VENV_DIR}/bin/activate"
log_success "Virtual environment activated"

# Upgrade pip
log_info "Upgrading pip..."
python -m pip install --upgrade pip setuptools wheel
log_success "pip upgraded"

# 3. Install dependencies
log_info "Step 3/7: Installing Python dependencies..."

if [ ! -f "${PROJECT_ROOT}/requirements.txt" ]; then
    log_error "requirements.txt not found!"
    exit 1
fi

log_info "Installing dependencies from requirements.txt..."
pip install -r "${PROJECT_ROOT}/requirements.txt"
log_success "Dependencies installed successfully"

# 4. Create directory structure
log_info "Step 4/7: Creating directory structure..."

DIRS=(
    "runtime/logs"
    "runtime/logs/rl_state"
    "models"
    "data/cache"
    "backups"
)

for dir in "${DIRS[@]}"; do
    mkdir -p "${PROJECT_ROOT}/${dir}"
    log_info "Created ${dir}"
done
log_success "Directory structure created"

# 5. Setup environment configuration
log_info "Step 5/7: Setting up environment configuration..."

if [ ! -f "${PROJECT_ROOT}/.env" ]; then
    if [ -f "${PROJECT_ROOT}/.env.example" ]; then
        log_info "Creating .env from .env.example..."
        cp "${PROJECT_ROOT}/.env.example" "${PROJECT_ROOT}/.env"
        log_warning "Please edit .env file with your actual credentials"
        log_info "Configuration file: ${PROJECT_ROOT}/.env"
    else
        log_warning ".env.example not found, skipping .env creation"
    fi
else
    log_success ".env file already exists"
fi

# 6. Create startup scripts
log_info "Step 6/7: Creating startup scripts..."

# Create activate script
cat > "${PROJECT_ROOT}/activate.sh" << 'EOF'
#!/bin/bash
# Activate TrifectaOmni environment
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${PROJECT_ROOT}/venv/bin/activate"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"
echo "TrifectaOmni environment activated"
echo "Project root: ${PROJECT_ROOT}"
echo "Python: $(which python)"
echo "To run shadow mode: python examples/shadow_mode_example.py"
EOF
chmod +x "${PROJECT_ROOT}/activate.sh"
log_success "Created activate.sh"

# 7. Verify installation
log_info "Step 7/7: Verifying installation..."

# Test imports
python << EOF
import sys
sys.path.insert(0, '${PROJECT_ROOT}')

errors = []
try:
    import numpy
    print("✓ numpy imported successfully")
except ImportError as e:
    errors.append(f"numpy: {e}")

try:
    import pandas
    print("✓ pandas imported successfully")
except ImportError as e:
    errors.append(f"pandas: {e}")

try:
    import sklearn
    print("✓ scikit-learn imported successfully")
except ImportError as e:
    errors.append(f"scikit-learn: {e}")

try:
    import onnxruntime
    print("✓ onnxruntime imported successfully")
except ImportError as e:
    errors.append(f"onnxruntime: {e}")

try:
    import omni_trifecta
    print("✓ omni_trifecta package imported successfully")
except ImportError as e:
    errors.append(f"omni_trifecta: {e}")

if errors:
    print("\nErrors:")
    for error in errors:
        print(f"  ✗ {error}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    log_success "All imports verified successfully"
else
    log_error "Some imports failed. Please check the error messages above."
    exit 1
fi

# Installation complete
echo ""
log_success "=============================================="
log_success "  TrifectaOmni Installation Complete!"
log_success "=============================================="
echo ""
log_info "Next steps:"
echo "  1. Edit .env file with your credentials:"
echo "     nano ${PROJECT_ROOT}/.env"
echo ""
echo "  2. Activate the environment:"
echo "     source ${PROJECT_ROOT}/activate.sh"
echo ""
echo "  3. Run shadow mode test:"
echo "     python examples/shadow_mode_example.py"
echo ""
echo "  4. For production deployment, run:"
echo "     bash scripts/deploy.sh"
echo ""
