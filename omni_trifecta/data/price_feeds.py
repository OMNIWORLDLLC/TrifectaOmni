"""Price feed adapters for various data sources."""

from typing import Iterator, Optional
import time
from datetime import datetime


class PriceFeedAdapter:
    """Base class for price feed adapters."""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
    
    def __iter__(self) -> Iterator[float]:
        """Return iterator for price stream."""
        raise NotImplementedError


class MT5PriceFeedAdapter(PriceFeedAdapter):
    """MetaTrader 5 price feed adapter.
    
    Connects to MT5 terminal and yields mid-prices from bid/ask.
    """
    
    def __init__(self, symbol: str, poll_interval: float = 1.0):
        """Initialize MT5 adapter.
        
        Args:
            symbol: Trading symbol (e.g., "EURUSD")
            poll_interval: Polling interval in seconds
        """
        super().__init__(symbol)
        self.poll_interval = poll_interval
        self._mt5 = None
    
    def _initialize_mt5(self):
        """Initialize MT5 connection (lazy loading)."""
        if self._mt5 is None:
            try:
                import MetaTrader5 as MT5
                self._mt5 = MT5
                if not self._mt5.initialize():
                    raise RuntimeError("MT5 initialization failed")
            except ImportError:
                raise ImportError("MetaTrader5 package not installed")
    
    def __iter__(self) -> Iterator[float]:
        """Yield mid-prices from MT5.
        
        Yields:
            Mid-price (average of bid and ask)
        """
        self._initialize_mt5()
        
        while True:
            try:
                tick = self._mt5.symbol_info_tick(self.symbol)
                if tick:
                    mid_price = (tick.bid + tick.ask) / 2.0
                    yield mid_price
                time.sleep(self.poll_interval)
            except Exception as e:
                print(f"MT5 feed error: {e}")
                time.sleep(self.poll_interval)


class BinancePriceFeedAdapter(PriceFeedAdapter):
    """Binance WebSocket price feed adapter.
    
    Connects to Binance WebSocket and yields latest trade prices.
    """
    
    def __init__(self, symbol: str):
        """Initialize Binance adapter.
        
        Args:
            symbol: Trading symbol (e.g., "BTCUSDT")
        """
        super().__init__(symbol)
        self._latest_price = None
    
    def __iter__(self) -> Iterator[float]:
        """Yield prices from Binance WebSocket.
        
        Yields:
            Latest trade price
        """
        try:
            import asyncio
            import websockets
            import json
        except ImportError:
            raise ImportError("websockets package not installed")
        
        async def price_stream():
            url = f"wss://stream.binance.com:9443/ws/{self.symbol.lower()}@trade"
            async with websockets.connect(url) as ws:
                while True:
                    try:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        self._latest_price = float(data["p"])
                        yield self._latest_price
                    except Exception as e:
                        print(f"Binance feed error: {e}")
                        await asyncio.sleep(1)
        
        # For synchronous interface, we use polling
        # In production, this should run in an async context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        gen = price_stream()
        while True:
            try:
                price = loop.run_until_complete(gen.__anext__())
                yield price
            except StopAsyncIteration:
                break


class SimulatedPriceFeedAdapter(PriceFeedAdapter):
    """Simulated price feed for testing and backtesting.
    
    Generates prices from a pre-loaded list or synthetic data.
    """
    
    def __init__(self, symbol: str, prices: list[float], delay: float = 0.1):
        """Initialize simulated adapter.
        
        Args:
            symbol: Trading symbol
            prices: List of historical prices
            delay: Delay between prices in seconds
        """
        super().__init__(symbol)
        self.prices = prices
        self.delay = delay
    
    def __iter__(self) -> Iterator[float]:
        """Yield prices from pre-loaded list.
        
        Yields:
            Price from historical data
        """
        for price in self.prices:
            yield price
            if self.delay > 0:
                time.sleep(self.delay)


def mt5_price_feed_iter(symbol: str, poll_interval: float = 1.0) -> Iterator[float]:
    """Convenience function for MT5 price feed.
    
    Args:
        symbol: Trading symbol
        poll_interval: Polling interval in seconds
    
    Yields:
        Mid-prices from MT5
    """
    adapter = MT5PriceFeedAdapter(symbol, poll_interval)
    yield from adapter


def binance_price_feed_iter(symbol: str) -> Iterator[float]:
    """Convenience function for Binance price feed.
    
    Args:
        symbol: Trading symbol
    
    Yields:
        Trade prices from Binance
    """
    adapter = BinancePriceFeedAdapter(symbol)
    yield from adapter
