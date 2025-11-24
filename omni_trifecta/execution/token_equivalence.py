"""
Cross-Chain Token Equivalence Mapping and Bridge Detection

Comprehensive token mapping for multi-chain arbitrage opportunities.
Supports native tokens, bridged variants, wrapped tokens, and stablecoins.
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal


class ChainId(Enum):
    """Supported blockchain networks."""
    ETHEREUM = 1
    POLYGON = 137
    ARBITRUM = 42161
    OPTIMISM = 10
    BASE = 8453
    AVALANCHE = 43114
    BNB_CHAIN = 56
    FANTOM = 250


class TokenType(Enum):
    """Token variant types."""
    NATIVE = "native"
    BRIDGED = "bridged"
    WRAPPED = "wrapped"
    LIQUID_STAKING = "liquid_staking"
    SYNTHETIC = "synthetic"


@dataclass
class TokenInfo:
    """Complete token information."""
    symbol: str
    address: str
    chain_id: int
    chain_name: str
    token_type: TokenType
    decimals: int
    equivalent_group: str  # e.g., "USDC", "WETH", "WBTC"
    base_value_usd: float  # Reference price
    notes: str = ""
    
    def is_equivalent_to(self, other: 'TokenInfo') -> bool:
        """Check if two tokens are equivalent (same underlying asset)."""
        return self.equivalent_group == other.equivalent_group
    
    def get_bridge_pair_key(self) -> str:
        """Get unique identifier for bridge pair detection."""
        return f"{self.chain_id}_{self.address.lower()}"


# ============================================================================
# STABLECOIN EQUIVALENTS (All = $1.00 USD)
# ============================================================================

USDC_TOKENS = [
    # Ethereum
    TokenInfo(
        symbol="USDC",
        address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        chain_id=ChainId.ETHEREUM.value,
        chain_name="Ethereum",
        token_type=TokenType.NATIVE,
        decimals=6,
        equivalent_group="USDC",
        base_value_usd=1.00,
        notes="Circle native USDC"
    ),
    # Polygon
    TokenInfo(
        symbol="USDC",
        address="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        chain_id=ChainId.POLYGON.value,
        chain_name="Polygon",
        token_type=TokenType.NATIVE,
        decimals=6,
        equivalent_group="USDC",
        base_value_usd=1.00,
        notes="Circle native on Polygon"
    ),
    TokenInfo(
        symbol="USDC.e",
        address="0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174",
        chain_id=ChainId.POLYGON.value,
        chain_name="Polygon",
        token_type=TokenType.BRIDGED,
        decimals=6,
        equivalent_group="USDC",
        base_value_usd=1.00,
        notes="Ethereum → Polygon bridge"
    ),
    # Arbitrum
    TokenInfo(
        symbol="USDC",
        address="0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
        chain_id=ChainId.ARBITRUM.value,
        chain_name="Arbitrum",
        token_type=TokenType.NATIVE,
        decimals=6,
        equivalent_group="USDC",
        base_value_usd=1.00,
        notes="Circle native on Arbitrum"
    ),
    TokenInfo(
        symbol="USDC.e",
        address="0xFF970A61A04b1cA14834A43f5dE4533eBDDB5CC8",
        chain_id=ChainId.ARBITRUM.value,
        chain_name="Arbitrum",
        token_type=TokenType.BRIDGED,
        decimals=6,
        equivalent_group="USDC",
        base_value_usd=1.00,
        notes="Ethereum → Arbitrum bridge"
    ),
    # Optimism
    TokenInfo(
        symbol="USDC",
        address="0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85",
        chain_id=ChainId.OPTIMISM.value,
        chain_name="Optimism",
        token_type=TokenType.NATIVE,
        decimals=6,
        equivalent_group="USDC",
        base_value_usd=1.00,
        notes="Circle native on Optimism"
    ),
    TokenInfo(
        symbol="USDC.e",
        address="0x7F5c764cBc14f9669B88837ca1490cCa17c31607",
        chain_id=ChainId.OPTIMISM.value,
        chain_name="Optimism",
        token_type=TokenType.BRIDGED,
        decimals=6,
        equivalent_group="USDC",
        base_value_usd=1.00,
        notes="Ethereum → Optimism bridge"
    ),
    # Base
    TokenInfo(
        symbol="USDbC",
        address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
        chain_id=ChainId.BASE.value,
        chain_name="Base",
        token_type=TokenType.NATIVE,
        decimals=6,
        equivalent_group="USDC",
        base_value_usd=1.00,
        notes="Base-native USDC"
    ),
    # Avalanche
    TokenInfo(
        symbol="USDC",
        address="0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",
        chain_id=ChainId.AVALANCHE.value,
        chain_name="Avalanche",
        token_type=TokenType.NATIVE,
        decimals=6,
        equivalent_group="USDC",
        base_value_usd=1.00,
        notes="Circle native on Avalanche"
    ),
    TokenInfo(
        symbol="USDC.e",
        address="0xA7D7079b0FEaD91F3e65f86E8915Cb59c1a4C664",
        chain_id=ChainId.AVALANCHE.value,
        chain_name="Avalanche",
        token_type=TokenType.BRIDGED,
        decimals=6,
        equivalent_group="USDC",
        base_value_usd=1.00,
        notes="Ethereum → Avalanche bridge"
    ),
]

USDT_TOKENS = [
    TokenInfo(
        symbol="USDT",
        address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
        chain_id=ChainId.ETHEREUM.value,
        chain_name="Ethereum",
        token_type=TokenType.NATIVE,
        decimals=6,
        equivalent_group="USDT",
        base_value_usd=1.00,
        notes="Tether native"
    ),
    TokenInfo(
        symbol="USDT",
        address="0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
        chain_id=ChainId.POLYGON.value,
        chain_name="Polygon",
        token_type=TokenType.BRIDGED,
        decimals=6,
        equivalent_group="USDT",
        base_value_usd=1.00,
        notes="Bridged USDT"
    ),
    TokenInfo(
        symbol="USDT",
        address="0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
        chain_id=ChainId.ARBITRUM.value,
        chain_name="Arbitrum",
        token_type=TokenType.BRIDGED,
        decimals=6,
        equivalent_group="USDT",
        base_value_usd=1.00,
        notes="Bridged USDT"
    ),
    TokenInfo(
        symbol="USDT",
        address="0x94b008aA00579c1307B0EF2c499aD98a8ce58e58",
        chain_id=ChainId.OPTIMISM.value,
        chain_name="Optimism",
        token_type=TokenType.BRIDGED,
        decimals=6,
        equivalent_group="USDT",
        base_value_usd=1.00,
        notes="Bridged USDT"
    ),
    TokenInfo(
        symbol="USDT",
        address="0x9702230A8Ea53601f5cD2dc00fDBc13d4dF4A8c7",
        chain_id=ChainId.AVALANCHE.value,
        chain_name="Avalanche",
        token_type=TokenType.NATIVE,
        decimals=6,
        equivalent_group="USDT",
        base_value_usd=1.00,
        notes="Native USDT"
    ),
    TokenInfo(
        symbol="USDT",
        address="0x55d398326f99059fF775485246999027B3197955",
        chain_id=ChainId.BNB_CHAIN.value,
        chain_name="BNB Chain",
        token_type=TokenType.NATIVE,
        decimals=18,
        equivalent_group="USDT",
        base_value_usd=1.00,
        notes="Native USDT on BSC"
    ),
]

# ============================================================================
# ETH/WETH EQUIVALENTS (Price varies ~$2,200)
# ============================================================================

WETH_TOKENS = [
    TokenInfo(
        symbol="WETH",
        address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        chain_id=ChainId.ETHEREUM.value,
        chain_name="Ethereum",
        token_type=TokenType.WRAPPED,
        decimals=18,
        equivalent_group="WETH",
        base_value_usd=2200.00,
        notes="Canonical WETH"
    ),
    TokenInfo(
        symbol="WETH",
        address="0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619",
        chain_id=ChainId.POLYGON.value,
        chain_name="Polygon",
        token_type=TokenType.BRIDGED,
        decimals=18,
        equivalent_group="WETH",
        base_value_usd=2200.00,
        notes="ETH from Ethereum"
    ),
    TokenInfo(
        symbol="WETH",
        address="0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
        chain_id=ChainId.ARBITRUM.value,
        chain_name="Arbitrum",
        token_type=TokenType.WRAPPED,
        decimals=18,
        equivalent_group="WETH",
        base_value_usd=2200.00,
        notes="Arbitrum native ETH wrap"
    ),
    TokenInfo(
        symbol="WETH",
        address="0x4200000000000000000000000000000000000006",
        chain_id=ChainId.OPTIMISM.value,
        chain_name="Optimism",
        token_type=TokenType.WRAPPED,
        decimals=18,
        equivalent_group="WETH",
        base_value_usd=2200.00,
        notes="Optimism native ETH wrap"
    ),
    TokenInfo(
        symbol="WETH",
        address="0x4200000000000000000000000000000000000006",
        chain_id=ChainId.BASE.value,
        chain_name="Base",
        token_type=TokenType.WRAPPED,
        decimals=18,
        equivalent_group="WETH",
        base_value_usd=2200.00,
        notes="Base native ETH wrap"
    ),
    TokenInfo(
        symbol="WETH.e",
        address="0x49D5c2BdFfac6CE2BFdB6640F4F80f226bc10bAB",
        chain_id=ChainId.AVALANCHE.value,
        chain_name="Avalanche",
        token_type=TokenType.BRIDGED,
        decimals=18,
        equivalent_group="WETH",
        base_value_usd=2200.00,
        notes="ETH from Ethereum"
    ),
]

# Liquid Staking Derivatives
ETH_LST_TOKENS = [
    TokenInfo(
        symbol="stETH",
        address="0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84",
        chain_id=ChainId.ETHEREUM.value,
        chain_name="Ethereum",
        token_type=TokenType.LIQUID_STAKING,
        decimals=18,
        equivalent_group="stETH",
        base_value_usd=2200.00,
        notes="Lido staked ETH ~1:1"
    ),
    TokenInfo(
        symbol="wstETH",
        address="0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0",
        chain_id=ChainId.ETHEREUM.value,
        chain_name="Ethereum",
        token_type=TokenType.WRAPPED,
        decimals=18,
        equivalent_group="stETH",
        base_value_usd=2200.00,
        notes="Wrapped stETH"
    ),
    TokenInfo(
        symbol="cbETH",
        address="0x2Ae3F1Ec7F1F5012CFEab0185bfc7aa3cf0DEc22",
        chain_id=ChainId.BASE.value,
        chain_name="Base",
        token_type=TokenType.LIQUID_STAKING,
        decimals=18,
        equivalent_group="cbETH",
        base_value_usd=2244.00,
        notes="Coinbase ETH ~1.02:1"
    ),
]

# ============================================================================
# BTC/WBTC EQUIVALENTS (Price varies ~$43,500)
# ============================================================================

WBTC_TOKENS = [
    TokenInfo(
        symbol="WBTC",
        address="0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
        chain_id=ChainId.ETHEREUM.value,
        chain_name="Ethereum",
        token_type=TokenType.WRAPPED,
        decimals=8,
        equivalent_group="WBTC",
        base_value_usd=43500.00,
        notes="Wrapped Bitcoin"
    ),
    TokenInfo(
        symbol="WBTC",
        address="0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6",
        chain_id=ChainId.POLYGON.value,
        chain_name="Polygon",
        token_type=TokenType.BRIDGED,
        decimals=8,
        equivalent_group="WBTC",
        base_value_usd=43500.00,
        notes="Bridged WBTC"
    ),
    TokenInfo(
        symbol="WBTC",
        address="0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f",
        chain_id=ChainId.ARBITRUM.value,
        chain_name="Arbitrum",
        token_type=TokenType.BRIDGED,
        decimals=8,
        equivalent_group="WBTC",
        base_value_usd=43500.00,
        notes="Bridged WBTC"
    ),
    TokenInfo(
        symbol="WBTC",
        address="0x68f180fcCe6836688e9084f035309E29Bf0A2095",
        chain_id=ChainId.OPTIMISM.value,
        chain_name="Optimism",
        token_type=TokenType.BRIDGED,
        decimals=8,
        equivalent_group="WBTC",
        base_value_usd=43500.00,
        notes="Bridged WBTC"
    ),
    TokenInfo(
        symbol="BTC.b",
        address="0x152b9d0FdC40C096757F570A51E494bd4b943E50",
        chain_id=ChainId.AVALANCHE.value,
        chain_name="Avalanche",
        token_type=TokenType.WRAPPED,
        decimals=8,
        equivalent_group="WBTC",
        base_value_usd=43500.00,
        notes="Wrapped BTC on Avalanche"
    ),
    TokenInfo(
        symbol="BTCB",
        address="0x7130d2A12B9BCbFAe4f2634d864A1Ee1Ce3Ead9c",
        chain_id=ChainId.BNB_CHAIN.value,
        chain_name="BNB Chain",
        token_type=TokenType.WRAPPED,
        decimals=8,
        equivalent_group="WBTC",
        base_value_usd=43500.00,
        notes="Wrapped BTC on BSC"
    ),
]

# ============================================================================
# NATIVE CHAIN TOKENS
# ============================================================================

NATIVE_TOKENS = [
    TokenInfo(
        symbol="WMATIC",
        address="0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
        chain_id=ChainId.POLYGON.value,
        chain_name="Polygon",
        token_type=TokenType.WRAPPED,
        decimals=18,
        equivalent_group="MATIC",
        base_value_usd=0.80,
        notes="Wrapped MATIC"
    ),
    TokenInfo(
        symbol="WAVAX",
        address="0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
        chain_id=ChainId.AVALANCHE.value,
        chain_name="Avalanche",
        token_type=TokenType.WRAPPED,
        decimals=18,
        equivalent_group="AVAX",
        base_value_usd=35.00,
        notes="Wrapped AVAX"
    ),
    TokenInfo(
        symbol="WBNB",
        address="0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
        chain_id=ChainId.BNB_CHAIN.value,
        chain_name="BNB Chain",
        token_type=TokenType.WRAPPED,
        decimals=18,
        equivalent_group="BNB",
        base_value_usd=320.00,
        notes="Wrapped BNB"
    ),
    TokenInfo(
        symbol="WFTM",
        address="0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83",
        chain_id=ChainId.FANTOM.value,
        chain_name="Fantom",
        token_type=TokenType.WRAPPED,
        decimals=18,
        equivalent_group="FTM",
        base_value_usd=0.45,
        notes="Wrapped FTM"
    ),
    TokenInfo(
        symbol="OP",
        address="0x4200000000000000000000000000000000000042",
        chain_id=ChainId.OPTIMISM.value,
        chain_name="Optimism",
        token_type=TokenType.NATIVE,
        decimals=18,
        equivalent_group="OP",
        base_value_usd=1.80,
        notes="Optimism token"
    ),
    TokenInfo(
        symbol="ARB",
        address="0x912CE59144191C1204E64559FE8253a0e49E6548",
        chain_id=ChainId.ARBITRUM.value,
        chain_name="Arbitrum",
        token_type=TokenType.NATIVE,
        decimals=18,
        equivalent_group="ARB",
        base_value_usd=0.95,
        notes="Arbitrum token"
    ),
]


class TokenEquivalenceRegistry:
    """
    Registry for token equivalence and cross-chain mapping.
    Enables detection of arbitrage opportunities across chains and token variants.
    """
    
    def __init__(self):
        """Initialize the token registry."""
        self.tokens: List[TokenInfo] = []
        self.address_lookup: Dict[str, TokenInfo] = {}
        self.equivalence_groups: Dict[str, List[TokenInfo]] = {}
        self.chain_tokens: Dict[int, List[TokenInfo]] = {}
        
        # Load all token definitions
        self._load_tokens()
        self._build_indexes()
    
    def _load_tokens(self):
        """Load all token definitions."""
        self.tokens.extend(USDC_TOKENS)
        self.tokens.extend(USDT_TOKENS)
        self.tokens.extend(WETH_TOKENS)
        self.tokens.extend(ETH_LST_TOKENS)
        self.tokens.extend(WBTC_TOKENS)
        self.tokens.extend(NATIVE_TOKENS)
    
    def _build_indexes(self):
        """Build lookup indexes for fast queries."""
        for token in self.tokens:
            # Address lookup
            key = f"{token.chain_id}_{token.address.lower()}"
            self.address_lookup[key] = token
            
            # Equivalence groups
            if token.equivalent_group not in self.equivalence_groups:
                self.equivalence_groups[token.equivalent_group] = []
            self.equivalence_groups[token.equivalent_group].append(token)
            
            # Chain tokens
            if token.chain_id not in self.chain_tokens:
                self.chain_tokens[token.chain_id] = []
            self.chain_tokens[token.chain_id].append(token)
    
    def get_token(self, chain_id: int, address: str) -> Optional[TokenInfo]:
        """Get token info by chain and address."""
        key = f"{chain_id}_{address.lower()}"
        return self.address_lookup.get(key)
    
    def get_equivalent_tokens(self, token: TokenInfo) -> List[TokenInfo]:
        """Get all tokens equivalent to the given token."""
        return self.equivalence_groups.get(token.equivalent_group, [])
    
    def find_cross_chain_arbitrage(
        self,
        token_group: str,
        prices: Dict[str, float]
    ) -> List[Dict]:
        """
        Find cross-chain arbitrage opportunities for a token group.
        
        Args:
            token_group: Equivalent group (e.g., "USDC", "WETH")
            prices: Dict mapping "chain_id_address" to current price
            
        Returns:
            List of arbitrage opportunities
        """
        opportunities = []
        tokens = self.equivalence_groups.get(token_group, [])
        
        if len(tokens) < 2:
            return opportunities
        
        # Compare prices across all pairs
        for i, token1 in enumerate(tokens):
            key1 = token1.get_bridge_pair_key()
            price1 = prices.get(key1)
            
            if price1 is None:
                continue
            
            for token2 in tokens[i+1:]:
                key2 = token2.get_bridge_pair_key()
                price2 = prices.get(key2)
                
                if price2 is None:
                    continue
                
                # Calculate price difference
                price_diff = abs(price1 - price2)
                price_diff_pct = (price_diff / min(price1, price2)) * 100
                
                # Potential arbitrage if difference > 0.1%
                if price_diff_pct > 0.1:
                    opportunities.append({
                        'token_group': token_group,
                        'buy_token': token2 if price2 < price1 else token1,
                        'sell_token': token1 if price2 < price1 else token2,
                        'buy_price': min(price1, price2),
                        'sell_price': max(price1, price2),
                        'price_diff_pct': price_diff_pct,
                        'price_diff_usd': price_diff,
                        'route_type': '2-hop-cross-chain'
                    })
        
        return opportunities
    
    def get_tokens_by_chain(self, chain_id: int) -> List[TokenInfo]:
        """Get all tokens on a specific chain."""
        return self.chain_tokens.get(chain_id, [])
    
    def is_stablecoin(self, token: TokenInfo) -> bool:
        """Check if token is a stablecoin."""
        return token.equivalent_group in ['USDC', 'USDT', 'DAI', 'BUSD']
    
    def get_bridge_variants(self, token: TokenInfo) -> Dict[str, List[TokenInfo]]:
        """
        Get native and bridged variants of a token.
        
        Returns:
            Dict with 'native' and 'bridged' lists
        """
        equivalent_tokens = self.get_equivalent_tokens(token)
        
        return {
            'native': [t for t in equivalent_tokens if t.token_type == TokenType.NATIVE],
            'bridged': [t for t in equivalent_tokens if t.token_type == TokenType.BRIDGED],
            'wrapped': [t for t in equivalent_tokens if t.token_type == TokenType.WRAPPED]
        }
    
    def format_token_info(self, token: TokenInfo) -> str:
        """Format token information for display."""
        return (
            f"{token.symbol} on {token.chain_name}\n"
            f"  Address: {token.address}\n"
            f"  Type: {token.token_type.value}\n"
            f"  Decimals: {token.decimals}\n"
            f"  Base Value: ${token.base_value_usd:,.2f} USD\n"
            f"  Group: {token.equivalent_group}\n"
            f"  Notes: {token.notes}"
        )
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics of the registry."""
        return {
            'total_tokens': len(self.tokens),
            'unique_groups': len(self.equivalence_groups),
            'chains_supported': len(self.chain_tokens),
            'stablecoins': len([t for t in self.tokens if self.is_stablecoin(t)]),
            'native_tokens': len([t for t in self.tokens if t.token_type == TokenType.NATIVE]),
            'bridged_tokens': len([t for t in self.tokens if t.token_type == TokenType.BRIDGED]),
            'wrapped_tokens': len([t for t in self.tokens if t.token_type == TokenType.WRAPPED]),
            'lst_tokens': len([t for t in self.tokens if t.token_type == TokenType.LIQUID_STAKING])
        }


# Global registry instance
TOKEN_REGISTRY = TokenEquivalenceRegistry()


def detect_native_vs_bridged_arbitrage(
    native_price: float,
    bridged_price: float,
    bridge_fee_bps: float = 10.0
) -> Optional[Dict]:
    """
    Detect arbitrage between native and bridged token variants.
    
    Args:
        native_price: Price of native token
        bridged_price: Price of bridged token
        bridge_fee_bps: Bridge fee in basis points (default 10 bps = 0.1%)
        
    Returns:
        Arbitrage opportunity dict or None
    """
    price_diff_pct = abs(native_price - bridged_price) / min(native_price, bridged_price) * 100
    bridge_fee_pct = bridge_fee_bps / 100
    
    # Net profit after bridge fees
    net_profit_pct = price_diff_pct - bridge_fee_pct
    
    if net_profit_pct > 0.05:  # Minimum 0.05% profit
        return {
            'buy_variant': 'bridged' if bridged_price < native_price else 'native',
            'sell_variant': 'native' if bridged_price < native_price else 'bridged',
            'price_diff_pct': price_diff_pct,
            'bridge_fee_pct': bridge_fee_pct,
            'net_profit_pct': net_profit_pct,
            'recommended': net_profit_pct > 0.1
        }
    
    return None
