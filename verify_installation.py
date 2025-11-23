#!/usr/bin/env python3
"""
TrifectaOmni Installation Verification Script

This script verifies that the TrifectaOmni system is properly installed
and ready to run. It checks:
1. Python version
2. Required packages
3. Module imports
4. Directory structure
5. Configuration files

Run this script after installation to ensure everything is set up correctly.
"""

import sys
import importlib
import os
from pathlib import Path


# Configuration
PYTHON_VERSION_REQUIRED = (3, 10)  # Minimum Python version required


# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print a section header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text:^70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.END}\n")


def print_check(name, passed, message=""):
    """Print a check result"""
    if passed:
        symbol = f"{Colors.GREEN}✓{Colors.END}"
        status = f"{Colors.GREEN}PASS{Colors.END}"
    else:
        symbol = f"{Colors.RED}✗{Colors.END}"
        status = f"{Colors.RED}FAIL{Colors.END}"
    
    print(f"{symbol} {name:.<50} {status}")
    if message:
        print(f"  {Colors.YELLOW}{message}{Colors.END}")


def check_python_version():
    """Check if Python version meets requirements"""
    print_header("Python Version Check")
    
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    passed = version >= PYTHON_VERSION_REQUIRED
    print_check(
        f"Python {version_str}",
        passed,
        f"Required: Python {PYTHON_VERSION_REQUIRED[0]}.{PYTHON_VERSION_REQUIRED[1]}+" if not passed else ""
    )
    
    return passed


def check_packages():
    """Check if required packages are installed"""
    print_header("Required Packages Check")
    
    required_packages = {
        'numpy': 'numpy',
        'pandas': 'pandas',
        'sklearn': 'scikit-learn',
        'onnxruntime': 'onnxruntime',
        'websockets': 'websockets',
        'dotenv': 'python-dotenv',
        'web3': 'web3',
        'aiohttp': 'aiohttp',
        'ccxt': 'ccxt',
    }
    
    all_passed = True
    
    for module_name, package_name in required_packages.items():
        try:
            importlib.import_module(module_name)
            print_check(package_name, True)
        except ImportError:
            print_check(package_name, False, f"Install with: pip install {package_name}")
            all_passed = False
    
    return all_passed


def check_omni_modules():
    """Check if omni_trifecta modules can be imported"""
    print_header("OmniTrifecta Modules Check")
    
    # Core modules that must be importable
    core_modules = [
        'omni_trifecta.core.config',
        'omni_trifecta.data.price_feeds',
        'omni_trifecta.fibonacci.master_governor',
        'omni_trifecta.decision.master_governor',
        'omni_trifecta.execution.executors',
        'omni_trifecta.safety.managers',
        'omni_trifecta.learning.orchestrator',
        'omni_trifecta.runtime.orchestration',
    ]
    
    # Optional modules
    optional_modules = [
        'omni_trifecta.prediction.sequence_models',
    ]
    
    all_passed = True
    
    for module in core_modules:
        try:
            importlib.import_module(module)
            print_check(module, True)
        except ImportError as e:
            print_check(module, False, str(e))
            all_passed = False
    
    for module in optional_modules:
        try:
            importlib.import_module(module)
            print_check(f"{module} (optional)", True)
        except ImportError:
            print_check(f"{module} (optional)", True, "Not found (optional)")
    
    return all_passed


def check_directory_structure():
    """Check if required directories exist"""
    print_header("Directory Structure Check")
    
    required_dirs = [
        'omni_trifecta',
        'examples',
        'scripts',
        'omni_trifecta/core',
        'omni_trifecta/data',
        'omni_trifecta/prediction',
        'omni_trifecta/fibonacci',
        'omni_trifecta/decision',
        'omni_trifecta/execution',
        'omni_trifecta/safety',
        'omni_trifecta/learning',
        'omni_trifecta/runtime',
    ]
    
    all_passed = True
    project_root = Path(__file__).parent
    
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        exists = full_path.exists() and full_path.is_dir()
        print_check(dir_path, exists, f"Path: {full_path}" if not exists else "")
        if not exists:
            all_passed = False
    
    return all_passed


def check_configuration_files():
    """Check if configuration files exist"""
    print_header("Configuration Files Check")
    
    project_root = Path(__file__).parent
    
    files = {
        'requirements.txt': True,  # Required
        '.env.example': True,      # Required
        '.env': False,             # Optional
        'README.md': True,         # Required
        'SETUP.md': True,          # Required
        'QUICKSTART.md': True,     # Required
        'STATUS.md': True,         # Required
    }
    
    all_passed = True
    
    for filename, required in files.items():
        full_path = project_root / filename
        exists = full_path.exists() and full_path.is_file()
        
        if required:
            print_check(filename, exists, "REQUIRED" if not exists else "")
            if not exists:
                all_passed = False
        else:
            status_text = "Present" if exists else "Not configured (optional)"
            print_check(filename, True, status_text)
    
    return all_passed


def check_example_scripts():
    """Check if example scripts exist and are executable"""
    print_header("Example Scripts Check")
    
    project_root = Path(__file__).parent
    examples_dir = project_root / 'examples'
    
    scripts = [
        'shadow_mode_example.py',
        'production_ready_example.py',
        'advanced_integration_example.py',
    ]
    
    all_passed = True
    
    for script in scripts:
        full_path = examples_dir / script
        exists = full_path.exists() and full_path.is_file()
        print_check(script, exists, f"Path: {full_path}" if not exists else "")
        if not exists:
            all_passed = False
    
    return all_passed


def run_basic_import_test():
    """Try to run a basic import test"""
    print_header("Basic System Import Test")
    
    all_passed = True
    
    # Test imports individually for better error reporting
    imports = [
        ('omni_trifecta.decision.master_governor', 'MasterGovernorX100'),
        ('omni_trifecta.execution.executors', 'ShadowExecutionHub'),
        ('omni_trifecta.safety.managers', 'SafetyManager'),
        ('omni_trifecta.runtime.orchestration', 'OmniRuntime'),
    ]
    
    components = {}
    
    for module_name, class_name in imports:
        try:
            module = importlib.import_module(module_name)
            components[class_name] = getattr(module, class_name)
            print_check(f"Import {class_name}", True)
        except Exception as e:
            print_check(f"Import {class_name}", False, str(e))
            all_passed = False
            return False
    
    # Try to instantiate if imports succeeded
    try:
        governor = components['MasterGovernorX100']()
        print_check("Instantiate MasterGovernorX100", True)
    except Exception as e:
        print_check("Instantiate MasterGovernorX100", False, str(e))
        all_passed = False
    
    try:
        hub = components['ShadowExecutionHub']()
        print_check("Instantiate ShadowExecutionHub", True)
    except Exception as e:
        print_check("Instantiate ShadowExecutionHub", False, str(e))
        all_passed = False
    
    try:
        safety = components['SafetyManager'](max_daily_loss=100, max_daily_trades=50, max_loss_streak=5)
        print_check("Instantiate SafetyManager", True)
    except Exception as e:
        print_check("Instantiate SafetyManager", False, str(e))
        all_passed = False
    
    return all_passed


def main():
    """Run all verification checks"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║        TrifectaOmni Installation Verification Script              ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Required Packages", check_packages),
        ("OmniTrifecta Modules", check_omni_modules),
        ("Directory Structure", check_directory_structure),
        ("Configuration Files", check_configuration_files),
        ("Example Scripts", check_example_scripts),
        ("Basic System Import", run_basic_import_test),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            passed = check_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n{Colors.RED}Error during {name}: {e}{Colors.END}")
            results.append((name, False))
    
    # Summary
    print_header("Verification Summary")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    failed = total - passed
    
    for name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {name:.<50} {status}")
    
    print(f"\n{Colors.BOLD}Total Checks: {total}{Colors.END}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {failed}{Colors.END}\n")
    
    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All checks passed!{Colors.END}")
        print(f"{Colors.GREEN}The TrifectaOmni system is properly installed and ready to run.{Colors.END}\n")
        print(f"{Colors.CYAN}Next steps:{Colors.END}")
        print(f"  1. Run shadow mode example: python examples/shadow_mode_example.py")
        print(f"  2. Configure .env file for live trading (see .env.example)")
        print(f"  3. Read SETUP.md for detailed usage instructions\n")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some checks failed!{Colors.END}")
        print(f"{Colors.YELLOW}Please resolve the issues above before running the system.{Colors.END}")
        print(f"{Colors.CYAN}If you need help:{Colors.END}")
        print(f"  - Check requirements.txt for package versions")
        print(f"  - Run: pip install -r requirements.txt")
        print(f"  - See STATUS.md for installation instructions\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
