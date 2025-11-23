#!/bin/bash
#
# TrifectaOmni Full System Operations Script
# End-to-end installation, build, wire, and deployment
#
# This master script orchestrates the complete setup and deployment process
# Usage: ./full-system-install.sh [mode]
#   mode: shadow (default) | production | service
#

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="${PROJECT_ROOT}/scripts"
DEPLOYMENT_MODE="${1:-shadow}"

# Logging functions
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

log_phase() {
    echo ""
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC} $1"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Show banner
show_banner() {
    echo ""
    echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║                                                            ║${NC}"
    echo -e "${MAGENTA}║${NC}        ${GREEN}TrifectaOmni Full System Operations${NC}              ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}║                                                            ║${NC}"
    echo -e "${MAGENTA}║${NC}    End-to-End Installation, Build, Wire & Deploy       ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}║                                                            ║${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Show usage
show_usage() {
    echo "Usage: $0 [mode]"
    echo ""
    echo "Deployment Modes:"
    echo "  shadow      - Full setup + shadow mode testing (default, recommended)"
    echo "  production  - Full setup + production deployment (requires credentials)"
    echo "  service     - Full setup + systemd service installation"
    echo ""
    echo "This script will:"
    echo "  1. Install all dependencies and create virtual environment"
    echo "  2. Build and compile the system"
    echo "  3. Wire up configuration and validate connectivity"
    echo "  4. Deploy in the specified mode"
    echo ""
    echo "Examples:"
    echo "  $0              # Install and test in shadow mode"
    echo "  $0 shadow       # Same as above"
    echo "  $0 production   # Install and deploy to production"
    echo "  $0 service      # Install and create systemd service"
    echo ""
    exit 1
}

# Validate deployment mode
validate_mode() {
    if [[ ! "$DEPLOYMENT_MODE" =~ ^(shadow|production|service)$ ]]; then
        log_error "Invalid deployment mode: ${DEPLOYMENT_MODE}"
        show_usage
    fi
}

# Error handler
error_handler() {
    log_error "An error occurred during execution"
    log_error "Phase: $1"
    log_error "Check the output above for details"
    exit 1
}

# Main execution
main() {
    show_banner
    
    log_info "Project root: ${PROJECT_ROOT}"
    log_info "Deployment mode: ${DEPLOYMENT_MODE}"
    echo ""
    
    # Validate mode
    validate_mode
    
    # Interactive confirmation for production
    if [ "$DEPLOYMENT_MODE" == "production" ]; then
        log_warning "⚠️  Production mode will deploy for real trading!"
        read -p "Continue? (yes/NO): " -r
        echo
        if [[ ! $REPLY =~ ^yes$ ]]; then
            log_info "Cancelled by user"
            exit 0
        fi
    fi
    
    # Phase 1: Installation
    log_phase "PHASE 1/4: INSTALLATION"
    log_info "Installing dependencies and setting up environment..."
    
    if [ ! -f "${SCRIPTS_DIR}/install.sh" ]; then
        log_error "install.sh not found in ${SCRIPTS_DIR}"
        exit 1
    fi
    
    # Set auto mode for non-interactive operation
    export TRIFECTA_AUTO=1
    
    if ! bash "${SCRIPTS_DIR}/install.sh"; then
        error_handler "Installation"
    fi
    
    log_success "✓ Phase 1 Complete: Installation successful"
    sleep 2
    
    # Phase 2: Build
    log_phase "PHASE 2/4: BUILD"
    log_info "Building and compiling the system..."
    
    if [ ! -f "${SCRIPTS_DIR}/build.sh" ]; then
        log_error "build.sh not found in ${SCRIPTS_DIR}"
        exit 1
    fi
    
    if ! bash "${SCRIPTS_DIR}/build.sh"; then
        error_handler "Build"
    fi
    
    log_success "✓ Phase 2 Complete: Build successful"
    sleep 2
    
    # Phase 3: Wire/Setup
    log_phase "PHASE 3/4: WIRE & CONFIGURATION"
    log_info "Wiring up configuration and validating connectivity..."
    
    if [ ! -f "${SCRIPTS_DIR}/wire.sh" ]; then
        log_error "wire.sh not found in ${SCRIPTS_DIR}"
        exit 1
    fi
    
    if ! bash "${SCRIPTS_DIR}/wire.sh"; then
        error_handler "Wire/Configuration"
    fi
    
    log_success "✓ Phase 3 Complete: Configuration and wiring successful"
    sleep 2
    
    # Phase 4: Deployment
    log_phase "PHASE 4/4: DEPLOYMENT"
    log_info "Deploying in ${DEPLOYMENT_MODE} mode..."
    
    if [ ! -f "${SCRIPTS_DIR}/deploy.sh" ]; then
        log_error "deploy.sh not found in ${SCRIPTS_DIR}"
        exit 1
    fi
    
    # Keep auto mode for deployment
    export TRIFECTA_AUTO=1
    
    if ! bash "${SCRIPTS_DIR}/deploy.sh" "${DEPLOYMENT_MODE}"; then
        error_handler "Deployment"
    fi
    
    log_success "✓ Phase 4 Complete: Deployment successful"
    
    # Final summary
    echo ""
    echo ""
    log_success "════════════════════════════════════════════════════════════"
    log_success "    🎉 FULL SYSTEM OPERATIONS COMPLETED SUCCESSFULLY! 🎉"
    log_success "════════════════════════════════════════════════════════════"
    echo ""
    
    log_info "All phases completed:"
    echo "  ✓ Installation"
    echo "  ✓ Build"
    echo "  ✓ Wire & Configuration"
    echo "  ✓ Deployment (${DEPLOYMENT_MODE})"
    echo ""
    
    case "$DEPLOYMENT_MODE" in
        shadow)
            log_info "System tested in shadow mode"
            echo "  Next steps:"
            echo "    - Review logs in: runtime/logs/"
            echo "    - When ready for production: ./full-system-install.sh production"
            ;;
        production)
            log_info "System deployed in production mode"
            echo "  Monitor your system:"
            echo "    - Logs: tail -f runtime/logs/trades.jsonl"
            echo "    - Emergency stop: Ctrl+C"
            ;;
        service)
            log_info "System configured as service"
            echo "  Install the service:"
            echo "    - See instructions displayed above"
            echo "    - Or check: ${PROJECT_ROOT}/runtime/logs/"
            ;;
    esac
    
    echo ""
    log_info "Documentation:"
    echo "  - Quick Start: QUICKSTART.md"
    echo "  - Setup Guide: SETUP.md"
    echo "  - Architecture: README.md"
    echo ""
    log_success "Happy Trading! 🚀"
    echo ""
}

# Handle script arguments
if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    show_usage
fi

# Run main function
main
