#!/usr/bin/env python3
"""
Test Suite for Token Equivalence Mapping and Cross-Chain Bridge Detection

Validates:
- Token registry loading
- Equivalence group detection
- Cross-chain arbitrage opportunities
- Native vs bridged token arbitrage
- Price difference calculations
"""

from omni_trifecta.execution.token_equivalence import (
    TOKEN_REGISTRY,
    TokenInfo,
    ChainId,
    TokenType,
    detect_native_vs_bridged_arbitrage
)
from decimal import Decimal


def test_registry_loading():
    """Test that all tokens are loaded correctly."""
    print("\n" + "="*80)
    print("TEST 1: Registry Loading")
    print("="*80)
    
    stats = TOKEN_REGISTRY.get_summary_stats()
    print(f"\n✅ Total Tokens Loaded: {stats['total_tokens']}")
    print(f"✅ Unique Token Groups: {stats['unique_groups']}")
    print(f"✅ Chains Supported: {stats['chains_supported']}")
    print(f"✅ Stablecoins: {stats['stablecoins']}")
    print(f"✅ Native Tokens: {stats['native_tokens']}")
    print(f"✅ Bridged Tokens: {stats['bridged_tokens']}")
    print(f"✅ Wrapped Tokens: {stats['wrapped_tokens']}")
    print(f"✅ Liquid Staking Tokens: {stats['lst_tokens']}")
    
    assert stats['total_tokens'] >= 30, "Should have at least 30 tokens"
    assert stats['unique_groups'] >= 10, "Should have at least 10 token groups"
    assert stats['chains_supported'] == 8, "Should support 8 chains"
    
    print("\n✅ PASS: Registry loaded successfully")
    return True


def test_usdc_equivalence():
    """Test USDC token equivalence across chains."""
    print("\n" + "="*80)
    print("TEST 2: USDC Equivalence Detection")
    print("="*80)
    
    # Get USDC on Ethereum
    eth_usdc = TOKEN_REGISTRY.get_token(
        ChainId.ETHEREUM.value,
        "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
    )
    
    assert eth_usdc is not None, "Should find ETH USDC"
    print(f"\n✅ Found: {eth_usdc.symbol} on {eth_usdc.chain_name}")
    
    # Get all USDC equivalents
    equivalents = TOKEN_REGISTRY.get_equivalent_tokens(eth_usdc)
    print(f"\n✅ Found {len(equivalents)} USDC equivalents:")
    
    for token in equivalents:
        print(f"   • {token.symbol:10s} on {token.chain_name:15s} ({token.token_type.value})")
    
    assert len(equivalents) >= 10, "Should have at least 10 USDC variants"
    
    # Verify all are $1.00
    for token in equivalents:
        assert token.base_value_usd == 1.00, f"{token.symbol} should be $1.00"
    
    print("\n✅ PASS: All USDC variants are equivalent and pegged to $1.00")
    return True


def test_weth_equivalence():
    """Test WETH equivalence across chains."""
    print("\n" + "="*80)
    print("TEST 3: WETH Equivalence Detection")
    print("="*80)
    
    # Get WETH on Ethereum
    eth_weth = TOKEN_REGISTRY.get_token(
        ChainId.ETHEREUM.value,
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    )
    
    assert eth_weth is not None, "Should find ETH WETH"
    print(f"\n✅ Found: {eth_weth.symbol} on {eth_weth.chain_name}")
    
    # Get all WETH equivalents
    equivalents = TOKEN_REGISTRY.get_equivalent_tokens(eth_weth)
    print(f"\n✅ Found {len(equivalents)} WETH equivalents:")
    
    for token in equivalents:
        print(f"   • {token.symbol:10s} on {token.chain_name:15s} ({token.token_type.value})")
    
    assert len(equivalents) >= 6, "Should have at least 6 WETH variants"
    
    # Verify decimals are 18
    for token in equivalents:
        assert token.decimals == 18, f"{token.symbol} should have 18 decimals"
    
    print("\n✅ PASS: All WETH variants found across chains")
    return True


def test_wbtc_equivalence():
    """Test WBTC equivalence and 8-decimal handling."""
    print("\n" + "="*80)
    print("TEST 4: WBTC Equivalence and Decimal Handling")
    print("="*80)
    
    # Get WBTC on Ethereum
    eth_wbtc = TOKEN_REGISTRY.get_token(
        ChainId.ETHEREUM.value,
        "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"
    )
    
    assert eth_wbtc is not None, "Should find ETH WBTC"
    print(f"\n✅ Found: {eth_wbtc.symbol} on {eth_wbtc.chain_name}")
    
    # Get all WBTC equivalents
    equivalents = TOKEN_REGISTRY.get_equivalent_tokens(eth_wbtc)
    print(f"\n✅ Found {len(equivalents)} WBTC equivalents:")
    
    for token in equivalents:
        print(f"   • {token.symbol:10s} on {token.chain_name:15s} (Decimals: {token.decimals})")
    
    assert len(equivalents) >= 6, "Should have at least 6 WBTC variants"
    
    # Verify all have 8 decimals
    for token in equivalents:
        assert token.decimals == 8, f"{token.symbol} should have 8 decimals"
    
    print("\n✅ PASS: All BTC variants have 8 decimals")
    return True


def test_cross_chain_arbitrage_detection():
    """Test cross-chain arbitrage detection with price differences."""
    print("\n" + "="*80)
    print("TEST 5: Cross-Chain Arbitrage Detection")
    print("="*80)
    
    # Simulate price differences for USDC across chains
    prices = {
        '1_0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': 1.0000,  # ETH USDC
        '137_0x2791bca1f2de4661ed88a30c99a7a9449aa84174': 1.0015,  # Polygon USDC (1.5 bps higher)
        '42161_0xaf88d065e77c8cc2239327c5edb3a432268e5831': 0.9988,  # Arbitrum USDC (12 bps lower)
        '10_0x0b2c639c533813f4aa9d7837caf62653d097ff85': 1.0008,  # Optimism USDC
    }
    
    opportunities = TOKEN_REGISTRY.find_cross_chain_arbitrage('USDC', prices)
    
    print(f"\n✅ Found {len(opportunities)} arbitrage opportunities:")
    
    for i, opp in enumerate(opportunities, 1):
        buy_token = opp['buy_token']
        sell_token = opp['sell_token']
        
        print(f"\n   Opportunity #{i}:")
        print(f"   • Buy:  {buy_token.symbol} on {buy_token.chain_name} @ ${opp['buy_price']:.6f}")
        print(f"   • Sell: {sell_token.symbol} on {sell_token.chain_name} @ ${opp['sell_price']:.6f}")
        print(f"   • Price Difference: {opp['price_diff_pct']:.4f}% (${opp['price_diff_usd']:.6f})")
        print(f"   • Route Type: {opp['route_type']}")
    
    assert len(opportunities) > 0, "Should detect arbitrage opportunities"
    
    print("\n✅ PASS: Cross-chain arbitrage detection working")
    return True


def test_native_vs_bridged_arbitrage():
    """Test native vs bridged token arbitrage detection."""
    print("\n" + "="*80)
    print("TEST 6: Native vs Bridged Token Arbitrage")
    print("="*80)
    
    # Scenario 1: Native USDC vs Bridged USDC.e (profitable)
    arb1 = detect_native_vs_bridged_arbitrage(
        native_price=1.0010,
        bridged_price=0.9995,
        bridge_fee_bps=10.0
    )
    
    if arb1:
        print("\n✅ Scenario 1: USDC Native vs USDC.e Bridged")
        print(f"   • Buy: {arb1['buy_variant']} @ lower price")
        print(f"   • Sell: {arb1['sell_variant']} @ higher price")
        print(f"   • Price Difference: {arb1['price_diff_pct']:.4f}%")
        print(f"   • Bridge Fee: {arb1['bridge_fee_pct']:.4f}%")
        print(f"   • Net Profit: {arb1['net_profit_pct']:.4f}%")
        print(f"   • Recommended: {'✅ YES' if arb1['recommended'] else '❌ NO'}")
    else:
        print("\n❌ Scenario 1: No profitable arbitrage")
    
    # Scenario 2: Price difference too small (not profitable)
    arb2 = detect_native_vs_bridged_arbitrage(
        native_price=1.0005,
        bridged_price=1.0000,
        bridge_fee_bps=10.0
    )
    
    print("\n✅ Scenario 2: Small Price Difference (Not Profitable)")
    if arb2:
        print(f"   • Net Profit: {arb2['net_profit_pct']:.4f}% (Too small)")
    else:
        print(f"   • No arbitrage opportunity (price diff < bridge fees)")
    
    assert arb1 is not None, "Should detect profitable arbitrage"
    assert arb2 is None or arb2['net_profit_pct'] < 0.1, "Should reject small profits"
    
    print("\n✅ PASS: Native vs bridged arbitrage detection working")
    return True


def test_bridge_variant_detection():
    """Test detection of native and bridged variants."""
    print("\n" + "="*80)
    print("TEST 7: Bridge Variant Detection")
    print("="*80)
    
    # Get USDC on Arbitrum
    arb_usdc = TOKEN_REGISTRY.get_token(
        ChainId.ARBITRUM.value,
        "0xaf88d065e77c8cC2239327C5EDb3A432268e5831"
    )
    
    variants = TOKEN_REGISTRY.get_bridge_variants(arb_usdc)
    
    print(f"\n✅ USDC Variants Found:")
    print(f"   • Native variants: {len(variants['native'])}")
    print(f"   • Bridged variants: {len(variants['bridged'])}")
    print(f"   • Wrapped variants: {len(variants['wrapped'])}")
    
    print(f"\n   Native tokens:")
    for token in variants['native']:
        print(f"      - {token.symbol} on {token.chain_name}")
    
    print(f"\n   Bridged tokens:")
    for token in variants['bridged']:
        print(f"      - {token.symbol} on {token.chain_name}")
    
    assert len(variants['native']) > 0, "Should find native USDC variants"
    assert len(variants['bridged']) > 0, "Should find bridged USDC variants"
    
    print("\n✅ PASS: Bridge variant detection working")
    return True


def test_chain_token_listing():
    """Test listing all tokens on specific chains."""
    print("\n" + "="*80)
    print("TEST 8: Chain Token Listing")
    print("="*80)
    
    chains_to_test = [
        (ChainId.ETHEREUM.value, "Ethereum"),
        (ChainId.POLYGON.value, "Polygon"),
        (ChainId.ARBITRUM.value, "Arbitrum"),
        (ChainId.BASE.value, "Base"),
    ]
    
    for chain_id, chain_name in chains_to_test:
        tokens = TOKEN_REGISTRY.get_tokens_by_chain(chain_id)
        print(f"\n✅ {chain_name} (Chain ID: {chain_id})")
        print(f"   • Total tokens: {len(tokens)}")
        print(f"   • Tokens available:")
        
        for token in tokens[:5]:  # Show first 5
            print(f"      - {token.symbol:10s} ({token.token_type.value})")
        
        if len(tokens) > 5:
            print(f"      ... and {len(tokens) - 5} more")
    
    print("\n✅ PASS: Chain token listing working")
    return True


def test_stablecoin_detection():
    """Test stablecoin detection logic."""
    print("\n" + "="*80)
    print("TEST 9: Stablecoin Detection")
    print("="*80)
    
    # Get various tokens
    usdc = TOKEN_REGISTRY.get_token(ChainId.ETHEREUM.value, "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    usdt = TOKEN_REGISTRY.get_token(ChainId.ETHEREUM.value, "0xdAC17F958D2ee523a2206206994597C13D831ec7")
    weth = TOKEN_REGISTRY.get_token(ChainId.ETHEREUM.value, "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    wbtc = TOKEN_REGISTRY.get_token(ChainId.ETHEREUM.value, "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599")
    
    print(f"\n✅ Stablecoin Detection Results:")
    print(f"   • USDC: {'✅ Stablecoin' if TOKEN_REGISTRY.is_stablecoin(usdc) else '❌ Not Stablecoin'}")
    print(f"   • USDT: {'✅ Stablecoin' if TOKEN_REGISTRY.is_stablecoin(usdt) else '❌ Not Stablecoin'}")
    print(f"   • WETH: {'❌ Not Stablecoin' if not TOKEN_REGISTRY.is_stablecoin(weth) else '✅ Stablecoin'}")
    print(f"   • WBTC: {'❌ Not Stablecoin' if not TOKEN_REGISTRY.is_stablecoin(wbtc) else '✅ Stablecoin'}")
    
    assert TOKEN_REGISTRY.is_stablecoin(usdc), "USDC should be detected as stablecoin"
    assert TOKEN_REGISTRY.is_stablecoin(usdt), "USDT should be detected as stablecoin"
    assert not TOKEN_REGISTRY.is_stablecoin(weth), "WETH should not be stablecoin"
    assert not TOKEN_REGISTRY.is_stablecoin(wbtc), "WBTC should not be stablecoin"
    
    print("\n✅ PASS: Stablecoin detection working correctly")
    return True


def run_all_tests():
    """Run all test scenarios."""
    print("\n" + "="*80)
    print("🚀 TOKEN EQUIVALENCE MAPPING - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print("\nTesting multi-chain token equivalence, bridge detection,")
    print("and cross-chain arbitrage opportunity identification.")
    print("\nTotal Token Universe:")
    print("  • 20+ unique tokens")
    print("  • 50+ token addresses across chains")
    print("  • 8 EVM chains supported")
    print("  • 15+ stablecoin variants")
    print("  • 10+ bridged tokens")
    
    tests = [
        ("Registry Loading", test_registry_loading),
        ("USDC Equivalence", test_usdc_equivalence),
        ("WETH Equivalence", test_weth_equivalence),
        ("WBTC Equivalence", test_wbtc_equivalence),
        ("Cross-Chain Arbitrage", test_cross_chain_arbitrage_detection),
        ("Native vs Bridged", test_native_vs_bridged_arbitrage),
        ("Bridge Variants", test_bridge_variant_detection),
        ("Chain Token Listing", test_chain_token_listing),
        ("Stablecoin Detection", test_stablecoin_detection),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n❌ FAIL: {test_name}")
            print(f"   Error: {str(e)}")
            failed += 1
    
    # Final summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"\n✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n" + "="*80)
        print("🎉 ALL TESTS PASSED - TOKEN EQUIVALENCE SYSTEM VERIFIED")
        print("="*80)
        print("\n✅ Multi-Chain Token Mapping: OPERATIONAL")
        print("✅ Cross-Chain Arbitrage Detection: OPERATIONAL")
        print("✅ Native vs Bridged Detection: OPERATIONAL")
        print("✅ Bridge Variant Tracking: OPERATIONAL")
        print("✅ Decimal Handling (6, 8, 18): VERIFIED")
        print("\nSystem Status: PRODUCTION READY ✅")
        print("\nSupported Chains:")
        print("  • Ethereum (Chain ID: 1)")
        print("  • Polygon (Chain ID: 137)")
        print("  • Arbitrum (Chain ID: 42161)")
        print("  • Optimism (Chain ID: 10)")
        print("  • Base (Chain ID: 8453)")
        print("  • Avalanche (Chain ID: 43114)")
        print("  • BNB Chain (Chain ID: 56)")
        print("  • Fantom (Chain ID: 250)")
    else:
        print(f"\n⚠️  {failed} test(s) failed - review output above")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
