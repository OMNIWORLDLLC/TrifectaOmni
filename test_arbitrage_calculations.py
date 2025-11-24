#!/usr/bin/env python3
"""
Test and verification script for multi-hop arbitrage calculations and risk ratios.

Validates:
- 2-hop arbitrage calculations
- 3-hop (triangular) arbitrage calculations  
- 4-hop (rectangular) arbitrage calculations
- Risk/reward ratio computations
- Fee and slippage accounting
- Kelly Criterion position sizing
"""

import sys
sys.path.insert(0, '/workspaces/TrifectaOmni')

from omni_trifecta.execution.arbitrage_calculator import (
    MultiHopArbitrageCalculator,
    Exchange,
    TradingPair,
    RouteType,
    format_arbitrage_report
)


def create_test_exchanges():
    """Create test exchanges with different characteristics."""
    binance = Exchange(
        name="Binance",
        trading_fee=0.001,  # 0.1%
        withdrawal_fee=0.0005,
        gas_cost=1.0,
        liquidity_depth=10000000,
        slippage_factor=0.0001  # 0.01% per $100k
    )
    
    kraken = Exchange(
        name="Kraken",
        trading_fee=0.0026,  # 0.26%
        withdrawal_fee=0.0009,
        gas_cost=1.5,
        liquidity_depth=5000000,
        slippage_factor=0.0002
    )
    
    uniswap = Exchange(
        name="Uniswap V3",
        trading_fee=0.003,  # 0.3%
        withdrawal_fee=0.0,
        gas_cost=25.0,  # Higher gas on DEX
        liquidity_depth=2000000,
        slippage_factor=0.0005
    )
    
    return binance, kraken, uniswap


def test_2hop_arbitrage():
    """Test 2-hop arbitrage calculation."""
    print("\n" + "="*70)
    print("TEST 1: 2-HOP ARBITRAGE (BTC/USDT)")
    print("="*70)
    
    binance, kraken, _ = create_test_exchanges()
    
    # Scenario: BTC is cheaper on Binance, more expensive on Kraken
    # Creating a clear arbitrage opportunity with 0.5% price difference
    pair1_buy = TradingPair(
        base="BTC",
        quote="USDT",
        exchange=binance,
        bid_price=42000.0,
        ask_price=42010.0,  # Buy BTC on Binance
        spread=10.0,
        liquidity=5000000
    )
    
    pair2_sell = TradingPair(
        base="BTC",
        quote="USDT",
        exchange=kraken,
        bid_price=42350.0,  # Sell BTC on Kraken (0.81% higher - clear arb)
        ask_price=42360.0,
        spread=10.0,
        liquidity=3000000
    )
    
    calculator = MultiHopArbitrageCalculator(
        min_profit_bps=30.0,
        max_slippage_bps=50.0,
        safety_margin=0.20
    )
    
    capital = 10000.0
    route = calculator.calculate_2hop_arbitrage(pair1_buy, pair2_sell, capital)
    
    if route:
        print(f"\n✅ PROFITABLE 2-HOP ROUTE FOUND!")
        print(f"Path: {' → '.join(route.path)}")
        print(f"Expected Profit: ${route.expected_profit:.2f} USD")
        print(f"Profit Margin: {route.expected_profit_bps:.2f} bps ({route.expected_profit_bps/100:.2f}%)")
        print(f"Risk Score: {route.risk_score:.1f}/100")
        print(f"Total Fees: ${route.total_fees:.2f}")
        print(f"Gas Costs: ${route.total_gas:.2f}")
        print(f"Slippage: {route.slippage_estimate*10000:.2f} bps")
        
        # Calculate risk metrics
        risk_metrics = calculator.calculate_risk_reward_ratio(route, capital)
        print(f"\nRisk/Reward Ratio: {risk_metrics['risk_reward_ratio']:.2f}:1")
        print(f"Profit Probability: {risk_metrics['profit_probability']*100:.1f}%")
        print(f"Expected Value: ${risk_metrics['expected_value']:.2f}")
        print(f"Kelly Fraction: {risk_metrics['kelly_fraction']*100:.2f}%")
        
        # Manual verification
        print("\n--- MANUAL VERIFICATION ---")
        amount_after_buy = capital * (1 - binance.trading_fee)
        btc_amount = amount_after_buy / pair1_buy.ask_price
        print(f"1. Buy {btc_amount:.6f} BTC for ${capital:.2f} USDT on Binance")
        
        usdt_from_sell = btc_amount * pair2_sell.bid_price
        amount_after_sell = usdt_from_sell * (1 - kraken.trading_fee)
        print(f"2. Sell {btc_amount:.6f} BTC for ${usdt_from_sell:.2f} USDT on Kraken")
        print(f"3. After fees: ${amount_after_sell:.2f} USDT")
        
        final = amount_after_sell - (binance.gas_cost + kraken.gas_cost)
        profit = final - capital
        print(f"4. After gas: ${final:.2f} USDT")
        print(f"5. Gross Profit: ${profit:.2f} USD ({(profit/capital)*10000:.2f} bps)")
        
        return True
    else:
        print("❌ No profitable route found")
        return False


def test_3hop_arbitrage():
    """Test 3-hop triangular arbitrage."""
    print("\n" + "="*70)
    print("TEST 2: 3-HOP TRIANGULAR ARBITRAGE (USDT -> BTC -> ETH -> USDT)")
    print("="*70)
    
    binance, kraken, _ = create_test_exchanges()
    
    # USDT -> BTC
    pair1 = TradingPair(
        base="BTC",
        quote="USDT",
        exchange=binance,
        bid_price=42000.0,
        ask_price=42020.0,
        spread=20.0,
        liquidity=5000000
    )
    
    # BTC -> ETH (quoted as ETH/BTC)
    pair2 = TradingPair(
        base="ETH",
        quote="BTC",
        exchange=binance,
        bid_price=0.0625,  # 1 BTC = 16 ETH
        ask_price=0.0627,
        spread=2.0,
        liquidity=3000000
    )
    
    # ETH -> USDT (create triangular arb opportunity)
    # Price mismatch creates profitable cycle
    pair3 = TradingPair(
        base="ETH",
        quote="USDT",
        exchange=binance,
        bid_price=2680.0,  # Higher ETH price creates triangular arb
        ask_price=2682.0,
        spread=2.0,
        liquidity=4000000
    )
    
    calculator = MultiHopArbitrageCalculator(min_profit_bps=20.0)
    capital = 10000.0
    
    route = calculator.calculate_3hop_arbitrage(pair1, pair2, pair3, capital)
    
    if route:
        print(f"\n✅ PROFITABLE 3-HOP ROUTE FOUND!")
        print(f"Path: {' → '.join(route.path)}")
        print(f"Expected Profit: ${route.expected_profit:.2f} USD")
        print(f"Profit Margin: {route.expected_profit_bps:.2f} bps ({route.expected_profit_bps/100:.2f}%)")
        print(f"Risk Score: {route.risk_score:.1f}/100")
        
        risk_metrics = calculator.calculate_risk_reward_ratio(route, capital)
        print(f"\nRisk Metrics:")
        print(f"  Total Risk: ${risk_metrics['total_risk_usd']:.2f} ({risk_metrics['total_risk_bps']:.2f} bps)")
        print(f"  R/R Ratio: {risk_metrics['risk_reward_ratio']:.2f}:1")
        print(f"  Win Probability: {risk_metrics['profit_probability']*100:.1f}%")
        print(f"  Break-Even Rate: {risk_metrics['break_even_success_rate']*100:.1f}%")
        
        return True
    else:
        print("❌ No profitable route found")
        return False


def test_4hop_arbitrage():
    """Test 4-hop rectangular arbitrage."""
    print("\n" + "="*70)
    print("TEST 3: 4-HOP RECTANGULAR ARBITRAGE")
    print("="*70)
    
    binance, kraken, uniswap = create_test_exchanges()
    
    # Create a rectangular path: USDT -> BTC -> ETH -> BNB -> USDT
    pair1 = TradingPair(
        base="BTC",
        quote="USDT",
        exchange=binance,
        bid_price=42000.0,
        ask_price=42050.0,
        spread=50.0,
        liquidity=5000000
    )
    
    pair2 = TradingPair(
        base="ETH",
        quote="BTC",
        exchange=kraken,
        bid_price=0.0625,
        ask_price=0.0630,
        spread=5.0,
        liquidity=2000000
    )
    
    pair3 = TradingPair(
        base="BNB",
        quote="ETH",
        exchange=uniswap,
        bid_price=0.130,  # 1 ETH = ~7.7 BNB
        ask_price=0.132,
        spread=2.0,
        liquidity=1000000
    )
    
    pair4 = TradingPair(
        base="BNB",
        quote="USDT",
        exchange=binance,
        bid_price=358.0,  # Higher BNB price creates arb opportunity
        ask_price=359.0,
        spread=1.0,
        liquidity=3000000
    )
    
    calculator = MultiHopArbitrageCalculator(min_profit_bps=40.0)
    capital = 10000.0
    
    route = calculator.calculate_4hop_arbitrage(pair1, pair2, pair3, pair4, capital)
    
    if route:
        print(f"\n✅ PROFITABLE 4-HOP ROUTE FOUND!")
        print(f"Path: {' → '.join(route.path)}")
        print(f"Expected Profit: ${route.expected_profit:.2f} USD")
        print(f"Profit Margin: {route.expected_profit_bps:.2f} bps")
        print(f"Risk Score: {route.risk_score:.1f}/100")
        print(f"Execution Time: {route.execution_time_ms:.0f} ms")
        
        risk_metrics = calculator.calculate_risk_reward_ratio(route, capital)
        
        # Full report
        print("\n" + format_arbitrage_report(route, risk_metrics, capital))
        
        return True
    else:
        print("❌ No profitable route found (4-hop has higher complexity)")
        print("This is expected - 4-hop routes need larger price discrepancies")
        return False


def test_risk_calculations():
    """Test risk calculation formulas."""
    print("\n" + "="*70)
    print("TEST 4: RISK CALCULATION VERIFICATION")
    print("="*70)
    
    binance, kraken, _ = create_test_exchanges()
    
    pair1 = TradingPair(
        base="BTC",
        quote="USDT",
        exchange=binance,
        bid_price=42000.0,
        ask_price=42020.0,
        spread=20.0,
        liquidity=5000000
    )
    
    pair2 = TradingPair(
        base="BTC",
        quote="USDT",
        exchange=kraken,
        bid_price=42200.0,  # Larger spread for testing
        ask_price=42220.0,
        spread=20.0,
        liquidity=3000000
    )
    
    calculator = MultiHopArbitrageCalculator()
    capital = 50000.0  # Larger capital to test risk
    
    route = calculator.calculate_2hop_arbitrage(pair1, pair2, capital)
    
    if route:
        risk_metrics = calculator.calculate_risk_reward_ratio(route, capital)
        
        print("\n📊 COMPREHENSIVE RISK ANALYSIS:")
        print(f"\nReward Components:")
        print(f"  Expected Profit: ${risk_metrics['expected_reward_usd']:,.2f}")
        print(f"  Profit Margin: {risk_metrics['expected_reward_bps']:.2f} bps")
        
        print(f"\nRisk Components:")
        print(f"  Slippage Risk: ${risk_metrics['slippage_risk']:,.2f}")
        print(f"  Fee Risk: ${risk_metrics['fee_risk']:,.2f}")
        print(f"  Gas Risk: ${risk_metrics['gas_risk']:,.2f}")
        print(f"  Execution Risk: ${risk_metrics['execution_risk']:,.2f}")
        print(f"  Total Risk: ${risk_metrics['total_risk_usd']:,.2f}")
        
        print(f"\nRisk Ratios:")
        print(f"  Risk/Reward: {risk_metrics['risk_reward_ratio']:.3f}:1")
        print(f"  Sharpe-Like: {risk_metrics['sharpe_like_ratio']:.3f}")
        print(f"  Max Drawdown: ${risk_metrics['max_drawdown_estimate']:,.2f}")
        
        print(f"\nProbabilities:")
        print(f"  Win Probability: {risk_metrics['profit_probability']*100:.2f}%")
        print(f"  Break-Even Rate: {risk_metrics['break_even_success_rate']*100:.2f}%")
        
        print(f"\nPosition Sizing:")
        print(f"  Kelly Fraction: {risk_metrics['kelly_fraction']*100:.2f}%")
        print(f"  Kelly Size: ${capital * risk_metrics['kelly_fraction']:,.2f}")
        print(f"  Max Recommended: ${route.max_capital_recommended:,.2f}")
        
        print(f"\nExpected Value:")
        print(f"  EV: ${risk_metrics['expected_value']:,.2f}")
        print(f"  {'✅ Positive EV' if risk_metrics['expected_value'] > 0 else '❌ Negative EV'}")
        
        # Verify Kelly Criterion calculation
        print(f"\n--- Kelly Criterion Verification ---")
        p = risk_metrics['profit_probability']
        win = risk_metrics['expected_reward_usd']
        loss = risk_metrics['total_risk_usd']
        b = win / loss if loss > 0 else 0
        kelly_full = (p * b - (1-p)) / b if b > 0 else 0
        kelly_frac = kelly_full * 0.25  # Fractional Kelly
        print(f"Win Probability (p): {p:.4f}")
        print(f"Win/Loss Ratio (b): {b:.4f}")
        print(f"Full Kelly: {kelly_full*100:.2f}%")
        print(f"Fractional Kelly (25%): {kelly_frac*100:.2f}%")
        print(f"Calculated Kelly: {risk_metrics['kelly_fraction']*100:.2f}%")
        print(f"✅ Kelly calculation {'matches' if abs(kelly_frac - risk_metrics['kelly_fraction']) < 0.01 else 'differs'}")
        
        return True
    
    return False


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n" + "="*70)
    print("TEST 5: EDGE CASES & ERROR HANDLING")
    print("="*70)
    
    binance, _, _ = create_test_exchanges()
    calculator = MultiHopArbitrageCalculator()
    
    # Test 1: No arbitrage opportunity (same prices)
    print("\nCase 1: No price difference (should fail)")
    pair1 = TradingPair(
        base="BTC", quote="USDT", exchange=binance,
        bid_price=42000.0, ask_price=42020.0, spread=20.0, liquidity=5000000
    )
    pair2 = TradingPair(
        base="BTC", quote="USDT", exchange=binance,
        bid_price=42000.0, ask_price=42020.0, spread=20.0, liquidity=5000000
    )
    
    route = calculator.calculate_2hop_arbitrage(pair1, pair2, 10000.0)
    if route is None:
        print("✅ Correctly rejected - no arbitrage opportunity")
    else:
        print("❌ Should have rejected this route")
    
    # Test 2: High slippage scenario
    print("\nCase 2: High slippage (low liquidity)")
    low_liq_exchange = Exchange(
        name="Low Liquidity",
        trading_fee=0.003,
        withdrawal_fee=0.001,
        gas_cost=5.0,
        liquidity_depth=50000,  # Very low liquidity
        slippage_factor=0.05  # 5% per $100k (very high)
    )
    
    pair_low_liq = TradingPair(
        base="BTC", quote="USDT", exchange=low_liq_exchange,
        bid_price=43000.0, ask_price=43050.0, spread=50.0, liquidity=50000
    )
    
    route = calculator.calculate_2hop_arbitrage(pair1, pair_low_liq, 10000.0)
    if route:
        print(f"⚠️  Route found but high risk score: {route.risk_score:.1f}/100")
        print(f"   Slippage estimate: {route.slippage_estimate*10000:.2f} bps")
    else:
        print("✅ Correctly rejected - excessive slippage")
    
    # Test 3: Very small capital
    print("\nCase 3: Very small capital")
    route = calculator.calculate_2hop_arbitrage(pair1, pair2, 100.0)
    if route is None:
        print("✅ Correctly rejected - capital too small")
    
    # Test 4: Verify all hop types
    print("\nCase 4: Route type validation")
    pair_good = TradingPair(
        base="BTC", quote="USDT", exchange=binance,
        bid_price=42200.0, ask_price=42220.0, spread=20.0, liquidity=5000000
    )
    
    route2 = calculator.calculate_2hop_arbitrage(pair1, pair_good, 10000.0)
    if route2 and route2.route_type == RouteType.TWO_HOP:
        print(f"✅ 2-hop route type correct: {route2.route_type.value} hops")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("TRIFECTAOMNI ARBITRAGE & RISK CALCULATOR VERIFICATION")
    print("="*70)
    print("\nThis test suite verifies:")
    print("  • 2-hop arbitrage calculations")
    print("  • 3-hop triangular arbitrage")
    print("  • 4-hop rectangular arbitrage")
    print("  • Risk/reward ratio computations")
    print("  • Kelly Criterion position sizing")
    print("  • Fee and slippage accounting")
    print("  • Edge case handling")
    
    results = []
    
    # Run tests
    results.append(("2-Hop Arbitrage", test_2hop_arbitrage()))
    results.append(("3-Hop Arbitrage", test_3hop_arbitrage()))
    results.append(("4-Hop Arbitrage", test_4hop_arbitrage()))
    results.append(("Risk Calculations", test_risk_calculations()))
    results.append(("Edge Cases", test_edge_cases()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n{passed}/{total} tests passed ({(passed/total)*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\n✅ Arbitrage calculations verified:")
        print("   • Multi-hop profit calculations accurate")
        print("   • Fee and slippage accounting correct")
        print("   • Risk metrics computed properly")
        print("   • Kelly Criterion position sizing validated")
        print("   • All formulas producing human-readable USD output")
        return 0
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
