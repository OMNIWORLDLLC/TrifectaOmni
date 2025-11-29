"""
Multi-hop arbitrage calculator with comprehensive profit and risk calculations.

Supports 2-hop, 3-hop, and 4-hop arbitrage routes with:
- Profit calculation accounting for fees
- Risk/reward ratio analysis
- Slippage modeling
- Gas cost estimation
- Minimum profit thresholds

Also includes the Universal Arbitrage Equation with Dynamic Flash Loans:
  Π_net = V_loan * ([P_A * (1 - S_A)] - [P_B * (1 + S_B)] - F_rate)

With TVL-based constraints:
  C_min * TVL ≤ V_loan ≤ C_max * TVL
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


class CalculatorType(Enum):
    """Calculator implementation type."""
    LEGACY = "legacy"  # Original multi-hop calculator
    UNIVERSAL = "universal"  # Universal Arbitrage Equation


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


# ============================================================================
# Universal Arbitrage Equation with Dynamic Flash Loans
# ============================================================================

@dataclass
class FlashLoanParams:
    """Flash loan configuration parameters.
    
    Implements the Universal Arbitrage Equation with TVL constraints:
    
    Profit Equation:
        net_profit = loan_volume * (price_ratio - 1 - fee_rate)
        
    Where:
        price_ratio = (price_sell * (1 - slippage_sell)) / (price_buy * (1 + slippage_buy))
    
    Volume Constraint:
        min_volume <= loan_volume <= max_volume
        min_volume = min_coefficient * tvl
        max_volume = max_coefficient * tvl
    
    Attributes:
        tvl: Total Value Locked in the liquidity pool (USD)
        fee_rate: Flash loan fee rate (e.g., 0.0009 = 0.09% for Aave)
        c_min: Minimum liquidity coefficient (e.g., 0.05 = 5% of TVL)
        c_max: Maximum liquidity coefficient (e.g., 0.20 = 20% of TVL)
    """
    tvl: float  # Total Value Locked in the liquidity pool
    fee_rate: float = 0.0009  # Flash loan fee rate (0.09% for Aave)
    c_min: float = 0.05  # Minimum Liquidity Coefficient (5%)
    c_max: float = 0.20  # Maximum Liquidity Coefficient (20%)
    
    @property
    def v_min(self) -> float:
        """Minimum flash loan volume based on TVL."""
        return self.c_min * self.tvl
    
    @property
    def v_max(self) -> float:
        """Maximum flash loan volume based on TVL."""
        return self.c_max * self.tvl


@dataclass
class UniversalArbitrageResult:
    """Result from Universal Arbitrage Equation calculation."""
    net_profit: float
    gross_profit: float
    loan_volume: float
    effective_sell_price: float
    effective_buy_price: float
    slippage_sell: float
    slippage_buy: float
    flash_loan_cost: float
    flash_fee_rate: float
    profit_bps: float
    is_profitable: bool
    optimal_volume: float
    max_loan_allowed: float
    min_loan_required: float
    price_spread_bps: float
    # Additional accuracy variables
    market_volatility: float = 0.0
    liquidity_depth_ratio: float = 1.0
    execution_probability: float = 1.0
    time_decay_factor: float = 1.0
    gas_adjusted_profit: float = 0.0


class UniversalArbitrageCalculator:
    """
    Universal Arbitrage Calculator implementing the Master Equation:
    
        Π_net = V_loan * ([P_A * (1 - S_A)] - [P_B * (1 + S_B)] - F_rate)
    
    This provides a cleaner, more mathematically rigorous approach to
    arbitrage profit calculation compared to the legacy multi-hop approach.
    
    Key differences from legacy calculator:
    1. Explicit flash loan integration with fee modeling
    2. TVL-based volume constraints
    3. Symmetric slippage modeling (buy vs sell)
    4. Single formula for profit calculation
    5. Built-in optimal volume calculation
    
    Additional accuracy variables:
    - Market volatility adjustment
    - Liquidity depth ratio
    - Execution probability
    - Time decay factor (MEV protection)
    - Gas price adjustment
    """
    
    def __init__(
        self,
        min_profit_bps: float = 30.0,
        max_slippage_pct: float = 0.5,  # 0.5% max slippage
        safety_margin: float = 0.20,
        gas_price_gwei: float = 50.0,  # Current gas price
        block_time_ms: float = 12000.0  # Ethereum ~12 seconds
    ):
        """
        Initialize Universal Arbitrage Calculator.
        
        Args:
            min_profit_bps: Minimum profit in basis points (30 = 0.30%)
            max_slippage_pct: Maximum acceptable slippage as percentage
            safety_margin: Safety margin fraction (0.2 = 20%)
            gas_price_gwei: Gas price in Gwei for cost estimation
            block_time_ms: Block time in milliseconds for execution timing
        """
        self.min_profit_bps = min_profit_bps
        self.max_slippage_pct = max_slippage_pct / 100  # Convert to decimal
        self.safety_margin = safety_margin
        self.gas_price_gwei = gas_price_gwei
        self.block_time_ms = block_time_ms
        
    def calculate_profit(
        self,
        amount_borrowed: float,
        price_sell: float,
        slippage_sell: float,
        price_buy: float,
        slippage_buy: float,
        flash_fee_rate: float
    ) -> float:
        """
        Raw Universal Arbitrage Equation.
        
        The equation models the actual arbitrage flow:
        1. Borrow V_loan USD via flash loan
        2. Buy tokens at P_B (with slippage): tokens = V_loan / (P_B * (1 + S_B))
        3. Sell tokens at P_A (with slippage): USD = tokens * P_A * (1 - S_A)
        4. Repay flash loan + fee
        
        Simplified to:
            Π_net = V_loan * [(P_A * (1 - S_A)) / (P_B * (1 + S_B)) - 1 - F_rate]
        
        Or equivalently:
            Π_net = V_loan * [Price_Ratio - 1 - F_rate]
            
        Where Price_Ratio = Effective_Sell / Effective_Buy
        
        Args:
            amount_borrowed: V_loan - Flash loan volume in USD
            price_sell: P_A - Price on Sell Chain (High Price, USD per token)
            slippage_sell: S_A - Slippage on Sell Chain (decimal, e.g., 0.01)
            price_buy: P_B - Price on Buy Chain (Low Price, USD per token)
            slippage_buy: S_B - Slippage on Buy Chain (decimal, e.g., 0.01)
            flash_fee_rate: F_rate - Flash loan fee rate (e.g., 0.0009)
        
        Returns:
            Net profit in quote currency (USD)
        """
        # 1. Effective Sell Price (Slippage reduces sell price)
        eff_sell = price_sell * (1 - slippage_sell)
        
        # 2. Effective Buy Price (Slippage increases buy cost)
        eff_buy = price_buy * (1 + slippage_buy)
        
        # 3. Calculate tokens bought
        if eff_buy <= 0:
            return 0.0
        tokens_bought = amount_borrowed / eff_buy
        
        # 4. Calculate USD received from selling
        usd_received = tokens_bought * eff_sell
        
        # 5. Flash Loan Cost
        loan_cost = amount_borrowed * flash_fee_rate
        
        # 6. Net Profit = USD received - original loan - loan fee
        return usd_received - amount_borrowed - loan_cost
    
    def calculate_optimal_volume(
        self,
        flash_params: FlashLoanParams,
        price_sell: float,
        price_buy: float,
        base_slippage_sell: float,
        base_slippage_buy: float,
        slippage_impact_factor: float = 0.00001
    ) -> float:
        """
        Calculate optimal flash loan volume that maximizes profit.
        
        As volume increases:
        - Gross profit increases linearly
        - Slippage increases (often quadratically with volume)
        
        The optimal volume balances these effects.
        
        Mathematical derivation:
        Profit(V) = V * (spread / price_buy - slippage_factor * V - fee_rate)
        dProfit/dV = spread / price_buy - 2 * slippage_factor * V - fee_rate = 0
        V_optimal = (spread / price_buy - fee_rate) / (2 * slippage_factor)
        
        Simplified: V_opt ≈ (spread - fee_rate * price_avg) / (2 * slippage_factor * price_avg)
        
        Args:
            flash_params: Flash loan parameters with TVL constraints
            price_sell: Sell price (higher price chain)
            price_buy: Buy price (lower price chain)
            base_slippage_sell: Base slippage on sell side
            base_slippage_buy: Base slippage on buy side
            slippage_impact_factor: How slippage scales with volume (per dollar)
        
        Returns:
            Optimal loan volume constrained by TVL limits
        """
        # Price spread: the raw price difference between exchanges
        spread = price_sell - price_buy
        
        if spread <= 0:
            # No arbitrage opportunity exists
            return 0.0
        
        # Calculate combined slippage factor across both exchanges
        # This scales with the average price level to normalize impact
        total_slippage_factor = slippage_impact_factor * (price_sell + price_buy)
        
        # Use small epsilon to avoid division by zero
        epsilon = 1e-12
        if total_slippage_factor <= epsilon:
            # Negligible slippage means we can use max allowed volume
            return flash_params.v_max
        
        # Optimal volume from derivative of profit function set to zero
        v_optimal = (spread - flash_params.fee_rate) / (2 * total_slippage_factor)
        
        # Constrain to TVL limits
        return max(flash_params.v_min, min(flash_params.v_max, v_optimal))
    
    def calculate_dynamic_slippage(
        self,
        volume: float,
        base_slippage: float,
        liquidity: float,
        volatility: float = 0.0
    ) -> float:
        """
        Calculate dynamic slippage based on volume and market conditions.
        
        Slippage model:
            S = S_base + (V / L) * k + σ * c
        
        Where:
            S_base = base slippage
            V = trade volume
            L = liquidity depth
            k = volume impact coefficient
            σ = volatility
            c = volatility coefficient
        
        Args:
            volume: Trade volume in USD
            base_slippage: Base slippage rate (decimal)
            liquidity: Pool liquidity in USD
            volatility: Market volatility (decimal, 0-1)
        
        Returns:
            Effective slippage as decimal
        """
        # Volume impact (quadratic for large trades)
        if liquidity > 0:
            volume_ratio = volume / liquidity
            volume_impact = volume_ratio * (1 + volume_ratio)  # Quadratic
        else:
            volume_impact = 0.1  # Default high slippage for no liquidity
        
        # Volatility impact
        volatility_impact = volatility * 0.5  # 50% of volatility adds to slippage
        
        # Total slippage
        total_slippage = base_slippage + volume_impact + volatility_impact
        
        return min(total_slippage, self.max_slippage_pct)
    
    def calculate_arbitrage(
        self,
        price_sell: float,
        price_buy: float,
        flash_params: FlashLoanParams,
        liquidity_sell: float,
        liquidity_buy: float,
        base_slippage_sell: float = 0.001,
        base_slippage_buy: float = 0.001,
        volatility: float = 0.0,
        gas_cost_usd: float = 0.0,
        execution_probability: float = 1.0
    ) -> UniversalArbitrageResult:
        """
        Full arbitrage calculation using Universal Arbitrage Equation.
        
        Args:
            price_sell: P_A - Price on sell chain (should be higher)
            price_buy: P_B - Price on buy chain (should be lower)
            flash_params: Flash loan configuration
            liquidity_sell: Liquidity on sell chain
            liquidity_buy: Liquidity on buy chain
            base_slippage_sell: Base slippage on sell side
            base_slippage_buy: Base slippage on buy side
            volatility: Current market volatility (0-1)
            gas_cost_usd: Estimated gas cost in USD
            execution_probability: Probability of successful execution
        
        Returns:
            UniversalArbitrageResult with full profit analysis
        """
        # Calculate optimal volume
        optimal_volume = self.calculate_optimal_volume(
            flash_params, price_sell, price_buy,
            base_slippage_sell, base_slippage_buy
        )
        
        # Calculate dynamic slippage for optimal volume
        slippage_sell = self.calculate_dynamic_slippage(
            optimal_volume, base_slippage_sell, liquidity_sell, volatility
        )
        slippage_buy = self.calculate_dynamic_slippage(
            optimal_volume, base_slippage_buy, liquidity_buy, volatility
        )
        
        # Calculate effective prices
        effective_sell = price_sell * (1 - slippage_sell)
        effective_buy = price_buy * (1 + slippage_buy)
        
        # Calculate profit using master equation
        net_profit = self.calculate_profit(
            optimal_volume,
            price_sell, slippage_sell,
            price_buy, slippage_buy,
            flash_params.fee_rate
        )
        
        # Gross profit (before flash loan cost) - correctly calculated
        # tokens_bought = optimal_volume / effective_buy
        # usd_received = tokens_bought * effective_sell
        # gross_profit = usd_received - optimal_volume
        if effective_buy > 0:
            tokens_bought = optimal_volume / effective_buy
            usd_received = tokens_bought * effective_sell
            gross_profit = usd_received - optimal_volume
        else:
            gross_profit = 0.0
        
        # Flash loan cost
        flash_loan_cost = optimal_volume * flash_params.fee_rate
        
        # Gas adjusted profit
        gas_adjusted_profit = net_profit - gas_cost_usd
        
        # Calculate price spread in basis points
        price_spread_bps = ((price_sell - price_buy) / price_buy) * 10000
        
        # Profit in basis points
        if optimal_volume > 0:
            profit_bps = (net_profit / optimal_volume) * 10000
        else:
            profit_bps = 0.0
        
        # Liquidity depth ratio (average of both sides)
        min_liquidity = min(liquidity_sell, liquidity_buy)
        liquidity_depth_ratio = min_liquidity / flash_params.tvl if flash_params.tvl > 0 else 0
        
        # Time decay factor (MEV protection) - reduces with volatility
        time_decay_factor = max(0.5, 1.0 - volatility * 0.5)
        
        # Apply safety margin and execution probability
        adjusted_profit = gas_adjusted_profit * (1 - self.safety_margin) * execution_probability * time_decay_factor
        
        return UniversalArbitrageResult(
            net_profit=net_profit,
            gross_profit=gross_profit,
            loan_volume=optimal_volume,
            effective_sell_price=effective_sell,
            effective_buy_price=effective_buy,
            slippage_sell=slippage_sell,
            slippage_buy=slippage_buy,
            flash_loan_cost=flash_loan_cost,
            flash_fee_rate=flash_params.fee_rate,
            profit_bps=profit_bps,
            is_profitable=adjusted_profit > 0 and profit_bps >= self.min_profit_bps,
            optimal_volume=optimal_volume,
            max_loan_allowed=flash_params.v_max,
            min_loan_required=flash_params.v_min,
            price_spread_bps=price_spread_bps,
            market_volatility=volatility,
            liquidity_depth_ratio=liquidity_depth_ratio,
            execution_probability=execution_probability,
            time_decay_factor=time_decay_factor,
            gas_adjusted_profit=gas_adjusted_profit
        )
    
    def compare_with_legacy(
        self,
        pair_buy: TradingPair,
        pair_sell: TradingPair,
        capital: float,
        flash_params: Optional[FlashLoanParams] = None,
        legacy_calculator: Optional[MultiHopArbitrageCalculator] = None
    ) -> Dict[str, Any]:
        """
        Compare Universal Arbitrage Equation with legacy calculator.
        
        This method enables direct A/B comparison between the two approaches.
        
        Args:
            pair_buy: Trading pair for buying
            pair_sell: Trading pair for selling
            capital: Capital amount for comparison
            flash_params: Flash loan parameters (derived from TVL if not provided)
            legacy_calculator: Legacy calculator instance (created if not provided)
        
        Returns:
            Comparison results with both calculations and analysis
        """
        # Create default flash params from liquidity
        if flash_params is None:
            tvl = min(pair_buy.liquidity, pair_sell.liquidity)
            flash_params = FlashLoanParams(tvl=tvl)
        
        # Create legacy calculator if not provided
        if legacy_calculator is None:
            legacy_calculator = MultiHopArbitrageCalculator(
                min_profit_bps=self.min_profit_bps,
                max_slippage_bps=self.max_slippage_pct * 10000,
                safety_margin=self.safety_margin
            )
        
        # Legacy calculation
        legacy_route = legacy_calculator.calculate_2hop_arbitrage(
            pair_buy, pair_sell, capital
        )
        
        # Universal calculation
        universal_result = self.calculate_arbitrage(
            price_sell=pair_sell.bid_price,
            price_buy=pair_buy.ask_price,
            flash_params=flash_params,
            liquidity_sell=pair_sell.liquidity,
            liquidity_buy=pair_buy.liquidity,
            base_slippage_sell=pair_sell.exchange.slippage_factor,
            base_slippage_buy=pair_buy.exchange.slippage_factor,
            gas_cost_usd=pair_buy.exchange.gas_cost + pair_sell.exchange.gas_cost
        )
        
        # Comparison analysis
        comparison = {
            "legacy": {
                "profit": legacy_route.expected_profit if legacy_route else 0,
                "profit_bps": legacy_route.expected_profit_bps if legacy_route else 0,
                "is_profitable": legacy_route is not None,
                "total_fees": legacy_route.total_fees if legacy_route else 0,
                "slippage": legacy_route.slippage_estimate if legacy_route else 0,
            },
            "universal": {
                "profit": universal_result.net_profit,
                "profit_bps": universal_result.profit_bps,
                "is_profitable": universal_result.is_profitable,
                "total_fees": universal_result.flash_loan_cost,
                "slippage": (universal_result.slippage_sell + universal_result.slippage_buy) / 2,
                "optimal_volume": universal_result.optimal_volume,
                "gas_adjusted_profit": universal_result.gas_adjusted_profit,
            },
            "analysis": {
                "profit_difference": universal_result.net_profit - (legacy_route.expected_profit if legacy_route else 0),
                "profit_bps_difference": universal_result.profit_bps - (legacy_route.expected_profit_bps if legacy_route else 0),
                "recommended_calculator": self._recommend_calculator(legacy_route, universal_result),
                "accuracy_improvements": self._list_accuracy_improvements(universal_result),
            }
        }
        
        return comparison
    
    def _recommend_calculator(
        self,
        legacy_route: Optional[ArbitrageRoute],
        universal_result: UniversalArbitrageResult
    ) -> str:
        """Recommend which calculator to use based on results."""
        legacy_profit = legacy_route.expected_profit if legacy_route else 0
        universal_profit = universal_result.net_profit
        
        if universal_profit > legacy_profit * 1.1:
            return "UNIVERSAL - Higher estimated profit with flash loan optimization"
        elif legacy_profit > universal_profit * 1.1:
            return "LEGACY - More conservative approach preferred"
        else:
            return "EITHER - Results are similar, choose based on execution preference"
    
    def _list_accuracy_improvements(self, result: UniversalArbitrageResult) -> List[str]:
        """List accuracy improvements provided by Universal calculator."""
        improvements = []
        
        if result.market_volatility > 0:
            improvements.append("Market volatility adjustment applied")
        if result.liquidity_depth_ratio < 1:
            improvements.append("Liquidity depth ratio factored in")
        if result.execution_probability < 1:
            improvements.append("Execution probability discount applied")
        if result.time_decay_factor < 1:
            improvements.append("MEV protection time decay applied")
        if result.gas_adjusted_profit != result.net_profit:
            improvements.append("Gas costs subtracted from profit")
        
        return improvements


def format_comparison_report(comparison: Dict[str, Any], capital: float) -> str:
    """
    Format comparison between Universal and Legacy calculators.
    
    Args:
        comparison: Comparison dictionary from compare_with_legacy
        capital: Capital amount used
    
    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 80)
    report.append("ARBITRAGE CALCULATOR COMPARISON REPORT")
    report.append("Universal Arbitrage Equation vs Legacy Multi-Hop Calculator")
    report.append("=" * 80)
    report.append("")
    
    report.append(f"Capital: ${capital:,.2f}")
    report.append("")
    
    legacy = comparison["legacy"]
    universal = comparison["universal"]
    analysis = comparison["analysis"]
    
    report.append("LEGACY CALCULATOR (Multi-Hop):")
    report.append(f"  Expected Profit: ${legacy['profit']:,.2f}")
    report.append(f"  Profit Margin: {legacy['profit_bps']:.2f} bps")
    report.append(f"  Is Profitable: {'Yes' if legacy['is_profitable'] else 'No'}")
    report.append(f"  Total Fees: ${legacy['total_fees']:,.2f}")
    report.append(f"  Slippage: {legacy['slippage']*10000:.2f} bps")
    report.append("")
    
    report.append("UNIVERSAL CALCULATOR (Flash Loan Equation):")
    report.append(f"  Net Profit: ${universal['profit']:,.2f}")
    report.append(f"  Profit Margin: {universal['profit_bps']:.2f} bps")
    report.append(f"  Is Profitable: {'Yes' if universal['is_profitable'] else 'No'}")
    report.append(f"  Flash Loan Cost: ${universal['total_fees']:,.2f}")
    report.append(f"  Avg Slippage: {universal['slippage']*10000:.2f} bps")
    report.append(f"  Optimal Volume: ${universal['optimal_volume']:,.2f}")
    report.append(f"  Gas Adjusted Profit: ${universal['gas_adjusted_profit']:,.2f}")
    report.append("")
    
    report.append("COMPARISON ANALYSIS:")
    report.append(f"  Profit Difference: ${analysis['profit_difference']:,.2f}")
    report.append(f"  Profit BPS Difference: {analysis['profit_bps_difference']:.2f} bps")
    report.append(f"  Recommendation: {analysis['recommended_calculator']}")
    report.append("")
    
    if analysis['accuracy_improvements']:
        report.append("ACCURACY IMPROVEMENTS (Universal):")
        for improvement in analysis['accuracy_improvements']:
            report.append(f"  • {improvement}")
        report.append("")
    
    report.append("EQUATION REFERENCE:")
    report.append("  Π_net = V_loan × ([P_A × (1 - S_A)] - [P_B × (1 + S_B)] - F_rate)")
    report.append("  Where: V_loan constrained by C_min × TVL ≤ V_loan ≤ C_max × TVL")
    report.append("=" * 80)
    
    return "\n".join(report)


# ============================================================================
# OmniArb V2 - Zone 6 Real-Yield Equation with Total Cost of Execution
# ============================================================================

class FlashLoanSource(Enum):
    """Flash loan source providers with their fee structures."""
    DYDX = "dydx"       # 0% fee (highest priority)
    BALANCER = "balancer"  # 0% fee (high priority)
    UNISWAP = "uniswap"   # 0.05% fee
    AAVE = "aave"        # 0.09% fee (standard)
    MAKER = "maker"      # Variable fee


class ChainType(Enum):
    """Blockchain network types for chain selection logic."""
    ETHEREUM_MAINNET = "ethereum_mainnet"
    ARBITRUM = "arbitrum"
    OPTIMISM = "optimism"
    POLYGON = "polygon"
    BASE = "base"
    BSC = "bsc"


@dataclass
class FlashLoanSourceConfig:
    """Configuration for different flash loan sources.
    
    Prioritized by fee:
    1. DyDx/Balancer (0% fee) - highest priority
    2. Uniswap (0.05% fee)
    3. Aave (0.09% fee) - standard
    """
    source: FlashLoanSource
    fee_rate: float  # As decimal (0.0009 = 0.09%)
    max_loan_usd: float  # Maximum loan amount in USD
    min_loan_usd: float  # Minimum loan amount in USD
    available: bool = True
    
    @classmethod
    def get_default_sources(cls) -> List["FlashLoanSourceConfig"]:
        """Get default flash loan sources sorted by fee (lowest first)."""
        return [
            cls(FlashLoanSource.DYDX, 0.0, 100_000_000, 10_000, True),
            cls(FlashLoanSource.BALANCER, 0.0, 50_000_000, 5_000, True),
            cls(FlashLoanSource.UNISWAP, 0.0005, 25_000_000, 1_000, True),
            cls(FlashLoanSource.AAVE, 0.0009, 500_000_000, 100, True),
        ]


@dataclass
class ChainConfig:
    """Configuration for different blockchain networks.
    
    Chain Selection Logic (from T.r.u.OG Strategy):
    - Focus on Polygon, Arbitrum, or Base for gas efficiency
    - Ethereum Mainnet only for million-dollar trades due to gas
    """
    chain: ChainType
    avg_gas_cost_usd: float  # Average gas cost for arbitrage tx
    block_time_seconds: float
    is_l2: bool
    recommended_min_trade_usd: float  # Minimum trade size for profitability
    
    @classmethod
    def get_default_chains(cls) -> List["ChainConfig"]:
        """Get default chain configurations."""
        return [
            cls(ChainType.ARBITRUM, 0.10, 0.25, True, 1_000),
            cls(ChainType.OPTIMISM, 0.15, 2.0, True, 1_000),
            cls(ChainType.POLYGON, 0.02, 2.0, True, 500),
            cls(ChainType.BASE, 0.05, 2.0, True, 500),
            cls(ChainType.BSC, 0.10, 3.0, False, 1_000),
            cls(ChainType.ETHEREUM_MAINNET, 50.0, 12.0, False, 1_000_000),
        ]


@dataclass
class TotalCostOfExecution:
    """Total Cost of Execution (T_ce) breakdown.
    
    The Zone 6 Real-Yield Equation requires accounting for all costs:
        T_ce = G_gas + F_flash + F_bridge + B_mev
    
    Where:
        G_gas: Gas cost (critical - must calculate before execution)
        F_flash: Flash loan fee (0.09% Aave, 0% DyDx/Balancer)
        F_bridge: Cross-chain bridge fees (if applicable)
        B_mev: Miner/Validator bribe (priority fee for front-running protection)
    """
    gas_cost: float = 0.0  # G_gas - Gas cost in USD
    flash_loan_fee: float = 0.0  # F_flash - Flash loan fee in USD
    bridge_fee: float = 0.0  # F_bridge - Cross-chain bridge cost
    mev_bribe: float = 0.0  # B_mev - MEV protection bribe
    
    @property
    def total(self) -> float:
        """Total cost of execution in USD."""
        return self.gas_cost + self.flash_loan_fee + self.bridge_fee + self.mev_bribe


@dataclass
class LiquidityDepth:
    """Liquidity Depth (L_d) information for slippage calculation.
    
    Uses Constant Product Formula derivative for dynamic slippage:
        S_dynamic = Δx / (x + Δx)
    
    Where:
        Δx: Size of the Flash Loan / Trade
        x: Total Liquidity in the Pool (TVL)
    
    Sweet Spot Logic (T.r.u.OG Strategy):
        - If loan > 20% TVL: Slippage spikes, avoid
        - If loan < 5% TVL: Profit may not cover gas
        - Optimal: Slippage < 0.5%
    """
    tvl: float  # Total Value Locked in the pool
    token_reserve_a: float  # Reserve of token A (x)
    token_reserve_b: float  # Reserve of token B (y)
    
    def calculate_dynamic_slippage(self, trade_size: float) -> float:
        """
        Calculate dynamic slippage using Constant Product Formula derivative.
        
        Formula: S_dynamic = Δx / (x + Δx)
        
        Args:
            trade_size: Size of the trade in USD (Δx)
            
        Returns:
            Dynamic slippage as decimal (0.005 = 0.5%)
        """
        if self.tvl <= 0:
            return 1.0  # Maximum slippage for empty pool
        
        # S_dynamic = Δx / (x + Δx)
        x = self.tvl
        delta_x = trade_size
        return delta_x / (x + delta_x)
    
    def is_trade_size_safe(self, trade_size: float, max_tvl_pct: float = 0.10) -> bool:
        """
        Check if trade size is within safe bounds.
        
        T.r.u.OG Slippage Guard: Reduce size if Loan_Size > 10% of Pool_Liquidity
        
        Args:
            trade_size: Size of the trade in USD
            max_tvl_pct: Maximum % of TVL to trade (default 10%)
            
        Returns:
            True if trade size is safe
        """
        if self.tvl <= 0:
            return False
        return (trade_size / self.tvl) <= max_tvl_pct
    
    def get_optimal_trade_size(self, target_slippage: float = 0.005) -> float:
        """
        Calculate optimal trade size for target slippage.
        
        From S_dynamic = Δx / (x + Δx), solve for Δx:
            Δx = S * x / (1 - S)
        
        Args:
            target_slippage: Target slippage as decimal (0.005 = 0.5%)
            
        Returns:
            Optimal trade size in USD
        """
        if target_slippage >= 1.0 or target_slippage <= 0:
            return 0.0
        
        # Δx = S * x / (1 - S)
        return (target_slippage * self.tvl) / (1 - target_slippage)


@dataclass
class TriangularArbitrageOpportunity:
    """Triangular arbitrage opportunity on a single DEX/chain.
    
    Equation: R = (P_A→B × P_B→C) / P_A→C > 1.0 + Fees
    
    If R > 1.0 + total_fees, there's a profitable cycle:
        Token A → Token B → Token C → Token A
    """
    token_a: str
    token_b: str
    token_c: str
    price_a_to_b: float  # P_A→B
    price_b_to_c: float  # P_B→C
    price_a_to_c: float  # P_A→C (for comparison)
    total_fees_pct: float  # Total fees as decimal
    
    @property
    def arbitrage_ratio(self) -> float:
        """
        Calculate arbitrage ratio R.
        
        R = (P_A→B × P_B→C) / P_A→C
        """
        if self.price_a_to_c <= 0:
            return 0.0
        return (self.price_a_to_b * self.price_b_to_c) / self.price_a_to_c
    
    @property
    def is_profitable(self) -> bool:
        """Check if triangular arbitrage is profitable."""
        return self.arbitrage_ratio > (1.0 + self.total_fees_pct)
    
    @property
    def profit_pct(self) -> float:
        """Calculate profit percentage if executed."""
        return max(0, self.arbitrage_ratio - 1.0 - self.total_fees_pct)


@dataclass
class Zone6Result:
    """Result from Zone 6 Real-Yield Equation calculation.
    
    The Zone 6 Equation:
        Π_net = Σ[(P_A - P_B) · V · (1 - S)] - (G_gas + F_flash + F_bridge + B_mev)
    
    Where:
        Π_net: Real Net Profit (actual profit after all costs)
        P_A, P_B: Prices on Exchange A and B
        V: Volume (Loan Size)
        S: Slippage % (Dynamic, based on liquidity depth)
        G_gas: Gas Cost (CRITICAL - check before execution)
        F_flash: Flash Loan Fee
        F_bridge: Bridge Fee (cross-chain)
        B_mev: MEV Bribe (priority fee)
    """
    # Core profit calculation
    gross_profit: float  # Before any costs
    net_profit: float  # Π_net - Real profit after all costs
    profit_bps: float  # Net profit in basis points
    
    # Trade parameters
    volume: float  # V - Trade/Loan size
    price_a: float  # P_A - Higher price (sell side)
    price_b: float  # P_B - Lower price (buy side)
    price_spread_pct: float  # (P_A - P_B) / P_B as percentage
    
    # Slippage
    dynamic_slippage: float  # S - Calculated from liquidity depth
    slippage_cost: float  # Dollar cost of slippage
    
    # Total Cost of Execution breakdown
    cost_of_execution: TotalCostOfExecution
    
    # Profitability checks
    is_profitable: bool  # Passes all T.r.u.OG checks
    passed_gas_check: bool  # Expected_Profit >= Gas_Cost * 1.5
    passed_slippage_guard: bool  # Loan_Size <= 10% Pool_Liquidity
    
    # Recommendations
    recommended_flash_source: Optional[FlashLoanSource] = None
    recommended_chain: Optional[ChainType] = None
    abort_reason: Optional[str] = None


class OmniArbV2Calculator:
    """
    OmniArb V2 Calculator implementing the Zone 6 Real-Yield Equation.
    
    The Zone 6 Equation:
        Π_net = Σ[(P_A - P_B) · V · (1 - S)] - (G_gas + F_flash + F_bridge + B_mev)
    
    Key Features:
    1. Total Cost of Execution (T_ce) accounting
    2. Dynamic slippage from Constant Product Formula: S_dynamic = Δx / (x + Δx)
    3. Liquidity Depth optimization (L_d)
    4. Triangular arbitrage support: R = (P_A→B × P_B→C) / P_A→C > 1.0 + Fees
    5. T.r.u.OG Profitability Checklist enforcement
    
    T.r.u.OG Profitability Checklist:
    - Gas Check: If Expected_Profit < (Gas_Cost * 1.5), ABORT TRADE
    - Slippage Guard: If Loan_Size > 10% of Pool_Liquidity, REDUCE SIZE
    - Flash Source: Prioritize DyDx/Balancer (0% fee) over Aave (0.09%)
    - Chain Selection: Focus on L2s (Arbitrum, Polygon, Base) for low gas
    """
    
    # Default thresholds from T.r.u.OG strategy
    GAS_SAFETY_MULTIPLIER = 1.5  # Expected_Profit must be >= Gas_Cost * 1.5
    MAX_TVL_PERCENTAGE = 0.10  # Loan_Size <= 10% of Pool_Liquidity
    TARGET_SLIPPAGE = 0.005  # Aim for slippage < 0.5%
    MIN_PROFIT_BPS = 30.0  # Minimum 0.30% profit
    
    def __init__(
        self,
        min_profit_bps: float = 30.0,
        gas_safety_multiplier: float = 1.5,
        max_tvl_pct: float = 0.10,
        target_slippage: float = 0.005,
        safety_margin: float = 0.20,
    ):
        """
        Initialize OmniArb V2 Calculator.
        
        Args:
            min_profit_bps: Minimum profit in basis points (30 = 0.30%)
            gas_safety_multiplier: Gas check multiplier (1.5 = profit >= gas * 1.5)
            max_tvl_pct: Maximum loan as % of TVL (0.10 = 10%)
            target_slippage: Target slippage as decimal (0.005 = 0.5%)
            safety_margin: Safety margin fraction (0.2 = 20%)
        """
        self.min_profit_bps = min_profit_bps
        self.gas_safety_multiplier = gas_safety_multiplier
        self.max_tvl_pct = max_tvl_pct
        self.target_slippage = target_slippage
        self.safety_margin = safety_margin
        
        # Initialize default configurations
        self.flash_sources = FlashLoanSourceConfig.get_default_sources()
        self.chain_configs = ChainConfig.get_default_chains()
    
    def calculate_zone6_profit(
        self,
        price_a: float,
        price_b: float,
        volume: float,
        liquidity_depth: LiquidityDepth,
        cost_of_execution: TotalCostOfExecution,
    ) -> Zone6Result:
        """
        Calculate profit using Zone 6 Real-Yield Equation.
        
        Equation:
            Π_net = Σ[(P_A - P_B) · V · (1 - S)] - (G_gas + F_flash + F_bridge + B_mev)
        
        Args:
            price_a: Price on Exchange A (higher, sell side)
            price_b: Price on Exchange B (lower, buy side)
            volume: Trade volume in USD (V)
            liquidity_depth: Pool liquidity information for slippage
            cost_of_execution: All execution costs (gas, flash fee, bridge, MEV)
            
        Returns:
            Zone6Result with full profit analysis and checks
        """
        # Validate inputs
        if price_a <= 0 or price_b <= 0 or volume <= 0:
            return self._create_abort_result(
                "Invalid input: prices and volume must be positive",
                price_a, price_b, volume, cost_of_execution
            )
        
        # Calculate price spread
        price_spread_pct = ((price_a - price_b) / price_b) * 100
        
        # Calculate dynamic slippage using Constant Product Formula
        # S_dynamic = Δx / (x + Δx)
        dynamic_slippage = liquidity_depth.calculate_dynamic_slippage(volume)
        
        # Check slippage guard: Loan_Size <= 10% Pool_Liquidity
        passed_slippage_guard = liquidity_depth.is_trade_size_safe(volume, self.max_tvl_pct)
        
        # Calculate gross profit (before costs)
        # Gross = (P_A - P_B) · V · (1 - S)
        price_diff = price_a - price_b
        slippage_multiplier = 1 - dynamic_slippage
        gross_profit = price_diff * volume * slippage_multiplier / price_a  # Normalize by price
        
        # Actually, the correct way to calculate:
        # 1. Buy at P_B (with slippage): tokens = V / (P_B * (1 + S))
        # 2. Sell at P_A (with slippage): USD = tokens * P_A * (1 - S)
        # Net = USD - V - costs
        
        # Simplified for price spread arbitrage:
        # tokens_bought = volume / price_b  # At lower price
        # usd_from_sell = tokens_bought * price_a * (1 - dynamic_slippage)
        # gross_profit = usd_from_sell - volume
        
        if price_b > 0:
            tokens_bought = volume / price_b
            usd_from_sell = tokens_bought * price_a * slippage_multiplier
            gross_profit = usd_from_sell - volume
        else:
            gross_profit = 0.0
        
        # Calculate slippage cost in USD
        slippage_cost = volume * dynamic_slippage
        
        # Calculate net profit (Zone 6 equation)
        # Π_net = Gross - T_ce
        # T_ce = G_gas + F_flash + F_bridge + B_mev
        total_execution_cost = cost_of_execution.total
        net_profit = gross_profit - total_execution_cost
        
        # Gas check: Expected_Profit >= Gas_Cost * 1.5
        expected_profit = gross_profit  # Before other costs but we check vs gas
        gas_threshold = cost_of_execution.gas_cost * self.gas_safety_multiplier
        passed_gas_check = expected_profit >= gas_threshold
        
        # Calculate profit in basis points
        profit_bps = (net_profit / volume) * 10000 if volume > 0 else 0.0
        
        # Determine if profitable (all checks must pass)
        is_profitable = (
            net_profit > 0 and
            passed_gas_check and
            passed_slippage_guard and
            profit_bps >= self.min_profit_bps
        )
        
        # Get recommendations
        recommended_flash_config = self._select_best_flash_source(volume)
        recommended_flash = recommended_flash_config.source if recommended_flash_config else None
        recommended_chain = self._select_best_chain(volume, cost_of_execution.gas_cost)
        
        # Determine abort reason if not profitable
        abort_reason = None
        if not is_profitable:
            if not passed_gas_check:
                abort_reason = f"Gas check failed: Profit ${gross_profit:.2f} < Gas ${gas_threshold:.2f} (gas * {self.gas_safety_multiplier})"
            elif not passed_slippage_guard:
                abort_reason = f"Slippage guard failed: Volume ${volume:,.2f} > {self.max_tvl_pct*100:.0f}% of TVL ${liquidity_depth.tvl:,.2f}"
            elif net_profit <= 0:
                abort_reason = f"Net profit negative: ${net_profit:.2f}"
            else:
                abort_reason = f"Profit too low: {profit_bps:.2f} bps < {self.min_profit_bps:.2f} bps minimum"
        
        return Zone6Result(
            gross_profit=gross_profit,
            net_profit=net_profit,
            profit_bps=profit_bps,
            volume=volume,
            price_a=price_a,
            price_b=price_b,
            price_spread_pct=price_spread_pct,
            dynamic_slippage=dynamic_slippage,
            slippage_cost=slippage_cost,
            cost_of_execution=cost_of_execution,
            is_profitable=is_profitable,
            passed_gas_check=passed_gas_check,
            passed_slippage_guard=passed_slippage_guard,
            recommended_flash_source=recommended_flash,
            recommended_chain=recommended_chain,
            abort_reason=abort_reason,
        )
    
    def calculate_triangular_arbitrage(
        self,
        opportunity: TriangularArbitrageOpportunity,
        volume: float,
        liquidity_depth: LiquidityDepth,
        gas_cost_usd: float,
    ) -> Zone6Result:
        """
        Calculate triangular arbitrage profit.
        
        Triangular Equation:
            R = (P_A→B × P_B→C) / P_A→C > 1.0 + Fees
        
        If R > 1.0 + fees, execute:
            Token A → Token B → Token C → Token A
        
        Benefits:
        - Single chain execution (no bridge fees)
        - Lower gas (one DEX, multiple swaps)
        - Exploits mispricing within DEX pairs
        
        Args:
            opportunity: Triangular arbitrage opportunity details
            volume: Trade volume in USD
            liquidity_depth: Pool liquidity for slippage calculation
            gas_cost_usd: Gas cost estimate
            
        Returns:
            Zone6Result with profit analysis
        """
        # Check if opportunity is profitable
        if not opportunity.is_profitable:
            cost = TotalCostOfExecution(gas_cost=gas_cost_usd)
            return self._create_abort_result(
                f"Triangular arbitrage not profitable: R={opportunity.arbitrage_ratio:.6f} <= 1.0 + fees",
                opportunity.price_a_to_c, 1.0, volume, cost
            )
        
        # Calculate effective prices for Zone 6 equation
        # Treat as: buying at 1.0, selling at R (the arbitrage ratio)
        effective_sell_price = opportunity.arbitrage_ratio
        effective_buy_price = 1.0
        
        # Create cost of execution (no bridge fee for single-chain triangular)
        flash_config = self._select_best_flash_source(volume)
        flash_fee_rate = flash_config.fee_rate if flash_config else 0.0009
        cost = TotalCostOfExecution(
            gas_cost=gas_cost_usd,
            flash_loan_fee=volume * flash_fee_rate,
            bridge_fee=0.0,  # No bridge for triangular
            mev_bribe=0.0,
        )
        
        return self.calculate_zone6_profit(
            price_a=effective_sell_price,
            price_b=effective_buy_price,
            volume=volume,
            liquidity_depth=liquidity_depth,
            cost_of_execution=cost,
        )
    
    def optimize_trade_size(
        self,
        price_a: float,
        price_b: float,
        liquidity_depth: LiquidityDepth,
        gas_cost_usd: float,
        flash_fee_rate: float = 0.0,
    ) -> Tuple[float, Zone6Result]:
        """
        Find optimal trade size that maximizes net profit.
        
        Trade size optimization considers:
        1. Slippage increases with size (S_dynamic = Δx / (x + Δx))
        2. Gas cost is fixed per trade
        3. Flash loan fee scales with size
        4. Must stay within TVL limits
        
        Args:
            price_a: Sell price (higher)
            price_b: Buy price (lower)
            liquidity_depth: Pool liquidity
            gas_cost_usd: Fixed gas cost
            flash_fee_rate: Flash loan fee rate
            
        Returns:
            Tuple of (optimal_volume, Zone6Result)
        """
        # Start with optimal size for target slippage
        max_volume = min(
            liquidity_depth.get_optimal_trade_size(self.target_slippage),
            liquidity_depth.tvl * self.max_tvl_pct  # Max 10% of TVL
        )
        
        # Binary search for optimal volume
        best_result = None
        best_volume = 0.0
        best_profit = float('-inf')
        
        # Test different volume levels
        for pct in [0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50, 0.75, 1.0]:
            test_volume = max_volume * pct
            if test_volume <= 0:
                continue
                
            cost = TotalCostOfExecution(
                gas_cost=gas_cost_usd,
                flash_loan_fee=test_volume * flash_fee_rate,
            )
            
            result = self.calculate_zone6_profit(
                price_a, price_b, test_volume, liquidity_depth, cost
            )
            
            if result.net_profit > best_profit:
                best_profit = result.net_profit
                best_volume = test_volume
                best_result = result
        
        if best_result is None:
            cost = TotalCostOfExecution(gas_cost=gas_cost_usd)
            best_result = self._create_abort_result(
                "No profitable trade size found",
                price_a, price_b, 0.0, cost
            )
        
        return best_volume, best_result
    
    def should_execute(self, result: Zone6Result) -> Tuple[bool, str]:
        """
        Final execution decision based on T.r.u.OG Profitability Checklist.
        
        Checklist:
        1. Gas Check: Expected_Profit >= Gas_Cost * 1.5
        2. Slippage Guard: Loan_Size <= 10% of Pool_Liquidity
        3. Minimum Profit: Net profit > 0 and meets bps threshold
        4. All system checks pass
        
        Args:
            result: Zone6Result from calculation
            
        Returns:
            Tuple of (should_execute, reason)
        """
        if not result.passed_gas_check:
            return False, f"❌ ABORT: {result.abort_reason}"
        
        if not result.passed_slippage_guard:
            return False, f"⚠️ REDUCE SIZE: {result.abort_reason}"
        
        if not result.is_profitable:
            return False, f"❌ ABORT: {result.abort_reason}"
        
        return True, f"✅ EXECUTE: Net profit ${result.net_profit:.2f} ({result.profit_bps:.2f} bps)"
    
    def _select_best_flash_source(self, volume: float) -> Optional[FlashLoanSourceConfig]:
        """Select best flash loan source for given volume (lowest fee first)."""
        for source in self.flash_sources:
            if source.available and source.min_loan_usd <= volume <= source.max_loan_usd:
                return source
        return None
    
    def _select_best_chain(self, volume: float, current_gas: float) -> Optional[ChainType]:
        """Select best chain for execution based on gas and volume."""
        for chain in self.chain_configs:
            if volume >= chain.recommended_min_trade_usd:
                # Prefer L2s for lower gas
                if chain.is_l2 and chain.avg_gas_cost_usd < current_gas:
                    return chain.chain
        
        # Default to mainnet for large trades
        if volume >= 1_000_000:
            return ChainType.ETHEREUM_MAINNET
        
        # Default to Arbitrum for best overall
        return ChainType.ARBITRUM
    
    def _create_abort_result(
        self,
        reason: str,
        price_a: float,
        price_b: float,
        volume: float,
        cost: TotalCostOfExecution,
    ) -> Zone6Result:
        """Create an abort result with the given reason."""
        return Zone6Result(
            gross_profit=0.0,
            net_profit=0.0,
            profit_bps=0.0,
            volume=volume,
            price_a=price_a,
            price_b=price_b,
            price_spread_pct=((price_a - price_b) / price_b * 100) if price_b > 0 else 0.0,
            dynamic_slippage=0.0,
            slippage_cost=0.0,
            cost_of_execution=cost,
            is_profitable=False,
            passed_gas_check=False,
            passed_slippage_guard=False,
            abort_reason=reason,
        )


def format_zone6_report(result: Zone6Result) -> str:
    """
    Format Zone 6 calculation result into human-readable report.
    
    Args:
        result: Zone6Result from OmniArbV2Calculator
        
    Returns:
        Formatted report string
    """
    report = []
    report.append("=" * 80)
    report.append("OMNIARB V2 - ZONE 6 REAL-YIELD ANALYSIS")
    report.append("=" * 80)
    report.append("")
    
    # Equation reference
    report.append("EQUATION: Π_net = Σ[(P_A - P_B) · V · (1 - S)] - (G_gas + F_flash + F_bridge + B_mev)")
    report.append("")
    
    # Input parameters
    report.append("TRADE PARAMETERS:")
    report.append(f"  Price A (Sell): ${result.price_a:,.4f}")
    report.append(f"  Price B (Buy): ${result.price_b:,.4f}")
    report.append(f"  Price Spread: {result.price_spread_pct:.4f}%")
    report.append(f"  Volume (V): ${result.volume:,.2f}")
    report.append("")
    
    # Slippage analysis
    report.append("SLIPPAGE ANALYSIS (Constant Product Formula):")
    report.append(f"  S_dynamic = Δx / (x + Δx)")
    report.append(f"  Dynamic Slippage: {result.dynamic_slippage * 100:.4f}%")
    report.append(f"  Slippage Cost: ${result.slippage_cost:,.2f}")
    report.append("")
    
    # Cost of execution breakdown
    cost = result.cost_of_execution
    report.append("TOTAL COST OF EXECUTION (T_ce):")
    report.append(f"  G_gas (Gas Cost): ${cost.gas_cost:,.2f}")
    report.append(f"  F_flash (Flash Fee): ${cost.flash_loan_fee:,.2f}")
    report.append(f"  F_bridge (Bridge Fee): ${cost.bridge_fee:,.2f}")
    report.append(f"  B_mev (MEV Bribe): ${cost.mev_bribe:,.2f}")
    report.append(f"  ─────────────────────────")
    report.append(f"  TOTAL T_ce: ${cost.total:,.2f}")
    report.append("")
    
    # Profit analysis
    report.append("PROFIT ANALYSIS:")
    report.append(f"  Gross Profit: ${result.gross_profit:,.2f}")
    report.append(f"  Net Profit (Π_net): ${result.net_profit:,.2f}")
    report.append(f"  Profit Margin: {result.profit_bps:.2f} bps ({result.profit_bps/100:.2f}%)")
    report.append("")
    
    # T.r.u.OG Profitability Checklist
    report.append("T.r.u.OG PROFITABILITY CHECKLIST:")
    gas_check = "✅ PASS" if result.passed_gas_check else "❌ FAIL"
    slip_check = "✅ PASS" if result.passed_slippage_guard else "❌ FAIL"
    report.append(f"  Gas Check (Profit >= Gas * 1.5): {gas_check}")
    report.append(f"  Slippage Guard (Size <= 10% TVL): {slip_check}")
    report.append("")
    
    # Recommendations
    report.append("RECOMMENDATIONS:")
    if result.recommended_flash_source:
        report.append(f"  Flash Source: {result.recommended_flash_source.value.upper()}")
    if result.recommended_chain:
        report.append(f"  Chain: {result.recommended_chain.value}")
    report.append("")
    
    # Final decision
    report.append("DECISION:")
    if result.is_profitable:
        report.append(f"  ✅ EXECUTE - Profitable trade opportunity")
        report.append(f"     Expected Net Profit: ${result.net_profit:,.2f}")
    else:
        report.append(f"  ❌ ABORT TRADE")
        report.append(f"     Reason: {result.abort_reason}")
    
    report.append("=" * 80)
    
    return "\n".join(report)
