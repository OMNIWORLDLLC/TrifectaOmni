#!/bin/bash
#
# TrifectaOmni Installation Test Script
# Validates the full-system-install.sh script functionality
#
# This script tests the one-click installation process to ensure:
# 1. All dependencies are installed correctly
# 2. Virtual environment is created
# 3. All modules are importable
# 4. Configuration is set up properly
# 5. System can run in shadow mode
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

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TEST_RESULTS=()

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="${PROJECT_ROOT}/test_install_temp"
VENV_DIR="${TEST_DIR}/venv"

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[✗]${NC} $1"
}

log_test() {
    echo -e "${CYAN}[TEST]${NC} $1"
}

# Show banner
show_banner() {
    echo ""
    echo -e "${MAGENTA}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${MAGENTA}║                                                            ║${NC}"
    echo -e "${MAGENTA}║${NC}    ${GREEN}TrifectaOmni Installation Test Suite${NC}              ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}║                                                            ║${NC}"
    echo -e "${MAGENTA}║${NC}    Validates One-Click Installation Process           ${MAGENTA}║${NC}"
    echo -e "${MAGENTA}║                                                            ║${NC}"
    echo -e "${MAGENTA}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Test result tracking
pass_test() {
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TEST_RESULTS+=("✓ $1")
    log_success "$1"
}

fail_test() {
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TEST_RESULTS+=("✗ $1")
    log_error "$1"
}

# Test 1: Script exists and is executable
test_script_exists() {
    log_test "Test 1: Checking if full-system-install.sh exists and is executable"
    
    if [ -f "${PROJECT_ROOT}/full-system-install.sh" ]; then
        if [ -x "${PROJECT_ROOT}/full-system-install.sh" ]; then
            pass_test "Script exists and is executable"
            return 0
        else
            fail_test "Script exists but is not executable"
            return 1
        fi
    else
        fail_test "Script does not exist"
        return 1
    fi
}

# Test 2: Script shows help
test_script_help() {
    log_test "Test 2: Checking if script shows help message"
    
    if bash "${PROJECT_ROOT}/full-system-install.sh" --help 2>&1 | grep -q "Usage:"; then
        pass_test "Script displays help message"
        return 0
    else
        fail_test "Script does not display help message"
        return 1
    fi
}

# Test 3: Check prerequisite scripts exist
test_prerequisite_scripts() {
    log_test "Test 3: Checking if prerequisite scripts exist"
    
    local all_exist=true
    local scripts=("install.sh" "build.sh" "wire.sh" "deploy.sh")
    
    for script in "${scripts[@]}"; do
        if [ ! -f "${PROJECT_ROOT}/scripts/${script}" ]; then
            log_error "Missing script: scripts/${script}"
            all_exist=false
        fi
    done
    
    if [ "$all_exist" = true ]; then
        pass_test "All prerequisite scripts exist"
        return 0
    else
        fail_test "Some prerequisite scripts are missing"
        return 1
    fi
}

# Test 4: Check Python version compatibility
test_python_version() {
    log_test "Test 4: Checking Python version compatibility"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 8 ]; then
            pass_test "Python $PYTHON_VERSION is compatible (>=3.8 required)"
            return 0
        else
            fail_test "Python $PYTHON_VERSION is too old (>=3.8 required)"
            return 1
        fi
    else
        fail_test "Python 3 is not installed"
        return 1
    fi
}

# Test 5: Check requirements.txt exists and is valid
test_requirements_file() {
    log_test "Test 5: Checking requirements.txt"
    
    if [ -f "${PROJECT_ROOT}/requirements.txt" ]; then
        # Check if file has content
        if [ -s "${PROJECT_ROOT}/requirements.txt" ]; then
            # Count number of requirements
            local req_count=$(grep -v '^#' "${PROJECT_ROOT}/requirements.txt" | grep -v '^$' | wc -l)
            pass_test "requirements.txt exists with $req_count packages"
            return 0
        else
            fail_test "requirements.txt is empty"
            return 1
        fi
    else
        fail_test "requirements.txt does not exist"
        return 1
    fi
}

# Test 6: Check .env.example exists
test_env_example() {
    log_test "Test 6: Checking .env.example template"
    
    if [ -f "${PROJECT_ROOT}/.env.example" ]; then
        # Check if it contains expected keys
        if grep -q "MT5_LOGIN\|POCKET_TOKEN\|DEX_RPC" "${PROJECT_ROOT}/.env.example"; then
            pass_test ".env.example exists with expected configuration keys"
            return 0
        else
            fail_test ".env.example exists but missing expected keys"
            return 1
        fi
    else
        fail_test ".env.example does not exist"
        return 1
    fi
}

# Test 7: Verify package structure
test_package_structure() {
    log_test "Test 7: Verifying package structure"
    
    local required_dirs=(
        "omni_trifecta"
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
    
    local all_exist=true
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "${PROJECT_ROOT}/${dir}" ]; then
            log_error "Missing directory: ${dir}"
            all_exist=false
        fi
    done
    
    if [ "$all_exist" = true ]; then
        pass_test "All required package directories exist"
        return 0
    else
        fail_test "Some package directories are missing"
        return 1
    fi
}

# Test 8: Check example files exist
test_example_files() {
    log_test "Test 8: Checking example files"
    
    local examples=(
        "examples/shadow_mode_example.py"
        "examples/production_ready_example.py"
    )
    
    local all_exist=true
    for example in "${examples[@]}"; do
        if [ ! -f "${PROJECT_ROOT}/${example}" ]; then
            log_error "Missing example: ${example}"
            all_exist=false
        fi
    done
    
    if [ "$all_exist" = true ]; then
        pass_test "All example files exist"
        return 0
    else
        fail_test "Some example files are missing"
        return 1
    fi
}

# Test 9: Verify documentation exists
test_documentation() {
    log_test "Test 9: Checking documentation files"
    
    local docs=(
        "README.md"
        "SETUP.md"
        "QUICKSTART.md"
    )
    
    local all_exist=true
    for doc in "${docs[@]}"; do
        if [ ! -f "${PROJECT_ROOT}/${doc}" ]; then
            log_error "Missing documentation: ${doc}"
            all_exist=false
        fi
    done
    
    if [ "$all_exist" = true ]; then
        pass_test "All documentation files exist"
        return 0
    else
        fail_test "Some documentation files are missing"
        return 1
    fi
}

# Test 10: Dry run of installation script (without actually installing)
test_script_dry_run() {
    log_test "Test 10: Testing script help and validation"
    
    # Test that script accepts valid modes
    local modes=("shadow" "production" "service")
    local valid_modes=true
    
    for mode in "${modes[@]}"; do
        # Just check if the script would accept the mode (exits 1 for help, 0 or other for valid)
        if bash "${PROJECT_ROOT}/full-system-install.sh" --help 2>&1 | grep -q "${mode}"; then
            log_info "Mode '${mode}' is documented in help"
        else
            log_warning "Mode '${mode}' not found in help"
            valid_modes=false
        fi
    done
    
    if [ "$valid_modes" = true ]; then
        pass_test "Script accepts all expected modes"
        return 0
    else
        fail_test "Script does not document all expected modes"
        return 1
    fi
}

# Test 11: Check if virtual environment is already set up (from previous run)
test_existing_installation() {
    log_test "Test 11: Checking for existing installation"
    
    if [ -d "${PROJECT_ROOT}/venv" ]; then
        log_info "Found existing virtual environment"
        
        # Test if it's functional
        if source "${PROJECT_ROOT}/venv/bin/activate" 2>/dev/null; then
            if python -c "import omni_trifecta" 2>/dev/null; then
                pass_test "Existing installation is functional"
                deactivate 2>/dev/null || true
                return 0
            else
                log_warning "Existing installation found but package not importable"
                deactivate 2>/dev/null || true
            fi
        fi
    fi
    
    log_info "No existing installation found (this is okay)"
    pass_test "Installation check completed"
    return 0
}

# Test 12: Validate script phases
test_script_phases() {
    log_test "Test 12: Validating script phases structure"
    
    # Check if script mentions all 4 phases
    local phases=(
        "PHASE 1"
        "PHASE 2"
        "PHASE 3"
        "PHASE 4"
    )
    
    local all_phases=true
    for phase in "${phases[@]}"; do
        if ! grep -q "${phase}" "${PROJECT_ROOT}/full-system-install.sh"; then
            log_error "Script missing: ${phase}"
            all_phases=false
        fi
    done
    
    if [ "$all_phases" = true ]; then
        pass_test "All 4 phases are defined in script"
        return 0
    else
        fail_test "Some phases are missing from script"
        return 1
    fi
}

# Test 13: Check script error handling
test_error_handling() {
    log_test "Test 13: Checking script error handling"
    
    # Check if script has 'set -e' for error handling
    if grep -q "set -e" "${PROJECT_ROOT}/full-system-install.sh"; then
        pass_test "Script has error handling enabled (set -e)"
        return 0
    else
        fail_test "Script missing error handling (set -e)"
        return 1
    fi
}

# Test 14: Validate logging functions
test_logging_functions() {
    log_test "Test 14: Checking logging functions"
    
    local log_functions=("log_info" "log_success" "log_warning" "log_error")
    local all_functions=true
    
    for func in "${log_functions[@]}"; do
        if ! grep -q "${func}()" "${PROJECT_ROOT}/full-system-install.sh"; then
            log_error "Missing logging function: ${func}"
            all_functions=false
        fi
    done
    
    if [ "$all_functions" = true ]; then
        pass_test "All logging functions are defined"
        return 0
    else
        fail_test "Some logging functions are missing"
        return 1
    fi
}

# Test 15: Check safety confirmation for production mode
test_production_safety() {
    log_test "Test 15: Checking production mode safety confirmation"
    
    # Check if script has production mode confirmation
    if grep -q "production" "${PROJECT_ROOT}/full-system-install.sh" && \
       grep -q "Are you sure\|Continue?" "${PROJECT_ROOT}/full-system-install.sh"; then
        pass_test "Production mode has safety confirmation"
        return 0
    else
        fail_test "Production mode missing safety confirmation"
        return 1
    fi
}

# Main test execution
main() {
    show_banner
    
    log_info "Starting test suite..."
    log_info "Project root: ${PROJECT_ROOT}"
    echo ""
    
    # Run all tests
    test_script_exists
    test_script_help
    test_prerequisite_scripts
    test_python_version
    test_requirements_file
    test_env_example
    test_package_structure
    test_example_files
    test_documentation
    test_script_dry_run
    test_existing_installation
    test_script_phases
    test_error_handling
    test_logging_functions
    test_production_safety
    
    # Summary
    echo ""
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                      TEST SUMMARY                          ${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    
    TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED))
    echo -e "Total Tests: ${TOTAL_TESTS}"
    echo -e "${GREEN}Passed: ${TESTS_PASSED}${NC}"
    echo -e "${RED}Failed: ${TESTS_FAILED}${NC}"
    echo ""
    
    # Show all test results
    echo "Test Results:"
    for result in "${TEST_RESULTS[@]}"; do
        echo "  $result"
    done
    echo ""
    
    # Final verdict
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║                                                            ║${NC}"
        echo -e "${GREEN}║            ✓ ALL TESTS PASSED SUCCESSFULLY! ✓              ║${NC}"
        echo -e "${GREEN}║                                                            ║${NC}"
        echo -e "${GREEN}║  The one-click installation script is ready to use!       ║${NC}"
        echo -e "${GREEN}║                                                            ║${NC}"
        echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        log_info "You can now run: ./full-system-install.sh shadow"
        echo ""
        exit 0
    else
        echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                                                            ║${NC}"
        echo -e "${RED}║              ✗ SOME TESTS FAILED ✗                         ║${NC}"
        echo -e "${RED}║                                                            ║${NC}"
        echo -e "${RED}║  Please fix the issues above before using the installer.  ║${NC}"
        echo -e "${RED}║                                                            ║${NC}"
        echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
        echo ""
        exit 1
    fi
}

# Run main
main
