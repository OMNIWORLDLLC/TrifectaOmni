#!/usr/bin/env python3
"""
TrifectaOmni Live Demo
Real-time market data streaming with AI predictions and shadow trading
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np
import pandas as pd
import yfinance as yf
from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import redis.asyncio as redis

# Import TrifectaOmni components
from omni_trifecta.data.price_feeds import UnifiedDataFeed
from omni_trifecta.prediction.sequence_models import LSTMPredictor, TransformerPredictor
from omni_trifecta.decision.master_governor import MasterDecisionGovernor
from omni_trifecta.execution.oms import OrderManagementSystem
from omni_trifecta.safety.managers import RiskManager
from omni_trifecta.fibonacci.engines import FibonacciResonanceEngine
from omni_trifecta.learning.orchestrator import LearningOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/live_demo.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="TrifectaOmni Live Demo")

# Global state
SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'SPY']
UPDATE_INTERVAL = 60  # seconds
active_connections: List[WebSocket] = []
redis_client = None


class LiveDemoOrchestrator:
    """Orchestrates the live demo with real data streaming"""
    
    def __init__(self):
        self.symbols = SYMBOLS
        self.data_feed = None
        self.predictors = {}
        self.governor = None
        self.oms = None
        self.risk_manager = None
        self.fib_engine = None
        self.learning_orchestrator = None
        
        self.market_data = {symbol: [] for symbol in self.symbols}
        self.predictions = {symbol: [] for symbol in self.symbols}
        self.positions = {}
        self.metrics = {
            'total_signals': 0,
            'buy_signals': 0,
            'sell_signals': 0,
            'portfolio_value': 100000.0,
            'cash': 100000.0,
            'unrealized_pnl': 0.0,
            'realized_pnl': 0.0,
            'win_rate': 0.0,
            'sharpe_ratio': 0.0
        }
        
        self.historical_portfolio_values = []
        self.trade_history = []
        
        logger.info("LiveDemoOrchestrator initialized")
    
    async def initialize(self):
        """Initialize all components"""
        logger.info("Initializing system components...")
        
        # Initialize data feed
        self.data_feed = UnifiedDataFeed()
        
        # Initialize predictors
        self.predictors['lstm'] = LSTMPredictor(
            input_size=10,
            hidden_size=64,
            num_layers=2
        )
        self.predictors['transformer'] = TransformerPredictor(
            input_dim=10,
            model_dim=64,
            num_heads=4,
            num_layers=2
        )
        
        # Initialize Fibonacci engine
        self.fib_engine = FibonacciResonanceEngine()
        
        # Initialize risk manager
        self.risk_manager = RiskManager(
            max_position_size=0.2,
            max_portfolio_risk=0.05,
            stop_loss_pct=0.02
        )
        
        # Initialize OMS
        self.oms = OrderManagementSystem(
            initial_capital=100000.0,
            shadow_mode=True  # No real executions
        )
        
        # Initialize decision governor
        self.governor = MasterDecisionGovernor(
            risk_manager=self.risk_manager,
            oms=self.oms
        )
        
        # Initialize learning orchestrator
        self.learning_orchestrator = LearningOrchestrator()
        
        logger.info("All components initialized successfully")
    
    async def fetch_market_data(self) -> Dict[str, pd.DataFrame]:
        """Fetch latest market data for all symbols"""
        data = {}
        
        for symbol in self.symbols:
            try:
                ticker = yf.Ticker(symbol)
                # Get last 100 bars of 1-minute data
                df = ticker.history(period='1d', interval='1m')
                
                if not df.empty:
                    data[symbol] = df
                    
                    # Store in memory
                    latest = {
                        'timestamp': df.index[-1].isoformat(),
                        'open': float(df['Open'].iloc[-1]),
                        'high': float(df['High'].iloc[-1]),
                        'low': float(df['Low'].iloc[-1]),
                        'close': float(df['Close'].iloc[-1]),
                        'volume': int(df['Volume'].iloc[-1])
                    }
                    
                    self.market_data[symbol].append(latest)
                    
                    # Keep only last 500 data points
                    if len(self.market_data[symbol]) > 500:
                        self.market_data[symbol] = self.market_data[symbol][-500:]
                    
                    logger.debug(f"Fetched data for {symbol}: ${latest['close']:.2f}")
                
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
        
        return data
    
    def generate_predictions(self, symbol: str, data: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictions using AI models"""
        try:
            # Prepare features
            features = self._prepare_features(data)
            
            if len(features) < 50:
                return None
            
            # LSTM prediction
            lstm_pred = self._predict_lstm(features)
            
            # Transformer prediction
            transformer_pred = self._predict_transformer(features)
            
            # Ensemble prediction
            ensemble_pred = (lstm_pred + transformer_pred) / 2
            
            # Calculate confidence
            confidence = 1.0 - abs(lstm_pred - transformer_pred)
            
            current_price = float(data['Close'].iloc[-1])
            predicted_price = current_price * (1 + ensemble_pred)
            
            prediction = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'current_price': current_price,
                'predicted_price': predicted_price,
                'predicted_change': ensemble_pred * 100,
                'confidence': confidence,
                'lstm_prediction': lstm_pred * 100,
                'transformer_prediction': transformer_pred * 100,
                'direction': 'BUY' if ensemble_pred > 0.002 else 'SELL' if ensemble_pred < -0.002 else 'HOLD'
            }
            
            self.predictions[symbol].append(prediction)
            
            # Keep only last 100 predictions
            if len(self.predictions[symbol]) > 100:
                self.predictions[symbol] = self.predictions[symbol][-100:]
            
            return prediction
            
        except Exception as e:
            logger.error(f"Error generating predictions for {symbol}: {e}")
            return None
    
    def _prepare_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for prediction"""
        df = data.copy()
        
        # Calculate technical indicators
        df['returns'] = df['Close'].pct_change()
        df['sma_20'] = df['Close'].rolling(20).mean()
        df['sma_50'] = df['Close'].rolling(50).mean()
        df['rsi'] = self._calculate_rsi(df['Close'], 14)
        df['macd'] = df['Close'].ewm(span=12).mean() - df['Close'].ewm(span=26).mean()
        df['bb_upper'] = df['Close'].rolling(20).mean() + 2 * df['Close'].rolling(20).std()
        df['bb_lower'] = df['Close'].rolling(20).mean() - 2 * df['Close'].rolling(20).std()
        df['volume_sma'] = df['Volume'].rolling(20).mean()
        
        # Normalize features
        features = df[['returns', 'rsi', 'macd', 'volume_sma']].fillna(0).values[-50:]
        
        # Simple normalization
        features = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)
        
        return features
    
    def _calculate_rsi(self, prices, period=14):
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
    
    def _predict_lstm(self, features: np.ndarray) -> float:
        """Mock LSTM prediction"""
        # Simple momentum-based prediction for demo
        recent_trend = features[-10:, 0].mean()  # Average recent returns
        return np.tanh(recent_trend * 10) * 0.01  # Scale to reasonable range
    
    def _predict_transformer(self, features: np.ndarray) -> float:
        """Mock Transformer prediction"""
        # Simple volatility-adjusted prediction for demo
        volatility = features[:, 0].std()
        trend = features[-5:, 0].mean()
        return np.tanh(trend / (volatility + 1e-8)) * 0.01
    
    async def generate_trading_signals(self, symbol: str, prediction: Dict) -> Dict[str, Any]:
        """Generate trading signals based on predictions and Fibonacci levels"""
        try:
            if prediction is None:
                return None
            
            current_price = prediction['current_price']
            predicted_change = prediction['predicted_change']
            confidence = prediction['confidence']
            
            # Calculate Fibonacci levels
            recent_data = self.market_data[symbol][-100:]
            if len(recent_data) < 50:
                return None
            
            prices = [d['close'] for d in recent_data]
            high = max(prices)
            low = min(prices)
            
            fib_levels = self.fib_engine.calculate_levels(high, low)
            
            # Generate signal
            signal = None
            signal_strength = 0
            
            if predicted_change > 0.5 and confidence > 0.6:
                # Check if near Fibonacci support
                if any(abs(current_price - level) / current_price < 0.01 for level in fib_levels['support']):
                    signal = 'BUY'
                    signal_strength = min(confidence * abs(predicted_change) / 2, 1.0)
            elif predicted_change < -0.5 and confidence > 0.6:
                # Check if near Fibonacci resistance
                if any(abs(current_price - level) / current_price < 0.01 for level in fib_levels['resistance']):
                    signal = 'SELL'
                    signal_strength = min(confidence * abs(predicted_change) / 2, 1.0)
            
            if signal:
                self.metrics['total_signals'] += 1
                if signal == 'BUY':
                    self.metrics['buy_signals'] += 1
                elif signal == 'SELL':
                    self.metrics['sell_signals'] += 1
                
                # Execute in shadow mode
                await self._execute_shadow_trade(symbol, signal, signal_strength, current_price)
            
            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'signal': signal or 'HOLD',
                'strength': signal_strength,
                'price': current_price,
                'fibonacci_levels': fib_levels,
                'reason': f"Prediction: {predicted_change:.2f}%, Confidence: {confidence:.2f}"
            }
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    async def _execute_shadow_trade(self, symbol: str, signal: str, strength: float, price: float):
        """Execute trade in shadow mode (no real execution)"""
        try:
            position_size = self.metrics['cash'] * 0.1 * strength  # 10% of cash * signal strength
            shares = int(position_size / price)
            
            if shares <= 0:
                return
            
            if signal == 'BUY':
                cost = shares * price
                if cost <= self.metrics['cash']:
                    self.positions[symbol] = self.positions.get(symbol, 0) + shares
                    self.metrics['cash'] -= cost
                    
                    trade = {
                        'timestamp': datetime.now().isoformat(),
                        'symbol': symbol,
                        'action': 'BUY',
                        'shares': shares,
                        'price': price,
                        'cost': cost
                    }
                    self.trade_history.append(trade)
                    
                    logger.info(f"SHADOW BUY: {shares} shares of {symbol} @ ${price:.2f}")
            
            elif signal == 'SELL' and symbol in self.positions and self.positions[symbol] > 0:
                shares_to_sell = min(shares, self.positions[symbol])
                proceeds = shares_to_sell * price
                
                # Calculate P&L
                avg_cost = self._get_average_cost(symbol)
                pnl = (price - avg_cost) * shares_to_sell
                
                self.positions[symbol] -= shares_to_sell
                self.metrics['cash'] += proceeds
                self.metrics['realized_pnl'] += pnl
                
                if self.positions[symbol] == 0:
                    del self.positions[symbol]
                
                trade = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'action': 'SELL',
                    'shares': shares_to_sell,
                    'price': price,
                    'proceeds': proceeds,
                    'pnl': pnl
                }
                self.trade_history.append(trade)
                
                logger.info(f"SHADOW SELL: {shares_to_sell} shares of {symbol} @ ${price:.2f} (P&L: ${pnl:.2f})")
            
            # Update portfolio value
            await self._update_portfolio_value()
            
        except Exception as e:
            logger.error(f"Error executing shadow trade: {e}")
    
    def _get_average_cost(self, symbol: str) -> float:
        """Get average cost of position (simplified)"""
        # In real implementation, track actual cost basis
        recent_trades = [t for t in self.trade_history if t['symbol'] == symbol and t['action'] == 'BUY']
        if recent_trades:
            return recent_trades[-1]['price']
        return 0.0
    
    async def _update_portfolio_value(self):
        """Update portfolio metrics"""
        try:
            # Calculate unrealized P&L
            unrealized_pnl = 0
            for symbol, shares in self.positions.items():
                if self.market_data[symbol]:
                    current_price = self.market_data[symbol][-1]['close']
                    avg_cost = self._get_average_cost(symbol)
                    unrealized_pnl += (current_price - avg_cost) * shares
            
            self.metrics['unrealized_pnl'] = unrealized_pnl
            self.metrics['portfolio_value'] = self.metrics['cash'] + sum(
                self.market_data[s][-1]['close'] * shares
                for s, shares in self.positions.items()
                if self.market_data[s]
            )
            
            self.historical_portfolio_values.append({
                'timestamp': datetime.now().isoformat(),
                'value': self.metrics['portfolio_value']
            })
            
            # Calculate returns
            if len(self.historical_portfolio_values) > 1:
                returns = [
                    (self.historical_portfolio_values[i]['value'] - self.historical_portfolio_values[i-1]['value']) / 
                    self.historical_portfolio_values[i-1]['value']
                    for i in range(1, len(self.historical_portfolio_values))
                ]
                
                if returns:
                    avg_return = np.mean(returns)
                    std_return = np.std(returns)
                    self.metrics['sharpe_ratio'] = (avg_return / std_return * np.sqrt(252)) if std_return > 0 else 0
            
            # Calculate win rate
            winning_trades = sum(1 for t in self.trade_history if t.get('pnl', 0) > 0)
            total_trades = len([t for t in self.trade_history if t['action'] == 'SELL'])
            self.metrics['win_rate'] = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
        except Exception as e:
            logger.error(f"Error updating portfolio value: {e}")
    
    async def run_streaming_loop(self):
        """Main streaming loop"""
        logger.info("Starting live data streaming loop...")
        
        while True:
            try:
                # Fetch market data
                market_data = await self.fetch_market_data()
                
                # Process each symbol
                for symbol, data in market_data.items():
                    if data.empty:
                        continue
                    
                    # Generate predictions
                    prediction = self.generate_predictions(symbol, data)
                    
                    # Generate trading signals
                    signal = await self.generate_trading_signals(symbol, prediction)
                    
                    # Broadcast updates to connected clients
                    await self.broadcast_update({
                        'type': 'market_update',
                        'symbol': symbol,
                        'data': self.market_data[symbol][-1] if self.market_data[symbol] else None,
                        'prediction': prediction,
                        'signal': signal,
                        'metrics': self.metrics,
                        'positions': self.positions
                    })
                
                # Wait before next update
                await asyncio.sleep(UPDATE_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error in streaming loop: {e}")
                await asyncio.sleep(5)
    
    async def broadcast_update(self, data: Dict):
        """Broadcast update to all connected WebSocket clients"""
        if not active_connections:
            return
        
        message = json.dumps(data)
        disconnected = []
        
        for connection in active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            active_connections.remove(conn)


# Initialize orchestrator
orchestrator = LiveDemoOrchestrator()


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Starting TrifectaOmni Live Demo...")
    await orchestrator.initialize()
    
    # Start streaming loop
    asyncio.create_task(orchestrator.run_streaming_loop())
    
    logger.info("Live demo is running!")


@app.get("/")
async def get_dashboard():
    """Serve the main dashboard"""
    with open("dashboard/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    active_connections.append(websocket)
    
    logger.info(f"New WebSocket connection. Total connections: {len(active_connections)}")
    
    # Send initial state
    initial_data = {
        'type': 'initial_state',
        'symbols': orchestrator.symbols,
        'metrics': orchestrator.metrics,
        'positions': orchestrator.positions,
        'market_data': {s: orchestrator.market_data[s][-50:] for s in orchestrator.symbols}
    }
    await websocket.send_text(json.dumps(initial_data))
    
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(active_connections)}")


@app.get("/api/status")
async def get_status():
    """Get current system status"""
    return {
        'status': 'running',
        'symbols': orchestrator.symbols,
        'metrics': orchestrator.metrics,
        'positions': orchestrator.positions,
        'active_connections': len(active_connections),
        'uptime': 'N/A'  # Could track actual uptime
    }


@app.get("/api/history")
async def get_history():
    """Get trade history"""
    return {
        'trades': orchestrator.trade_history[-100:],
        'portfolio_values': orchestrator.historical_portfolio_values[-500:]
    }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 TrifectaOmni Live Demo Starting...")
    print("="*70)
    print(f"\n📊 Tracking symbols: {', '.join(SYMBOLS)}")
    print(f"🔄 Update interval: {UPDATE_INTERVAL} seconds")
    print(f"💰 Initial capital: $100,000")
    print(f"🛡️  Mode: SHADOW (No real executions)")
    print(f"\n🌐 Dashboard: http://localhost:8080")
    print(f"📡 WebSocket: ws://localhost:8080/ws")
    print("\n" + "="*70 + "\n")
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Run the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
