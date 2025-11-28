/**
 * OMNIARB Route Matrix Module
 *
 * Mainnet-production route matrix precomputation and persistent store.
 * Designed for OMNIARB FULL MATRIX implementation with protocol-aware routing.
 */

// Core route matrix builder
export {
  // Types
  TokenSymbol,
  ProtocolKey,
  RobustPairEdge,
  RouteSegment,
  RobustRoute,
  RouteMatrixOutput,

  // Core functions
  buildAllRoutes,
  buildAndPersistRouteMatrix,

  // Index and filter utilities
  buildRouteIndex,
  filterRoutesByDestination,
  filterRoutesByHops,
  filterRoutesByProtocol,
  getUniqueProtocols,
  findCyclicRoutes,
  buildArbitrageRoutes
} from './mainnetRouteMatrixBuilder';

// Sample mainnet data (Polygon)
export {
  MAINNET_TOKENS,
  MAINNET_PAIRS,
  PROTOCOLS,
  getTokenSymbols,
  getTokenAddress,
  getPairsByProtocol,
  getPairsForToken
} from './data/mainnet_source';
