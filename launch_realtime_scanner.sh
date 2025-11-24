#!/bin/bash
# TrifectaOmni Real-Time Multi-Asset Scanner - Quick Launch Script

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   🎯 TrifectaOmni - Real-Time Multi-Asset Scanner           ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""
echo "Scanning for:"
echo "  💎 Cryptocurrency Arbitrage (2-hop, 3-hop, cross-chain)"
echo "  💱 Forex Trading Opportunities (All major USD pairs)"
echo "  ⚡ Binary Options Opportunities (60-second expiry)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if running in workspace
if [ ! -d "/workspaces/TrifectaOmni" ]; then
    echo "⚠️  Warning: Not in expected workspace directory"
fi

# Navigate to project root
cd /workspaces/TrifectaOmni

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check/activate virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q yfinance fastapi uvicorn websockets numpy pandas 2>/dev/null || {
    echo "⚠️  Some packages may already be installed"
}

# Create logs directory
mkdir -p logs

# Check if dashboard directory exists
if [ ! -d "dashboard" ]; then
    echo "⚠️  Dashboard directory not found, creating..."
    mkdir -p dashboard
fi

# Verify files exist
if [ ! -f "realtime_multi_asset_demo.py" ]; then
    echo "❌ Error: realtime_multi_asset_demo.py not found"
    exit 1
fi

if [ ! -f "dashboard/realtime_scanner.html" ]; then
    echo "❌ Error: dashboard/realtime_scanner.html not found"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 Starting Real-Time Scanner..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Dashboard will be available at:"
echo ""
echo "    🌐 http://localhost:8080"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Press Ctrl+C to stop the scanner"
echo ""

# Small delay for readability
sleep 2

# Launch the scanner
python3 realtime_multi_asset_demo.py
