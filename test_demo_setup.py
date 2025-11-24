#!/usr/bin/env python3
"""
Quick test to verify the live demo components are properly configured
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("\n" + "="*70)
    print("TESTING MODULE IMPORTS")
    print("="*70)
    
    test_modules = [
        ('numpy', 'NumPy'),
        ('pandas', 'Pandas'),
        ('torch', 'PyTorch'),
        ('tensorflow', 'TensorFlow'),
        ('yfinance', 'Yahoo Finance'),
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('websockets', 'WebSockets'),
    ]
    
    failed = []
    for module, name in test_modules:
        try:
            __import__(module)
            print(f"✓ {name:20} OK")
        except ImportError:
            print(f"✗ {name:20} FAILED")
            failed.append(name)
    
    return len(failed) == 0

def test_trifecta_modules():
    """Test TrifectaOmni modules"""
    print("\n" + "="*70)
    print("TESTING TRIFECTAOMNI MODULES")
    print("="*70)
    
    test_modules = [
        ('omni_trifecta.data.price_feeds', 'Data Feeds'),
        ('omni_trifecta.prediction.sequence_models', 'Prediction Models'),
        ('omni_trifecta.decision.master_governor', 'Decision Governor'),
        ('omni_trifecta.execution.oms', 'Order Management'),
        ('omni_trifecta.fibonacci.engines', 'Fibonacci Engine'),
        ('omni_trifecta.safety.managers', 'Risk Manager'),
        ('omni_trifecta.learning.orchestrator', 'Learning Orchestrator'),
    ]
    
    failed = []
    for module, name in test_modules:
        try:
            __import__(module)
            print(f"✓ {name:25} OK")
        except ImportError as e:
            print(f"✗ {name:25} FAILED ({e})")
            failed.append(name)
    
    return len(failed) == 0

def test_files():
    """Test that required files exist"""
    print("\n" + "="*70)
    print("TESTING FILE STRUCTURE")
    print("="*70)
    
    required_files = [
        'live_demo.py',
        'dashboard/index.html',
        'one_click_install.sh',
        'build_and_run_demo.sh',
    ]
    
    failed = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file:40} EXISTS")
        else:
            print(f"✗ {file:40} MISSING")
            failed.append(file)
    
    return len(failed) == 0

def test_directories():
    """Test that required directories exist"""
    print("\n" + "="*70)
    print("TESTING DIRECTORY STRUCTURE")
    print("="*70)
    
    required_dirs = [
        'omni_trifecta',
        'omni_trifecta/data',
        'omni_trifecta/prediction',
        'omni_trifecta/decision',
        'omni_trifecta/execution',
        'omni_trifecta/fibonacci',
        'omni_trifecta/safety',
        'dashboard',
    ]
    
    failed = []
    for dir in required_dirs:
        if os.path.isdir(dir):
            print(f"✓ {dir:40} EXISTS")
        else:
            print(f"✗ {dir:40} MISSING")
            failed.append(dir)
    
    return len(failed) == 0

def main():
    print("\n" + "="*70)
    print("TRIFECTAOMNI LIVE DEMO - VERIFICATION TEST")
    print("="*70)
    
    tests = [
        ("Import Test", test_imports),
        ("TrifectaOmni Modules", test_trifecta_modules),
        ("File Structure", test_files),
        ("Directory Structure", test_directories),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} failed with error: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    all_passed = True
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {name:30} {status}")
        if not result:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED! Ready to run the live demo.")
        print("\nTo start the demo, run:")
        print("    ./build_and_run_demo.sh")
        print("\nOr manually:")
        print("    source venv/bin/activate")
        print("    python3 live_demo.py")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED. Please run the installation:")
        print("    ./one_click_install.sh")
        return 1

if __name__ == "__main__":
    sys.exit(main())
