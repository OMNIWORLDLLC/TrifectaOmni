"""Fibonacci and harmonic intelligence components."""

from typing import List, Dict, Optional, Any
import numpy as np
from sklearn.cluster import KMeans

from ..utils.technical import (
    fibonacci_retracements,
    fibonacci_extensions,
    atr_adjusted_zone,
    calculate_atr,
)


class FibonacciClusterAI:
    """ML-based clustering for adaptive Fibonacci zones.
    
    Uses K-Means clustering to identify dynamic support/resistance levels.
    """
    
    def __init__(self, n_clusters: int = 5):
        """Initialize Fibonacci cluster AI.
        
        Args:
            n_clusters: Number of clusters to identify
        """
        self.n_clusters = n_clusters
        self.model = None
        self.cluster_centers = []
    
    def learn_zones(self, price_series: List[float]) -> List[float]:
        """Learn adaptive zones from price series.
        
        Args:
            price_series: Recent price history
        
        Returns:
            List of cluster centers (support/resistance zones)
        """
        if len(price_series) < self.n_clusters:
            return []
        
        # Reshape for sklearn
        X = np.array(price_series).reshape(-1, 1)
        
        # Perform K-Means clustering
        self.model = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
        self.model.fit(X)
        
        # Extract and sort cluster centers
        self.cluster_centers = sorted([float(c[0]) for c in self.model.cluster_centers_])
        return self.cluster_centers
    
    def get_nearest_zone(self, price: float) -> Optional[float]:
        """Get nearest cluster zone to current price.
        
        Args:
            price: Current price
        
        Returns:
            Nearest cluster center or None
        """
        if not self.cluster_centers:
            return None
        
        distances = [abs(price - center) for center in self.cluster_centers]
        min_idx = np.argmin(distances)
        return self.cluster_centers[min_idx]


class ElliottWaveForecastEngine:
    """Elliott Wave detection and forecasting engine.
    
    Detects wave patterns and forecasts potential targets.
    """
    
    def __init__(self):
        """Initialize Elliott Wave engine."""
        self.wave_state = "UNKNOWN"
    
    def detect_wave(self, swings: List[tuple[int, float, str]]) -> str:
        """Detect Elliott Wave pattern from swing points.
        
        Args:
            swings: List of swing points (index, price, type)
        
        Returns:
            Wave state classification
        """
        if len(swings) < 5:
            self.wave_state = "INSUFFICIENT_DATA"
            return self.wave_state
        
        # Simple impulse pattern detection (5 swings alternating HIGH/LOW)
        last_5 = swings[-5:]
        
        # Check for impulse pattern: LOW -> HIGH -> LOW -> HIGH -> LOW (or inverse)
        types = [s[2] for s in last_5]
        
        if types == ['LOW', 'HIGH', 'LOW', 'HIGH', 'LOW']:
            self.wave_state = "IMPULSE_UP"
        elif types == ['HIGH', 'LOW', 'HIGH', 'LOW', 'HIGH']:
            self.wave_state = "IMPULSE_DOWN"
        else:
            self.wave_state = "CORRECTIVE"
        
        return self.wave_state
    
    def forecast_targets(self, high: float, low: float) -> Dict[str, float]:
        """Forecast wave targets using Fibonacci extensions.
        
        Args:
            high: Recent high
            low: Recent low
        
        Returns:
            Dictionary of target levels
        """
        return fibonacci_extensions(high, low)


class PatternMemory:
    """Memory system for harmonic patterns.
    
    Stores and recalls historical harmonic patterns.
    """
    
    PATTERNS = ["GARTLEY", "BAT", "BUTTERFLY", "CYPHER", "CRAB"]
    
    def __init__(self):
        """Initialize pattern memory."""
        self.history: List[str] = []
        self.pattern_frequencies: Dict[str, int] = {p: 0 for p in self.PATTERNS}
    
    def store(self, pattern: str):
        """Store a detected pattern.
        
        Args:
            pattern: Pattern name
        """
        if pattern in self.PATTERNS:
            self.history.append(pattern)
            self.pattern_frequencies[pattern] += 1
    
    def recall(self, limit: int = 100) -> Dict[str, Any]:
        """Recall recent pattern history.
        
        Args:
            limit: Number of recent patterns to consider
        
        Returns:
            Dictionary with pattern statistics
        """
        recent = self.history[-limit:] if len(self.history) > limit else self.history
        
        if not recent:
            return {
                "most_common": None,
                "frequency": 0,
                "recent_count": 0
            }
        
        # Find most common pattern
        most_common = max(self.pattern_frequencies.items(), key=lambda x: x[1])[0]
        
        return {
            "most_common": most_common,
            "frequency": self.pattern_frequencies[most_common],
            "recent_count": len(recent)
        }


class VolatilityScoreMatrix:
    """Multi-domain volatility scoring system.
    
    Combines volatility from FX, Binary, and DEX markets into unified score.
    """
    
    def __init__(self):
        """Initialize volatility score matrix."""
        self.weights = {"fx": 0.4, "binary": 0.3, "dex": 0.3}
    
    def score(
        self,
        fx_vol: List[float],
        binary_vol: List[float],
        dex_vol: List[float]
    ) -> float:
        """Calculate composite volatility score.
        
        Args:
            fx_vol: FX volatility history
            binary_vol: Binary volatility history
            dex_vol: DEX volatility history
        
        Returns:
            Weighted volatility score
        """
        scores = []
        
        # Normalize each domain by its mean
        if fx_vol:
            fx_mean = np.mean(fx_vol) if np.mean(fx_vol) != 0 else 1.0
            fx_score = fx_vol[-1] / fx_mean if fx_vol else 0
            scores.append(("fx", fx_score))
        
        if binary_vol:
            bin_mean = np.mean(binary_vol) if np.mean(binary_vol) != 0 else 1.0
            bin_score = binary_vol[-1] / bin_mean if binary_vol else 0
            scores.append(("binary", bin_score))
        
        if dex_vol:
            dex_mean = np.mean(dex_vol) if np.mean(dex_vol) != 0 else 1.0
            dex_score = dex_vol[-1] / dex_mean if dex_vol else 0
            scores.append(("dex", dex_score))
        
        if not scores:
            return 0.0
        
        # Weighted average
        weighted_sum = sum(self.weights.get(domain, 0) * score for domain, score in scores)
        weight_sum = sum(self.weights.get(domain, 0) for domain, _ in scores)
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.0
