"""Price feed adapters for various data sources."""

from typing import Iterator, Optional, Dict, Any
import time
from datetime import datetime
import asyncio
import json


class PriceFeedAdapter:
    """Base class for price feed adapters."""
    
    def __init__(self, symbol: str):
        """Initialize price feed adapter.
        
        Args:
            symbol: Trading symbol to get prices for
        """
        self.symbol = symbol
    
    def __iter__(self) -> Iterator[float]:
        """Return iterator for price stream.
        
        Yields:
            Price values as they become available
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement __iter__")


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


class CCXTPriceFeedAdapter(PriceFeedAdapter):
    """Universal exchange price feed using CCXT library.
    
    Supports 100+ exchanges with unified interface.
    """
    
    def __init__(self, exchange_id: str, symbol: str, poll_interval: float = 1.0):
        """Initialize CCXT adapter.
        
        Args:
            exchange_id: Exchange ID (e.g., 'binance', 'kraken', 'coinbase')
            symbol: Trading symbol in CCXT format (e.g., 'BTC/USDT')
            poll_interval: Polling interval in seconds
        """
        super().__init__(symbol)
        self.exchange_id = exchange_id
        self.poll_interval = poll_interval
        self._exchange = None
    
    def _initialize_exchange(self):
        """Initialize exchange connection."""
        if self._exchange is None:
            try:
                import ccxt
                exchange_class = getattr(ccxt, self.exchange_id)
                self._exchange = exchange_class({
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'}
                })
            except ImportError:
                raise ImportError("ccxt package not installed")
            except AttributeError:
                raise ValueError(f"Exchange '{self.exchange_id}' not supported by CCXT")
    
    def __iter__(self) -> Iterator[float]:
        """Yield prices from exchange via CCXT.
        
        Yields:
            Last trade price
        """
        self._initialize_exchange()
        
        while True:
            try:
                ticker = self._exchange.fetch_ticker(self.symbol)
                price = ticker['last']
                if price:
                    yield float(price)
                time.sleep(self.poll_interval)
            except Exception as e:
                print(f"CCXT feed error for {self.exchange_id}/{self.symbol}: {e}")
                time.sleep(self.poll_interval * 2)


class AlpacaPriceFeedAdapter(PriceFeedAdapter):
    """Alpaca Markets price feed adapter for stocks and crypto."""
    
    def __init__(self, symbol: str, api_key: str, api_secret: str, feed_type: str = "iex"):
        """Initialize Alpaca adapter.
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'BTCUSD')
            api_key: Alpaca API key
            api_secret: Alpaca API secret
            feed_type: Data feed ('iex' or 'sip')
        """
        super().__init__(symbol)
        self.api_key = api_key
        self.api_secret = api_secret
        self.feed_type = feed_type
        self._session = None
    
    def _initialize_session(self):
        """Initialize HTTP session."""
        if self._session is None:
            try:
                import requests
                self._session = requests.Session()
                self._session.headers.update({
                    'APCA-API-KEY-ID': self.api_key,
                    'APCA-API-SECRET-KEY': self.api_secret
                })
            except ImportError:
                raise ImportError("requests package not installed")
    
    def __iter__(self) -> Iterator[float]:
        """Yield prices from Alpaca.
        
        Yields:
            Last trade price
        """
        self._initialize_session()
        
        base_url = "https://data.alpaca.markets/v2"
        endpoint = f"{base_url}/stocks/{self.symbol}/trades/latest"
        
        while True:
            try:
                response = self._session.get(endpoint, params={'feed': self.feed_type})
                if response.status_code == 200:
                    data = response.json()
                    price = data['trade']['p']
                    yield float(price)
                time.sleep(1.0)
            except Exception as e:
                print(f"Alpaca feed error for {self.symbol}: {e}")
                time.sleep(2.0)


class ForexComPriceFeedAdapter(PriceFeedAdapter):
    """Forex.com (FXCM) price feed adapter."""
    
    def __init__(self, symbol: str, access_token: str):
        """Initialize Forex.com adapter.
        
        Args:
            symbol: Currency pair (e.g., 'EUR/USD')
            access_token: Forex.com API access token
        """
        super().__init__(symbol)
        self.access_token = access_token
        self._session = None
    
    def _initialize_session(self):
        """Initialize HTTP session."""
        if self._session is None:
            try:
                import requests
                self._session = requests.Session()
                self._session.headers.update({
                    'Authorization': f'Bearer {self.access_token}',
                    'Content-Type': 'application/json'
                })
            except ImportError:
                raise ImportError("requests package not installed")
    
    def __iter__(self) -> Iterator[float]:
        """Yield prices from Forex.com.
        
        Yields:
            Mid price (bid + ask) / 2
        """
        self._initialize_session()
        
        base_url = "https://api-demo.fxcm.com"
        endpoint = f"{base_url}/prices/{self.symbol}"
        
        while True:
            try:
                response = self._session.get(endpoint)
                if response.status_code == 200:
                    data = response.json()
                    bid = float(data['bid'])
                    ask = float(data['ask'])
                    mid_price = (bid + ask) / 2.0
                    yield mid_price
                time.sleep(0.5)
            except Exception as e:
                print(f"Forex.com feed error for {self.symbol}: {e}")
                time.sleep(2.0)


class OandaPriceFeedAdapter(PriceFeedAdapter):
    """Oanda price feed adapter for forex trading."""
    
    def __init__(self, symbol: str, api_key: str, account_id: str, practice: bool = True):
        """Initialize Oanda adapter.
        
        Args:
            symbol: Currency pair (e.g., 'EUR_USD')
            api_key: Oanda API key
            account_id: Oanda account ID
            practice: Use practice (demo) account
        """
        super().__init__(symbol)
        self.api_key = api_key
        self.account_id = account_id
        self.practice = practice
        self._session = None
    
    def _initialize_session(self):
        """Initialize HTTP session."""
        if self._session is None:
            try:
                import requests
                self._session = requests.Session()
                self._session.headers.update({
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                })
            except ImportError:
                raise ImportError("requests package not installed")
    
    def __iter__(self) -> Iterator[float]:
        """Yield prices from Oanda.
        
        Yields:
            Mid price
        """
        self._initialize_session()
        
        base_url = "https://api-fxpractice.oanda.com" if self.practice else "https://api-fxtrade.oanda.com"
        endpoint = f"{base_url}/v3/accounts/{self.account_id}/pricing"
        
        while True:
            try:
                response = self._session.get(endpoint, params={'instruments': self.symbol})
                if response.status_code == 200:
                    data = response.json()
                    if data['prices']:
                        price_data = data['prices'][0]
                        bid = float(price_data['bids'][0]['price'])
                        ask = float(price_data['asks'][0]['price'])
                        mid_price = (bid + ask) / 2.0
                        yield mid_price
                time.sleep(0.5)
            except Exception as e:
                print(f"Oanda feed error for {self.symbol}: {e}")
                time.sleep(2.0)


class PolygonIOPriceFeedAdapter(PriceFeedAdapter):
    """Polygon.io price feed adapter for stocks, forex, and crypto."""
    
    def __init__(self, symbol: str, api_key: str, market_type: str = "stocks"):
        """Initialize Polygon.io adapter.
        
        Args:
            symbol: Trading symbol (e.g., 'AAPL', 'C:EURUSD', 'X:BTCUSD')
            api_key: Polygon.io API key
            market_type: Market type ('stocks', 'forex', 'crypto')
        """
        super().__init__(symbol)
        self.api_key = api_key
        self.market_type = market_type
        self._session = None
    
    def _initialize_session(self):
        """Initialize HTTP session."""
        if self._session is None:
            try:
                import requests
                self._session = requests.Session()
            except ImportError:
                raise ImportError("requests package not installed")
    
    def __iter__(self) -> Iterator[float]:
        """Yield prices from Polygon.io.
        
        Yields:
            Last trade price
        """
        self._initialize_session()
        
        base_url = "https://api.polygon.io"
        endpoint = f"{base_url}/v2/last/trade/{self.symbol}"
        
        while True:
            try:
                response = self._session.get(endpoint, params={'apiKey': self.api_key})
                if response.status_code == 200:
                    data = response.json()
                    if data['status'] == 'success':
                        price = data['results']['p']
                        yield float(price)
                time.sleep(1.0)
            except Exception as e:
                print(f"Polygon.io feed error for {self.symbol}: {e}")
                time.sleep(2.0)


def create_price_feed(
    source: str,
    symbol: str,
    config: Optional[Dict[str, Any]] = None
) -> PriceFeedAdapter:
    """Factory function to create appropriate price feed adapter.
    
    Args:
        source: Data source ('binance', 'ccxt', 'alpaca', 'oanda', 'polygon', etc.)
        symbol: Trading symbol
        config: Additional configuration parameters
    
    Returns:
        Price feed adapter instance
    """
    config = config or {}
    
    if source == "simulated":
        return SimulatedPriceFeedAdapter(
            symbol=symbol,
            prices=config.get('prices', []),
            delay=config.get('delay', 0.1)
        )
    
    elif source == "binance":
        return BinancePriceFeedAdapter(symbol)
    
    elif source == "ccxt":
        return CCXTPriceFeedAdapter(
            exchange_id=config.get('exchange_id', 'binance'),
            symbol=symbol,
            poll_interval=config.get('poll_interval', 1.0)
        )
    
    elif source == "alpaca":
        return AlpacaPriceFeedAdapter(
            symbol=symbol,
            api_key=config['api_key'],
            api_secret=config['api_secret'],
            feed_type=config.get('feed_type', 'iex')
        )
    
    elif source == "oanda":
        return OandaPriceFeedAdapter(
            symbol=symbol,
            api_key=config['api_key'],
            account_id=config['account_id'],
            practice=config.get('practice', True)
        )
    
    elif source == "polygon":
        return PolygonIOPriceFeedAdapter(
            symbol=symbol,
            api_key=config['api_key'],
            market_type=config.get('market_type', 'stocks')
        )
    
    elif source == "forex_com":
        return ForexComPriceFeedAdapter(
            symbol=symbol,
            access_token=config['access_token']
        )
    
    elif source == "mt5":
        return MT5PriceFeedAdapter(
            symbol=symbol,
            poll_interval=config.get('poll_interval', 1.0)
        )
    
    else:
        raise ValueError(f"Unknown price feed source: {source}")

