#!/usr/bin/env python3
"""
TrifectaOmni - PRODUCTION Real-Time Multi-Asset Opportunity Scanner

Uses REAL APIs from .env configuration:
1. Cryptocurrency Arbitrage - CCXT (Binance, Kraken, etc.) + DEX RPC
2. Forex Trading - MetaTrader 5 (MT5) for real-time spot forex
3. Binary Options - Pocket Option API for binary signals

Real-time WebSocket streaming with LIVE market data from configured endpoints.
"""

import asyncio
import json
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from decimal import Decimal
import numpy as np
import pandas as pd
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
from dotenv import load_dotenv

# Import TrifectaOmni components
from omni_trifecta.execution.arbitrage_calculator import (
    MultiHopArbitrageCalculator,
    Exchange,
    TradingPair,
    ArbitrageRoute
)
from omni_trifecta.execution.token_equivalence import TOKEN_REGISTRY, ChainId
from omni_trifecta.execution.executors import ArbitrageExecutor, ForexExecutor
from omni_trifecta.execution.oms import OrderManagementSystem, Order, OrderType, OrderSide
from omni_trifecta.decision.master_governor import MasterGovernorX100
from omni_trifecta.decision.rl_agents import ArbitrageRLAgent, ForexRLAgent
from omni_trifecta.safety.managers import RiskManager
# from omni_trifecta.prediction.sequence_models import LSTMPredictor, TransformerPredictor  # Optional - not essential
# from omni_trifecta.fibonacci.engines import FibonacciResonanceEngine  # Optional - not essential
from omni_trifecta.data.price_feeds import CCXTPriceFeedAdapter, MT5PriceFeedAdapter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/realtime_production.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="TrifectaOmni - PRODUCTION Real-Time Multi-Asset Scanner")

# Forex pairs - All majors involving USD (G7 + majors)
FOREX_PAIRS = [
    'EURUSD',  # Euro (MT5 format)
    'GBPUSD',  # British Pound
    'USDJPY',  # Japanese Yen
    'AUDUSD',  # Australian Dollar
    'USDCAD',  # Canadian Dollar
    'USDCHF',  # Swiss Franc
    'NZDUSD',  # New Zealand Dollar
]

# Crypto pairs for arbitrage (CCXT format)
CRYPTO_PAIRS = [
    'BTC/USDT',
    'ETH/USDT',
    'BNB/USDT',
    'ADA/USDT',
    'SOL/USDT',
    'MATIC/USDT',
    'AVAX/USDT',
]

# Exchanges to scan for arbitrage (via CCXT)
EXCHANGES = ['binance', 'kraken', 'coinbase', 'bitfinex']

# Update intervals
ARBITRAGE_SCAN_INTERVAL = 30  # seconds
FOREX_SCAN_INTERVAL = 5       # seconds (MT5 is fast!)
BINARY_SCAN_INTERVAL = 10     # seconds
BROADCAST_INTERVAL = 10       # seconds

# Active WebSocket connections
active_connections: List[WebSocket] = []


class ProductionDataProvider:
    """Production data provider using real APIs from .env"""
    
    def __init__(self):
        """Initialize production data connections."""
        self.mt5_enabled = False
        self.ccxt_enabled = False
        self.dex_enabled = False
        self.pocket_enabled = False
        
        # MT5 configuration
        self.mt5_login = os.getenv('MT5_LOGIN')
        self.mt5_server = os.getenv('MT5_SERVER')
        self.mt5_password = os.getenv('MT5_PASSWORD')
        
        # DEX configuration
        self.dex_rpc = os.getenv('DEX_RPC')
        self.dex_privkey = os.getenv('DEX_PRIVKEY')
        
        # Pocket Option configuration
        self.pocket_token = os.getenv('POCKET_TOKEN')
        self.pocket_base_url = os.getenv('POCKET_BASE_URL', 'https://api.po.trade')
        
        # Initialize connections
        self._initialize_connections()
        
        # CCXT exchanges cache
        self.ccxt_exchanges = {}
        
    def _initialize_connections(self):
        """Initialize API connections based on .env configuration."""
        
        # Check MT5
        if self.mt5_login and self.mt5_server and self.mt5_password:
            try:
                import MetaTrader5 as MT5
                if MT5.initialize(
                    login=int(self.mt5_login),
                    server=self.mt5_server,
                    password=self.mt5_password
                ):
                    self.mt5_enabled = True
                    logger.info("✅ MetaTrader 5 connected successfully")
                else:
                    logger.warning("⚠️ MT5 credentials found but connection failed")
            except Exception as e:
                logger.warning(f"⚠️ MT5 not available: {e}")
        else:
            logger.info("ℹ️ MT5 credentials not configured in .env")
        
        # Check CCXT
        try:
            import ccxt
            self.ccxt_enabled = True
            logger.info("✅ CCXT library available")
        except ImportError:
            logger.warning("⚠️ CCXT not installed: pip install ccxt")
        
        # Check DEX
        if self.dex_rpc and self.dex_privkey:
            try:
                from web3 import Web3
                w3 = Web3(Web3.HTTPProvider(self.dex_rpc))
                if w3.is_connected():
                    self.dex_enabled = True
                    logger.info("✅ DEX RPC connected successfully")
                else:
                    logger.warning("⚠️ DEX RPC configured but connection failed")
            except Exception as e:
                logger.warning(f"⚠️ DEX not available: {e}")
        else:
            logger.info("ℹ️ DEX credentials not configured in .env")
        
        # Check Pocket Option
        if self.pocket_token:
            self.pocket_enabled = True
            logger.info("✅ Pocket Option API token configured")
        else:
            logger.info("ℹ️ Pocket Option token not configured in .env")
    
    def get_ccxt_exchange(self, exchange_id: str):
        """Get or create CCXT exchange instance."""
        if exchange_id not in self.ccxt_exchanges:
            try:
                import ccxt
                exchange_class = getattr(ccxt, exchange_id)
                self.ccxt_exchanges[exchange_id] = exchange_class({
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                })
            except Exception as e:
                logger.error(f"Failed to initialize {exchange_id}: {e}")
                return None
        return self.ccxt_exchanges[exchange_id]
    
    async def get_crypto_price_ccxt(self, exchange_id: str, symbol: str) -> Optional[Dict[str, float]]:
        """Get real-time crypto price from exchange via CCXT."""
        if not self.ccxt_enabled:
            return None
        
        try:
            exchange = self.get_ccxt_exchange(exchange_id)
            if not exchange:
                return None
            
            ticker = exchange.fetch_ticker(symbol)
            return {
                'bid': float(ticker['bid']) if ticker['bid'] else None,
                'ask': float(ticker['ask']) if ticker['ask'] else None,
                'last': float(ticker['last']),
                'volume': float(ticker['volume']) if ticker['volume'] else 0,
                'timestamp': ticker['timestamp']
            }
        except Exception as e:
            logger.error(f"Error fetching {symbol} from {exchange_id}: {e}")
            return None
    
    async def get_forex_price_mt5(self, symbol: str) -> Optional[Dict[str, float]]:
        """Get real-time forex price from MetaTrader 5."""
        if not self.mt5_enabled:
            return None
        
        try:
            import MetaTrader5 as MT5
            tick = MT5.symbol_info_tick(symbol)
            if tick:
                return {
                    'bid': tick.bid,
                    'ask': tick.ask,
                    'last': (tick.bid + tick.ask) / 2.0,
                    'spread': tick.ask - tick.bid,
                    'timestamp': tick.time
                }
        except Exception as e:
            logger.error(f"Error fetching {symbol} from MT5: {e}")
            return None
    
    async def get_binary_signals_pocket(self) -> List[Dict[str, Any]]:
        """Get binary options signals from Pocket Option API."""
        if not self.pocket_enabled:
            return []
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                headers = {
                    'Authorization': f'Bearer {self.pocket_token}',
                    'Content-Type': 'application/json'
                }
                async with session.get(
                    f'{self.pocket_base_url}/signals',
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('signals', [])
        except Exception as e:
            logger.error(f"Error fetching Pocket Option signals: {e}")
            return []


class RealTimeProductionScanner:
    """Production real-time multi-asset opportunity scanner with real APIs."""
    
    def __init__(self):
        """Initialize the production scanner."""
        logger.info("Initializing Production Real-Time Scanner...")
        
        # Initialize data provider
        self.data_provider = ProductionDataProvider()
        
        # Initialize arbitrage calculator
        self.arb_calculator = MultiHopArbitrageCalculator(
            min_profit_bps=25.0,
            max_slippage_bps=50.0,
            safety_margin=0.15
        )
        
        # Initialize execution system
        self._initialize_execution_system()
        
        # Opportunity storage
        self.arbitrage_opportunities = []
        self.forex_opportunities = []
        self.binary_opportunities = []
        
        # Statistics
        self.total_scans = 0
        self.scan_start_time = datetime.now()
        
        # Paper trading stats
        self.paper_trades = {
            'arbitrage': {'count': 0, 'pnl': 0.0, 'wins': 0},
            'forex': {'count': 0, 'pnl': 0.0, 'wins': 0},
            'binary': {'count': 0, 'pnl': 0.0, 'wins': 0}
        }
        self.trade_history = []
        
        # Execution control
        self.auto_execute_enabled = os.getenv('AUTO_EXECUTE', 'false').lower() == 'true'
        
        logger.info("✅ Production Scanner initialized successfully")
        self._display_startup_info()
    
    def _initialize_execution_system(self):
        """Initialize full system components for paper execution."""
        try:
            # Order Management System
            self.oms = OrderManagementSystem()
            
            # Risk Manager
            self.risk_manager = RiskManager(
                max_daily_loss=5000.0,
                max_daily_trades=50,
                max_loss_streak=5
            )
            
            # Master Decision Governor
            self.governor = MasterGovernorX100()
            
            # RL Agents
            self.arb_rl_agent = ArbitrageRLAgent()
            self.forex_rl_agent = ForexRLAgent()
            
            # AI Predictors (optional - comment out if not available)
            # self.lstm_predictor = LSTMPredictor()
            # self.transformer_predictor = TransformerPredictor()
            
            # Fibonacci Resonance Engine (optional - comment out if not available)
            # self.fib_engine = FibonacciResonanceEngine()
            
            # Executors
            self.arb_executor = ArbitrageExecutor()
            self.forex_executor = ForexExecutor()
            
            logger.info("✅ Full execution system initialized")
        except Exception as e:
            logger.error(f"Error initializing execution system: {e}")
            raise
    
    def _display_startup_info(self):
        """Display startup configuration and status."""
        print("\n" + "="*80)
        print("🚀 TRIFECTA OMNI - PRODUCTION SCANNER")
        print("="*80)
        print(f"\n⚙️  EXECUTION MODE: {'AUTO-EXECUTE ✅' if self.auto_execute_enabled else 'DISPLAY ONLY 📊'}")
        print("\n📡 API CONNECTION STATUS:")
        print(f"  • MetaTrader 5 (Forex): {'✅ CONNECTED' if self.data_provider.mt5_enabled else '❌ NOT CONFIGURED'}")
        print(f"  • CCXT (Crypto): {'✅ AVAILABLE' if self.data_provider.ccxt_enabled else '❌ NOT INSTALLED'}")
        print(f"  • DEX/Blockchain: {'✅ CONNECTED' if self.data_provider.dex_enabled else '❌ NOT CONFIGURED'}")
        print(f"  • Pocket Option (Binary): {'✅ CONFIGURED' if self.data_provider.pocket_enabled else '❌ NOT CONFIGURED'}")
        
        print("\n🎯 SYSTEM COMPONENTS:")
        print(f"  • OMS (Order Management): ✅ ACTIVE")
        print(f"  • Portfolio Value: $100,000.00")
        print(f"  • Risk Manager: Max Daily Loss ${self.risk_manager.max_daily_loss:.0f}")
        print(f"  • Master Governor: ✅ Active")
        print(f"  • RL Agents: ✅ Arbitrage + Forex")
        print(f"  • Executors: ✅ Arbitrage + Forex")
        
        print("\n📊 SCAN CONFIGURATION:")
        print(f"  • Arbitrage: {len(CRYPTO_PAIRS)} pairs across {len(EXCHANGES)} exchanges (every {ARBITRAGE_SCAN_INTERVAL}s)")
        print(f"  • Forex: {len(FOREX_PAIRS)} pairs via MT5 (every {FOREX_SCAN_INTERVAL}s)")
        print(f"  • Binary: 60s signals via Pocket API (every {BINARY_SCAN_INTERVAL}s)")
        print(f"  • Broadcast: WebSocket updates every {BROADCAST_INTERVAL}s")
        
        print("\n⚠️ IMPORTANT NOTES:")
        if not self.data_provider.mt5_enabled:
            print("  • Configure MT5 in .env for real-time forex data")
        if not self.data_provider.ccxt_enabled:
            print("  • Install CCXT: pip install ccxt")
        if not self.data_provider.dex_enabled:
            print("  • Configure DEX_RPC in .env for on-chain arbitrage")
        if not self.data_provider.pocket_enabled:
            print("  • Configure POCKET_TOKEN in .env for binary options")
        
        print("\n" + "="*80)
        print("🌐 Dashboard: http://localhost:8080")
        print("="*80 + "\n")
    
    async def scan_arbitrage_opportunities(self):
        """Scan for cryptocurrency arbitrage using CCXT."""
        if not self.data_provider.ccxt_enabled:
            logger.warning("CCXT not available, skipping arbitrage scan")
            return
        
        opportunities = []
        
        try:
            # Scan cross-exchange arbitrage
            for symbol in CRYPTO_PAIRS:
                prices_by_exchange = {}
                
                # Fetch prices from multiple exchanges
                for exchange_id in EXCHANGES:
                    price_data = await self.data_provider.get_crypto_price_ccxt(exchange_id, symbol)
                    if price_data and price_data['bid'] and price_data['ask']:
                        prices_by_exchange[exchange_id] = price_data
                
                # Find arbitrage opportunities
                if len(prices_by_exchange) >= 2:
                    exchanges_list = list(prices_by_exchange.keys())
                    
                    for i in range(len(exchanges_list)):
                        for j in range(i + 1, len(exchanges_list)):
                            buy_exchange = exchanges_list[i]
                            sell_exchange = exchanges_list[j]
                            
                            buy_price = prices_by_exchange[buy_exchange]['ask']
                            sell_price = prices_by_exchange[sell_exchange]['bid']
                            
                            # Calculate profit
                            spread_pct = ((sell_price - buy_price) / buy_price) * 100
                            
                            if spread_pct > 0.25:  # Min 0.25% profit
                                capital = 10000.0
                                gross_profit = capital * (spread_pct / 100)
                                
                                # Estimate costs
                                fees = capital * 0.002  # 0.2% total fees
                                gas = 2.5
                                net_profit = gross_profit - fees - gas
                                
                                if net_profit > 0:
                                    opportunity = {
                                        'type': 'ARBITRAGE',
                                        'route_type': '2-HOP',
                                        'asset': symbol.split('/')[0],
                                        'buy_exchange': buy_exchange.upper(),
                                        'sell_exchange': sell_exchange.upper(),
                                        'buy_price': buy_price,
                                        'sell_price': sell_price,
                                        'spread_pct': spread_pct,
                                        'capital': capital,
                                        'expected_profit': net_profit,
                                        'fees': fees,
                                        'gas': gas,
                                        'risk_score': min(15.0, (0.5 - spread_pct) * 10),
                                        'recommendation': 'EXECUTE' if spread_pct > 0.5 else 'CONSIDER',
                                        'timestamp': datetime.now().isoformat()
                                    }
                                    opportunities.append(opportunity)
            
            self.arbitrage_opportunities = sorted(
                opportunities,
                key=lambda x: x['expected_profit'],
                reverse=True
            )[:10]
            
            # AUTO-EXECUTION: Execute top opportunities if enabled
            if self.auto_execute_enabled and self.arbitrage_opportunities:
                for opp in self.arbitrage_opportunities[:3]:  # Top 3 only
                    # Threshold: >0.5% spread, >$50 profit, risk < 30/100
                    if (opp['spread_pct'] > 0.5 and 
                        opp['expected_profit'] > 50.0 and 
                        opp['risk_score'] < 30.0):
                        await self.execute_paper_trade_arbitrage(opp)
            
        except Exception as e:
            logger.error(f"Error scanning arbitrage: {e}")
    
    async def scan_forex_opportunities(self):
        """Scan for forex opportunities using MT5."""
        if not self.data_provider.mt5_enabled:
            logger.warning("MT5 not connected, skipping forex scan")
            return
        
        opportunities = []
        
        try:
            for symbol in FOREX_PAIRS:
                price_data = await self.data_provider.get_forex_price_mt5(symbol)
                
                if not price_data:
                    continue
                
                # Get historical data for technical analysis
                try:
                    import MetaTrader5 as MT5
                    from datetime import timedelta
                    
                    rates = MT5.copy_rates_from_pos(symbol, MT5.TIMEFRAME_M15, 0, 100)
                    if rates is None or len(rates) < 50:
                        continue
                    
                    df = pd.DataFrame(rates)
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    
                    # Calculate indicators
                    close_prices = df['close'].values
                    
                    # RSI
                    rsi = self._calculate_rsi(close_prices, period=14)
                    
                    # SMA
                    sma_20 = np.mean(close_prices[-20:])
                    sma_50 = np.mean(close_prices[-50:])
                    
                    # Current price
                    current_price = price_data['last']
                    
                    # Signal generation
                    signal = None
                    signal_strength = 0.0
                    
                    if rsi < 30 and current_price < sma_20:
                        signal = 'BUY'
                        signal_strength = (30 - rsi) + ((sma_20 - current_price) / sma_20 * 100)
                    elif rsi > 70 and current_price > sma_20:
                        signal = 'SELL'
                        signal_strength = (rsi - 70) + ((current_price - sma_20) / sma_20 * 100)
                    
                    if signal and signal_strength > 5.0:
                        # Calculate ATR for stop loss/take profit
                        atr = self._calculate_atr(df[['high', 'low', 'close']].values, period=14)
                        
                        if signal == 'BUY':
                            entry = price_data['ask']
                            stop_loss = entry - (atr * 2)
                            take_profit = entry + (atr * 3)
                        else:
                            entry = price_data['bid']
                            stop_loss = entry + (atr * 2)
                            take_profit = entry - (atr * 3)
                        
                        risk_reward = abs(take_profit - entry) / abs(entry - stop_loss)
                        
                        if risk_reward >= 1.5:
                            normalized_strength = min(100, signal_strength * 10)
                            
                            opportunity = {
                                'type': 'FOREX',
                                'pair': self._format_forex_pair(symbol),
                                'signal': signal,
                                'strength': normalized_strength,
                                'entry': entry,
                                'stop_loss': stop_loss,
                                'take_profit': take_profit,
                                'risk_reward': risk_reward,
                                'rsi': rsi,
                                'spread': price_data['spread'],
                                'recommendation': 'EXECUTE' if normalized_strength > 70 else 'CONSIDER',
                                'timestamp': datetime.now().isoformat()
                            }
                            opportunities.append(opportunity)
                
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {e}")
                    continue
            
            self.forex_opportunities = sorted(
                opportunities,
                key=lambda x: x['strength'],
                reverse=True
            )[:10]
            
            # AUTO-EXECUTION: Execute top forex signals if enabled
            if self.auto_execute_enabled and self.forex_opportunities:
                for opp in self.forex_opportunities[:2]:  # Top 2 only
                    # Threshold: >70% confidence, risk/reward > 2.0
                    if (opp['strength'] > 70.0 and 
                        opp['risk_reward'] > 2.0):
                        formatted_opp = {
                            'pair': opp['pair'],
                            'signal': opp['signal'],
                            'entry_price': opp['entry'],
                            'take_profit': opp['take_profit'],
                            'stop_loss': opp['stop_loss'],
                            'confidence': f"{opp['strength']:.1f}%"
                        }
                        await self.execute_paper_trade_forex(formatted_opp)
            
        except Exception as e:
            logger.error(f"Error scanning forex: {e}")
    
    async def scan_binary_opportunities(self):
        """Scan for binary options opportunities."""
        if self.data_provider.pocket_enabled:
            # Use Pocket Option API signals
            signals = await self.data_provider.get_binary_signals_pocket()
            self.binary_opportunities = signals[:10]
        elif self.data_provider.mt5_enabled:
            # Generate signals from MT5 data with ultra-short momentum
            opportunities = []
            
            try:
                for symbol in FOREX_PAIRS:
                    price_data = await self.data_provider.get_forex_price_mt5(symbol)
                    
                    if not price_data:
                        continue
                    
                    try:
                        import MetaTrader5 as MT5
                        
                        # Get 1-minute data for ultra-short analysis
                        rates = MT5.copy_rates_from_pos(symbol, MT5.TIMEFRAME_M1, 0, 30)
                        if rates is None or len(rates) < 20:
                            continue
                        
                        df = pd.DataFrame(rates)
                        close_prices = df['close'].values
                        
                        # Calculate momentum
                        momentum = (close_prices[-1] - close_prices[-5]) / close_prices[-5] * 100
                        volatility = np.std(close_prices[-10:]) / np.mean(close_prices[-10:]) * 100
                        
                        # Generate binary signal
                        if abs(momentum) > 0.02 and volatility < 0.5:
                            direction = 'CALL' if momentum > 0 else 'PUT'
                            probability = min(85, 50 + abs(momentum) * 1000)
                            
                            if probability >= 65:
                                risk_amount = 100.0
                                payout_ratio = 1.85
                                potential_profit = risk_amount * (payout_ratio - 1)
                                
                                opportunity = {
                                    'type': 'BINARY',
                                    'pair': self._format_forex_pair(symbol),
                                    'direction': direction,
                                    'expiry': '60s',
                                    'probability': probability,
                                    'risk': risk_amount,
                                    'potential_profit': potential_profit,
                                    'payout_ratio': payout_ratio,
                                    'momentum': momentum,
                                    'recommendation': 'EXECUTE' if probability > 75 else 'CONSIDER',
                                    'timestamp': datetime.now().isoformat()
                                }
                                opportunities.append(opportunity)
                    
                    except Exception as e:
                        logger.error(f"Error analyzing binary {symbol}: {e}")
                        continue
                
                self.binary_opportunities = sorted(
                    opportunities,
                    key=lambda x: x['probability'],
                    reverse=True
                )[:10]
                
                # AUTO-EXECUTION: Execute top binary signals if enabled
                if self.auto_execute_enabled and self.binary_opportunities:
                    for opp in self.binary_opportunities[:1]:  # Top 1 only (high risk)
                        # Threshold: >75% probability, 60s expiry
                        if (opp['probability'] > 75.0 and 
                            opp['expiry'] == '60s'):
                            formatted_opp = {
                                'pair': opp['pair'],
                                'direction': opp['direction'],
                                'expiry': opp['expiry'],
                                'entry_price': opp['entry'],
                                'risk_amount': opp['risk'],
                                'potential_profit': opp['potential_profit'],
                                'probability': f"{opp['probability']:.1f}%"
                            }
                            await self.execute_paper_trade_binary(formatted_opp)
            
            except Exception as e:
                logger.error(f"Error scanning binary options: {e}")
        else:
            logger.warning("No data source for binary options")
    
    def _calculate_rsi(self, prices: np.ndarray, period: int = 14) -> float:
        """Calculate RSI indicator."""
        deltas = np.diff(prices)
        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gain[-period:])
        avg_loss = np.mean(loss[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def _calculate_atr(self, hlc_data: np.ndarray, period: int = 14) -> float:
        """Calculate Average True Range."""
        high = hlc_data[:, 0]
        low = hlc_data[:, 1]
        close = hlc_data[:, 2]
        
        tr1 = high[1:] - low[1:]
        tr2 = np.abs(high[1:] - close[:-1])
        tr3 = np.abs(low[1:] - close[:-1])
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr = np.mean(tr[-period:])
        return atr
    
    def _format_forex_pair(self, mt5_symbol: str) -> str:
        """Format MT5 symbol to display format."""
        if len(mt5_symbol) == 6:
            return f"{mt5_symbol[:3]}/{mt5_symbol[3:]}"
        return mt5_symbol
    
    async def execute_paper_trade_arbitrage(
        self,
        opportunity: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Execute paper arbitrage trade with full system integration.
        Uses: OMS, Risk Manager, RL Agent, Master Governor, Arbitrage Executor
        """
        try:
            # Step 1: Create order proposal
            order_proposal = {
                'type': 'arbitrage',
                'route': opportunity['route'],
                'asset': opportunity['asset'],
                'capital': 10000.0,  # Default capital
                'expected_profit': float(opportunity['expected_profit'].replace('$', '').replace(',', '')),
                'risk_score': float(opportunity.get('risk_score', '50.0/100').split('/')[0]),
                'timestamp': datetime.now()
            }
            
            # Step 2: RL Agent evaluates opportunity
            rl_decision = self.arb_rl_agent.evaluate_opportunity(order_proposal)
            
            if rl_decision['action'] == 'skip':
                logger.info(f"RL Agent skipped arbitrage: {rl_decision['reason']}")
                return None
            
            # Step 3: Risk Manager approval
            risk_check = self.risk_manager.check_trade_approval(
                asset=order_proposal['asset'],
                size=order_proposal['capital'],
                direction='long',  # Arbitrage is neutral but classified as long
                current_portfolio_value=100000.0  # Default portfolio value
            )
            
            if not risk_check['approved']:
                logger.info(f"Risk Manager rejected: {risk_check['reason']}")
                return None
            
            # Step 4: Master Governor final decision
            governor_decision = self.governor.make_decision(
                opportunity_type='arbitrage',
                opportunity_data=order_proposal,
                market_conditions={'volatility': 'medium', 'liquidity': 'high'}
            )
            
            if not governor_decision['execute']:
                logger.info(f"Governor rejected: {governor_decision['reason']}")
                return None
            
            # Step 5: Execute via Arbitrage Executor
            execution_result = await self.arb_executor.execute_paper_trade(
                route=opportunity['route'],
                asset=opportunity['asset'],
                capital=order_proposal['capital'],
                expected_profit=order_proposal['expected_profit'],
                buy_exchange=opportunity.get('buy_exchange'),
                sell_exchange=opportunity.get('sell_exchange')
            )
            
            if execution_result['success']:
                # Update stats
                self.paper_trades += 1
                
                # Store in history
                trade_record = {
                    'type': 'arbitrage',
                    'timestamp': datetime.now().isoformat(),
                    'asset': opportunity['asset'],
                    'route': opportunity['route'],
                    'capital': order_proposal['capital'],
                    'pnl': execution_result['pnl'],
                    'execution_id': execution_result['execution_id']
                }
                
                logger.info(f"✅ Paper Arbitrage Executed: {opportunity['asset']} - PnL: ${execution_result['pnl']:.2f}")
                return execution_result
            
        except Exception as e:
            logger.error(f"Error executing paper arbitrage: {e}")
        
        return None
    
    async def execute_paper_trade_forex(
        self,
        opportunity: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Execute paper forex trade with full system integration.
        Uses: OMS, Risk Manager, RL Agent, Master Governor, Forex Executor
        """
        try:
            # Step 1: Create order proposal
            order_proposal = {
                'type': 'forex',
                'pair': opportunity['pair'],
                'signal': opportunity['signal'],
                'entry_price': float(opportunity['entry_price']),
                'take_profit': float(opportunity['take_profit']),
                'stop_loss': float(opportunity['stop_loss']),
                'size': 10000.0,  # Default position size
                'confidence': float(opportunity['confidence'].replace('%', '')),
                'timestamp': datetime.now()
            }
            
            # Step 2: RL Agent evaluates
            rl_decision = self.forex_rl_agent.evaluate_signal(
                pair=order_proposal['pair'],
                signal=order_proposal['signal'],
                confidence=order_proposal['confidence']
            )
            
            if rl_decision['action'] == 'skip':
                logger.info(f"RL Agent skipped forex: {rl_decision['reason']}")
                return None
            
            # Adjust size based on RL recommendation
            order_proposal['size'] *= rl_decision['size_multiplier']
            
            # Step 3: Risk Manager approval
            risk_check = self.risk_manager.check_trade_approval(
                asset=order_proposal['pair'],
                size=order_proposal['size'],
                direction='long' if order_proposal['signal'] == 'BUY' else 'short',
                current_portfolio_value=100000.0  # Default portfolio value
            )
            
            if not risk_check['approved']:
                logger.info(f"Risk Manager rejected forex: {risk_check['reason']}")
                return None
            
            # Step 4: Master Governor final decision
            governor_decision = self.governor.make_decision(
                opportunity_type='forex',
                opportunity_data=order_proposal,
                market_conditions={
                    'volatility': 'medium',
                    'trend': 'bullish' if order_proposal['signal'] == 'BUY' else 'bearish'
                }
            )
            
            if not governor_decision['execute']:
                logger.info(f"Governor rejected forex: {governor_decision['reason']}")
                return None
            
            # Step 5: Execute via Forex Executor
            execution_result = await self.forex_executor.execute_paper_trade(
                pair=order_proposal['pair'],
                signal=order_proposal['signal'],
                entry_price=order_proposal['entry_price'],
                take_profit=order_proposal['take_profit'],
                stop_loss=order_proposal['stop_loss'],
                size=order_proposal['size']
            )
            
            if execution_result['success']:
                # Update stats
                self.paper_trades += 1
                
                # Update RL agent with result
                profitable = execution_result['pnl'] > 0
                self.forex_rl_agent.update_signal_result(
                    pair=order_proposal['pair'],
                    signal=order_proposal['signal'],
                    profitable=profitable
                )
                
                # Store in history
                trade_record = {
                    'type': 'forex',
                    'timestamp': datetime.now().isoformat(),
                    'pair': opportunity['pair'],
                    'signal': opportunity['signal'],
                    'size': order_proposal['size'],
                    'pnl': execution_result['pnl'],
                    'execution_id': execution_result['execution_id']
                }
                
                logger.info(f"✅ Paper Forex Executed: {opportunity['pair']} {opportunity['signal']} - PnL: ${execution_result['pnl']:.2f}")
                return execution_result
            
        except Exception as e:
            logger.error(f"Error executing paper forex: {e}")
        
        return None
    
    async def execute_paper_trade_binary(
        self,
        opportunity: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Execute paper binary options trade with full system integration.
        Uses: OMS, Risk Manager, Master Governor
        """
        try:
            # Step 1: Create order proposal
            risk_amount = float(opportunity['risk_amount'].replace('$', '').replace(',', ''))
            potential_profit = float(opportunity['potential_profit'].replace('$', '').replace(',', ''))
            
            order_proposal = {
                'type': 'binary_options',
                'pair': opportunity['pair'],
                'direction': opportunity['direction'],
                'expiry': opportunity['expiry'],
                'entry_price': float(opportunity['entry_price']),
                'risk_amount': risk_amount,
                'potential_profit': potential_profit,
                'probability': float(opportunity['probability'].replace('%', '')),
                'timestamp': datetime.now()
            }
            
            # Step 2: Risk Manager approval (binary options are high risk)
            risk_check = self.risk_manager.check_trade_approval(
                asset=order_proposal['pair'],
                size=order_proposal['risk_amount'],
                direction='long' if order_proposal['direction'] == 'CALL' else 'short',
                current_portfolio_value=100000.0  # Default portfolio value
            )
            
            if not risk_check['approved']:
                logger.info(f"Risk Manager rejected binary: {risk_check['reason']}")
                return None
            
            # Step 3: Master Governor final decision (extra scrutiny for binary options)
            governor_decision = self.governor.make_decision(
                opportunity_type='binary_options',
                opportunity_data=order_proposal,
                market_conditions={'volatility': 'high', 'timeframe': '60s'}
            )
            
            if not governor_decision['execute']:
                logger.info(f"Governor rejected binary: {governor_decision['reason']}")
                return None
            
            # Step 4: Simulate execution (binary options are instant)
            # Determine outcome based on probability
            win = np.random.random() < (order_proposal['probability'] / 100)
            
            if win:
                pnl = order_proposal['potential_profit']
            else:
                pnl = -order_proposal['risk_amount']
            
            execution_result = {
                'success': True,
                'execution_id': f"BINARY_{datetime.now().timestamp()}",
                'pnl': pnl,
                'outcome': 'WIN' if win else 'LOSS',
                'timestamp': datetime.now().isoformat()
            }
            
            # Update stats
            self.paper_trades += 1
            
            # Store in history
            trade_record = {
                'type': 'binary_options',
                'timestamp': datetime.now().isoformat(),
                'pair': opportunity['pair'],
                'direction': opportunity['direction'],
                'risk': order_proposal['risk_amount'],
                'pnl': pnl,
                'outcome': execution_result['outcome'],
                'execution_id': execution_result['execution_id']
            }
            
            logger.info(f"✅ Paper Binary Executed: {opportunity['pair']} {opportunity['direction']} - {execution_result['outcome']} - PnL: ${pnl:.2f}")
            return execution_result
            
        except Exception as e:
            logger.error(f"Error executing paper binary: {e}")
        
        return None
    
    async def scan_all_assets(self):
        """Scan all asset types concurrently."""
        self.total_scans += 1
        
        await asyncio.gather(
            self.scan_arbitrage_opportunities(),
            self.scan_forex_opportunities(),
            self.scan_binary_opportunities()
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get scanner statistics."""
        uptime = datetime.now() - self.scan_start_time
        
        return {
            'arbitrage_count': len(self.arbitrage_opportunities),
            'forex_count': len(self.forex_opportunities),
            'binary_count': len(self.binary_opportunities),
            'total_scans': self.total_scans,
            'uptime_seconds': int(uptime.total_seconds()),
            'portfolio_value': 100000.0,  # Default portfolio value
            'paper_trades': self.paper_trades,
            'api_status': {
                'mt5': self.data_provider.mt5_enabled,
                'ccxt': self.data_provider.ccxt_enabled,
                'dex': self.data_provider.dex_enabled,
                'pocket': self.data_provider.pocket_enabled
            }
        }


# Global scanner instance
scanner = RealTimeProductionScanner()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def broadcast_opportunities():
    """Broadcast opportunities to all connected clients."""
    while True:
        if active_connections:
            data = {
                'arbitrage': scanner.arbitrage_opportunities,
                'forex': scanner.forex_opportunities,
                'binary': scanner.binary_opportunities,
                'stats': scanner.get_stats(),
                'timestamp': datetime.now().isoformat()
            }
            
            message = json.dumps(data)
            
            for connection in active_connections[:]:
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error sending to client: {e}")
                    active_connections.remove(connection)
        
        await asyncio.sleep(BROADCAST_INTERVAL)


async def periodic_scanning():
    """Run periodic scans for all asset types."""
    while True:
        await scanner.scan_all_assets()
        await asyncio.sleep(min(ARBITRAGE_SCAN_INTERVAL, FOREX_SCAN_INTERVAL, BINARY_SCAN_INTERVAL))


@app.on_event("startup")
async def startup_event():
    """Start background tasks on server startup."""
    asyncio.create_task(broadcast_opportunities())
    asyncio.create_task(periodic_scanning())
    logger.info("✅ Production scanner started")


@app.get("/")
async def get_dashboard():
    """Serve the real-time dashboard."""
    try:
        with open('dashboard/realtime_scanner.html', 'r') as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Dashboard not found</h1><p>Please ensure dashboard/realtime_scanner.html exists</p>",
            status_code=404
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "scanner": "running",
        "connections": len(active_connections),
        "stats": scanner.get_stats()
    }


if __name__ == "__main__":
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
