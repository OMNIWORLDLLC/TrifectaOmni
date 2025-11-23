"""Tri-Fecta Fibonacci engines for Binary, Spot, and Arbitrage."""

from typing import List, Dict, Any, Optional
import numpy as np

from ..utils.technical import (
    fibonacci_retracements,
    fibonacci_extensions,
    atr_adjusted_zone,
    calculate_atr,
)


class BinaryFibonacciEngine:
    """Fibonacci-based signal generator for binary options.
    
    Uses Fibonacci retracements and ATR zones to trigger CALL/PUT signals.
    """
    
    def __init__(self):
        """Initialize binary Fibonacci engine."""
        self.last_signal = None
    
    def analyze(
        self,
        price_series: List[float],
        high: float,
        low: float,
        atr: float
    ) -> Dict[str, Any]:
        """Analyze market for binary option entry.
        
        Args:
            price_series: Recent price history
            high: Recent high
            low: Recent low
            atr: Average True Range
        
        Returns:
            Signal dictionary with direction and confidence
        """
        if len(price_series) < 2:
            return {"signal": "NONE", "confidence": 0.0}
        
        current_price = price_series[-1]
        
        # Calculate Fibonacci levels
        fib_levels = fibonacci_retracements(high, low)
        
        # Check if price is near key Fibonacci levels with ATR adjustment
        signals = []
        
        for level_name, level_price in fib_levels.items():
            lower, upper = atr_adjusted_zone(level_price, atr, multiplier=0.5)
            
            if lower <= current_price <= upper:
                # Near a Fibonacci level
                if level_name in ["0.382", "0.618"]:  # Key retracement levels
                    # Determine direction based on recent momentum
                    momentum = current_price - price_series[-10] if len(price_series) >= 10 else 0
                    
                    if momentum > 0:
                        signals.append(("CALL", 0.7))
                    else:
                        signals.append(("PUT", 0.7))
        
        if signals:
            # Return strongest signal
            signal, confidence = max(signals, key=lambda x: x[1])
            self.last_signal = signal
            return {
                "signal": signal,
                "confidence": confidence,
                "fib_levels": fib_levels
            }
        
        return {"signal": "NONE", "confidence": 0.0, "fib_levels": fib_levels}


class SpotFibonacciEngine:
    """Fibonacci-based signal generator for spot forex trading.
    
    Uses 61.8% retracement and extensions for trend continuation entries.
    """
    
    def __init__(self):
        """Initialize spot Fibonacci engine."""
        self.last_signal = None
    
    def analyze(
        self,
        price_series: List[float],
        high: float,
        low: float,
        atr: float,
        trend_strength: float
    ) -> Dict[str, Any]:
        """Analyze market for spot forex entry.
        
        Args:
            price_series: Recent price history
            high: Recent high
            low: Recent low
            atr: Average True Range
            trend_strength: Trend strength indicator
        
        Returns:
            Signal dictionary with direction, entry, and targets
        """
        if len(price_series) < 2:
            return {"signal": "NONE", "confidence": 0.0}
        
        current_price = price_series[-1]
        
        # Calculate Fibonacci levels
        fib_retracements = fibonacci_retracements(high, low)
        fib_extensions = fibonacci_extensions(high, low)
        
        # Look for 61.8% retracement entry in strong trend
        golden_ratio = fib_retracements["0.618"]
        lower, upper = atr_adjusted_zone(golden_ratio, atr, multiplier=0.5)
        
        signal_data = {
            "signal": "NONE",
            "confidence": 0.0,
            "entry": current_price,
            "tp_targets": fib_extensions,
            "fib_retracements": fib_retracements
        }
        
        if trend_strength > 0.5:  # Strong trend
            if lower <= current_price <= upper:
                # At golden ratio retracement
                if high > low:  # Uptrend
                    signal_data["signal"] = "BUY"
                    signal_data["confidence"] = 0.8 * trend_strength
                else:  # Downtrend
                    signal_data["signal"] = "SELL"
                    signal_data["confidence"] = 0.8 * trend_strength
                
                self.last_signal = signal_data["signal"]
        
        return signal_data


class ArbitrageFibonacciTiming:
    """Fibonacci-based timing for arbitrage opportunities.
    
    Uses volatility compression to flag expansion windows.
    """
    
    def __init__(self):
        """Initialize arbitrage Fibonacci timing."""
        self.last_signal = None
    
    def analyze(
        self,
        dex_vol: List[float],
        volatility_score: float
    ) -> Dict[str, Any]:
        """Analyze timing for arbitrage execution.
        
        Args:
            dex_vol: DEX volatility history
            volatility_score: Current volatility score
        
        Returns:
            Timing signal dictionary
        """
        if len(dex_vol) < 10:
            return {"timing": "WAIT", "confidence": 0.0}
        
        # Calculate volatility statistics
        vol_mean = np.mean(dex_vol)
        vol_std = np.std(dex_vol)
        
        if vol_mean == 0:
            return {"timing": "WAIT", "confidence": 0.0}
        
        # Check if volatility is compressed (below 61.8% of mean)
        compression_threshold = vol_mean * 0.618
        
        if volatility_score < compression_threshold:
            # Volatility compression detected - potential expansion coming
            return {
                "timing": "READY",
                "confidence": 0.7,
                "reason": "volatility_compression"
            }
        elif volatility_score > vol_mean + vol_std:
            # High volatility - opportunity window
            return {
                "timing": "EXECUTE",
                "confidence": 0.9,
                "reason": "high_volatility"
            }
        
        return {"timing": "WAIT", "confidence": 0.0}


class TriFectaFibonacciSystem:
    """Unified system coordinating all three Fibonacci engines.
    
    Routes analysis to appropriate engine based on trading mode.
    """
    
    def __init__(self):
        """Initialize tri-fecta Fibonacci system."""
        self.binary_engine = BinaryFibonacciEngine()
        self.spot_engine = SpotFibonacciEngine()
        self.arb_engine = ArbitrageFibonacciTiming()
    
    def analyze(self, engine_type: str, **kwargs) -> Dict[str, Any]:
        """Analyze market using appropriate engine.
        
        Args:
            engine_type: Type of engine ("binary", "spot", "arbitrage")
            **kwargs: Engine-specific parameters
        
        Returns:
            Analysis results from selected engine
        """
        if engine_type == "binary":
            return self.binary_engine.analyze(
                price_series=kwargs.get("price_series", []),
                high=kwargs.get("high", 0),
                low=kwargs.get("low", 0),
                atr=kwargs.get("atr", 0)
            )
        elif engine_type == "spot":
            return self.spot_engine.analyze(
                price_series=kwargs.get("price_series", []),
                high=kwargs.get("high", 0),
                low=kwargs.get("low", 0),
                atr=kwargs.get("atr", 0),
                trend_strength=kwargs.get("trend_strength", 0)
            )
        elif engine_type == "arbitrage":
            return self.arb_engine.analyze(
                dex_vol=kwargs.get("dex_vol", []),
                volatility_score=kwargs.get("volatility_score", 0)
            )
        else:
            return {"signal": "NONE", "confidence": 0.0}
