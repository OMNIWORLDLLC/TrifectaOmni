"""Advanced risk management and dynamic position sizing."""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class RiskParameters:
    """Risk parameters for position sizing."""
    max_position_size: float = 1.0
    max_portfolio_risk: float = 0.02
    max_position_risk: float = 0.01
    max_correlation_exposure: float = 0.5
    max_sector_exposure: float = 0.3
    max_leverage: float = 2.0
    min_sharpe_ratio: float = 0.5


class KellyCalculator:
    """Kelly Criterion calculator for optimal position sizing."""
    
    @staticmethod
    def calculate_kelly_fraction(
        win_rate: float,
        avg_win: float,
        avg_loss: float,
        fractional: float = 0.25
    ) -> float:
        """Calculate Kelly fraction for position sizing.
        
        Args:
            win_rate: Historical win rate [0, 1]
            avg_win: Average winning trade size
            avg_loss: Average losing trade size (positive)
            fractional: Fraction of full Kelly to use (0.25 = quarter Kelly)
        
        Returns:
            Recommended position size fraction
        """
        if avg_loss == 0 or win_rate <= 0 or win_rate >= 1:
            return 0.0
        
        win_loss_ratio = avg_win / avg_loss
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        kelly = max(0.0, min(1.0, kelly))
        
        return kelly * fractional
    
    @staticmethod
    def calculate_optimal_f(returns: List[float]) -> float:
        """Calculate optimal f using Ralph Vince's method.
        
        Args:
            returns: List of historical returns
        
        Returns:
            Optimal f value
        """
        if not returns or min(returns) >= 0:
            return 0.0
        
        max_loss = abs(min(returns))
        
        best_f = 0.0
        best_twr = 0.0
        
        for f in np.linspace(0.01, 1.0, 100):
            twr = 1.0
            for ret in returns:
                hpr = 1 + (f * ret / max_loss)
                twr *= max(0.01, hpr)
            
            if twr > best_twr:
                best_twr = twr
                best_f = f
        
        return best_f * 0.5


class VolatilityAdjuster:
    """Adjust position sizes based on volatility."""
    
    @staticmethod
    def calculate_volatility_scalar(
        current_volatility: float,
        target_volatility: float = 0.15
    ) -> float:
        """Calculate position size scalar based on volatility.
        
        Args:
            current_volatility: Current market volatility
            target_volatility: Target portfolio volatility
        
        Returns:
            Position size multiplier
        """
        if current_volatility <= 0:
            return 1.0
        
        scalar = target_volatility / current_volatility
        
        return max(0.1, min(3.0, scalar))
    
    @staticmethod
    def calculate_atr_position_size(
        account_balance: float,
        atr: float,
        price: float,
        risk_per_trade: float = 0.01
    ) -> float:
        """Calculate position size based on ATR.
        
        Args:
            account_balance: Current account balance
            atr: Average True Range
            price: Current price
            risk_per_trade: Risk per trade as fraction of balance
        
        Returns:
            Position size in units
        """
        if atr <= 0 or price <= 0:
            return 0.0
        
        risk_amount = account_balance * risk_per_trade
        
        position_size = risk_amount / atr
        
        return position_size


class CorrelationMatrix:
    """Track and manage position correlations."""
    
    def __init__(self):
        """Initialize correlation matrix."""
        self.price_history: Dict[str, List[float]] = {}
        self.correlation_cache: Dict[Tuple[str, str], float] = {}
    
    def update_prices(self, symbol: str, price: float):
        """Update price history for symbol."""
        if symbol not in self.price_history:
            self.price_history[symbol] = []
        
        self.price_history[symbol].append(price)
        
        if len(self.price_history[symbol]) > 100:
            self.price_history[symbol].pop(0)
        
        self.correlation_cache.clear()
    
    def calculate_correlation(self, symbol1: str, symbol2: str) -> float:
        """Calculate correlation between two symbols."""
        cache_key = tuple(sorted([symbol1, symbol2]))
        
        if cache_key in self.correlation_cache:
            return self.correlation_cache[cache_key]
        
        if symbol1 not in self.price_history or symbol2 not in self.price_history:
            return 0.0
        
        prices1 = self.price_history[symbol1]
        prices2 = self.price_history[symbol2]
        
        if len(prices1) < 20 or len(prices2) < 20:
            return 0.0
        
        min_length = min(len(prices1), len(prices2))
        prices1 = prices1[-min_length:]
        prices2 = prices2[-min_length:]
        
        returns1 = np.diff(prices1) / prices1[:-1]
        returns2 = np.diff(prices2) / prices2[:-1]
        
        correlation = np.corrcoef(returns1, returns2)[0, 1]
        
        correlation = 0.0 if np.isnan(correlation) else correlation
        
        self.correlation_cache[cache_key] = correlation
        
        return correlation
    
    def get_portfolio_correlation_exposure(
        self,
        positions: Dict[str, float]
    ) -> float:
        """Calculate total correlation exposure of portfolio.
        
        Args:
            positions: Dictionary of symbol -> position size
        
        Returns:
            Average absolute correlation
        """
        if len(positions) < 2:
            return 0.0
        
        symbols = list(positions.keys())
        correlations = []
        
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                corr = self.calculate_correlation(symbols[i], symbols[j])
                weight = abs(positions[symbols[i]] * positions[symbols[j]])
                correlations.append(abs(corr) * weight)
        
        if not correlations:
            return 0.0
        
        return np.mean(correlations)


class DynamicPositionSizer:
    """Advanced position sizing with multiple methodologies."""
    
    def __init__(self, risk_params: Optional[RiskParameters] = None):
        """Initialize position sizer.
        
        Args:
            risk_params: Risk parameters
        """
        self.risk_params = risk_params or RiskParameters()
        self.correlation_matrix = CorrelationMatrix()
        self.trade_history: List[Dict[str, Any]] = []
    
    def calculate_position_size(
        self,
        symbol: str,
        account_balance: float,
        current_price: float,
        stop_loss_price: Optional[float] = None,
        volatility: Optional[float] = None,
        confidence: float = 0.5,
        current_positions: Optional[Dict[str, float]] = None
    ) -> float:
        """Calculate optimal position size using multiple methods.
        
        Args:
            symbol: Trading symbol
            account_balance: Current account balance
            current_price: Current market price
            stop_loss_price: Stop loss price (if any)
            volatility: Current volatility measure (ATR, std dev, etc.)
            confidence: Signal confidence [0, 1]
            current_positions: Current open positions
        
        Returns:
            Recommended position size
        """
        if account_balance <= 0 or current_price <= 0:
            return 0.0
        
        sizes = []
        
        base_size = account_balance * self.risk_params.max_position_risk
        sizes.append(base_size / current_price)
        
        if stop_loss_price and stop_loss_price > 0:
            risk_per_unit = abs(current_price - stop_loss_price)
            if risk_per_unit > 0:
                risk_amount = account_balance * self.risk_params.max_position_risk
                sl_size = risk_amount / risk_per_unit
                sizes.append(sl_size)
        
        if volatility and volatility > 0:
            vol_size = VolatilityAdjuster.calculate_atr_position_size(
                account_balance,
                volatility,
                current_price,
                self.risk_params.max_position_risk
            )
            sizes.append(vol_size)
        
        if len(self.trade_history) >= 10:
            returns = [trade['return'] for trade in self.trade_history[-100:]]
            wins = [r for r in returns if r > 0]
            losses = [abs(r) for r in returns if r < 0]
            
            if wins and losses:
                win_rate = len(wins) / len(returns)
                avg_win = np.mean(wins)
                avg_loss = np.mean(losses)
                
                kelly_fraction = KellyCalculator.calculate_kelly_fraction(
                    win_rate, avg_win, avg_loss
                )
                kelly_size = (account_balance * kelly_fraction) / current_price
                sizes.append(kelly_size)
        
        if sizes:
            median_size = np.median(sizes)
        else:
            median_size = base_size / current_price
        
        median_size *= confidence
        
        max_size = (account_balance * self.risk_params.max_position_size) / current_price
        median_size = min(median_size, max_size)
        
        if current_positions:
            current_exposure = sum(
                abs(size * current_price) for size in current_positions.values()
            )
            max_total_exposure = account_balance * self.risk_params.max_portfolio_risk * 10
            
            if current_exposure + median_size * current_price > max_total_exposure:
                available = max_total_exposure - current_exposure
                median_size = max(0, available / current_price)
        
        return median_size
    
    def register_trade(self, pnl: float, initial_capital: float):
        """Register trade result for Kelly calculation."""
        trade_return = pnl / initial_capital if initial_capital > 0 else 0
        
        self.trade_history.append({
            'pnl': pnl,
            'return': trade_return,
            'capital': initial_capital
        })
        
        if len(self.trade_history) > 1000:
            self.trade_history.pop(0)
    
    def get_risk_metrics(self) -> Dict[str, float]:
        """Calculate current risk metrics."""
        if len(self.trade_history) < 10:
            return {
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'profit_factor': 0.0,
                'avg_return': 0.0
            }
        
        returns = [trade['return'] for trade in self.trade_history]
        
        avg_return = np.mean(returns)
        std_return = np.std(returns)
        sharpe_ratio = (avg_return / std_return * np.sqrt(252)) if std_return > 0 else 0
        
        cumulative = np.cumprod([1 + r for r in returns])
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(np.min(drawdown))
        
        wins = [r for r in returns if r > 0]
        losses = [r for r in returns if r < 0]
        win_rate = len(wins) / len(returns) if returns else 0
        
        total_wins = sum(wins) if wins else 0
        total_losses = abs(sum(losses)) if losses else 1
        profit_factor = total_wins / total_losses if total_losses > 0 else 0
        
        return {
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'avg_return': avg_return
        }


class PortfolioHeatMap:
    """Monitor portfolio heat and concentration risk."""
    
    def __init__(self, max_heat: float = 1.0):
        """Initialize heat map.
        
        Args:
            max_heat: Maximum allowed portfolio heat
        """
        self.max_heat = max_heat
        self.sector_exposure: Dict[str, float] = {}
        self.asset_class_exposure: Dict[str, float] = {}
    
    def calculate_portfolio_heat(
        self,
        positions: Dict[str, float],
        stop_losses: Dict[str, float],
        current_prices: Dict[str, float],
        account_balance: float
    ) -> float:
        """Calculate total portfolio heat (risk).
        
        Args:
            positions: Symbol -> position size
            stop_losses: Symbol -> stop loss price
            current_prices: Symbol -> current price
            account_balance: Account balance
        
        Returns:
            Portfolio heat as fraction of balance
        """
        total_risk = 0.0
        
        for symbol, size in positions.items():
            if symbol in stop_losses and symbol in current_prices:
                risk_per_unit = abs(current_prices[symbol] - stop_losses[symbol])
                position_risk = risk_per_unit * abs(size)
                total_risk += position_risk
        
        heat = total_risk / account_balance if account_balance > 0 else 0
        
        return heat
    
    def can_add_position(
        self,
        new_risk: float,
        current_heat: float
    ) -> bool:
        """Check if new position would exceed heat limit.
        
        Args:
            new_risk: Risk amount for new position
            current_heat: Current portfolio heat
        
        Returns:
            True if position can be added
        """
        return (current_heat + new_risk) <= self.max_heat
    
    def update_sector_exposure(self, symbol: str, size: float, sector: str):
        """Update sector exposure."""
        if sector not in self.sector_exposure:
            self.sector_exposure[sector] = 0.0
        
        self.sector_exposure[sector] += size
    
    def get_sector_concentration(self) -> Dict[str, float]:
        """Get sector concentration percentages."""
        total = sum(abs(exp) for exp in self.sector_exposure.values())
        
        if total == 0:
            return {}
        
        return {
            sector: abs(exposure) / total
            for sector, exposure in self.sector_exposure.items()
        }
