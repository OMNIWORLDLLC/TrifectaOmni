# OMNIARB Route Matrix Module

Mainnet-production route matrix precomputation and persistent store for OMNIARB.

## Overview

This TypeScript module is designed for OMNIARB FULL MATRIX implementation. It finds all non-cyclic 2–4-hop routes, attaching the protocol (DEX/Bridge) used for each segment, which is critical for transaction encoding (OMNIARB Decoder/Executor).

## Key Features

1. **Protocol-Aware Data Structure:** Uses `RobustRoute` with `segments: RouteSegment[]` array. Each segment includes the protocol (Router/Pool) that handles the hop.

2. **Protocol Tracing DFS:** The route builder tracks and traces **all available protocols** for a given token pair, ensuring maximal market depth coverage across multiple DEXes.

3. **Production Persistence Guard:** Uses **Atomic Write Logic** to prevent concurrent readers from loading a partially-written route matrix.

4. **Cyclic Arbitrage Routes:** Includes `buildArbitrageRoutes()` for generating true arbitrage loops that start and end at the same token.

## Installation

```bash
cd ts
npm install
```

## Build

```bash
npm run build
```

## Test

```bash
npm test
```

## Lint

```bash
npm run lint
```

## Usage

### Basic Route Building

```typescript
import {
  buildAllRoutes,
  buildAndPersistRouteMatrix,
  buildArbitrageRoutes,
  RobustPairEdge
} from '@omniarb/route-matrix';

const tokens = ['WMATIC', 'USDC', 'WETH', 'DAI'];
const pairs: RobustPairEdge[] = [
  ['WMATIC', 'USDC', 'QUICKSWAP'],
  ['WMATIC', 'USDC', 'UNISWAP_V3'],
  ['USDC', 'WETH', 'QUICKSWAP'],
  ['WETH', 'DAI', 'SUSHISWAP']
];

// Build all non-cyclic routes
const routes = buildAllRoutes(tokens, pairs, 4);

// Build cyclic arbitrage routes
const arbRoutes = buildArbitrageRoutes(tokens, pairs, 4);

// Persist to file with atomic write
await buildAndPersistRouteMatrix('polygon', tokens, pairs, 4, 'routes.polygon.json');
```

### Using the Sample Polygon Data

```typescript
import {
  buildAllRoutes,
  MAINNET_TOKENS,
  MAINNET_PAIRS,
  getTokenSymbols
} from '@omniarb/route-matrix';

const tokens = getTokenSymbols();
const routes = buildAllRoutes(tokens, MAINNET_PAIRS, 4);
console.log(`Generated ${routes.length} routes`);
```

### Filtering Routes

```typescript
import {
  buildAllRoutes,
  buildRouteIndex,
  filterRoutesByDestination,
  filterRoutesByHops,
  filterRoutesByProtocol
} from '@omniarb/route-matrix';

const routes = buildAllRoutes(tokens, pairs, 4);

// Index by source token for O(1) lookup
const index = buildRouteIndex(routes);
const wmaticRoutes = index.get('WMATIC') || [];

// Filter by destination
const toUsdc = filterRoutesByDestination(routes, 'USDC');

// Filter by hop count
const twoHops = filterRoutesByHops(routes, 2);

// Filter by protocol
const curveRoutes = filterRoutesByProtocol(routes, 'CURVE');
```

## Types

### RobustPairEdge

```typescript
type RobustPairEdge = [TokenSymbol, TokenSymbol, ProtocolKey];
// Example: ['USDC', 'WETH', 'UNISWAP_V3']
```

### RouteSegment

```typescript
interface RouteSegment {
  tokenIn: TokenSymbol;
  tokenOut: TokenSymbol;
  protocol: ProtocolKey;
}
```

### RobustRoute

```typescript
interface RobustRoute {
  segments: RouteSegment[];  // Array of swaps
  path: TokenSymbol[];       // Token sequence: ['WETH', 'USDC', 'DAI']
  hops: number;              // segments.length
}
```

## Integration with External Data Sources

The input `pairs` must be in `RobustPairEdge[]` format (`[TokenA, TokenB, ProtocolKey]`). This data should come from your DEX/GraphQL parser. Example sources:

- **The Graph**: Subgraph queries for Uniswap, Quickswap, etc.
- **DEX APIs**: Direct API calls to DEX protocols
- **On-chain scanning**: Direct contract reads for pool discovery

## License

UNLICENSED - Proprietary
