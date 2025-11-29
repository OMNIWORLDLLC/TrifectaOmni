/**
 * Tests for mainnetRouteMatrixBuilder
 */

import fs from 'fs';
import os from 'os';
import path from 'path';
import {
  buildAllRoutes,
  buildAndPersistRouteMatrix,
  buildRouteIndex,
  filterRoutesByDestination,
  filterRoutesByHops,
  filterRoutesByProtocol,
  getUniqueProtocols,
  findCyclicRoutes,
  buildArbitrageRoutes,
  RobustPairEdge
} from './mainnetRouteMatrixBuilder';

describe('mainnetRouteMatrixBuilder', () => {
  // Sample test data
  const testTokens = ['WMATIC', 'USDC', 'WETH', 'DAI'];
  const testPairs: RobustPairEdge[] = [
    ['WMATIC', 'USDC', 'QUICKSWAP'],
    ['WMATIC', 'USDC', 'UNISWAP_V3'],
    ['WMATIC', 'WETH', 'QUICKSWAP'],
    ['USDC', 'WETH', 'QUICKSWAP'],
    ['USDC', 'DAI', 'CURVE'],
    ['WETH', 'DAI', 'SUSHISWAP']
  ];

  describe('buildAllRoutes', () => {
    it('should build routes from tokens and pairs', () => {
      const routes = buildAllRoutes(testTokens, testPairs, 4);

      expect(routes).toBeDefined();
      expect(Array.isArray(routes)).toBe(true);
      expect(routes.length).toBeGreaterThan(0);
    });

    it('should respect maxHops parameter', () => {
      const routes2Hop = buildAllRoutes(testTokens, testPairs, 2);
      const routes4Hop = buildAllRoutes(testTokens, testPairs, 4);

      // All 2-hop routes should have at most 2 hops
      for (const route of routes2Hop) {
        expect(route.hops).toBeLessThanOrEqual(2);
      }

      // 4-hop should have more routes
      expect(routes4Hop.length).toBeGreaterThanOrEqual(routes2Hop.length);
    });

    it('should generate non-cyclic routes', () => {
      const routes = buildAllRoutes(testTokens, testPairs, 4);

      for (const route of routes) {
        // Check for unique tokens in path (non-cyclic)
        const uniqueTokens = new Set(route.path);
        expect(uniqueTokens.size).toBe(route.path.length);
      }
    });

    it('should include protocol information in segments', () => {
      const routes = buildAllRoutes(testTokens, testPairs, 4);

      for (const route of routes) {
        for (const segment of route.segments) {
          expect(segment.tokenIn).toBeDefined();
          expect(segment.tokenOut).toBeDefined();
          expect(segment.protocol).toBeDefined();
          expect(typeof segment.protocol).toBe('string');
        }
      }
    });

    it('should correctly set hops count', () => {
      const routes = buildAllRoutes(testTokens, testPairs, 4);

      for (const route of routes) {
        expect(route.hops).toBe(route.segments.length);
        expect(route.hops).toBe(route.path.length - 1);
      }
    });

    it('should handle bi-directional pairs', () => {
      const routes = buildAllRoutes(testTokens, testPairs, 2);

      // Should have routes in both directions
      const hasWmaticToUsdc = routes.some(
        r => r.path[0] === 'WMATIC' && r.path[1] === 'USDC'
      );
      const hasUsdcToWmatic = routes.some(
        r => r.path[0] === 'USDC' && r.path[1] === 'WMATIC'
      );

      expect(hasWmaticToUsdc).toBe(true);
      expect(hasUsdcToWmatic).toBe(true);
    });

    it('should generate routes for each protocol variant', () => {
      const routes = buildAllRoutes(testTokens, testPairs, 1);

      // WMATIC-USDC has two protocols: QUICKSWAP and UNISWAP_V3
      const wmaticUsdcRoutes = routes.filter(
        r => r.path[0] === 'WMATIC' && r.path[1] === 'USDC'
      );

      const protocols = new Set(wmaticUsdcRoutes.map(r => r.segments[0].protocol));
      expect(protocols.has('QUICKSWAP')).toBe(true);
      expect(protocols.has('UNISWAP_V3')).toBe(true);
    });

    it('should return empty array for empty inputs', () => {
      const emptyTokens = buildAllRoutes([], testPairs, 4);
      const emptyPairs = buildAllRoutes(testTokens, [], 4);

      expect(emptyTokens).toEqual([]);
      expect(emptyPairs).toEqual([]);
    });
  });

  describe('buildRouteIndex', () => {
    it('should index routes by source token', () => {
      const routes = buildAllRoutes(testTokens, testPairs, 2);
      const index = buildRouteIndex(routes);

      expect(index).toBeDefined();
      expect(index instanceof Map).toBe(true);

      // Each token should have entries
      for (const token of testTokens) {
        expect(index.has(token)).toBe(true);
      }
    });

    it('should provide O(1) lookup by source token', () => {
      const routes = buildAllRoutes(testTokens, testPairs, 2);
      const index = buildRouteIndex(routes);

      const wmaticRoutes = index.get('WMATIC') || [];
      expect(wmaticRoutes.length).toBeGreaterThan(0);

      // All routes should start with WMATIC
      for (const route of wmaticRoutes) {
        expect(route.path[0]).toBe('WMATIC');
      }
    });
  });

  describe('filterRoutesByDestination', () => {
    it('should filter routes by destination token', () => {
      const routes = buildAllRoutes(testTokens, testPairs, 2);
      const usdcRoutes = filterRoutesByDestination(routes, 'USDC');

      expect(usdcRoutes.length).toBeGreaterThan(0);
      for (const route of usdcRoutes) {
        expect(route.path[route.path.length - 1]).toBe('USDC');
      }
    });
  });

  describe('filterRoutesByHops', () => {
    it('should filter routes by exact hop count', () => {
      const routes = buildAllRoutes(testTokens, testPairs, 4);
      const twoHopRoutes = filterRoutesByHops(routes, 2);

      expect(twoHopRoutes.length).toBeGreaterThan(0);
      for (const route of twoHopRoutes) {
        expect(route.hops).toBe(2);
      }
    });
  });

  describe('filterRoutesByProtocol', () => {
    it('should filter routes containing specific protocol', () => {
      const routes = buildAllRoutes(testTokens, testPairs, 2);
      const curveRoutes = filterRoutesByProtocol(routes, 'CURVE');

      expect(curveRoutes.length).toBeGreaterThan(0);
      for (const route of curveRoutes) {
        const hasCurve = route.segments.some(s => s.protocol === 'CURVE');
        expect(hasCurve).toBe(true);
      }
    });
  });

  describe('getUniqueProtocols', () => {
    it('should return all unique protocols', () => {
      const routes = buildAllRoutes(testTokens, testPairs, 2);
      const protocols = getUniqueProtocols(routes);

      expect(protocols.size).toBeGreaterThan(0);
      expect(protocols.has('QUICKSWAP')).toBe(true);
      expect(protocols.has('CURVE')).toBe(true);
    });
  });

  describe('findCyclicRoutes', () => {
    it('should return empty for non-cyclic routes from buildAllRoutes', () => {
      // buildAllRoutes generates non-cyclic routes
      const routes = buildAllRoutes(testTokens, testPairs, 4);
      const cyclic = findCyclicRoutes(routes);

      // Should be empty since buildAllRoutes avoids cycles
      expect(cyclic).toEqual([]);
    });
  });

  describe('buildArbitrageRoutes', () => {
    it('should build cyclic arbitrage routes', () => {
      const arbRoutes = buildArbitrageRoutes(testTokens, testPairs, 4);

      expect(arbRoutes.length).toBeGreaterThan(0);

      for (const route of arbRoutes) {
        // Cyclic: starts and ends at same token
        expect(route.path[0]).toBe(route.path[route.path.length - 1]);
      }
    });

    it('should respect maxHops for arbitrage routes', () => {
      const routes2 = buildArbitrageRoutes(testTokens, testPairs, 2);
      const routes4 = buildArbitrageRoutes(testTokens, testPairs, 4);

      for (const route of routes2) {
        expect(route.hops).toBeLessThanOrEqual(2);
      }

      // More hops = potentially more routes
      expect(routes4.length).toBeGreaterThanOrEqual(routes2.length);
    });

    it('should include protocol in each segment', () => {
      const arbRoutes = buildArbitrageRoutes(testTokens, testPairs, 3);

      for (const route of arbRoutes) {
        for (const segment of route.segments) {
          expect(segment.protocol).toBeDefined();
          expect(typeof segment.protocol).toBe('string');
        }
      }
    });
  });

  describe('buildAndPersistRouteMatrix', () => {
    const tmpDir = os.tmpdir();
    const testFile = path.join(tmpDir, 'test-routes.json');

    afterEach(() => {
      // Cleanup test files
      if (fs.existsSync(testFile)) {
        fs.unlinkSync(testFile);
      }
      // Clean up any temp files
      const files = fs.readdirSync(tmpDir);
      for (const file of files) {
        if (file.startsWith('test-routes.json.tmp.')) {
          fs.unlinkSync(path.join(tmpDir, file));
        }
      }
    });

    it('should persist route matrix to file', async () => {
      const result = await buildAndPersistRouteMatrix(
        'test-chain',
        testTokens,
        testPairs,
        4,
        testFile
      );

      expect(result).toBeDefined();
      expect(result?.chain).toBe('test-chain');
      expect(result?.tokenCount).toBe(testTokens.length);
      expect(result?.pairCount).toBe(testPairs.length);
      expect(result?.routeCount).toBeGreaterThan(0);

      // File should exist
      expect(fs.existsSync(testFile)).toBe(true);

      // File should be valid JSON
      const fileContent = fs.readFileSync(testFile, 'utf-8');
      const parsed = JSON.parse(fileContent);
      expect(parsed.chain).toBe('test-chain');
    });

    it('should return null for empty inputs', async () => {
      const emptyTokenResult = await buildAndPersistRouteMatrix(
        'test-chain',
        [],
        testPairs,
        4,
        testFile
      );
      expect(emptyTokenResult).toBeNull();

      const emptyPairResult = await buildAndPersistRouteMatrix(
        'test-chain',
        testTokens,
        [],
        4,
        testFile
      );
      expect(emptyPairResult).toBeNull();
    });

    it('should use atomic write (no partial files)', async () => {
      await buildAndPersistRouteMatrix(
        'test-chain',
        testTokens,
        testPairs,
        4,
        testFile
      );

      // Check no temp files remain
      const files = fs.readdirSync('/tmp');
      const tempFiles = files.filter(f => f.startsWith('test-routes.json.tmp.'));
      expect(tempFiles.length).toBe(0);
    });
  });
});
