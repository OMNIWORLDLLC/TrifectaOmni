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
    
    def evaluate_opportunity(self, order_proposal: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate arbitrage opportunity.
        
        Args:
            order_proposal: Arbitrage order details
        
        Returns:
            Decision dict with action and reason
        """
        # Check if expected profit meets threshold
        expected_profit = order_proposal.get('expected_profit', 0.0)
        capital = order_proposal.get('capital', 1.0)
        profit_pct = (expected_profit / capital) * 100
        
        if profit_pct < 0.5:  # Minimum 0.5% profit
            return {
                'action': 'skip',
                'reason': f'Profit margin too low: {profit_pct:.2f}%',
                'confidence': 0.0
            }
        
        # Check risk score
        risk_score = order_proposal.get('risk_score', 50.0)
        if risk_score > 75.0:
            return {
                'action': 'skip',
                'reason': f'Risk score too high: {risk_score:.1f}/100',
                'confidence': 0.0
            }
        
        return {
            'action': 'execute',
            'reason': f'Good opportunity: {profit_pct:.2f}% profit, {risk_score:.1f}/100 risk',
            'confidence': min(profit_pct * 10, 95.0)
        }


class ForexRLAgent:
    """RL agent for forex trade decisions.
    
    Learns which forex signals and pairs are most profitable.
    """
    
    def __init__(self, learning_rate: float = 0.1):
        """Initialize forex RL agent.
        
        Args:
            learning_rate: Learning rate for updates
        """
        self.learning_rate = learning_rate
        self.pair_scores: Dict[str, float] = {}
        self.signal_accuracy: Dict[str, Dict[str, float]] = {}  # {pair: {signal: accuracy}}
    
    def evaluate_signal(self, pair: str, signal: str, confidence: float) -> Dict[str, Any]:
        """Evaluate forex trading signal.
        
        Args:
            pair: Currency pair (e.g., 'EUR/USD')
            signal: Trading signal ('BUY', 'SELL', 'HOLD')
            confidence: Signal confidence (0-100)
        
        Returns:
            Decision dict with action, size_multiplier, and reason
        """
        # Initialize tracking for new pairs
        if pair not in self.pair_scores:
            self.pair_scores[pair] = 0.5  # Neutral score
        
        if pair not in self.signal_accuracy:
            self.signal_accuracy[pair] = {'BUY': 0.5, 'SELL': 0.5, 'HOLD': 0.5}
        
        # Skip HOLD signals
        if signal == 'HOLD':
            return {
                'action': 'skip',
                'reason': 'HOLD signal - no action',
                'size_multiplier': 0.0
            }
        
        # Check confidence threshold
        if confidence < 60.0:
            return {
                'action': 'skip',
                'reason': f'Confidence too low: {confidence:.1f}%',
                'size_multiplier': 0.0
            }
        
        # Get historical accuracy for this pair+signal combo
        signal_accuracy = self.signal_accuracy[pair].get(signal, 0.5)
        pair_score = self.pair_scores[pair]
        
        # Combined score: confidence + historical accuracy + pair performance
        combined_score = (confidence / 100) * 0.4 + signal_accuracy * 0.3 + pair_score * 0.3
        
        # Decide on position sizing
        if combined_score < 0.4:
            return {
                'action': 'skip',
                'reason': f'Combined score too low: {combined_score:.2f}',
                'size_multiplier': 0.0
            }
        elif combined_score < 0.6:
            size_mult = 0.5  # Half position
        elif combined_score < 0.8:
            size_mult = 0.75  # 3/4 position
        else:
            size_mult = 1.0  # Full position
        
        return {
            'action': 'execute',
            'reason': f'{signal} signal: {confidence:.1f}% confidence, {combined_score:.2f} combined score',
            'size_multiplier': size_mult,
            'confidence': combined_score * 100
        }
    
    def update_signal_result(self, pair: str, signal: str, profitable: bool):
        """Update signal accuracy based on trade result.
        
        Args:
            pair: Currency pair
            signal: Signal that was used
            profitable: Whether trade was profitable
        """
        if pair not in self.signal_accuracy:
            self.signal_accuracy[pair] = {'BUY': 0.5, 'SELL': 0.5, 'HOLD': 0.5}
        
        # Update signal accuracy with exponential moving average
        current_accuracy = self.signal_accuracy[pair].get(signal, 0.5)
        new_accuracy = (1 - self.learning_rate) * current_accuracy + self.learning_rate * (1.0 if profitable else 0.0)
        self.signal_accuracy[pair][signal] = new_accuracy
        
        # Update overall pair score
        if pair in self.pair_scores:
            current_score = self.pair_scores[pair]
            self.pair_scores[pair] = (1 - self.learning_rate) * current_score + self.learning_rate * (1.0 if profitable else 0.0)
    
    def get_best_pairs(self, top_n: int = 5) -> list[str]:
        """Get top performing pairs.
        
        Args:
            top_n: Number of top pairs to return
        
        Returns:
            List of best performing pairs
        """
        if not self.pair_scores:
            return []
        
        sorted_pairs = sorted(self.pair_scores.items(), key=lambda x: x[1], reverse=True)
        return [pair for pair, _ in sorted_pairs[:top_n]]
