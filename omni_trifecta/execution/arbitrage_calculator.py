"""
Multi-hop arbitrage calculator with comprehensive profit and risk calculations.

Supports 2-hop, 3-hop, and 4-hop arbitrage routes with:
- Profit calculation accounting for fees
- Risk/reward ratio analysis
- Slippage modeling
- Gas cost estimation
- Minimum profit thresholds
"""

from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np
from decimal import Decimal, getcontext

# Set high precision for financial calculations
getcontext().prec = 18


class RouteType(Enum):
    """Arbitrage route types."""
    TWO_HOP = 2
    THREE_HOP = 3
    FOUR_HOP = 4


@dataclass
class Exchange:
    """Exchange information for arbitrage."""
    name: str
    trading_fee: float  # As decimal (0.003 = 0.3%)
    withdrawal_fee: float  # Fixed fee in quote currency
    gas_cost: float  # Gas cost in USD
    liquidity_depth: float  # Available liquidity in USD
    slippage_factor: float  # Slippage per $100k traded (0.001 = 0.1%)


@dataclass
class TradingPair:
    """Trading pair information."""
    base: str
    quote: str
    exchange: Exchange
    bid_price: float  # Best bid
    ask_price: float  # Best ask
    spread: float  # Spread in basis points
    liquidity: float  # Available liquidity
    

@dataclass
class ArbitrageRoute:
    """Complete arbitrage route definition."""
    route_type: RouteType
    pairs: List[TradingPair]
    path: List[str]  # ['USDT', 'BTC', 'ETH', 'USDT']
    expected_profit: float
    expected_profit_bps: float
    risk_score: float
    execution_time_ms: float
    total_fees: float
    total_gas: float
    slippage_estimate: float
    min_capital_required: float
    max_capital_recommended: float
    

@dataclass
class RouteExecutionResult:
    """Result of arbitrage route execution."""
    success: bool
    initial_amount: float
    final_amount: float
    actual_profit: float
    actual_profit_bps: float
    fees_paid: float
    gas_paid: float
    slippage_experienced: float
    execution_time_ms: float
    price_impact: float


class MultiHopArbitrageCalculator:
    """
    Calculate multi-hop arbitrage opportunities with comprehensive risk analysis.
    
    Supports:
    - 2-hop: A -> B -> A
    - 3-hop: A -> B -> C -> A (triangular)
    - 4-hop: A -> B -> C -> D -> A (rectangular)
    """
    
    def __init__(
        self,
        min_profit_bps: float = 30.0,  # Minimum 0.30% profit
        max_slippage_bps: float = 50.0,  # Maximum 0.50% slippage
        safety_margin: float = 0.20  # 20% safety margin
    ):
        """
        Initialize arbitrage calculator.
        
        Args:
            min_profit_bps: Minimum profit in basis points
            max_slippage_bps: Maximum acceptable slippage in basis points
            safety_margin: Safety margin as fraction (0.2 = 20%)
        """
        self.min_profit_bps = min_profit_bps
        self.max_slippage_bps = max_slippage_bps
        self.safety_margin = safety_margin
        
    def calculate_2hop_arbitrage(
        self,
        pair1: TradingPair,  # Buy: USDT -> BTC
        pair2: TradingPair,  # Sell: BTC -> USDT
        capital: float
    ) -> Optional[ArbitrageRoute]:
        """
        Calculate 2-hop arbitrage profit.
        
        Path: Currency A -> Currency B -> Currency A
        Example: USDT -> BTC -> USDT
        
        Args:
            pair1: First trading pair (buy)
            pair2: Second trading pair (sell)
            capital: Starting capital in quote currency
            
        Returns:
            ArbitrageRoute if profitable, None otherwise
        """
        # Step 1: Buy on Exchange 1
        amount_after_fee1 = capital * (1 - pair1.exchange.trading_fee)
        btc_bought = amount_after_fee1 / pair1.ask_price
        
        # Calculate slippage impact for first trade
        trade_size_factor1 = capital / 100000  # Per $100k
        slippage1 = pair1.exchange.slippage_factor * trade_size_factor1
        btc_bought *= (1 - slippage1)
        
        # Step 2: Sell on Exchange 2
        usdt_received = btc_bought * pair2.bid_price
        amount_after_fee2 = usdt_received * (1 - pair2.exchange.trading_fee)
        
        # Calculate slippage impact for second trade
        trade_size_factor2 = usdt_received / 100000
        slippage2 = pair2.exchange.slippage_factor * trade_size_factor2
        amount_after_fee2 *= (1 - slippage2)
        
        # Step 3: Account for gas costs
        total_gas = pair1.exchange.gas_cost + pair2.exchange.gas_cost
        final_amount = amount_after_fee2 - total_gas
        
        # Calculate metrics
        gross_profit = final_amount - capital
        gross_profit_bps = (gross_profit / capital) * 10000
        
        total_fees = (capital * pair1.exchange.trading_fee + 
                     usdt_received * pair2.exchange.trading_fee)
        total_slippage = slippage1 + slippage2
        
        # Risk score calculation
        risk_score = self._calculate_risk_score(
            profit_bps=gross_profit_bps,
            slippage=total_slippage,
            liquidity=min(pair1.liquidity, pair2.liquidity),
            execution_complexity=2
        )
        
        # Apply safety margin
        net_profit_bps = gross_profit_bps * (1 - self.safety_margin)
        
        # Check if profitable
        if net_profit_bps < self.min_profit_bps:
            return None
        
        # Check liquidity constraints
        max_capital = min(
            pair1.liquidity * 0.1,  # Max 10% of liquidity
            pair2.liquidity * 0.1
        )
        
        return ArbitrageRoute(
            route_type=RouteType.TWO_HOP,
            pairs=[pair1, pair2],
            path=[pair1.quote, pair1.base, pair2.quote],
            expected_profit=gross_profit * (1 - self.safety_margin),
            expected_profit_bps=net_profit_bps,
            risk_score=risk_score,
            execution_time_ms=100.0,  # Estimate
            total_fees=total_fees,
            total_gas=total_gas,
            slippage_estimate=total_slippage,
            min_capital_required=1000.0,
            max_capital_recommended=max_capital
        )
    
    def calculate_3hop_arbitrage(
        self,
        pair1: TradingPair,  # USDT -> BTC
        pair2: TradingPair,  # BTC -> ETH
        pair3: TradingPair,  # ETH -> USDT
        capital: float
    ) -> Optional[ArbitrageRoute]:
        """
        Calculate 3-hop (triangular) arbitrage profit.
        
        Path: A -> B -> C -> A
        Example: USDT -> BTC -> ETH -> USDT
        
        Args:
            pair1: First pair (A -> B)
            pair2: Second pair (B -> C)
            pair3: Third pair (C -> A)
            capital: Starting capital
            
        Returns:
            ArbitrageRoute if profitable, None otherwise
        """
        # Step 1: USDT -> BTC
        amount1 = capital * (1 - pair1.exchange.trading_fee)
        slippage1 = self._calculate_slippage(capital, pair1.exchange)
        amount1 *= (1 - slippage1)
        btc_amount = amount1 / pair1.ask_price
        
        # Step 2: BTC -> ETH
        btc_value = btc_amount * pair2.ask_price  # Convert to quote
        amount2 = btc_value * (1 - pair2.exchange.trading_fee)
        slippage2 = self._calculate_slippage(btc_value, pair2.exchange)
        amount2 *= (1 - slippage2)
        eth_amount = amount2 / pair2.ask_price
        
        # Step 3: ETH -> USDT
        eth_value = eth_amount * pair3.bid_price
        amount3 = eth_value * (1 - pair3.exchange.trading_fee)
        slippage3 = self._calculate_slippage(eth_value, pair3.exchange)
        amount3 *= (1 - slippage3)
        
        # Account for gas
        total_gas = (pair1.exchange.gas_cost + 
                    pair2.exchange.gas_cost + 
                    pair3.exchange.gas_cost)
        final_amount = amount3 - total_gas
        
        # Calculate metrics
        gross_profit = final_amount - capital
        gross_profit_bps = (gross_profit / capital) * 10000
        
        total_fees = (capital * pair1.exchange.trading_fee +
                     btc_value * pair2.exchange.trading_fee +
                     eth_value * pair3.exchange.trading_fee)
        
        total_slippage = slippage1 + slippage2 + slippage3
        
        # Risk score
        risk_score = self._calculate_risk_score(
            profit_bps=gross_profit_bps,
            slippage=total_slippage,
            liquidity=min(pair1.liquidity, pair2.liquidity, pair3.liquidity),
            execution_complexity=3
        )
        
        # Apply safety margin
        net_profit_bps = gross_profit_bps * (1 - self.safety_margin)
        
        if net_profit_bps < self.min_profit_bps:
            return None
        
        max_capital = min(
            pair1.liquidity * 0.1,
            pair2.liquidity * 0.1,
            pair3.liquidity * 0.1
        )
        
        return ArbitrageRoute(
            route_type=RouteType.THREE_HOP,
            pairs=[pair1, pair2, pair3],
            path=[pair1.quote, pair1.base, pair2.base, pair3.quote],
            expected_profit=gross_profit * (1 - self.safety_margin),
            expected_profit_bps=net_profit_bps,
            risk_score=risk_score,
            execution_time_ms=150.0,
            total_fees=total_fees,
            total_gas=total_gas,
            slippage_estimate=total_slippage,
            min_capital_required=2000.0,
            max_capital_recommended=max_capital
        )
    
    def calculate_4hop_arbitrage(
        self,
        pair1: TradingPair,
        pair2: TradingPair,
        pair3: TradingPair,
        pair4: TradingPair,
        capital: float
    ) -> Optional[ArbitrageRoute]:
        """
        Calculate 4-hop (rectangular) arbitrage profit.
        
        Path: A -> B -> C -> D -> A
        Example: USDT -> BTC -> ETH -> BNB -> USDT
        
        Args:
            pair1-pair4: Trading pairs
            capital: Starting capital
            
        Returns:
            ArbitrageRoute if profitable, None otherwise
        """
        pairs = [pair1, pair2, pair3, pair4]
        current_amount = Decimal(str(capital))
        
        total_fees = Decimal('0')
        total_slippage = 0.0
        total_gas = 0.0
        
        # Execute all 4 hops
        for i, pair in enumerate(pairs):
            # Apply trading fee
            fee = current_amount * Decimal(str(pair.exchange.trading_fee))
            total_fees += fee
            current_amount -= fee
            
            # Calculate and apply slippage
            slippage = self._calculate_slippage(float(current_amount), pair.exchange)
            total_slippage += slippage
            current_amount *= Decimal(str(1 - slippage))
            
            # Convert through the pair
            if i % 2 == 0:  # Buy
                current_amount = current_amount / Decimal(str(pair.ask_price))
            else:  # Sell
                current_amount = current_amount * Decimal(str(pair.bid_price))
            
            # Add gas cost
            total_gas += pair.exchange.gas_cost
        
        # Subtract total gas costs
        final_amount = float(current_amount) - total_gas
        
        # Calculate metrics
        gross_profit = final_amount - capital
        gross_profit_bps = (gross_profit / capital) * 10000
        
        # Risk score - highest complexity
        min_liquidity = min(p.liquidity for p in pairs)
        risk_score = self._calculate_risk_score(
            profit_bps=gross_profit_bps,
            slippage=total_slippage,
            liquidity=min_liquidity,
            execution_complexity=4
        )
        
        # Apply safety margin
        net_profit_bps = gross_profit_bps * (1 - self.safety_margin)
        
        if net_profit_bps < self.min_profit_bps:
            return None
        
        max_capital = min(p.liquidity * 0.05 for p in pairs)  # More conservative
        
        return ArbitrageRoute(
            route_type=RouteType.FOUR_HOP,
            pairs=pairs,
            path=[pair1.quote, pair1.base, pair2.base, pair3.base, pair4.quote],
            expected_profit=gross_profit * (1 - self.safety_margin),
            expected_profit_bps=net_profit_bps,
            risk_score=risk_score,
            execution_time_ms=200.0,
            total_fees=float(total_fees),
            total_gas=total_gas,
            slippage_estimate=total_slippage,
            min_capital_required=5000.0,
            max_capital_recommended=max_capital
        )
    
    def calculate_risk_reward_ratio(
        self,
        route: ArbitrageRoute,
        capital: float
    ) -> Dict[str, float]:
        """
        Calculate comprehensive risk/reward metrics for a route.
        
        Args:
            route: Arbitrage route
            capital: Capital to be deployed
            
        Returns:
            Dictionary with risk metrics
        """
        # Potential reward
        expected_reward = route.expected_profit
        
        # Potential risk factors
        slippage_risk = capital * (route.slippage_estimate * 2)  # 2x worst case
        fee_risk = route.total_fees * 1.5  # 1.5x expected fees
        gas_risk = route.total_gas * 2.0  # Gas can spike 2x
        liquidity_risk = capital * 0.01  # 1% liquidity risk
        
        # Execution risk (time-dependent)
        execution_risk = capital * (route.execution_time_ms / 1000) * 0.001
        
        # Total risk
        total_risk = (slippage_risk + fee_risk + gas_risk + 
                     liquidity_risk + execution_risk)
        
        # Risk/Reward ratio
        rr_ratio = expected_reward / total_risk if total_risk > 0 else 0
        
        # Probability of profit (based on historical data)
        profit_probability = self._estimate_profit_probability(
            route.expected_profit_bps,
            route.risk_score
        )
        
        # Expected value
        expected_value = (expected_reward * profit_probability) - \
                        (total_risk * (1 - profit_probability))
        
        # Sharpe-like ratio (reward per unit of risk)
        sharpe_like = expected_reward / (total_risk + 1e-10)
        
        return {
            'expected_reward_usd': expected_reward,
            'expected_reward_bps': route.expected_profit_bps,
            'total_risk_usd': total_risk,
            'total_risk_bps': (total_risk / capital) * 10000,
            'risk_reward_ratio': rr_ratio,
            'profit_probability': profit_probability,
            'expected_value': expected_value,
            'sharpe_like_ratio': sharpe_like,
            'slippage_risk': slippage_risk,
            'fee_risk': fee_risk,
            'gas_risk': gas_risk,
            'execution_risk': execution_risk,
            'max_drawdown_estimate': total_risk * 1.5,
            'break_even_success_rate': total_risk / (expected_reward + total_risk),
            'kelly_fraction': self._calculate_kelly_for_arb(
                profit_probability, expected_reward, total_risk
            )
        }
    
    def _calculate_slippage(self, trade_size: float, exchange: Exchange) -> float:
        """Calculate slippage for a trade size."""
        size_factor = trade_size / 100000  # Per $100k
        base_slippage = exchange.slippage_factor * size_factor
        
        # Non-linear slippage for large trades
        if size_factor > 5:
            base_slippage *= (1 + (size_factor - 5) * 0.1)
        
        return min(base_slippage, 0.05)  # Cap at 5%
    
    def _calculate_risk_score(
        self,
        profit_bps: float,
        slippage: float,
        liquidity: float,
        execution_complexity: int
    ) -> float:
        """
        Calculate risk score (0-100, lower is better).
        
        Args:
            profit_bps: Expected profit in basis points
            slippage: Total slippage estimate
            liquidity: Minimum liquidity in route
            execution_complexity: Number of hops
            
        Returns:
            Risk score
        """
        # Profit factor (inverse - lower profit = higher risk)
        profit_risk = max(0, 50 - profit_bps) / 50 * 30
        
        # Slippage risk
        slippage_risk = (slippage / self.max_slippage_bps * 10000) * 25
        
        # Liquidity risk (inverse)
        liquidity_risk = max(0, 1000000 - liquidity) / 1000000 * 25
        
        # Complexity risk
        complexity_risk = (execution_complexity - 2) * 10
        
        total_risk = profit_risk + slippage_risk + liquidity_risk + complexity_risk
        
        return min(100, max(0, total_risk))
    
    def _estimate_profit_probability(
        self,
        profit_bps: float,
        risk_score: float
    ) -> float:
        """
        Estimate probability of profitable execution.
        
        Args:
            profit_bps: Expected profit in basis points
            risk_score: Risk score (0-100)
            
        Returns:
            Probability (0-1)
        """
        # Base probability from profit margin
        base_prob = min(0.95, profit_bps / 200.0)  # 200 bps = 95% probability
        
        # Adjust for risk
        risk_adjustment = (100 - risk_score) / 100
        
        final_prob = base_prob * risk_adjustment
        
        return max(0.1, min(0.95, final_prob))
    
    def _calculate_kelly_for_arb(
        self,
        win_prob: float,
        win_amount: float,
        loss_amount: float
    ) -> float:
        """
        Calculate Kelly Criterion fraction for arbitrage.
        
        Args:
            win_prob: Probability of profit
            win_amount: Expected profit
            loss_amount: Expected loss
            
        Returns:
            Kelly fraction (0-1)
        """
        if loss_amount <= 0:
            return 0.0
        
        b = win_amount / loss_amount  # Win/loss ratio
        p = win_prob
        q = 1 - win_prob
        
        kelly = (p * b - q) / b if b > 0 else 0
        
        # Use fractional Kelly (25%) for safety
        return max(0, min(0.25, kelly * 0.25))


def format_arbitrage_report(
    route: ArbitrageRoute,
    risk_metrics: Dict[str, float],
    capital: float
) -> str:
    """
    Format arbitrage route and risk metrics into human-readable report.
    
    Args:
        route: Arbitrage route
        risk_metrics: Risk metrics dictionary
        capital: Capital amount
        
    Returns:
        Formatted report string
    """
    report = []
    report.append("="*70)
    report.append(f"ARBITRAGE OPPORTUNITY REPORT - {route.route_type.name}")
    report.append("="*70)
    report.append("")
    
    report.append(f"Route Path: {' → '.join(route.path)}")
    report.append(f"Number of Hops: {route.route_type.value}")
    report.append("")
    
    report.append("PROFIT ANALYSIS:")
    report.append(f"  Capital Required: ${capital:,.2f} USD")
    report.append(f"  Expected Profit: ${route.expected_profit:,.2f} USD")
    report.append(f"  Profit Margin: {route.expected_profit_bps:.2f} basis points ({route.expected_profit_bps/100:.2f}%)")
    report.append(f"  ROI: {(route.expected_profit/capital)*100:.2f}%")
    report.append("")
    
    report.append("COST BREAKDOWN:")
    report.append(f"  Trading Fees: ${route.total_fees:,.2f} USD")
    report.append(f"  Gas Costs: ${route.total_gas:,.2f} USD")
    report.append(f"  Estimated Slippage: {route.slippage_estimate*10000:.2f} bps ({route.slippage_estimate*100:.2f}%)")
    report.append(f"  Total Costs: ${route.total_fees + route.total_gas:,.2f} USD")
    report.append("")
    
    report.append("RISK ANALYSIS:")
    report.append(f"  Risk Score: {route.risk_score:.1f}/100 ({'LOW' if route.risk_score < 30 else 'MEDIUM' if route.risk_score < 60 else 'HIGH'})")
    report.append(f"  Total Risk Exposure: ${risk_metrics['total_risk_usd']:,.2f} USD ({risk_metrics['total_risk_bps']:.2f} bps)")
    report.append(f"  Risk/Reward Ratio: {risk_metrics['risk_reward_ratio']:.2f}:1")
    report.append(f"  Profit Probability: {risk_metrics['profit_probability']*100:.1f}%")
    report.append(f"  Expected Value: ${risk_metrics['expected_value']:,.2f} USD")
    report.append("")
    
    report.append("POSITION SIZING:")
    report.append(f"  Min Capital: ${route.min_capital_required:,.2f} USD")
    report.append(f"  Max Recommended: ${route.max_capital_recommended:,.2f} USD")
    report.append(f"  Kelly Fraction: {risk_metrics['kelly_fraction']*100:.2f}%")
    report.append(f"  Suggested Size: ${capital * risk_metrics['kelly_fraction']:,.2f} USD")
    report.append("")
    
    report.append("EXECUTION METRICS:")
    report.append(f"  Est. Execution Time: {route.execution_time_ms:.0f} ms")
    report.append(f"  Break-Even Success Rate: {risk_metrics['break_even_success_rate']*100:.1f}%")
    report.append(f"  Sharpe-Like Ratio: {risk_metrics['sharpe_like_ratio']:.2f}")
    report.append("")
    
    report.append("RECOMMENDATION:")
    if route.risk_score < 30 and risk_metrics['risk_reward_ratio'] > 2:
        report.append("  ✅ EXECUTE - Low risk, favorable risk/reward")
    elif route.risk_score < 60 and risk_metrics['risk_reward_ratio'] > 1.5:
        report.append("  ⚠️  CONSIDER - Moderate risk, acceptable risk/reward")
    else:
        report.append("  ❌ AVOID - High risk or unfavorable risk/reward")
    
    report.append("="*70)
    
    return "\n".join(report)
