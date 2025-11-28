/**
 * MAINNET SOURCE DATA
 *
 * This file contains sample mainnet token and pair data for Polygon network.
 * In production, this data should be populated from your DEX/GraphQL parser.
 *
 * Data sources include:
 * - Quickswap, SushiSwap, Curve, Balancer, UniV3, DFYN, APE, etc.
 */

import { TokenSymbol, RobustPairEdge } from '../mainnetRouteMatrixBuilder';

// --- TOKEN DATA ---
// Map of Symbol -> Address (Polygon Mainnet)
export const MAINNET_TOKENS: Record<TokenSymbol, string> = {
  'WMATIC': '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270',
  'USDC': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
  'USDT': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
  'DAI': '0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063',
  'WETH': '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619',
  'WBTC': '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6',
  'AAVE': '0xD6DF932A45C0f255f85145f286eA0b292B21C90B',
  'LINK': '0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39',
  'CRV': '0x172370d5Cd63279eFa6d502DAB29171933a610AF',
  'SUSHI': '0x0b3F868E0BE5597D5DB7fEB59E1CADBb0fdDa50a',
  'BAL': '0x9a71012B13CA4d3D0Cdc72A177DF3ef03b0E76A3',
  'UNI': '0xb33EaAd8d922B1083446DC23f610c2567fB5180f',
  'QUICK': '0xB5C064F955D8e7F38fE0460C556a72987494eE17',
  'FRAX': '0x45c32fA6DF82ead1e2EF74d17b76547EDdFaFF89',
  'MIMATIC': '0xa3Fa99A148fA48D14Ed51d610c367C61876997F1'
};

// --- PROTOCOL CONSTANTS ---
export const PROTOCOLS = {
  QUICKSWAP: 'QUICKSWAP',
  QUICKSWAP_V3: 'QUICKSWAP_V3',
  UNISWAP_V3: 'UNISWAP_V3',
  SUSHISWAP: 'SUSHISWAP',
  CURVE: 'CURVE',
  BALANCER: 'BALANCER',
  DFYN: 'DFYN',
  APE: 'APE',
  DODO: 'DODO',
  SYNAPSE: 'SYNAPSE'
} as const;

// --- PAIR DATA (ROBUSTPAIREDGE) ---
// This data must come from your DEX/GraphQL parser.
// Format: [Token A, Token B, Protocol]
export const MAINNET_PAIRS: RobustPairEdge[] = [
  // WMATIC pairs
  ['WMATIC', 'USDC', PROTOCOLS.QUICKSWAP],
  ['WMATIC', 'USDC', PROTOCOLS.UNISWAP_V3],
  ['WMATIC', 'USDC', PROTOCOLS.SUSHISWAP],
  ['WMATIC', 'USDT', PROTOCOLS.QUICKSWAP],
  ['WMATIC', 'USDT', PROTOCOLS.SUSHISWAP],
  ['WMATIC', 'WETH', PROTOCOLS.QUICKSWAP],
  ['WMATIC', 'WETH', PROTOCOLS.UNISWAP_V3],
  ['WMATIC', 'WETH', PROTOCOLS.APE],
  ['WMATIC', 'DAI', PROTOCOLS.QUICKSWAP],
  ['WMATIC', 'WBTC', PROTOCOLS.QUICKSWAP],
  ['WMATIC', 'AAVE', PROTOCOLS.QUICKSWAP],
  ['WMATIC', 'LINK', PROTOCOLS.QUICKSWAP],
  ['WMATIC', 'QUICK', PROTOCOLS.QUICKSWAP],

  // WETH pairs
  ['WETH', 'USDC', PROTOCOLS.QUICKSWAP],
  ['WETH', 'USDC', PROTOCOLS.UNISWAP_V3],
  ['WETH', 'USDC', PROTOCOLS.SUSHISWAP],
  ['WETH', 'USDT', PROTOCOLS.QUICKSWAP],
  ['WETH', 'USDT', PROTOCOLS.UNISWAP_V3],
  ['WETH', 'DAI', PROTOCOLS.QUICKSWAP],
  ['WETH', 'WBTC', PROTOCOLS.QUICKSWAP],
  ['WETH', 'WBTC', PROTOCOLS.UNISWAP_V3],
  ['WETH', 'AAVE', PROTOCOLS.QUICKSWAP],
  ['WETH', 'LINK', PROTOCOLS.QUICKSWAP],
  ['WETH', 'LINK', PROTOCOLS.SUSHISWAP],
  ['WETH', 'CRV', PROTOCOLS.SUSHISWAP],
  ['WETH', 'UNI', PROTOCOLS.QUICKSWAP],
  ['WETH', 'SUSHI', PROTOCOLS.SUSHISWAP],

  // Stablecoin pairs
  ['USDC', 'USDT', PROTOCOLS.QUICKSWAP],
  ['USDC', 'USDT', PROTOCOLS.CURVE],
  ['USDC', 'DAI', PROTOCOLS.QUICKSWAP],
  ['USDC', 'DAI', PROTOCOLS.CURVE],
  ['USDC', 'FRAX', PROTOCOLS.CURVE],
  ['USDC', 'MIMATIC', PROTOCOLS.QUICKSWAP],
  ['USDT', 'DAI', PROTOCOLS.QUICKSWAP],
  ['USDT', 'DAI', PROTOCOLS.CURVE],
  ['DAI', 'FRAX', PROTOCOLS.CURVE],
  ['DAI', 'MIMATIC', PROTOCOLS.QUICKSWAP],

  // WBTC pairs
  ['WBTC', 'USDC', PROTOCOLS.QUICKSWAP],
  ['WBTC', 'USDC', PROTOCOLS.UNISWAP_V3],
  ['WBTC', 'USDT', PROTOCOLS.QUICKSWAP],
  ['WBTC', 'DAI', PROTOCOLS.QUICKSWAP],

  // DeFi tokens
  ['AAVE', 'USDC', PROTOCOLS.QUICKSWAP],
  ['AAVE', 'WETH', PROTOCOLS.SUSHISWAP],
  ['LINK', 'USDC', PROTOCOLS.QUICKSWAP],
  ['CRV', 'USDC', PROTOCOLS.QUICKSWAP],
  ['CRV', 'WMATIC', PROTOCOLS.QUICKSWAP],
  ['BAL', 'WETH', PROTOCOLS.BALANCER],
  ['BAL', 'USDC', PROTOCOLS.BALANCER],
  ['UNI', 'USDC', PROTOCOLS.QUICKSWAP],
  ['SUSHI', 'WMATIC', PROTOCOLS.SUSHISWAP],
  ['SUSHI', 'USDC', PROTOCOLS.SUSHISWAP],
  ['QUICK', 'USDC', PROTOCOLS.QUICKSWAP],
  ['QUICK', 'WETH', PROTOCOLS.QUICKSWAP],

  // Cross-DEX opportunities
  ['FRAX', 'USDC', PROTOCOLS.QUICKSWAP],
  ['FRAX', 'WMATIC', PROTOCOLS.QUICKSWAP],
  ['MIMATIC', 'USDC', PROTOCOLS.CURVE]
];

/**
 * Get token symbols as array
 */
export function getTokenSymbols(): TokenSymbol[] {
  return Object.keys(MAINNET_TOKENS);
}

/**
 * Get token address by symbol
 */
export function getTokenAddress(symbol: TokenSymbol): string | undefined {
  return MAINNET_TOKENS[symbol];
}

/**
 * Get all pairs for a specific protocol
 */
export function getPairsByProtocol(protocol: string): RobustPairEdge[] {
  return MAINNET_PAIRS.filter(pair => pair[2] === protocol);
}

/**
 * Get all pairs containing a specific token
 */
export function getPairsForToken(token: TokenSymbol): RobustPairEdge[] {
  return MAINNET_PAIRS.filter(pair => pair[0] === token || pair[1] === token);
}
