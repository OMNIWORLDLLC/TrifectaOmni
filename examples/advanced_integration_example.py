#!/usr/bin/env python3
"""Advanced system integration example with OMS and risk management.

This demonstrates the full production system with:
- Real-time data feeds
- Advanced technical indicators
- Order Management System (OMS)
- Dynamic position sizing
- Portfolio risk management
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from omni_trifecta.core.config import OmniConfig
from omni_trifecta.data.price_feeds import SimulatedPriceFeedAdapter
from omni_trifecta.decision.master_governor import MasterGovernorX100
from omni_trifecta.execution.executors import ShadowExecutionHub
from omni_trifecta.execution.oms import OrderManagementSystem, OrderType
from omni_trifecta.learning.orchestrator import RLJSONStore
from omni_trifecta.safety.managers import SafetyManager
from omni_trifecta.safety.advanced_risk import DynamicPositionSizer, RiskParameters, PortfolioHeatMap
from omni_trifecta.runtime.logging import OmniLogger, DecisionAuditTrail, PerformanceRecorder
from omni_trifecta.runtime.orchestration import OmniRuntime
from omni_trifecta.utils.advanced_indicators import (
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    analyze_market_structure,
    detect_chart_patterns
)
from omni_trifecta.utils.technical import detect_swing_points

import numpy as np
from typing import List, Dict, Any
from datetime import datetime


class AdvancedTradingEngine:
    """Advanced trading engine with full integration."""
    
    def __init__(
        self,
        config: OmniConfig,
        starting_balance: float = 10000.0
    ):
        """Initialize advanced trading engine."""
        self.config = config
        self.balance = starting_balance
        self.starting_balance = starting_balance
        
        self.governor = MasterGovernorX100(base_stake=100.0, max_stake=1000.0)
        self.execution_hub = ShadowExecutionHub()
        self.oms = OrderManagementSystem()
        self.rl_store = RLJSONStore(config.log_dir / "rl_state")
        self.logger = OmniLogger(config.log_dir)
        self.audit_trail = DecisionAuditTrail(config.log_dir)
        self.perf_recorder = PerformanceRecorder(config.log_dir)
        
        self.safety_manager = SafetyManager(
            max_daily_loss=500.0,
            max_daily_trades=50,
            max_loss_streak=5
        )
        
        risk_params = RiskParameters(
            max_position_size=0.2,
            max_portfolio_risk=0.05,
            max_position_risk=0.02,
            max_correlation_exposure=0.5
        )
        self.position_sizer = DynamicPositionSizer(risk_params)
        self.heat_map = PortfolioHeatMap(max_heat=0.1)
        
        self.price_window: List[float] = []
        self.high_window: List[float] = []
        self.low_window: List[float] = []
        self.volume_window: List[float] = []
        
        self.window_size = 256
        self.tick_count = 0
    
    def process_tick(
        self,
        symbol: str,
        price: float,
        timestamp: datetime
    ) -> Dict[str, Any]:
        """Process single price tick with full analysis."""
        self.tick_count += 1
        
        self.price_window.append(price)
        self.high_window.append(price * 1.001)
        self.low_window.append(price * 0.999)
        self.volume_window.append(np.random.uniform(1000, 10000))
        
        if len(self.price_window) > self.window_size:
            self.price_window.pop(0)
            self.high_window.pop(0)
            self.low_window.pop(0)
            self.volume_window.pop(0)
        
        self.oms.update_market_price(symbol, price)
        
        self.logger.log_tick(symbol, price, timestamp)
        
        if not self.safety_manager.can_trade():
            return {
                'action': 'skip',
                'reason': 'cooldown',
                'balance': self.balance
            }
        
        if len(self.price_window) < 50:
            return {
                'action': 'skip',
                'reason': 'insufficient_data',
                'balance': self.balance
            }
        
        analysis = self.analyze_market(symbol, price)
        
        decision = self.make_decision(symbol, price, analysis)
        
        if decision['action'] == 'buy' or decision['action'] == 'sell':
            result = self.execute_trade(symbol, price, decision, analysis)
            return result
        
        return {
            'action': 'hold',
            'analysis': analysis,
            'balance': self.balance
        }
    
    def analyze_market(self, symbol: str, current_price: float) -> Dict[str, Any]:
        """Perform comprehensive market analysis."""
        rsi = calculate_rsi(self.price_window)
        
        macd, macd_signal, macd_hist = calculate_macd(self.price_window)
        
        bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(self.price_window)
        
        bb_width = (bb_upper - bb_lower) / bb_middle if bb_middle > 0 else 0
        bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
        
        market_structure = analyze_market_structure(
            self.price_window,
            self.high_window,
            self.low_window,
            self.volume_window
        )
        
        chart_patterns = detect_chart_patterns(self.price_window)
        
        swings = detect_swing_points(self.price_window, window=5)
        
        return {
            'rsi': rsi,
            'macd': {'line': macd, 'signal': macd_signal, 'histogram': macd_hist},
            'bollinger': {
                'upper': bb_upper,
                'middle': bb_middle,
                'lower': bb_lower,
                'width': bb_width,
                'position': bb_position
            },
            'market_structure': {
                'trend': market_structure.trend,
                'strength': market_structure.strength,
                'support_levels': market_structure.support_levels,
                'resistance_levels': market_structure.resistance_levels,
                'breakout_prob': market_structure.breakout_probability,
                'reversal_prob': market_structure.reversal_probability
            },
            'patterns': chart_patterns,
            'swings': swings
        }
    
    def make_decision(
        self,
        symbol: str,
        current_price: float,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Make trading decision based on analysis."""
        signal_strength = 0.0
        signals = []
        
        rsi = analysis['rsi']
        if rsi < 30:
            signal_strength += 0.2
            signals.append('RSI_OVERSOLD')
        elif rsi > 70:
            signal_strength -= 0.2
            signals.append('RSI_OVERBOUGHT')
        
        macd_hist = analysis['macd']['histogram']
        if macd_hist > 0:
            signal_strength += 0.1
            signals.append('MACD_BULLISH')
        else:
            signal_strength -= 0.1
            signals.append('MACD_BEARISH')
        
        bb_pos = analysis['bollinger']['position']
        if bb_pos < 0.2:
            signal_strength += 0.15
            signals.append('BB_LOWER')
        elif bb_pos > 0.8:
            signal_strength -= 0.15
            signals.append('BB_UPPER')
        
        trend = analysis['market_structure']['trend']
        trend_strength = analysis['market_structure']['strength']
        
        if trend == 'uptrend':
            signal_strength += trend_strength * 0.2
            signals.append('UPTREND')
        elif trend == 'downtrend':
            signal_strength -= trend_strength * 0.2
            signals.append('DOWNTREND')
        
        for pattern in analysis['patterns']:
            if pattern['direction'] == 'bullish':
                signal_strength += pattern['confidence'] * 0.1
                signals.append(f"PATTERN_{pattern['pattern'].upper()}_BULLISH")
            else:
                signal_strength -= pattern['confidence'] * 0.1
                signals.append(f"PATTERN_{pattern['pattern'].upper()}_BEARISH")
        
        threshold = 0.3
        confidence = abs(signal_strength)
        
        if signal_strength > threshold:
            return {
                'action': 'buy',
                'confidence': confidence,
                'signals': signals,
                'signal_strength': signal_strength
            }
        elif signal_strength < -threshold:
            return {
                'action': 'sell',
                'confidence': confidence,
                'signals': signals,
                'signal_strength': signal_strength
            }
        else:
            return {
                'action': 'hold',
                'confidence': 0.0,
                'signals': signals,
                'signal_strength': signal_strength
            }
    
    def execute_trade(
        self,
        symbol: str,
        current_price: float,
        decision: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute trade with position sizing and risk management."""
        atr = analysis['bollinger']['width'] * current_price * 0.5
        
        position = self.oms.get_position(symbol)
        current_positions = {symbol: position.quantity} if position else {}
        
        position_size = self.position_sizer.calculate_position_size(
            symbol=symbol,
            account_balance=self.balance,
            current_price=current_price,
            volatility=atr,
            confidence=decision['confidence'],
            current_positions=current_positions
        )
        
        if position_size < 0.01:
            return {
                'action': 'skip',
                'reason': 'position_size_too_small',
                'balance': self.balance
            }
        
        side = 'BUY' if decision['action'] == 'buy' else 'SELL'
        
        order = self.oms.create_order(
            symbol=symbol,
            side=side,
            order_type=OrderType.MARKET,
            quantity=position_size,
            price=current_price,
            metadata={
                'signals': decision['signals'],
                'confidence': decision['confidence'],
                'analysis': analysis
            }
        )
        
        pnl = np.random.normal(0, atr * position_size)
        
        self.oms.fill_order(order.order_id, current_price, position_size)
        
        self.balance += pnl
        
        self.safety_manager.register_trade(pnl)
        self.position_sizer.register_trade(pnl, position_size * current_price)
        
        trade_record = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'side': side,
            'quantity': position_size,
            'price': current_price,
            'pnl': pnl,
            'balance': self.balance,
            'signals': decision['signals'],
            'confidence': decision['confidence']
        }
        self.logger.log_trade(trade_record)
        
        return {
            'action': 'executed',
            'order_id': order.order_id,
            'side': side,
            'quantity': position_size,
            'price': current_price,
            'pnl': pnl,
            'balance': self.balance
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        oms_summary = self.oms.get_portfolio_summary()
        risk_metrics = self.position_sizer.get_risk_metrics()
        
        return_pct = ((self.balance - self.starting_balance) / self.starting_balance) * 100
        
        return {
            'balance': self.balance,
            'starting_balance': self.starting_balance,
            'total_pnl': self.balance - self.starting_balance,
            'return_pct': return_pct,
            'total_trades': len(self.oms.trade_history),
            'open_positions': len(self.oms.positions),
            'risk_metrics': risk_metrics,
            'oms_summary': oms_summary
        }


def main():
    """Main function."""
    print("=" * 80)
    print("OMNI-TRIFECTA ADVANCED INTEGRATION DEMO")
    print("=" * 80)
    
    config = OmniConfig()
    
    engine = AdvancedTradingEngine(config, starting_balance=10000.0)
    
    prices = []
    base_price = 100.0
    for i in range(500):
        trend = np.sin(i / 50) * 5
        noise = np.random.normal(0, 1)
        price = base_price + trend + noise
        prices.append(max(price, 1.0))
    
    price_feed = SimulatedPriceFeedAdapter(
        symbol="BTCUSD",
        prices=prices,
        delay=0.0
    )
    
    print("\nProcessing price ticks...")
    
    for i, price in enumerate(price_feed):
        timestamp = datetime.now()
        
        result = engine.process_tick("BTCUSD", price, timestamp)
        
        if (i + 1) % 50 == 0:
            print(f"\nTick {i+1}:")
            print(f"  Price: ${price:.2f}")
            print(f"  Balance: ${engine.balance:.2f}")
            print(f"  Action: {result.get('action', 'unknown')}")
            
            if 'signals' in result:
                print(f"  Signals: {', '.join(result['signals'][:3])}")
    
    print("\n" + "=" * 80)
    print("PERFORMANCE SUMMARY")
    print("=" * 80)
    
    summary = engine.get_performance_summary()
    
    print(f"\nFinal Balance: ${summary['balance']:.2f}")
    print(f"Starting Balance: ${summary['starting_balance']:.2f}")
    print(f"Total P&L: ${summary['total_pnl']:.2f}")
    print(f"Return: {summary['return_pct']:.2f}%")
    print(f"Total Trades: {summary['total_trades']}")
    print(f"Open Positions: {summary['open_positions']}")
    
    risk_metrics = summary['risk_metrics']
    print(f"\nRisk Metrics:")
    print(f"  Sharpe Ratio: {risk_metrics['sharpe_ratio']:.2f}")
    print(f"  Max Drawdown: {risk_metrics['max_drawdown']:.2%}")
    print(f"  Win Rate: {risk_metrics['win_rate']:.2%}")
    print(f"  Profit Factor: {risk_metrics['profit_factor']:.2f}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
