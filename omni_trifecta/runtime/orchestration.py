"""Runtime orchestration and main loop."""

from typing import Dict, Any, Iterator, Optional, List
from datetime import datetime
import time

from ..decision.master_governor import MasterGovernorX100
from ..execution.executors import RealTimeExecutionHub, ShadowExecutionHub
from ..learning.orchestrator import RLJSONStore
from ..safety.managers import SafetyManager
from .logging import OmniLogger, DecisionAuditTrail, PerformanceRecorder
from ..utils.technical import detect_swing_points


class OmniRuntime:
    """Main runtime orchestrator for the Omni-Trifecta system.
    
    Coordinates governor, execution, logging, and persistence.
    """
    
    def __init__(
        self,
        governor: MasterGovernorX100,
        execution_hub: RealTimeExecutionHub,
        rl_store: RLJSONStore,
        logger: OmniLogger,
        audit_trail: Optional[DecisionAuditTrail] = None,
        perf_recorder: Optional[PerformanceRecorder] = None
    ):
        """Initialize Omni runtime.
        
        Args:
            governor: Master Governor X100
            execution_hub: Execution hub (real or shadow)
            rl_store: RL persistence store
            logger: System logger
            audit_trail: Decision audit trail (optional)
            perf_recorder: Performance recorder (optional)
        """
        self.governor = governor
        self.execution_hub = execution_hub
        self.rl_store = rl_store
        self.logger = logger
        self.audit_trail = audit_trail
        self.perf_recorder = perf_recorder
        
        # Load persisted RL state
        self._load_rl_state()
    
    def on_tick(
        self,
        price_window: List[float],
        swings: List[tuple[int, float, str]],
        fx_vol: List[float],
        bin_vol: List[float],
        dex_vol: List[float],
        balance: float,
        ctx: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle a new price tick and make trading decision.
        
        Args:
            price_window: Recent price history
            swings: Detected swing points
            fx_vol: FX volatility history
            bin_vol: Binary volatility history
            dex_vol: DEX volatility history
            balance: Current balance
            ctx: Additional context
        
        Returns:
            Execution result
        """
        # Make decision via governor
        decision = self.governor.decide(
            price_window=price_window,
            swings=swings,
            fx_vol=fx_vol,
            bin_vol=bin_vol,
            dex_vol=dex_vol,
            balance=balance,
            ctx=ctx
        )
        
        # Log decision to audit trail
        if self.audit_trail:
            self.audit_trail.log_decision(
                decision=decision,
                regime_state=decision.get("regime_state"),
                fib_block=decision.get("fib_block", {})
            )
        
        # Execute trade
        result = self.execution_hub.execute(decision, ctx)
        
        return result
    
    def _load_rl_state(self):
        """Load persisted RL state."""
        # Load regime RL
        regime_state = self.rl_store.load_regime()
        if regime_state:
            self.governor.regime_rl.q_table = regime_state.get("q_table", {})
            self.governor.regime_rl.engine_performance = regime_state.get("engine_performance", {})
        
        # Load arbitrage routes
        routes_state = self.rl_store.load_routes()
        if routes_state:
            self.governor.arb_rl_agent.route_scores = routes_state.get("route_scores", {})
    
    def shutdown(self):
        """Shutdown runtime and persist state."""
        # Save RL state
        self.rl_store.save_regime(self.governor.regime_rl)
        self.rl_store.save_routes(self.governor.arb_rl_agent)
        
        self.logger.log_event("SHUTDOWN", {"reason": "Normal shutdown"})


def omni_main_loop(
    price_feed: Iterator[float],
    symbol: str,
    runtime: OmniRuntime,
    safety_manager: SafetyManager,
    starting_balance: float = 1000.0,
    window_size: int = 256
):
    """Main execution loop for the Omni-Trifecta system.
    
    Args:
        price_feed: Iterator yielding prices
        symbol: Trading symbol
        runtime: Runtime orchestrator
        safety_manager: Safety manager
        starting_balance: Starting account balance
        window_size: Size of price window
    """
    # Initialize state
    price_window: List[float] = []
    fx_vol: List[float] = []
    bin_vol: List[float] = []
    dex_vol: List[float] = []
    balance = starting_balance
    last_win = False
    tick_count = 0
    
    print(f"\n{'='*60}")
    print(f"OMNI-TRIFECTA QUANT ENGINE")
    print(f"Symbol: {symbol}")
    print(f"Starting Balance: ${balance:.2f}")
    print(f"{'='*60}\n")
    
    try:
        for price in price_feed:
            tick_count += 1
            timestamp = datetime.now()
            
            # Update price window
            price_window.append(price)
            if len(price_window) > window_size:
                price_window.pop(0)
            
            # Calculate volatility proxies
            if len(price_window) >= 2:
                vol_proxy = abs(price_window[-1] - price_window[-min(10, len(price_window))])
                fx_vol.append(vol_proxy)
                bin_vol.append(vol_proxy * 0.8)  # Simplified
                dex_vol.append(vol_proxy * 1.2)  # Simplified
                
                # Keep volatility windows manageable
                if len(fx_vol) > window_size:
                    fx_vol.pop(0)
                    bin_vol.pop(0)
                    dex_vol.pop(0)
            
            # Log tick
            runtime.logger.log_tick(symbol, price, timestamp)
            
            # Detect swing points
            swings = detect_swing_points(price_window, window=5)
            
            # Check safety manager
            if not safety_manager.can_trade():
                runtime.logger.log_trade({
                    "timestamp": timestamp.isoformat(),
                    "mode": "COOLDOWN",
                    "reason": "Safety limits triggered",
                    "balance": balance
                })
                
                # Print status every 100 ticks even in cooldown
                if tick_count % 100 == 0:
                    safety_status = safety_manager.get_status()
                    print(f"Tick {tick_count} | Price: ${price:.4f} | Balance: ${balance:.2f} | COOLDOWN")
                
                continue
            
            # Need minimum data for decisions
            if len(price_window) < 20:
                continue
            
            # Build context
            ctx = {
                "timestamp": timestamp,
                "symbol": symbol,
                "last_win": last_win,
                "tick_count": tick_count
            }
            
            # Make decision and execute
            result = runtime.on_tick(
                price_window=price_window,
                swings=swings,
                fx_vol=fx_vol,
                bin_vol=bin_vol,
                dex_vol=dex_vol,
                balance=balance,
                ctx=ctx
            )
            
            # Update balance
            pnl = result.get("pnl", 0.0)
            balance += pnl
            last_win = pnl > 0
            
            # Register trade with safety manager
            if result.get("success"):
                safety_manager.register_trade(pnl)
            
            # Update RL learning from trade outcome
            if result.get("success") and pnl != 0:
                # Build new state for learning update
                new_trend_strength = runtime.governor._calculate_trend_strength(price_window)
                new_vol_est = runtime.governor.seq_model.predict_volatility(price_window)
                from ..decision.rl_agents import RegimeState
                new_state = RegimeState(
                    vol_score=new_vol_est,
                    trend_strength=new_trend_strength,
                    mean_reversion_score=1.0 - new_trend_strength
                )
                runtime.governor.update_learning(reward=pnl, new_state=new_state)
            
            # Log trade with engine type for proper tracking
            decision = runtime.governor.last_state
            trade_record = {
                "timestamp": timestamp.isoformat(),
                "symbol": symbol,
                "mode": result.get("mode", "UNKNOWN"),
                "engine_type": runtime.governor.last_engine,
                "pnl": pnl,
                "balance": balance,
                "success": result.get("success", False)
            }
            runtime.logger.log_trade(trade_record)
            
            # Print status every 10 trades
            if tick_count % 10 == 0:
                print(f"Tick {tick_count} | Price: ${price:.4f} | Balance: ${balance:.2f} | PnL: ${pnl:+.2f}")
            
            # Record performance metrics every 100 ticks
            if runtime.perf_recorder and tick_count % 100 == 0:
                runtime.perf_recorder.record_metrics(
                    balance=balance,
                    equity_curve=[balance],
                    engine_stats=runtime.governor.regime_rl.get_stats(),
                    safety_status=safety_manager.get_status()
                )
            
            # Small delay to prevent excessive CPU usage in simulation
            time.sleep(0.01)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    
    finally:
        # Shutdown and save state
        runtime.shutdown()
        
        # Print final summary
        print(f"\n{'='*60}")
        print(f"SESSION SUMMARY")
        print(f"Total Ticks: {tick_count}")
        print(f"Final Balance: ${balance:.2f}")
        print(f"Total PnL: ${balance - starting_balance:+.2f}")
        print(f"Return: {((balance - starting_balance) / starting_balance * 100):+.2f}%")
        
        perf_summary = runtime.logger.get_performance_summary()
        print(f"\nTrades: {perf_summary['total_trades']}")
        print(f"Win Rate: {perf_summary['win_rate']*100:.1f}%")
        print(f"Avg PnL: ${perf_summary['avg_pnl']:+.4f}")
        print(f"{'='*60}\n")
