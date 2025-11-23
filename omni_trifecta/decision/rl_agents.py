"""Reinforcement learning and regime switching components."""

from typing import Dict, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class RegimeState:
    """Represents the current market regime state.
    
    Attributes:
        vol_score: Volatility score
        trend_strength: Strength of current trend
        mean_reversion_score: Mean reversion indicator
    """
    vol_score: float
    trend_strength: float
    mean_reversion_score: float
    
    def to_key(self) -> str:
        """Convert state to hashable key for Q-table.
        
        Returns:
            String representation of discretized state
        """
        # Discretize continuous values for Q-table
        vol_bucket = int(self.vol_score * 10) // 2  # 0-5 buckets
        trend_bucket = int(self.trend_strength * 10) // 2  # 0-5 buckets
        mr_bucket = int(self.mean_reversion_score * 10) // 2  # 0-5 buckets
        
        return f"v{vol_bucket}_t{trend_bucket}_m{mr_bucket}"


class RegimeSwitchingRL:
    """Reinforcement learning agent for regime-based engine selection.
    
    Uses Q-learning to select optimal trading engine based on market regime.
    """
    
    ENGINES = ["binary", "spot", "arbitrage"]
    
    def __init__(self, learning_rate: float = 0.1, discount: float = 0.9, epsilon: float = 0.1):
        """Initialize regime switching RL agent.
        
        Args:
            learning_rate: Learning rate (alpha)
            discount: Discount factor (gamma)
            epsilon: Exploration rate
        """
        self.learning_rate = learning_rate
        self.discount = discount
        self.epsilon = epsilon
        self.q_table: Dict[str, Dict[str, float]] = {}
        
        # Initialize performance tracking
        self.engine_performance = {engine: [] for engine in self.ENGINES}
    
    def choose_engine(self, state: RegimeState) -> str:
        """Choose trading engine based on regime state.
        
        Args:
            state: Current regime state
        
        Returns:
            Selected engine type
        """
        state_key = state.to_key()
        
        # Initialize Q-values for unseen states
        if state_key not in self.q_table:
            self.q_table[state_key] = {engine: 0.0 for engine in self.ENGINES}
        
        # Epsilon-greedy exploration
        if np.random.random() < self.epsilon:
            return np.random.choice(self.ENGINES)
        
        # Heuristic-based selection with Q-value bias
        q_values = self.q_table[state_key]
        
        # Apply heuristics
        if state.vol_score > 1.5:
            # High volatility favors binary
            q_values["binary"] += 0.2
        elif state.trend_strength > 0.7:
            # Strong trend favors spot
            q_values["spot"] += 0.2
        elif state.mean_reversion_score > 0.7:
            # Mean reversion favors arbitrage
            q_values["arbitrage"] += 0.2
        
        # Select engine with highest Q-value
        return max(q_values.items(), key=lambda x: x[1])[0]
    
    def update(self, state: RegimeState, engine: str, reward: float, next_state: RegimeState):
        """Update Q-values based on observed reward.
        
        Args:
            state: Previous state
            engine: Engine that was used
            reward: Observed reward (PnL)
            next_state: New state after action
        """
        state_key = state.to_key()
        next_state_key = next_state.to_key()
        
        # Initialize Q-values if needed
        if state_key not in self.q_table:
            self.q_table[state_key] = {e: 0.0 for e in self.ENGINES}
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {e: 0.0 for e in self.ENGINES}
        
        # Q-learning update
        current_q = self.q_table[state_key][engine]
        max_next_q = max(self.q_table[next_state_key].values())
        
        new_q = current_q + self.learning_rate * (reward + self.discount * max_next_q - current_q)
        self.q_table[state_key][engine] = new_q
        
        # Track performance
        self.engine_performance[engine].append(reward)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics for each engine.
        
        Returns:
            Dictionary of engine performance stats
        """
        stats = {}
        for engine, rewards in self.engine_performance.items():
            if rewards:
                stats[engine] = {
                    "count": len(rewards),
                    "total": sum(rewards),
                    "mean": np.mean(rewards),
                    "std": np.std(rewards)
                }
            else:
                stats[engine] = {"count": 0, "total": 0.0, "mean": 0.0, "std": 0.0}
        return stats


class LadderRiskAI:
    """Ladder-based position sizing for binary options.
    
    Adjusts stake based on win/loss streaks using martingale-like approach
    with risk limits.
    """
    
    def __init__(self, base_stake: float = 1.0, max_stake: float = 100.0, multiplier: float = 2.0):
        """Initialize ladder risk AI.
        
        Args:
            base_stake: Base stake amount
            max_stake: Maximum allowed stake
            multiplier: Multiplier after loss
        """
        self.base_stake = base_stake
        self.max_stake = max_stake
        self.multiplier = multiplier
        self.current_stake = base_stake
        self.win_streak = 0
        self.loss_streak = 0
    
    def next_stake(self, balance: float, last_win: bool) -> float:
        """Calculate next stake based on last result.
        
        Args:
            balance: Current account balance
            last_win: Whether last trade was a win
        
        Returns:
            Next stake amount
        """
        if last_win:
            # Win: reset to base stake
            self.current_stake = self.base_stake
            self.win_streak += 1
            self.loss_streak = 0
        else:
            # Loss: increase stake
            self.current_stake *= self.multiplier
            self.loss_streak += 1
            self.win_streak = 0
        
        # Apply limits
        self.current_stake = min(self.current_stake, self.max_stake)
        self.current_stake = min(self.current_stake, balance * 0.1)  # Max 10% of balance
        
        return self.current_stake


class SpotTPRotator:
    """Take-profit selector for spot forex trades.
    
    Rotates between Fibonacci extension levels based on trend strength.
    """
    
    def __init__(self):
        """Initialize TP rotator."""
        self.last_tp = None
    
    def choose_tp(
        self,
        fib_extensions: Dict[str, float],
        atr: float,
        trend_strength: float
    ) -> float:
        """Choose take-profit level.
        
        Args:
            fib_extensions: Fibonacci extension levels
            atr: Average True Range
            trend_strength: Trend strength indicator
        
        Returns:
            Selected TP level
        """
        if not fib_extensions:
            # Fallback to ATR-based TP
            return atr * 3.0
        
        # Select TP based on trend strength
        if trend_strength > 0.8:
            # Very strong trend: aim for 1.618 extension
            tp = fib_extensions.get("1.618", atr * 3.0)
        elif trend_strength > 0.6:
            # Strong trend: aim for 1.414 extension
            tp = fib_extensions.get("1.414", atr * 2.5)
        else:
            # Moderate trend: aim for 1.272 extension
            tp = fib_extensions.get("1.272", atr * 2.0)
        
        self.last_tp = tp
        return tp


class ArbitrageRLAgent:
    """RL agent for arbitrage route selection.
    
    Learns which arbitrage routes are most profitable.
    """
    
    def __init__(self, learning_rate: float = 0.1):
        """Initialize arbitrage RL agent.
        
        Args:
            learning_rate: Learning rate for updates
        """
        self.learning_rate = learning_rate
        self.route_scores: Dict[str, float] = {}
    
    def choose_best_route(self, candidate_routes: list[str]) -> str:
        """Choose best arbitrage route.
        
        Args:
            candidate_routes: List of available routes
        
        Returns:
            Selected route ID
        """
        if not candidate_routes:
            return "default"
        
        # Initialize scores for new routes
        for route in candidate_routes:
            if route not in self.route_scores:
                self.route_scores[route] = 0.0
        
        # Select route with highest score
        best_route = max(candidate_routes, key=lambda r: self.route_scores.get(r, 0.0))
        return best_route
    
    def update_route(self, route_id: str, reward: float):
        """Update route score based on reward.
        
        Args:
            route_id: Route that was used
            reward: Observed reward
        """
        if route_id not in self.route_scores:
            self.route_scores[route_id] = 0.0
        
        # Simple exponential moving average update
        self.route_scores[route_id] = (
            (1 - self.learning_rate) * self.route_scores[route_id] +
            self.learning_rate * reward
        )
