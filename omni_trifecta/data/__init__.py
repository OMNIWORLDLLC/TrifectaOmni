"""Data ingestion and normalization components."""

from .price_feeds import (
    PriceFeedAdapter,
    MT5PriceFeedAdapter,
    BinancePriceFeedAdapter,
    SimulatedPriceFeedAdapter,
    CCXTPriceFeedAdapter,
    AlpacaPriceFeedAdapter,
    ForexComPriceFeedAdapter,
    OandaPriceFeedAdapter,
    PolygonIOPriceFeedAdapter,
    mt5_price_feed_iter,
    binance_price_feed_iter,
    create_price_feed,
)

__all__ = [
    "PriceFeedAdapter",
    "MT5PriceFeedAdapter",
    "BinancePriceFeedAdapter",
    "SimulatedPriceFeedAdapter",
    "CCXTPriceFeedAdapter",
    "AlpacaPriceFeedAdapter",
    "ForexComPriceFeedAdapter",
    "OandaPriceFeedAdapter",
    "PolygonIOPriceFeedAdapter",
    "mt5_price_feed_iter",
    "binance_price_feed_iter",
    "create_price_feed",
]
