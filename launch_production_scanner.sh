#!/bin/bash

# TrifectaOmni - Production Real-Time Scanner Launcher
# Uses real APIs from .env configuration

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║     🚀 TrifectaOmni - PRODUCTION Scanner Launcher              ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo ""
    echo "You have two options:"
    echo ""
    echo "1️⃣  DEMO MODE (Free, Delayed Data)"
    echo "   • Uses Yahoo Finance (free)"
    echo "   • ~60 second delay"
    echo "   • No configuration needed"
    echo "   • Good for learning/testing"
    echo ""
    echo "   Run: ./launch_realtime_scanner.sh"
    echo ""
    echo "2️⃣  PRODUCTION MODE (Real-Time APIs)"
    echo "   • Uses MT5, CCXT, DEX RPC, Pocket Option"
    echo "   • <1 second latency"
    echo "   • Requires API configuration"
    echo "   • Production-grade reliability"
    echo ""
    echo "   Setup: cp .env.example .env"
    echo "   Then configure your API keys in .env"
    echo "   See: PRODUCTION_API_SETUP.md"
    echo ""
    read -p "Continue with demo mode? (y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Exiting. Please setup .env first."
        exit 1
    fi
    echo ""
    echo "📊 Starting in DEMO MODE (Yahoo Finance data)..."
    PRODUCTION_MODE=false
else
    echo "✅ .env file found"
    echo ""
    
    # Check which APIs are configured
    source .env
    
    echo "📡 Checking API Configuration..."
    echo ""
    
    API_CONFIGURED=false
    
    if [ -n "$MT5_LOGIN" ] && [ -n "$MT5_SERVER" ] && [ -n "$MT5_PASSWORD" ]; then
        echo "✅ MetaTrader 5 (Forex): CONFIGURED"
        API_CONFIGURED=true
    else
        echo "⚪ MetaTrader 5 (Forex): Not configured"
    fi
    
    if command -v python3 -c "import ccxt" &> /dev/null; then
        echo "✅ CCXT (Crypto): AVAILABLE"
        API_CONFIGURED=true
    else
        echo "⚪ CCXT (Crypto): Not installed (pip install ccxt)"
    fi
    
    if [ -n "$DEX_RPC" ]; then
        echo "✅ DEX/Blockchain: CONFIGURED"
        API_CONFIGURED=true
    else
        echo "⚪ DEX/Blockchain: Not configured"
    fi
    
    if [ -n "$POCKET_TOKEN" ]; then
        echo "✅ Pocket Option (Binary): CONFIGURED"
        API_CONFIGURED=true
    else
        echo "⚪ Pocket Option (Binary): Not configured"
    fi
    
    echo ""
    
    if [ "$API_CONFIGURED" = true ]; then
        echo "🚀 Starting in PRODUCTION MODE..."
        PRODUCTION_MODE=true
    else
        echo "⚠️  No APIs configured in .env"
        echo ""
        read -p "Start in demo mode instead? (y/N): " confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            echo "Exiting. Please configure APIs in .env"
            echo "See: PRODUCTION_API_SETUP.md"
            exit 1
        fi
        echo ""
        echo "📊 Starting in DEMO MODE..."
        PRODUCTION_MODE=false
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "⚠️  No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install/upgrade dependencies
echo ""
echo "📦 Checking dependencies..."

# Core dependencies
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Production-specific dependencies
if [ "$PRODUCTION_MODE" = true ]; then
    echo "📦 Installing production dependencies..."
    pip install -q ccxt python-dotenv aiohttp websockets 2>/dev/null || true
    
    # Try to install MT5 (may fail on non-Windows, that's ok)
    pip install -q MetaTrader5 2>/dev/null || echo "⚪ MT5 requires Windows/Wine"
    
    # Try to install web3 for DEX
    pip install -q web3 2>/dev/null || true
fi

echo "✅ Dependencies ready"
echo ""

# Create logs directory
mkdir -p logs

# Create dashboard directory if needed
mkdir -p dashboard

# Check if dashboard HTML exists
if [ ! -f "dashboard/realtime_scanner.html" ]; then
    echo "⚠️  Dashboard HTML not found at dashboard/realtime_scanner.html"
    echo "The scanner will still work, but no web dashboard will be available."
    echo ""
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Dashboard will be available at: http://localhost:8080"
echo "📊 Health check endpoint: http://localhost:8080/health"
echo ""
echo "Press Ctrl+C to stop the scanner"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Launch appropriate scanner
if [ "$PRODUCTION_MODE" = true ]; then
    python3 realtime_multi_asset_demo_production.py
else
    python3 realtime_multi_asset_demo.py
fi
