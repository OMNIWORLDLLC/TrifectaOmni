"""Advanced technical indicators and market structure analysis."""

import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class MarketStructure:
    """Market structure analysis result."""
    trend: str
    strength: float
    support_levels: List[float]
    resistance_levels: List[float]
    breakout_probability: float
    reversal_probability: float


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """Calculate Exponential Moving Average."""
    if len(prices) < period:
        return []
    
    multiplier = 2.0 / (period + 1)
    ema = [np.mean(prices[:period])]
    
    for price in prices[period:]:
        ema_value = (price - ema[-1]) * multiplier + ema[-1]
        ema.append(ema_value)
    
    return ema


def calculate_rsi(prices: List[float], period: int = 14) -> float:
    """Calculate Relative Strength Index."""
    if len(prices) < period + 1:
        return 50.0
    
    deltas = np.diff(prices[-period-1:])
    gains = deltas[deltas > 0]
    losses = -deltas[deltas < 0]
    
    avg_gain = np.mean(gains) if len(gains) > 0 else 0
    avg_loss = np.mean(losses) if len(losses) > 0 else 0
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    
    return rsi


def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
    """Calculate MACD, signal, and histogram."""
    if len(prices) < slow:
        return 0.0, 0.0, 0.0
    
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    if not ema_fast or not ema_slow:
        return 0.0, 0.0, 0.0
    
    macd_line = ema_fast[-1] - ema_slow[-1]
    
    macd_values = []
    for i in range(min(len(ema_fast), len(ema_slow))):
        macd_values.append(ema_fast[i] - ema_slow[i])
    
    if len(macd_values) < signal:
        return macd_line, 0.0, macd_line
    
    signal_line = np.mean(macd_values[-signal:])
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
    """Calculate Bollinger Bands (upper, middle, lower)."""
    if len(prices) < period:
        return 0.0, 0.0, 0.0
    
    recent = prices[-period:]
    middle = np.mean(recent)
    std = np.std(recent)
    
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    
    return upper, middle, lower


def calculate_stochastic(prices: List[float], high_prices: List[float], low_prices: List[float], period: int = 14) -> Tuple[float, float]:
    """Calculate Stochastic Oscillator (%K, %D)."""
    if len(prices) < period:
        return 50.0, 50.0
    
    recent_high = max(high_prices[-period:]) if high_prices else max(prices[-period:])
    recent_low = min(low_prices[-period:]) if low_prices else min(prices[-period:])
    current_close = prices[-1]
    
    if recent_high == recent_low:
        k = 50.0
    else:
        k = ((current_close - recent_low) / (recent_high - recent_low)) * 100.0
    
    d = k
    
    return k, d


def calculate_williams_r(prices: List[float], high_prices: List[float], low_prices: List[float], period: int = 14) -> float:
    """Calculate Williams %R."""
    if len(prices) < period:
        return -50.0
    
    recent_high = max(high_prices[-period:]) if high_prices else max(prices[-period:])
    recent_low = min(low_prices[-period:]) if low_prices else min(prices[-period:])
    current_close = prices[-1]
    
    if recent_high == recent_low:
        return -50.0
    
    wr = ((recent_high - current_close) / (recent_high - recent_low)) * -100.0
    
    return wr


def calculate_commodity_channel_index(prices: List[float], high_prices: List[float], low_prices: List[float], period: int = 20) -> float:
    """Calculate Commodity Channel Index (CCI)."""
    if len(prices) < period:
        return 0.0
    
    typical_prices = []
    for i in range(-period, 0):
        high = high_prices[i] if high_prices and len(high_prices) > abs(i) else prices[i]
        low = low_prices[i] if low_prices and len(low_prices) > abs(i) else prices[i]
        close = prices[i]
        typical_price = (high + low + close) / 3.0
        typical_prices.append(typical_price)
    
    sma = np.mean(typical_prices)
    mean_deviation = np.mean([abs(tp - sma) for tp in typical_prices])
    
    if mean_deviation == 0:
        return 0.0
    
    cci = (typical_prices[-1] - sma) / (0.015 * mean_deviation)
    
    return cci


def detect_divergence(prices: List[float], indicator_values: List[float], lookback: int = 20) -> str:
    """Detect bullish or bearish divergence.
    
    Returns:
        'bullish', 'bearish', or 'none'
    """
    if len(prices) < lookback or len(indicator_values) < lookback:
        return 'none'
    
    recent_prices = prices[-lookback:]
    recent_indicator = indicator_values[-lookback:]
    
    price_trend = recent_prices[-1] - recent_prices[0]
    indicator_trend = recent_indicator[-1] - recent_indicator[0]
    
    if price_trend < 0 and indicator_trend > 0:
        return 'bullish'
    elif price_trend > 0 and indicator_trend < 0:
        return 'bearish'
    
    return 'none'


def identify_support_resistance(prices: List[float], window: int = 10, threshold: float = 0.001) -> Tuple[List[float], List[float]]:
    """Identify support and resistance levels."""
    if len(prices) < window * 2:
        return [], []
    
    support_levels = []
    resistance_levels = []
    
    for i in range(window, len(prices) - window):
        is_support = True
        is_resistance = True
        
        for j in range(1, window + 1):
            if prices[i] > prices[i - j] or prices[i] > prices[i + j]:
                is_support = False
            if prices[i] < prices[i - j] or prices[i] < prices[i + j]:
                is_resistance = False
        
        if is_support:
            if not support_levels or abs(prices[i] - support_levels[-1]) / prices[i] > threshold:
                support_levels.append(prices[i])
        
        if is_resistance:
            if not resistance_levels or abs(prices[i] - resistance_levels[-1]) / prices[i] > threshold:
                resistance_levels.append(prices[i])
    
    return support_levels, resistance_levels


def calculate_average_directional_index(prices: List[float], high_prices: List[float], low_prices: List[float], period: int = 14) -> float:
    """Calculate Average Directional Index (ADX) for trend strength."""
    # Require 2x period: period for initial DI calculation + period for ADX smoothing
    if len(prices) < period * 2:
        return 0.0
    
    tr_values = []
    plus_dm_values = []
    minus_dm_values = []
    
    for i in range(1, len(prices)):
        high = high_prices[i] if high_prices and len(high_prices) > i else prices[i]
        low = low_prices[i] if low_prices and len(low_prices) > i else prices[i]
        prev_high = high_prices[i-1] if high_prices and len(high_prices) > i-1 else prices[i-1]
        prev_low = low_prices[i-1] if low_prices and len(low_prices) > i-1 else prices[i-1]
        prev_close = prices[i-1]
        
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        tr_values.append(tr)
        
        plus_dm = max(high - prev_high, 0) if (high - prev_high) > (prev_low - low) else 0
        minus_dm = max(prev_low - low, 0) if (prev_low - low) > (high - prev_high) else 0
        
        plus_dm_values.append(plus_dm)
        minus_dm_values.append(minus_dm)
    
    if len(tr_values) < period:
        return 0.0
    
    # Calculate DX values for smoothing
    # Note: This implementation prioritizes clarity over performance.
    # For large datasets, consider using rolling window or EMA for optimization.
    dx_values = []
    for i in range(period - 1, len(tr_values)):
        atr = np.mean(tr_values[i-period+1:i+1])
        plus_di = 100 * np.mean(plus_dm_values[i-period+1:i+1]) / atr if atr > 0 else 0
        minus_di = 100 * np.mean(minus_dm_values[i-period+1:i+1]) / atr if atr > 0 else 0
        
        # Only calculate DX when denominator is non-zero to avoid division by zero
        if plus_di + minus_di > 0:
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            dx_values.append(dx)
    
    # ADX is the smoothed average of DX values
    # Require at least 'period' DX values for reliable ADX calculation
    if len(dx_values) < period:
        return 0.0
    
    adx = np.mean(dx_values[-period:])
    
    return adx


def analyze_market_structure(
    prices: List[float],
    high_prices: Optional[List[float]] = None,
    low_prices: Optional[List[float]] = None,
    volume: Optional[List[float]] = None
) -> MarketStructure:
    """Comprehensive market structure analysis."""
    if len(prices) < 50:
        return MarketStructure(
            trend='unknown',
            strength=0.0,
            support_levels=[],
            resistance_levels=[],
            breakout_probability=0.0,
            reversal_probability=0.0
        )
    
    high_prices = high_prices or prices
    low_prices = low_prices or prices
    
    ema_20 = calculate_ema(prices, 20)
    ema_50 = calculate_ema(prices, 50)
    
    current_price = prices[-1]
    trend = 'neutral'
    
    if ema_20 and ema_50:
        if ema_20[-1] > ema_50[-1] and current_price > ema_20[-1]:
            trend = 'uptrend'
        elif ema_20[-1] < ema_50[-1] and current_price < ema_20[-1]:
            trend = 'downtrend'
    
    adx = calculate_average_directional_index(prices, high_prices, low_prices)
    strength = adx / 100.0
    
    support_levels, resistance_levels = identify_support_resistance(prices)
    
    rsi = calculate_rsi(prices)
    
    breakout_probability = 0.0
    if support_levels or resistance_levels:
        nearest_resistance = min([r for r in resistance_levels if r > current_price], default=float('inf'))
        nearest_support = max([s for s in support_levels if s < current_price], default=0)
        
        if nearest_resistance != float('inf'):
            distance_to_resistance = (nearest_resistance - current_price) / current_price
            if distance_to_resistance < 0.01:
                breakout_probability = min(0.9, strength + 0.1)
        
        if nearest_support > 0:
            distance_to_support = (current_price - nearest_support) / current_price
            if distance_to_support < 0.01:
                breakout_probability = max(breakout_probability, min(0.9, strength + 0.1))
    
    reversal_probability = 0.0
    if rsi > 70:
        reversal_probability = (rsi - 70) / 30.0
    elif rsi < 30:
        reversal_probability = (30 - rsi) / 30.0
    
    return MarketStructure(
        trend=trend,
        strength=strength,
        support_levels=support_levels,
        resistance_levels=resistance_levels,
        breakout_probability=breakout_probability,
        reversal_probability=reversal_probability
    )


def calculate_ichimoku_cloud(prices: List[float], high_prices: List[float], low_prices: List[float]) -> Dict[str, float]:
    """Calculate Ichimoku Cloud components."""
    if len(prices) < 52:
        return {
            'tenkan_sen': 0.0,
            'kijun_sen': 0.0,
            'senkou_span_a': 0.0,
            'senkou_span_b': 0.0,
            'chikou_span': 0.0
        }
    
    tenkan_high = max(high_prices[-9:])
    tenkan_low = min(low_prices[-9:])
    tenkan_sen = (tenkan_high + tenkan_low) / 2
    
    kijun_high = max(high_prices[-26:])
    kijun_low = min(low_prices[-26:])
    kijun_sen = (kijun_high + kijun_low) / 2
    
    senkou_span_a = (tenkan_sen + kijun_sen) / 2
    
    senkou_high = max(high_prices[-52:])
    senkou_low = min(low_prices[-52:])
    senkou_span_b = (senkou_high + senkou_low) / 2
    
    chikou_span = prices[-26] if len(prices) >= 26 else prices[0]
    
    return {
        'tenkan_sen': tenkan_sen,
        'kijun_sen': kijun_sen,
        'senkou_span_a': senkou_span_a,
        'senkou_span_b': senkou_span_b,
        'chikou_span': chikou_span
    }


def detect_chart_patterns(prices: List[float], window: int = 20) -> List[Dict[str, Any]]:
    """Detect common chart patterns."""
    if len(prices) < window:
        return []
    
    patterns = []
    recent = prices[-window:]
    
    high_idx = np.argmax(recent)
    low_idx = np.argmin(recent)
    
    if high_idx < len(recent) // 2 < low_idx:
        patterns.append({
            'pattern': 'double_top',
            'confidence': 0.6,
            'direction': 'bearish'
        })
    
    if low_idx < len(recent) // 2 < high_idx:
        patterns.append({
            'pattern': 'double_bottom',
            'confidence': 0.6,
            'direction': 'bullish'
        })
    
    first_half_trend = recent[window//2] - recent[0]
    second_half_trend = recent[-1] - recent[window//2]
    
    if first_half_trend > 0 and second_half_trend < 0:
        patterns.append({
            'pattern': 'head_and_shoulders',
            'confidence': 0.5,
            'direction': 'bearish'
        })
    
    if first_half_trend < 0 and second_half_trend > 0:
        patterns.append({
            'pattern': 'inverse_head_and_shoulders',
            'confidence': 0.5,
            'direction': 'bullish'
        })
    
    return patterns


def calculate_volume_profile(prices: List[float], volume: List[float], bins: int = 10) -> Dict[str, Any]:
    """Calculate volume profile and point of control."""
    if not volume or len(prices) != len(volume):
        return {'poc': 0.0, 'vah': 0.0, 'val': 0.0, 'profile': {}}
    
    price_range = max(prices) - min(prices)
    bin_size = price_range / bins
    
    profile = {}
    for price, vol in zip(prices, volume):
        bin_key = int((price - min(prices)) / bin_size) if bin_size > 0 else 0
        profile[bin_key] = profile.get(bin_key, 0) + vol
    
    if not profile:
        return {'poc': 0.0, 'vah': 0.0, 'val': 0.0, 'profile': {}}
    
    poc_bin = max(profile.items(), key=lambda x: x[1])[0]
    poc = min(prices) + (poc_bin * bin_size)
    
    total_volume = sum(profile.values())
    value_area_volume = total_volume * 0.7
    
    sorted_bins = sorted(profile.items(), key=lambda x: x[1], reverse=True)
    
    cumulative_volume = 0
    value_area_bins = []
    for bin_key, vol in sorted_bins:
        cumulative_volume += vol
        value_area_bins.append(bin_key)
        if cumulative_volume >= value_area_volume:
            break
    
    vah = min(prices) + (max(value_area_bins) * bin_size) if value_area_bins else poc
    val = min(prices) + (min(value_area_bins) * bin_size) if value_area_bins else poc
    
    return {
        'poc': poc,
        'vah': vah,
        'val': val,
        'profile': profile
    }
