"""Master Governor X100 - The main brain of the Omni-Trifecta system."""

from typing import List, Dict, Any
import numpy as np

from ..prediction.sequence_models import SequenceModelEngine
from ..fibonacci.master_governor import MasterFibonacciGovernor
from .rl_agents import (
    RegimeState,
    RegimeSwitchingRL,
    LadderRiskAI,
    SpotTPRotator,
    ArbitrageRLAgent,
)


class MasterGovernorX100:
    """Main decision brain of the Omni-Trifecta Quant Engine.
    
    Coordinates sequence models, regime switching, Fibonacci intelligence,
    and engine-specific modifiers to produce final trading decisions.
    """
    
    def __init__(
        self,
        seq_model: SequenceModelEngine = None,
        base_stake: float = 1.0,
        max_stake: float = 100.0
    ):
        """Initialize Master Governor X100.
        
        Args:
            seq_model: Sequence model engine (creates default if None)
            base_stake: Base stake for binary options
            max_stake: Maximum stake for binary options
        """
        # Core components
        self.seq_model = seq_model or SequenceModelEngine()
        self.regime_rl = RegimeSwitchingRL()
        self.fib_governor = MasterFibonacciGovernor()
        
        # Engine-specific modifiers
        self.ladder_risk = LadderRiskAI(base_stake=base_stake, max_stake=max_stake)
        self.spot_tp_rotator = SpotTPRotator()
        self.arb_rl_agent = ArbitrageRLAgent()
        
        # State tracking
        self.last_state = None
        self.last_engine = None
    
    def decide(
        self,
        price_window: List[float],
        swings: List[tuple[int, float, str]],
        fx_vol: List[float],
        bin_vol: List[float],
        dex_vol: List[float],
        balance: float,
        ctx: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Make trading decision based on all available intelligence.
        
        Args:
            price_window: Recent price history
            swings: Detected swing points
            fx_vol: FX volatility history
            bin_vol: Binary volatility history
            dex_vol: DEX volatility history
            balance: Current account balance
            ctx: Additional context
        
        Returns:
            Complete decision envelope with all parameters
        """
        ctx = ctx or {}
        
        if len(price_window) < 10:
            return self._empty_decision()
        
        # Step 1: Sequence Model Predictions
        dir_prob = self.seq_model.predict_direction(price_window)
        vol_est = self.seq_model.predict_volatility(price_window)
        
        # Step 2: Build Regime State
        trend_strength = self._calculate_trend_strength(price_window)
        mean_reversion_score = 1.0 - trend_strength
        
        state = RegimeState(
            vol_score=vol_est,
            trend_strength=trend_strength,
            mean_reversion_score=mean_reversion_score
        )
        
        # Step 3: Choose Engine via Regime Switching RL
        engine_type = self.regime_rl.choose_engine(state)
        
        # Step 4: Get Fibonacci Intelligence
        fib_block = self.fib_governor.evaluate_market(
            engine_type=engine_type,
            price_series=price_window,
            swings=swings,
            fx_vol=fx_vol,
            binary_vol=bin_vol,
            dex_vol=dex_vol,
            trend_strength=trend_strength
        )
        
        # Step 5: Build Base Decision
        decision = {
            "engine_type": engine_type,
            "direction_prob": dir_prob,
            "regime_state": state,
            "fib_block": fib_block,
            "timestamp": ctx.get("timestamp"),
            "symbol": ctx.get("symbol", "UNKNOWN")
        }
        
        # Step 6: Apply Engine-Specific Enhancements
        if engine_type == "binary":
            decision = self._enhance_binary_decision(decision, balance, ctx)
        elif engine_type == "spot":
            decision = self._enhance_spot_decision(decision, fib_block, trend_strength)
        elif engine_type == "arbitrage":
            decision = self._enhance_arbitrage_decision(decision, ctx)
        
        # Store state for learning
        self.last_state = state
        self.last_engine = engine_type
        
        return decision
    
    def _calculate_trend_strength(self, price_window: List[float]) -> float:
        """Calculate trend strength from price window.
        
        Args:
            price_window: Recent price history
        
        Returns:
            Trend strength [0.0, 1.0]
        """
        if len(price_window) < 2:
            return 0.0
        
        price_change = abs(price_window[-1] - price_window[0])
        std_dev = np.std(price_window) if len(price_window) > 1 else 1.0
        
        if std_dev == 0:
            return 0.0
        
        strength = price_change / (std_dev + 1e-8)
        return min(strength, 1.0)
    
    def _enhance_binary_decision(
        self,
        decision: Dict[str, Any],
        balance: float,
        ctx: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance decision for binary options trading.
        
        Args:
            decision: Base decision
            balance: Current balance
            ctx: Additional context
        
        Returns:
            Enhanced decision with stake
        """
        last_win = ctx.get("last_win", False)
        stake = self.ladder_risk.next_stake(balance, last_win)
        
        decision["stake"] = stake
        decision["expiry"] = ctx.get("expiry", 300)  # Default 5 min
        
        # Determine direction
        if decision["direction_prob"] > 0.5:
            decision["direction"] = "CALL"
        else:
            decision["direction"] = "PUT"
        
        return decision
    
    def _enhance_spot_decision(
        self,
        decision: Dict[str, Any],
        fib_block: Dict[str, Any],
        trend_strength: float
    ) -> Dict[str, Any]:
        """Enhance decision for spot forex trading.
        
        Args:
            decision: Base decision
            fib_block: Fibonacci analysis block
            trend_strength: Trend strength
        
        Returns:
            Enhanced decision with TP/SL
        """
        # Get Fibonacci extensions for TP
        base_signal = fib_block.get("base_signal", {})
        tp_targets = base_signal.get("tp_targets", {})
        atr = fib_block.get("atr", 0.001)
        
        # Choose TP level
        tp = self.spot_tp_rotator.choose_tp(tp_targets, atr, trend_strength)
        
        decision["tp"] = tp
        decision["sl"] = atr * 1.5  # SL at 1.5 ATR
        decision["volume"] = 0.01  # Standard micro lot
        
        # Determine direction
        if decision["direction_prob"] > 0.5:
            decision["direction"] = "BUY"
        else:
            decision["direction"] = "SELL"
        
        return decision
    
    def _enhance_arbitrage_decision(
        self,
        decision: Dict[str, Any],
        ctx: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance decision for arbitrage trading.
        
        Args:
            decision: Base decision
            ctx: Additional context
        
        Returns:
            Enhanced decision with route
        """
        # Get available routes from context
        candidate_routes = ctx.get("candidate_routes", ["uniswap_v3", "sushiswap", "curve"])
        
        # Choose best route
        route_id = self.arb_rl_agent.choose_best_route(candidate_routes)
        
        decision["route_id"] = route_id
        decision["amount"] = ctx.get("arb_amount", 1.0)
        
        return decision
    
    def update_learning(self, reward: float, new_state: RegimeState):
        """Update RL agents based on trade outcome.
        
        Args:
            reward: Observed reward (PnL)
            new_state: New regime state after trade
        """
        if self.last_state and self.last_engine:
            self.regime_rl.update(self.last_state, self.last_engine, reward, new_state)
    
    def _empty_decision(self) -> Dict[str, Any]:
        """Return empty decision when insufficient data.
        
        Returns:
            Empty decision dictionary
        """
        return {
            "engine_type": "none",
            "direction_prob": 0.5,
            "regime_state": None,
            "fib_block": {},
            "action": "WAIT"
        }
