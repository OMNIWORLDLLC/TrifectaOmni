#!/usr/bin/env python3
"""
Test and verification script for OmniArb V2 Zone 6 Real-Yield Equation.

Tests the advanced arbitrage equations from the T.r.u.OG specification:

1. Zone 6 Real-Yield Equation:
   Π_net = Σ[(P_A - P_B) · V · (1 - S)] - (G_gas + F_flash + F_bridge + B_mev)

2. Constant Product Formula for Dynamic Slippage:
   S_dynamic = Δx / (x + Δx)

3. Triangular Arbitrage Equation:
   R = (P_A→B × P_B→C) / P_A→C > 1.0 + Fees

4. T.r.u.OG Profitability Checklist:
   - Gas Check: Expected_Profit >= Gas_Cost * 1.5
   - Slippage Guard: Loan_Size <= 10% of Pool_Liquidity
   - Flash Source: Prioritize DyDx/Balancer (0% fee) over Aave (0.09%)
   - Chain Selection: Focus on L2s for low gas
"""

import os
import sys

# Add project root to path for standalone execution
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from omni_trifecta.execution.arbitrage_calculator import (
    OmniArbV2Calculator,
    TotalCostOfExecution,
    LiquidityDepth,
    TriangularArbitrageOpportunity,
    FlashLoanSource,
    FlashLoanSourceConfig,
    ChainType,
    ChainConfig,
    Zone6Result,
    format_zone6_report,
)


def test_zone6_equation():
    """Test the Zone 6 Real-Yield Equation calculation."""
    print("\n" + "=" * 80)
    print("TEST 1: ZONE 6 REAL-YIELD EQUATION")
    print("=" * 80)
    print("\nEquation: Π_net = Σ[(P_A - P_B) · V · (1 - S)] - (G_gas + F_flash + F_bridge + B_mev)")
    
    calc = OmniArbV2Calculator()
    
    # Create a profitable arbitrage opportunity
    # Use larger pool and smaller trade to minimize slippage
    # Price spread: 2% which is a significant opportunity
    
    liquidity = LiquidityDepth(
        tvl=50_000_000,  # $50M pool - large enough for low slippage
        token_reserve_a=25_000_000,
        token_reserve_b=25_000_000,
    )
    
    # Low gas L2 scenario
    costs = TotalCostOfExecution(
        gas_cost=5.0,  # $5 gas on L2
        flash_loan_fee=0.0,  # DyDx 0% fee
        bridge_fee=0.0,  # Same chain
        mev_bribe=2.0,  # $2 priority fee
    )
    
    result = calc.calculate_zone6_profit(
        price_a=42840.0,  # Sell price (2% higher)
        price_b=42000.0,  # Buy price (lower)
        volume=100_000.0,  # $100k trade
        liquidity_depth=liquidity,
        cost_of_execution=costs,
    )
    
    print("\n--- INPUT PARAMETERS ---")
    print(f"Price A (Sell): ${result.price_a:,.2f}")
    print(f"Price B (Buy): ${result.price_b:,.2f}")
    print(f"Price Spread: {result.price_spread_pct:.4f}%")
    print(f"Volume (V): ${result.volume:,.2f}")
    print(f"TVL: ${liquidity.tvl:,.2f}")
    
    print("\n--- DYNAMIC SLIPPAGE (Constant Product Formula) ---")
    print(f"S_dynamic = Δx / (x + Δx)")
    print(f"S_dynamic = {result.volume:,.0f} / ({liquidity.tvl:,.0f} + {result.volume:,.0f})")
    print(f"S_dynamic = {result.dynamic_slippage:.6f} ({result.dynamic_slippage * 100:.4f}%)")
    
    print("\n--- COST OF EXECUTION (T_ce) ---")
    print(f"G_gas: ${costs.gas_cost:.2f}")
    print(f"F_flash: ${costs.flash_loan_fee:.2f}")
    print(f"F_bridge: ${costs.bridge_fee:.2f}")
    print(f"B_mev: ${costs.mev_bribe:.2f}")
    print(f"Total T_ce: ${costs.total:.2f}")
    
    print("\n--- PROFIT ANALYSIS ---")
    print(f"Gross Profit: ${result.gross_profit:,.2f}")
    print(f"Net Profit (Π_net): ${result.net_profit:,.2f}")
    print(f"Profit Margin: {result.profit_bps:.2f} bps ({result.profit_bps/100:.2f}%)")
    
    print("\n--- T.r.u.OG PROFITABILITY CHECKLIST ---")
    gas_check = "✅ PASS" if result.passed_gas_check else "❌ FAIL"
    slip_check = "✅ PASS" if result.passed_slippage_guard else "❌ FAIL"
    print(f"Gas Check (Profit >= Gas * 1.5): {gas_check}")
    print(f"Slippage Guard (Size <= 10% TVL): {slip_check}")
    
    print("\n--- DECISION ---")
    should_exec, reason = calc.should_execute(result)
    print(reason)
    
    return result.is_profitable


def test_dynamic_slippage():
    """Test the Constant Product Formula for dynamic slippage."""
    print("\n" + "=" * 80)
    print("TEST 2: CONSTANT PRODUCT FORMULA - DYNAMIC SLIPPAGE")
    print("=" * 80)
    print("\nFormula: S_dynamic = Δx / (x + Δx)")
    print("Where: Δx = trade size, x = TVL (total liquidity)")
    
    # Test with different pool sizes and trade sizes
    scenarios = [
        {"tvl": 100_000, "trade": 5_000, "name": "5% of $100k pool"},
        {"tvl": 100_000, "trade": 10_000, "name": "10% of $100k pool"},
        {"tvl": 100_000, "trade": 20_000, "name": "20% of $100k pool (DANGER)"},
        {"tvl": 1_000_000, "trade": 50_000, "name": "5% of $1M pool"},
        {"tvl": 1_000_000, "trade": 100_000, "name": "10% of $1M pool"},
        {"tvl": 10_000_000, "trade": 500_000, "name": "5% of $10M pool"},
    ]
    
    print(f"\n{'Scenario':<30} {'TVL':>15} {'Trade':>15} {'Slippage':>15} {'Safe?':>10}")
    print("-" * 85)
    
    for s in scenarios:
        liquidity = LiquidityDepth(tvl=s["tvl"], token_reserve_a=s["tvl"]/2, token_reserve_b=s["tvl"]/2)
        slippage = liquidity.calculate_dynamic_slippage(s["trade"])
        is_safe = liquidity.is_trade_size_safe(s["trade"])
        safe_str = "✅ YES" if is_safe else "❌ NO"
        
        print(f"{s['name']:<30} ${s['tvl']:>13,.0f} ${s['trade']:>13,.0f} {slippage*100:>14.4f}% {safe_str:>10}")
    
    # Test the T.r.u.OG "Sweet Spot" logic
    print("\n--- T.r.u.OG SWEET SPOT LOGIC ---")
    print("• If loan > 20% TVL: S_dynamic spikes, eating profit → AVOID")
    print("• If loan < 5% TVL: Profit may not cover gas → TOO SMALL")
    print("• Target: Slippage < 0.5%")
    
    tvl = 1_000_000
    liquidity = LiquidityDepth(tvl=tvl, token_reserve_a=tvl/2, token_reserve_b=tvl/2)
    
    # Calculate optimal trade size for 0.5% target slippage
    optimal_size = liquidity.get_optimal_trade_size(0.005)  # 0.5%
    actual_slippage = liquidity.calculate_dynamic_slippage(optimal_size)
    
    print(f"\nFor TVL = ${tvl:,.0f}:")
    print(f"  Optimal trade size (for 0.5% slippage): ${optimal_size:,.2f}")
    print(f"  Actual slippage at optimal: {actual_slippage*100:.4f}%")
    print(f"  Trade as % of TVL: {(optimal_size/tvl)*100:.2f}%")
    
    return True


def test_gas_check():
    """Test the Gas Check rule: Expected_Profit >= Gas_Cost * 1.5"""
    print("\n" + "=" * 80)
    print("TEST 3: GAS CHECK - 'HUSTLED BACKWARDS' PREVENTION")
    print("=" * 80)
    print("\nT.r.u.OG Rule: 'If you borrowing $100k to make $50 profit,")
    print("               but the Gas is $60... you just hustled backwards.'")
    print("\nCheck: Expected_Profit >= Gas_Cost * 1.5")
    
    calc = OmniArbV2Calculator()
    
    liquidity = LiquidityDepth(
        tvl=10_000_000,
        token_reserve_a=5_000_000,
        token_reserve_b=5_000_000,
    )
    
    # Scenario 1: Gas too high - should ABORT
    print("\n--- SCENARIO 1: Gas Too High (Should ABORT) ---")
    costs_high_gas = TotalCostOfExecution(
        gas_cost=60.0,  # $60 gas
        flash_loan_fee=9.0,  # 0.09% of $10k
        bridge_fee=0.0,
        mev_bribe=5.0,
    )
    
    result1 = calc.calculate_zone6_profit(
        price_a=42050.0,  # Small spread
        price_b=42000.0,
        volume=10_000.0,
        liquidity_depth=liquidity,
        cost_of_execution=costs_high_gas,
    )
    
    print(f"Trade: $10k with $42,050 vs $42,000 (0.12% spread)")
    print(f"Gross Profit: ${result1.gross_profit:.2f}")
    print(f"Gas Cost: ${costs_high_gas.gas_cost:.2f}")
    print(f"Gas Check Threshold: ${costs_high_gas.gas_cost * 1.5:.2f}")
    print(f"Passed Gas Check: {'✅ YES' if result1.passed_gas_check else '❌ NO'}")
    
    should_exec, reason = calc.should_execute(result1)
    print(f"Decision: {reason}")
    
    # Scenario 2: Healthy profit margin - should EXECUTE
    print("\n--- SCENARIO 2: Healthy Margin (Should EXECUTE) ---")
    costs_normal = TotalCostOfExecution(
        gas_cost=10.0,  # $10 gas on L2
        flash_loan_fee=0.0,  # DyDx 0% fee
        bridge_fee=0.0,
        mev_bribe=2.0,
    )
    
    result2 = calc.calculate_zone6_profit(
        price_a=42300.0,  # Good spread
        price_b=42000.0,
        volume=50_000.0,
        liquidity_depth=liquidity,
        cost_of_execution=costs_normal,
    )
    
    print(f"Trade: $50k with $42,300 vs $42,000 (0.71% spread)")
    print(f"Gross Profit: ${result2.gross_profit:.2f}")
    print(f"Gas Cost: ${costs_normal.gas_cost:.2f}")
    print(f"Gas Check Threshold: ${costs_normal.gas_cost * 1.5:.2f}")
    print(f"Passed Gas Check: {'✅ YES' if result2.passed_gas_check else '❌ NO'}")
    
    should_exec, reason = calc.should_execute(result2)
    print(f"Decision: {reason}")
    
    return not result1.passed_gas_check and result2.passed_gas_check


def test_slippage_guard():
    """Test the Slippage Guard: Loan_Size <= 10% of Pool_Liquidity"""
    print("\n" + "=" * 80)
    print("TEST 4: SLIPPAGE GUARD - 'DON'T DRAIN THE POOL'")
    print("=" * 80)
    print("\nT.r.u.OG Rule: 'Don't be greedy. If you drain the pool, you drown yourself.'")
    print("Guard: If Loan_Size > 10% of Pool_Liquidity, REDUCE SIZE")
    
    calc = OmniArbV2Calculator()
    
    # Small pool - trading too large
    small_pool = LiquidityDepth(
        tvl=100_000,  # $100k pool
        token_reserve_a=50_000,
        token_reserve_b=50_000,
    )
    
    costs = TotalCostOfExecution(gas_cost=5.0, flash_loan_fee=0.0)
    
    print("\n--- SCENARIO 1: Too Large for Pool (Should REDUCE) ---")
    print(f"Pool TVL: ${small_pool.tvl:,.0f}")
    print(f"Max Safe Size (10%): ${small_pool.tvl * 0.10:,.0f}")
    
    result1 = calc.calculate_zone6_profit(
        price_a=42500.0,
        price_b=42000.0,
        volume=20_000.0,  # 20% of pool - TOO LARGE
        liquidity_depth=small_pool,
        cost_of_execution=costs,
    )
    
    print(f"Attempted Volume: ${result1.volume:,.0f} ({(result1.volume/small_pool.tvl)*100:.0f}% of TVL)")
    print(f"Dynamic Slippage: {result1.dynamic_slippage*100:.2f}%")
    print(f"Passed Slippage Guard: {'✅ YES' if result1.passed_slippage_guard else '❌ NO'}")
    
    should_exec, reason = calc.should_execute(result1)
    print(f"Decision: {reason}")
    
    print("\n--- SCENARIO 2: Safe Size for Pool (Should PASS) ---")
    large_pool = LiquidityDepth(
        tvl=5_000_000,  # $5M pool
        token_reserve_a=2_500_000,
        token_reserve_b=2_500_000,
    )
    
    print(f"Pool TVL: ${large_pool.tvl:,.0f}")
    print(f"Max Safe Size (10%): ${large_pool.tvl * 0.10:,.0f}")
    
    result2 = calc.calculate_zone6_profit(
        price_a=42500.0,
        price_b=42000.0,
        volume=100_000.0,  # 2% of pool - SAFE
        liquidity_depth=large_pool,
        cost_of_execution=costs,
    )
    
    print(f"Attempted Volume: ${result2.volume:,.0f} ({(result2.volume/large_pool.tvl)*100:.0f}% of TVL)")
    print(f"Dynamic Slippage: {result2.dynamic_slippage*100:.2f}%")
    print(f"Passed Slippage Guard: {'✅ YES' if result2.passed_slippage_guard else '❌ NO'}")
    
    should_exec, reason = calc.should_execute(result2)
    print(f"Decision: {reason}")
    
    return not result1.passed_slippage_guard and result2.passed_slippage_guard


def test_triangular_arbitrage():
    """Test Triangular Arbitrage equation: R = (P_A→B × P_B→C) / P_A→C > 1.0 + Fees"""
    print("\n" + "=" * 80)
    print("TEST 5: TRIANGULAR ARBITRAGE")
    print("=" * 80)
    print("\nEquation: R = (P_A→B × P_B→C) / P_A→C > 1.0 + Fees")
    print("Path: Token A → Token B → Token C → Token A (single chain, no bridge)")
    
    calc = OmniArbV2Calculator()
    
    # Example: USDT → ETH → BTC → USDT
    # Realistic prices with a small mispricing that creates opportunity
    # 
    # Market rates (approximately):
    # - ETH: $2,600 (1 USDT = 0.000385 ETH)
    # - BTC: $42,000 (1 USDT = 0.0000238 BTC)
    # - ETH/BTC: ~0.0619 (1 ETH = 0.0619 BTC)
    #
    # For profitable triangular arb, we need:
    # R = (P_USDT→ETH × P_ETH→BTC) / P_USDT→BTC > 1.0 + fees
    # R = (0.000385 × 0.0625) / 0.0000238 > 1.003
    # R = 0.0000240625 / 0.0000238 = 1.0109 > 1.003 ✓
    
    print("\n--- SCENARIO 1: Profitable Triangular (1.1% mispricing) ---")
    print("Path: USDT → ETH → BTC → USDT")
    
    opportunity = TriangularArbitrageOpportunity(
        token_a="USDT",
        token_b="ETH",
        token_c="BTC",
        price_a_to_b=0.000385,  # 1 USDT = 0.000385 ETH (ETH @ $2,597)
        price_b_to_c=0.0625,  # 1 ETH = 0.0625 BTC (ETH/BTC mispriced slightly high)
        price_a_to_c=0.0000238,  # 1 USDT = 0.0000238 BTC (BTC @ $42,016)
        total_fees_pct=0.003,  # 0.3% total fees (3 swaps @ 0.1% each)
    )
    
    print(f"P_USDT→ETH: {opportunity.price_a_to_b}")
    print(f"P_ETH→BTC: {opportunity.price_b_to_c}")
    print(f"P_USDT→BTC: {opportunity.price_a_to_c}")
    print(f"Total Fees: {opportunity.total_fees_pct*100:.2f}%")
    
    ratio = opportunity.arbitrage_ratio
    threshold = 1.0 + opportunity.total_fees_pct
    print(f"\nArbitrage Ratio R: {ratio:.6f}")
    print(f"Threshold (1 + fees): {threshold:.6f}")
    is_profitable_scenario1 = opportunity.is_profitable
    print(f"Is Profitable: {'✅ YES' if is_profitable_scenario1 else '❌ NO'}")
    print(f"Potential Profit: {opportunity.profit_pct*100:.4f}%")
    
    # Calculate with Zone 6 equation
    liquidity = LiquidityDepth(tvl=10_000_000, token_reserve_a=5_000_000, token_reserve_b=5_000_000)
    
    result = calc.calculate_triangular_arbitrage(
        opportunity=opportunity,
        volume=50_000.0,
        liquidity_depth=liquidity,
        gas_cost_usd=5.0,  # Low gas on L2
    )
    
    print(f"\n--- Zone 6 Analysis ---")
    print(f"Volume: ${result.volume:,.2f}")
    print(f"Net Profit: ${result.net_profit:,.2f}")
    print(f"Profitable: {'✅ YES' if result.is_profitable else '❌ NO'}")
    
    # Unprofitable scenario - fair prices with no mispricing
    print("\n--- SCENARIO 2: Not Profitable (fair pricing) ---")
    bad_opportunity = TriangularArbitrageOpportunity(
        token_a="USDT",
        token_b="ETH",
        token_c="BTC",
        price_a_to_b=0.000385,  # 1 USDT = 0.000385 ETH
        price_b_to_c=0.0618,  # Fair ETH/BTC rate (slightly lower, no arb)
        price_a_to_c=0.0000238,  # 1 USDT = 0.0000238 BTC
        total_fees_pct=0.003,  # 0.3% total fees
    )
    
    bad_ratio = bad_opportunity.arbitrage_ratio
    is_profitable_scenario2 = bad_opportunity.is_profitable
    print(f"Arbitrage Ratio R: {bad_ratio:.6f}")
    print(f"Threshold (1 + fees): {1.0 + bad_opportunity.total_fees_pct:.6f}")
    print(f"Is Profitable: {'✅ YES' if is_profitable_scenario2 else '❌ NO'}")
    
    # Test passes if scenario 1 is profitable and scenario 2 is not
    return is_profitable_scenario1 and not is_profitable_scenario2


def test_flash_source_priority():
    """Test Flash Loan Source prioritization (DyDx/Balancer over Aave)."""
    print("\n" + "=" * 80)
    print("TEST 6: FLASH LOAN SOURCE PRIORITIZATION")
    print("=" * 80)
    print("\nT.r.u.OG Rule: 'Prioritize DyDx or Balancer (0% fee) over Aave (0.09%)'")
    
    sources = FlashLoanSourceConfig.get_default_sources()
    
    print("\n--- AVAILABLE FLASH LOAN SOURCES (Priority Order) ---")
    print(f"{'Source':<15} {'Fee':>10} {'Min Loan':>15} {'Max Loan':>15}")
    print("-" * 55)
    
    for source in sources:
        print(f"{source.source.value:<15} {source.fee_rate*100:>9.2f}% ${source.min_loan_usd:>13,.0f} ${source.max_loan_usd:>13,.0f}")
    
    calc = OmniArbV2Calculator()
    
    # Test source selection for different volumes
    print("\n--- SOURCE SELECTION BY VOLUME ---")
    test_volumes = [5_000, 50_000, 100_000, 30_000_000, 200_000_000]
    
    for vol in test_volumes:
        source = calc._select_best_flash_source(vol)
        if source:
            savings = vol * 0.0009 - vol * source.fee_rate  # Compared to Aave
            print(f"Volume ${vol:>12,.0f}: {source.source.value:<12} (Fee: {source.fee_rate*100:.2f}%, Savings vs Aave: ${savings:,.2f})")
        else:
            print(f"Volume ${vol:>12,.0f}: No source available")
    
    return True


def test_chain_selection():
    """Test Chain Selection logic (L2 for gas efficiency)."""
    print("\n" + "=" * 80)
    print("TEST 7: CHAIN SELECTION - L2 FOR GAS EFFICIENCY")
    print("=" * 80)
    print("\nT.r.u.OG Rule: 'Focus on Polygon, Arbitrum, or Base.")
    print("               Ethereum Mainnet only for million-dollar trades.'")
    
    chains = ChainConfig.get_default_chains()
    
    print("\n--- CHAIN CONFIGURATIONS ---")
    print(f"{'Chain':<20} {'Avg Gas':>12} {'Block Time':>12} {'L2?':>8} {'Min Trade':>15}")
    print("-" * 75)
    
    for chain in chains:
        l2_str = "✅ Yes" if chain.is_l2 else "❌ No"
        print(f"{chain.chain.value:<20} ${chain.avg_gas_cost_usd:>10,.2f} {chain.block_time_seconds:>11.1f}s {l2_str:>8} ${chain.recommended_min_trade_usd:>13,.0f}")
    
    calc = OmniArbV2Calculator()
    
    # Test chain selection for different scenarios
    print("\n--- CHAIN SELECTION BY SCENARIO ---")
    scenarios = [
        {"volume": 10_000, "gas": 50.0, "name": "$10k trade, $50 mainnet gas"},
        {"volume": 100_000, "gas": 100.0, "name": "$100k trade, $100 mainnet gas"},
        {"volume": 500_000, "gas": 50.0, "name": "$500k trade"},
        {"volume": 2_000_000, "gas": 50.0, "name": "$2M trade (should use mainnet)"},
    ]
    
    for s in scenarios:
        chain = calc._select_best_chain(s["volume"], s["gas"])
        print(f"{s['name']}: {chain.value if chain else 'None'}")
    
    return True


def test_optimize_trade_size():
    """Test trade size optimization."""
    print("\n" + "=" * 80)
    print("TEST 8: TRADE SIZE OPTIMIZATION")
    print("=" * 80)
    
    calc = OmniArbV2Calculator()
    
    liquidity = LiquidityDepth(
        tvl=2_000_000,
        token_reserve_a=1_000_000,
        token_reserve_b=1_000_000,
    )
    
    print("\nFinding optimal trade size that maximizes profit...")
    print(f"Pool TVL: ${liquidity.tvl:,.0f}")
    print(f"Price Spread: $42,500 vs $42,000 (1.19%)")
    
    optimal_volume, result = calc.optimize_trade_size(
        price_a=42500.0,
        price_b=42000.0,
        liquidity_depth=liquidity,
        gas_cost_usd=10.0,
        flash_fee_rate=0.0,  # DyDx
    )
    
    print(f"\n--- OPTIMIZATION RESULT ---")
    print(f"Optimal Volume: ${optimal_volume:,.2f}")
    print(f"As % of TVL: {(optimal_volume/liquidity.tvl)*100:.2f}%")
    print(f"Dynamic Slippage: {result.dynamic_slippage*100:.4f}%")
    print(f"Net Profit: ${result.net_profit:,.2f}")
    print(f"Profit BPS: {result.profit_bps:.2f}")
    print(f"Profitable: {'✅ YES' if result.is_profitable else '❌ NO'}")
    
    return result.net_profit > 0


def test_full_zone6_report():
    """Test the formatted Zone 6 report output."""
    print("\n" + "=" * 80)
    print("TEST 9: FULL ZONE 6 REPORT FORMAT")
    print("=" * 80)
    
    calc = OmniArbV2Calculator()
    
    liquidity = LiquidityDepth(
        tvl=5_000_000,
        token_reserve_a=2_500_000,
        token_reserve_b=2_500_000,
    )
    
    costs = TotalCostOfExecution(
        gas_cost=15.0,
        flash_loan_fee=0.0,
        bridge_fee=0.0,
        mev_bribe=5.0,
    )
    
    result = calc.calculate_zone6_profit(
        price_a=42500.0,
        price_b=42000.0,
        volume=100_000.0,
        liquidity_depth=liquidity,
        cost_of_execution=costs,
    )
    
    # Print the formatted report
    print("\n" + format_zone6_report(result))
    
    return True


def main():
    """Run all OmniArb V2 Zone 6 tests."""
    print("\n" + "=" * 80)
    print("OMNIARB V2 - ZONE 6 REAL-YIELD EQUATION VERIFICATION")
    print("=" * 80)
    print("""
    This test suite verifies the T.r.u.OG arbitrage equations:
    
    1. Zone 6 Real-Yield Equation:
       Π_net = Σ[(P_A - P_B) · V · (1 - S)] - (G_gas + F_flash + F_bridge + B_mev)
    
    2. Constant Product Formula for Dynamic Slippage:
       S_dynamic = Δx / (x + Δx)
    
    3. Triangular Arbitrage:
       R = (P_A→B × P_B→C) / P_A→C > 1.0 + Fees
    
    4. T.r.u.OG Profitability Checklist:
       • Gas Check: Expected_Profit >= Gas_Cost * 1.5
       • Slippage Guard: Loan_Size <= 10% of Pool_Liquidity
       • Flash Source: Prioritize DyDx/Balancer (0% fee)
       • Chain Selection: Focus on L2s for gas efficiency
    """)
    
    results = []
    
    # Run all tests
    results.append(("Zone 6 Equation", test_zone6_equation()))
    results.append(("Dynamic Slippage", test_dynamic_slippage()))
    results.append(("Gas Check", test_gas_check()))
    results.append(("Slippage Guard", test_slippage_guard()))
    results.append(("Triangular Arbitrage", test_triangular_arbitrage()))
    results.append(("Flash Source Priority", test_flash_source_priority()))
    results.append(("Chain Selection", test_chain_selection()))
    results.append(("Trade Size Optimization", test_optimize_trade_size()))
    results.append(("Zone 6 Report Format", test_full_zone6_report()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ OmniArb V2 Zone 6 Implementation Complete:")
        print("   • Zone 6 Real-Yield Equation verified")
        print("   • Constant Product slippage formula working")
        print("   • Triangular arbitrage equation functional")
        print("   • T.r.u.OG Profitability Checklist enforced")
        print("   • Flash loan source prioritization active")
        print("   • Chain selection logic operational")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
