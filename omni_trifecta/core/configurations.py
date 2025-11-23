"""Real-world trading configuration examples.

This file provides production-ready configuration templates for different
trading scenarios and asset classes.
"""

FOREX_OANDA_CONFIG = {
    "data_source": "oanda",
    "broker": "oanda",
    "symbols": ["EUR_USD", "GBP_USD", "USD_JPY"],
    "data_config": {
        "api_key": "YOUR_OANDA_API_KEY",
        "account_id": "YOUR_OANDA_ACCOUNT_ID",
        "practice": True
    },
    "broker_config": {
        "api_key": "YOUR_OANDA_API_KEY",
        "account_id": "YOUR_OANDA_ACCOUNT_ID",
        "practice": True
    },
    "risk_params": {
        "max_position_size": 0.1,
        "max_portfolio_risk": 0.03,
        "max_position_risk": 0.01,
        "max_leverage": 10.0
    },
    "safety": {
        "max_daily_loss": 300.0,
        "max_daily_trades": 20,
        "max_loss_streak": 3
    }
}


CRYPTO_BINANCE_CONFIG = {
    "data_source": "ccxt",
    "broker": "ccxt",
    "symbols": ["BTC/USDT", "ETH/USDT", "BNB/USDT"],
    "data_config": {
        "exchange_id": "binance",
        "poll_interval": 1.0
    },
    "broker_config": {
        "exchange_id": "binance",
        "api_key": "YOUR_BINANCE_API_KEY",
        "api_secret": "YOUR_BINANCE_SECRET",
        "testnet": True
    },
    "risk_params": {
        "max_position_size": 0.2,
        "max_portfolio_risk": 0.05,
        "max_position_risk": 0.02,
        "max_leverage": 3.0
    },
    "safety": {
        "max_daily_loss": 500.0,
        "max_daily_trades": 30,
        "max_loss_streak": 5
    }
}


STOCKS_ALPACA_CONFIG = {
    "data_source": "alpaca",
    "broker": "alpaca",
    "symbols": ["AAPL", "TSLA", "MSFT", "GOOGL"],
    "data_config": {
        "api_key": "YOUR_ALPACA_API_KEY",
        "api_secret": "YOUR_ALPACA_SECRET",
        "feed_type": "iex"
    },
    "broker_config": {
        "api_key": "YOUR_ALPACA_API_KEY",
        "api_secret": "YOUR_ALPACA_SECRET",
        "paper": True
    },
    "risk_params": {
        "max_position_size": 0.15,
        "max_portfolio_risk": 0.04,
        "max_position_risk": 0.015,
        "max_leverage": 1.0
    },
    "safety": {
        "max_daily_loss": 400.0,
        "max_daily_trades": 15,
        "max_loss_streak": 4
    }
}


BINARY_OPTIONS_CONFIG = {
    "data_source": "binance",
    "broker": "binary",
    "symbols": ["EURUSD", "GBPUSD", "USDJPY"],
    "data_config": {},
    "broker_config": {
        "api_token": "YOUR_POCKET_TOKEN",
        "base_url": "https://api.po.trade",
        "platform": "pocket"
    },
    "risk_params": {
        "max_position_size": 0.05,
        "max_portfolio_risk": 0.02,
        "max_position_risk": 0.01,
        "max_leverage": 1.0
    },
    "safety": {
        "max_daily_loss": 200.0,
        "max_daily_trades": 50,
        "max_loss_streak": 5
    },
    "binary_specific": {
        "min_expiry": 60,
        "max_expiry": 300,
        "base_stake": 10.0,
        "max_stake": 100.0,
        "use_ladder_risk": True
    }
}


DEX_ARBITRAGE_CONFIG = {
    "data_source": "ccxt",
    "broker": "web3",
    "symbols": ["WETH", "USDC", "DAI"],
    "data_config": {
        "exchange_id": "uniswap",
        "poll_interval": 2.0
    },
    "broker_config": {
        "rpc_url": "https://YOUR_ETHEREUM_RPC",
        "private_key": "YOUR_PRIVATE_KEY",
        "contract_address": "YOUR_FLASHLOAN_CONTRACT"
    },
    "risk_params": {
        "max_position_size": 0.3,
        "max_portfolio_risk": 0.1,
        "max_position_risk": 0.05,
        "max_leverage": 1.0
    },
    "safety": {
        "max_daily_loss": 1000.0,
        "max_daily_trades": 100,
        "max_loss_streak": 10
    },
    "arb_specific": {
        "min_profit_bps": 30,
        "max_gas_price": 150,
        "slippage_tolerance": 0.005,
        "min_liquidity": 50000
    }
}


MULTI_ASSET_CONFIG = {
    "data_sources": {
        "forex": {
            "source": "oanda",
            "symbols": ["EUR_USD", "GBP_USD"],
            "config": {"api_key": "...", "account_id": "...", "practice": True}
        },
        "crypto": {
            "source": "ccxt",
            "symbols": ["BTC/USDT", "ETH/USDT"],
            "config": {"exchange_id": "binance"}
        },
        "stocks": {
            "source": "alpaca",
            "symbols": ["SPY", "QQQ"],
            "config": {"api_key": "...", "api_secret": "...", "feed_type": "iex"}
        }
    },
    "brokers": {
        "forex": {
            "type": "oanda",
            "config": {"api_key": "...", "account_id": "...", "practice": True}
        },
        "crypto": {
            "type": "ccxt",
            "config": {"exchange_id": "binance", "api_key": "...", "api_secret": "...", "testnet": True}
        },
        "stocks": {
            "type": "alpaca",
            "config": {"api_key": "...", "api_secret": "...", "paper": True}
        }
    },
    "risk_params": {
        "max_position_size": 0.1,
        "max_portfolio_risk": 0.05,
        "max_position_risk": 0.01,
        "max_correlation_exposure": 0.4,
        "max_sector_exposure": 0.3
    },
    "safety": {
        "max_daily_loss": 800.0,
        "max_daily_trades": 40,
        "max_loss_streak": 5
    }
}


CONSERVATIVE_CONFIG = {
    "profile": "conservative",
    "risk_params": {
        "max_position_size": 0.05,
        "max_portfolio_risk": 0.02,
        "max_position_risk": 0.005,
        "max_leverage": 1.0,
        "kelly_fraction": 0.1
    },
    "safety": {
        "max_daily_loss": 100.0,
        "max_daily_trades": 10,
        "max_loss_streak": 2
    },
    "trading_hours": {
        "enabled": True,
        "start": "09:30",
        "end": "16:00",
        "timezone": "America/New_York"
    }
}


AGGRESSIVE_CONFIG = {
    "profile": "aggressive",
    "risk_params": {
        "max_position_size": 0.3,
        "max_portfolio_risk": 0.1,
        "max_position_risk": 0.05,
        "max_leverage": 5.0,
        "kelly_fraction": 0.5
    },
    "safety": {
        "max_daily_loss": 2000.0,
        "max_daily_trades": 100,
        "max_loss_streak": 10
    },
    "trading_hours": {
        "enabled": False
    }
}


BALANCED_CONFIG = {
    "profile": "balanced",
    "risk_params": {
        "max_position_size": 0.15,
        "max_portfolio_risk": 0.04,
        "max_position_risk": 0.02,
        "max_leverage": 2.0,
        "kelly_fraction": 0.25
    },
    "safety": {
        "max_daily_loss": 500.0,
        "max_daily_trades": 30,
        "max_loss_streak": 5
    },
    "trading_hours": {
        "enabled": True,
        "start": "08:00",
        "end": "18:00",
        "timezone": "America/New_York"
    }
}


def get_config(config_name: str) -> dict:
    """Get configuration by name.
    
    Args:
        config_name: Configuration name (e.g., 'forex_oanda', 'crypto_binance')
    
    Returns:
        Configuration dictionary
    """
    configs = {
        'forex_oanda': FOREX_OANDA_CONFIG,
        'crypto_binance': CRYPTO_BINANCE_CONFIG,
        'stocks_alpaca': STOCKS_ALPACA_CONFIG,
        'binary_options': BINARY_OPTIONS_CONFIG,
        'dex_arbitrage': DEX_ARBITRAGE_CONFIG,
        'multi_asset': MULTI_ASSET_CONFIG,
        'conservative': CONSERVATIVE_CONFIG,
        'aggressive': AGGRESSIVE_CONFIG,
        'balanced': BALANCED_CONFIG
    }
    
    return configs.get(config_name, BALANCED_CONFIG)


def merge_configs(*configs) -> dict:
    """Merge multiple configurations.
    
    Args:
        *configs: Configuration dictionaries to merge
    
    Returns:
        Merged configuration
    """
    result = {}
    
    for config in configs:
        for key, value in config.items():
            if isinstance(value, dict) and key in result:
                result[key].update(value)
            else:
                result[key] = value
    
    return result
