"""Master Fibonacci Governor - coordinates all Fibonacci intelligence."""

from typing import List, Dict, Any
import numpy as np

from .core_components import (
    FibonacciClusterAI,
    ElliottWaveForecastEngine,
    PatternMemory,
    VolatilityScoreMatrix,
)
from .engines import TriFectaFibonacciSystem


class MasterFibonacciGovernor:
    """Master controller for Fibonacci and harmonic intelligence.
    
    Integrates clustering, wave analysis, pattern memory, and volatility scoring
    with engine-specific Fibonacci analysis.
    """
    
    def __init__(self):
        """Initialize Master Fibonacci Governor."""
        self.cluster_ai = FibonacciClusterAI(n_clusters=5)
        self.wave_engine = ElliottWaveForecastEngine()
        self.pattern_memory = PatternMemory()
        self.volatility_matrix = VolatilityScoreMatrix()
        self.trifecta_system = TriFectaFibonacciSystem()
    
    def evaluate_market(
        self,
        engine_type: str,
        price_series: List[float],
        swings: List[tuple[int, float, str]],
        fx_vol: List[float],
        binary_vol: List[float],
        dex_vol: List[float],
        trend_strength: float = 0.0
    ) -> Dict[str, Any]:
        """Evaluate market conditions using full Fibonacci intelligence.
        
        Args:
            engine_type: Trading engine type ("binary", "spot", "arbitrage")
            price_series: Recent price history
            swings: Detected swing points
            fx_vol: FX volatility history
            binary_vol: Binary volatility history
            dex_vol: DEX volatility history
            trend_strength: Trend strength indicator
        
        Returns:
            Enriched decision block with all Fibonacci intelligence
        """
        if len(price_series) < 10:
            return self._empty_evaluation()
        
        # 1. Compute cluster centers (adaptive zones)
        clusters = self.cluster_ai.learn_zones(price_series)
        
        # 2. Detect Elliott Wave state
        wave_state = self.wave_engine.detect_wave(swings)
        
        # 3. Recall pattern memory
        pattern_info = self.pattern_memory.recall()
        
        # 4. Calculate composite volatility score
        volatility_score = self.volatility_matrix.score(fx_vol, binary_vol, dex_vol)
        
        # 5. Get engine-specific Fibonacci analysis
        high = max(price_series[-50:]) if len(price_series) >= 50 else max(price_series)
        low = min(price_series[-50:]) if len(price_series) >= 50 else min(price_series)
        
        # Estimate ATR from price series (simplified)
        atr = np.std(price_series[-20:]) if len(price_series) >= 20 else np.std(price_series)
        
        base_signal = self.trifecta_system.analyze(
            engine_type=engine_type,
            price_series=price_series,
            high=high,
            low=low,
            atr=atr,
            trend_strength=trend_strength,
            dex_vol=dex_vol,
            volatility_score=volatility_score
        )
        
        # 6. Decide final decision based on all factors
        final_decision = self._make_final_decision(
            base_signal=base_signal,
            wave_state=wave_state,
            volatility_score=volatility_score,
            pattern_info=pattern_info
        )
        
        # 7. Store patterns if relevant
        if wave_state in ["IMPULSE_UP", "IMPULSE_DOWN"]:
            # Simplified: store a pattern based on wave state
            # In production, this would involve more sophisticated pattern detection
            if pattern_info["most_common"]:
                self.pattern_memory.store(pattern_info["most_common"])
        
        return {
            "base_signal": base_signal,
            "clusters": clusters,
            "wave_state": wave_state,
            "pattern_memory": pattern_info,
            "volatility_score": volatility_score,
            "final_decision": final_decision,
            "high": high,
            "low": low,
            "atr": atr
        }
    
    def _make_final_decision(
        self,
        base_signal: Dict[str, Any],
        wave_state: str,
        volatility_score: float,
        pattern_info: Dict[str, Any]
    ) -> str:
        """Make final decision based on all Fibonacci factors.
        
        Args:
            base_signal: Base signal from engine
            wave_state: Elliott Wave state
            volatility_score: Composite volatility score
            pattern_info: Pattern memory information
        
        Returns:
            Final decision ("TRADE", "WAIT", "NONE")
        """
        # Get signal from base analysis
        signal = base_signal.get("signal", "NONE")
        timing = base_signal.get("timing", None)
        confidence = base_signal.get("confidence", 0.0)
        
        # If no base signal, return NONE
        if signal == "NONE" and timing != "EXECUTE":
            return "NONE"
        
        # Boost confidence with wave alignment
        wave_boost = 0.0
        if wave_state in ["IMPULSE_UP", "IMPULSE_DOWN"]:
            wave_boost = 0.1
        
        # Adjust for volatility
        vol_factor = 1.0
        if volatility_score > 1.5:  # High volatility
            vol_factor = 1.2
        elif volatility_score < 0.5:  # Low volatility
            vol_factor = 0.8
        
        # Calculate adjusted confidence
        adjusted_confidence = (confidence + wave_boost) * vol_factor
        
        # Decision threshold
        if adjusted_confidence > 0.6:
            return "TRADE"
        elif adjusted_confidence > 0.4:
            return "WAIT"
        else:
            return "NONE"
    
    def _empty_evaluation(self) -> Dict[str, Any]:
        """Return empty evaluation when insufficient data.
        
        Returns:
            Empty evaluation dictionary
        """
        return {
            "base_signal": {"signal": "NONE", "confidence": 0.0},
            "clusters": [],
            "wave_state": "INSUFFICIENT_DATA",
            "pattern_memory": {"most_common": None, "frequency": 0, "recent_count": 0},
            "volatility_score": 0.0,
            "final_decision": "NONE",
            "high": 0.0,
            "low": 0.0,
            "atr": 0.0
        }
