"""Utility functions for technical analysis and calculations."""

import numpy as np
from typing import List, Dict


def fibonacci_retracements(high: float, low: float) -> Dict[str, float]:
    """Calculate Fibonacci retracement levels.
    
    Args:
        high: High price
        low: Low price
    
    Returns:
        Dictionary of Fibonacci levels
    """
    diff = high - low
    return {
        "0.0": high,
        "0.236": high - diff * 0.236,
        "0.382": high - diff * 0.382,
        "0.500": high - diff * 0.500,
        "0.618": high - diff * 0.618,
        "0.786": high - diff * 0.786,
        "1.0": low,
    }


def fibonacci_extensions(high: float, low: float) -> Dict[str, float]:
    """Calculate Fibonacci extension levels.
    
    Args:
        high: High price
        low: Low price
    
    Returns:
        Dictionary of Fibonacci extension levels
    """
    diff = high - low
    return {
        "1.272": high + diff * 0.272,
        "1.414": high + diff * 0.414,
        "1.618": high + diff * 0.618,
        "2.000": high + diff * 1.000,
        "2.618": high + diff * 1.618,
    }


def atr_adjusted_zone(price: float, atr: float, multiplier: float = 1.0) -> tuple[float, float]:
    """Calculate ATR-adjusted support/resistance zone.
    
    Args:
        price: Current price
        atr: Average True Range
        multiplier: ATR multiplier for zone width
    
    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    zone_width = atr * multiplier
    return price - zone_width, price + zone_width


def calculate_atr(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> float:
    """Calculate Average True Range.
    
    Args:
        highs: List of high prices
        lows: List of low prices
        closes: List of close prices
        period: ATR period
    
    Returns:
        ATR value
    """
    if len(highs) < period or len(lows) < period or len(closes) < period:
        return 0.0
    
    true_ranges = []
    for i in range(1, len(highs)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i-1]),
            abs(lows[i] - closes[i-1])
        )
        true_ranges.append(tr)
    
    if len(true_ranges) < period:
        return 0.0
    
    return float(np.mean(true_ranges[-period:]))


def detect_swing_points(prices: List[float], window: int = 5) -> List[tuple[int, float, str]]:
    """Detect swing high and low points.
    
    Args:
        prices: List of prices
        window: Window size for swing detection
    
    Returns:
        List of tuples (index, price, type) where type is 'HIGH' or 'LOW'
    """
    if len(prices) < window * 2 + 1:
        return []
    
    swings = []
    
    for i in range(window, len(prices) - window):
        # Check for swing high
        is_high = all(prices[i] >= prices[i-j] for j in range(1, window+1))
        is_high = is_high and all(prices[i] >= prices[i+j] for j in range(1, window+1))
        
        if is_high:
            swings.append((i, prices[i], 'HIGH'))
            continue
        
        # Check for swing low
        is_low = all(prices[i] <= prices[i-j] for j in range(1, window+1))
        is_low = is_low and all(prices[i] <= prices[i+j] for j in range(1, window+1))
        
        if is_low:
            swings.append((i, prices[i], 'LOW'))
    
    return swings


def calculate_momentum(prices: List[float], period: int = 14) -> float:
    """Calculate momentum indicator.
    
    Args:
        prices: List of prices
        period: Momentum period
    
    Returns:
        Momentum value
    """
    if len(prices) < period + 1:
        return 0.0
    
    return prices[-1] - prices[-period-1]


def normalize_prices(prices: List[float]) -> List[float]:
    """Normalize prices to [0, 1] range.
    
    Args:
        prices: List of prices
    
    Returns:
        Normalized prices
    """
    if len(prices) == 0:
        return []
    
    min_price = min(prices)
    max_price = max(prices)
    
    if max_price == min_price:
        return [0.5] * len(prices)
    
    return [(p - min_price) / (max_price - min_price) for p in prices]
