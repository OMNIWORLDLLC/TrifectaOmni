/**
 * MAINNET-PRODUCTION: Full-Scale Route Matrix Precomputation & Persistent Store
 *
 * This module is designed for OMNIARB FULL MATRIX implementation. It finds all non-cyclic
 * 2–4-hop routes, attaching the protocol (DEX/Bridge) used for each segment, which is
 * critical for transaction encoding (OMNIARB Decoder/Executor).
 *
 * - Max Hops: 4 (Optimized for performance against combinatorial explosion).
 * - Output: RobustRoute[] includes protocol/router information per segment.
 */

import fs from 'fs';

// =====================================
// PART 1: ENHANCED TYPES FOR OMNIARB EXECUTION
// =====================================

export type TokenSymbol = string;
export type ProtocolKey = string; // e.g., 'QUICKSWAP', 'UNISWAPV3', 'SYNAPSE'

/**
 * Augmented PairEdge: Input must now include the Protocol key for the specific pool/router.
 * Example: ['USDC', 'WETH', 'UNISWAPV3']
 */
export type RobustPairEdge = [TokenSymbol, TokenSymbol, ProtocolKey];

/** Defines one segment (one swap) of a multi-hop route. */
export interface RouteSegment {
  tokenIn: TokenSymbol;
  tokenOut: TokenSymbol;
  protocol: ProtocolKey; // DEX or Bridge used for this hop
  // NOTE: For full execution, you may add 'poolAddress' or 'feeTier' here later.
}

/** The final, executable route structure. */
export interface RobustRoute {
  segments: RouteSegment[]; // The array of swaps (actionable for the executor)
  path: TokenSymbol[];      // Simple token sequence: ['WETH', 'USDC', 'DAI']
  hops: number;             // segments.length
}

/** Output structure for the route matrix. */
export interface RouteMatrixOutput {
  chain: string;
  timestamp: number;
  tokenCount: number;
  pairCount: number;
  routeCount: number;
  routes: RobustRoute[];
}

// =====================================
// PART 2: CORE LOGIC (PROTOCOL-AWARE DFS)
// =====================================

/**
 * Dynamic, Protocol-Aware Adjacency Constructor
 * Maps TokenA -> {TokenB: Set<ProtocolKey>}
 */
function buildAdjacency(
  tokens: TokenSymbol[],
  pairs: RobustPairEdge[]
): Map<TokenSymbol, Map<TokenSymbol, Set<ProtocolKey>>> {

  const adjacency = new Map<TokenSymbol, Map<TokenSymbol, Set<ProtocolKey>>>();
  for (const t of tokens) adjacency.set(t, new Map());

  for (const [a, b, protocol] of pairs) {
    // Helper to get or create the map for neighbors
    const getOrCreate = (map: Map<TokenSymbol, Set<ProtocolKey>>, key: TokenSymbol) => {
      if (!map.has(key)) map.set(key, new Set());
      return map.get(key)!;
    };

    // A -> B
    const aNeighbors = adjacency.get(a);
    if (aNeighbors) {
      getOrCreate(aNeighbors, b).add(protocol);
    }

    // B -> A (assuming pools are bi-directional for AMM swaps)
    const bNeighbors = adjacency.get(b);
    if (bNeighbors) {
      getOrCreate(bNeighbors, a).add(protocol);
    }
  }
  return adjacency;
}

/**
 * Route engine: finds all non-cyclic 2–N hop RobustRoutes
 *
 * @param tokens - Array of token symbols in the universe
 * @param pairs - Array of RobustPairEdge containing [TokenA, TokenB, ProtocolKey]
 * @param maxHops - Maximum number of hops (default: 4)
 * @returns Array of RobustRoute objects
 */
export function buildAllRoutes(
  tokens: TokenSymbol[],
  pairs: RobustPairEdge[], // MUST now contain the ProtocolKey
  maxHops = 4
): RobustRoute[] {
  const graph = buildAdjacency(tokens, pairs);
  const out: RobustRoute[] = [];

  function recurse(
    path: TokenSymbol[],
    segments: RouteSegment[],
    visited: Set<TokenSymbol>
  ) {
    const L = path.length;

    // Route validity: path has 2+ tokens means 1+ hops (segments)
    // A path of L tokens has L-1 segments/hops
    // We allow up to maxHops segments, which means up to maxHops+1 tokens
    if (L >= 2 && L <= maxHops + 1) {
      out.push({
        path: [...path],
        segments: [...segments],
        hops: L - 1
      });
    }

    // Max hop guard
    if (L === maxHops + 1) return;

    const last = path[L - 1];
    const neighbors = graph.get(last) ?? new Map();

    for (const [next, protocols] of neighbors.entries()) {
      if (!visited.has(next)) {

        // --- KEY OPTIMIZATION: Trace all available protocols for this hop ---
        for (const protocol of protocols) {
          const newSegment: RouteSegment = {
            tokenIn: last,
            tokenOut: next,
            protocol: protocol
          };

          // DFS Recursion
          visited.add(next);
          recurse(
            [...path, next],
            [...segments, newSegment],
            visited
          );
          visited.delete(next); // Backtrack
        }
      }
    }
  }

  // Start the DFS from every token in the universe
  for (const t of tokens) recurse([t], [], new Set([t]));
  return out;
}


// =====================================
// PART 3: ORCHESTRATOR AND PERSISTENCE
// =====================================

/**
 * Main orchestrator: loads a universe, builds, and saves to disk
 *
 * @param chainKey - Chain identifier (e.g., 'polygon', 'ethereum')
 * @param tokens - Array of token symbols
 * @param pairs - Array of RobustPairEdge
 * @param maxHops - Maximum hops (default: 4)
 * @param targetFile - Output file path (default: routes.{chainKey}.json)
 * @returns RouteMatrixOutput or null if inputs are empty
 */
export async function buildAndPersistRouteMatrix(
  chainKey: string,
  tokens: TokenSymbol[],
  pairs: RobustPairEdge[], // Updated to accept RobustPairEdge
  maxHops = 4,
  targetFile = `routes.${chainKey}.json` // Simplified target file name
): Promise<RouteMatrixOutput | null> {
  if (tokens.length === 0 || pairs.length === 0) {
    console.warn(`[${chainKey}] WARNING: Token or pair list is empty. Skipping matrix build.`);
    return null;
  }

  console.time(`[${chainKey}] Route Matrix Build`);
  const routes = buildAllRoutes(tokens, pairs, maxHops);

  const output: RouteMatrixOutput = {
    chain: chainKey,
    timestamp: Date.now(),
    tokenCount: tokens.length,
    pairCount: pairs.length,
    routeCount: routes.length,
    routes
  };

  // --- PRODUCTION GUARD: Atomic Write ---
  // Write to a temporary file first, then rename it to the target file.
  const tempFile = `${targetFile}.tmp.${Date.now()}`;
  fs.writeFileSync(tempFile, JSON.stringify(output, null, 2));
  fs.renameSync(tempFile, targetFile);

  console.timeEnd(`[${chainKey}] Route Matrix Build`);
  console.log(`[${chainKey}] Matrix saved: ${targetFile} with ${routes.length} routes.`);

  return output;
}

// =====================================
// PART 4: HIGH-PERFORMANCE IN-MEMORY INDEX
// =====================================

/**
 * In-memory indexed map for rapid API/routing lookup
 * Index routes by source token for O(1) lookup of all routes originating from a token.
 *
 * @param routes - Array of RobustRoute objects
 * @returns Map indexed by source token symbol
 */
export function buildRouteIndex(
  routes: RobustRoute[]
): Map<TokenSymbol, RobustRoute[]> {
  const index = new Map<TokenSymbol, RobustRoute[]>();
  for (const r of routes) {
    const src = r.path[0];
    if (!index.has(src)) index.set(src, []);
    index.get(src)!.push(r);
  }
  return index;
}

/**
 * Filter routes by destination token
 *
 * @param routes - Array of RobustRoute objects
 * @param destination - Target token symbol
 * @returns Filtered array of routes ending at destination
 */
export function filterRoutesByDestination(
  routes: RobustRoute[],
  destination: TokenSymbol
): RobustRoute[] {
  return routes.filter(r => r.path[r.path.length - 1] === destination);
}

/**
 * Filter routes by hop count
 *
 * @param routes - Array of RobustRoute objects
 * @param hops - Exact number of hops to filter by
 * @returns Filtered array of routes with specified hop count
 */
export function filterRoutesByHops(
  routes: RobustRoute[],
  hops: number
): RobustRoute[] {
  return routes.filter(r => r.hops === hops);
}

/**
 * Filter routes by protocol
 *
 * @param routes - Array of RobustRoute objects
 * @param protocol - Protocol key to filter by
 * @returns Routes that use the specified protocol in at least one segment
 */
export function filterRoutesByProtocol(
  routes: RobustRoute[],
  protocol: ProtocolKey
): RobustRoute[] {
  return routes.filter(r =>
    r.segments.some(s => s.protocol === protocol)
  );
}

/**
 * Get all unique protocols used in routes
 *
 * @param routes - Array of RobustRoute objects
 * @returns Set of unique protocol keys
 */
export function getUniqueProtocols(routes: RobustRoute[]): Set<ProtocolKey> {
  const protocols = new Set<ProtocolKey>();
  for (const r of routes) {
    for (const s of r.segments) {
      protocols.add(s.protocol);
    }
  }
  return protocols;
}

/**
 * Find cyclic (arbitrage) routes that start and end at the same token
 *
 * @param routes - Array of RobustRoute objects
 * @returns Routes where path[0] === path[path.length - 1]
 */
export function findCyclicRoutes(routes: RobustRoute[]): RobustRoute[] {
  return routes.filter(r => r.path[0] === r.path[r.path.length - 1]);
}

/**
 * Build cyclic arbitrage routes from token universe
 * These are routes that start and end at the same token (true arbitrage loops)
 *
 * @param tokens - Array of token symbols
 * @param pairs - Array of RobustPairEdge
 * @param maxHops - Maximum hops (default: 4)
 * @returns Array of cyclic RobustRoute objects
 */
export function buildArbitrageRoutes(
  tokens: TokenSymbol[],
  pairs: RobustPairEdge[],
  maxHops = 4
): RobustRoute[] {
  const graph = buildAdjacency(tokens, pairs);
  const out: RobustRoute[] = [];

  function recurse(
    startToken: TokenSymbol,
    path: TokenSymbol[],
    segments: RouteSegment[],
    visited: Set<TokenSymbol>
  ) {
    const L = path.length;
    const last = path[L - 1];
    const neighbors = graph.get(last) ?? new Map();

    // Check if we can complete the cycle back to start
    if (L >= 2 && L <= maxHops) {
      const backToStart = neighbors.get(startToken);
      if (backToStart) {
        for (const protocol of backToStart) {
          const closingSegment: RouteSegment = {
            tokenIn: last,
            tokenOut: startToken,
            protocol
          };
          out.push({
            path: [...path, startToken],
            segments: [...segments, closingSegment],
            hops: segments.length + 1  // Adding one closing segment to complete the cycle
          });
        }
      }
    }

    // Max hop guard (need room for at least one more step back)
    if (L >= maxHops) return;

    for (const [next, protocols] of neighbors.entries()) {
      if (!visited.has(next)) {
        for (const protocol of protocols) {
          const newSegment: RouteSegment = {
            tokenIn: last,
            tokenOut: next,
            protocol
          };

          visited.add(next);
          recurse(
            startToken,
            [...path, next],
            [...segments, newSegment],
            visited
          );
          visited.delete(next);
        }
      }
    }
  }

  // Start from every token
  for (const t of tokens) {
    recurse(t, [t], [], new Set([t]));
  }

  return out;
}
