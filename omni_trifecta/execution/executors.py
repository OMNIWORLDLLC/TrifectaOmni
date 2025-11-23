"""Execution engines for different trading modes."""

from typing import Dict, Any, Callable, Optional
from abc import ABC, abstractmethod


class ExecutorBase(ABC):
    """Base class for trade executors."""
    
    @abstractmethod
    def execute(self, decision: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade based on decision.
        
        Args:
            decision: Trading decision
            ctx: Execution context
        
        Returns:
            Execution result
        """
        pass


class BinaryExecutor(ExecutorBase):
    """Binary options executor.
    
    Places binary option trades (CALL/PUT) with specified expiry.
    """
    
    def __init__(self, api_client=None):
        """Initialize binary executor.
        
        Args:
            api_client: Binary options API client (e.g., PocketOption)
        """
        self.api_client = api_client
    
    def execute(self, decision: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Execute binary option trade.
        
        Args:
            decision: Trading decision with direction, stake, expiry
            ctx: Execution context
        
        Returns:
            Execution result
        """
        symbol = decision.get("symbol", "UNKNOWN")
        direction = decision.get("direction", "CALL")
        stake = decision.get("stake", 1.0)
        expiry = decision.get("expiry", 300)
        
        if self.api_client:
            try:
                result = self.api_client.place_trade(
                    symbol=symbol,
                    direction=direction,
                    amount=stake,
                    expiry=expiry
                )
                return {
                    "success": True,
                    "trade_id": result.get("id"),
                    "pnl": 0.0,  # Unknown until expiry
                    "mode": "REAL"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "pnl": 0.0,
                    "mode": "REAL"
                }
        
        # Simulated execution
        return {
            "success": True,
            "trade_id": "SIMULATED",
            "pnl": 0.0,
            "mode": "SIMULATED"
        }


class MT5SpotExecutor(ExecutorBase):
    """MT5 spot forex executor.
    
    Opens spot forex positions via MetaTrader 5.
    """
    
    def __init__(self, mt5_bridge=None):
        """Initialize MT5 executor.
        
        Args:
            mt5_bridge: MT5 bridge implementing send_order
        """
        self.mt5_bridge = mt5_bridge
    
    def execute(self, decision: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Execute spot forex trade.
        
        Args:
            decision: Trading decision with direction, volume, TP, SL
            ctx: Execution context
        
        Returns:
            Execution result
        """
        symbol = decision.get("symbol", "UNKNOWN")
        direction = decision.get("direction", "BUY")
        volume = decision.get("volume", 0.01)
        tp = decision.get("tp")
        sl = decision.get("sl")
        
        if self.mt5_bridge:
            try:
                result = self.mt5_bridge.send_order(
                    symbol=symbol,
                    direction=direction,
                    volume=volume,
                    tp=tp,
                    sl=sl
                )
                return {
                    "success": True,
                    "order_id": result.get("order"),
                    "pnl": 0.0,  # Unknown until close
                    "mode": "REAL"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "pnl": 0.0,
                    "mode": "REAL"
                }
        
        # Simulated execution
        return {
            "success": True,
            "order_id": "SIMULATED",
            "pnl": 0.0,
            "mode": "SIMULATED"
        }


class ArbitrageExecutor(ExecutorBase):
    """Arbitrage/flashloan executor.
    
    Executes arbitrage routes via DEX or flashloan contracts.
    """
    
    def __init__(self, route_registry: Optional[Dict[str, Callable]] = None):
        """Initialize arbitrage executor.
        
        Args:
            route_registry: Dictionary mapping route_id to execution callable
        """
        self.route_registry = route_registry or {}
    
    def execute(self, decision: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Execute arbitrage trade.
        
        Args:
            decision: Trading decision with route_id and amount
            ctx: Execution context
        
        Returns:
            Execution result
        """
        route_id = decision.get("route_id", "default")
        amount = decision.get("amount", 1.0)
        
        if route_id in self.route_registry:
            try:
                execute_fn = self.route_registry[route_id]
                result = execute_fn(amount=amount, ctx=ctx)
                return {
                    "success": True,
                    "route": route_id,
                    "pnl": result.get("profit", 0.0),
                    "mode": "REAL"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "pnl": 0.0,
                    "mode": "REAL"
                }
        
        # Simulated execution
        return {
            "success": True,
            "route": route_id,
            "pnl": 0.0,
            "mode": "SIMULATED"
        }


class RealTimeExecutionHub:
    """Real-time execution hub coordinating all executors.
    
    Routes execution requests to appropriate executor based on engine type.
    """
    
    def __init__(
        self,
        binary_executor: Optional[BinaryExecutor] = None,
        spot_executor: Optional[MT5SpotExecutor] = None,
        arb_executor: Optional[ArbitrageExecutor] = None
    ):
        """Initialize execution hub.
        
        Args:
            binary_executor: Binary options executor
            spot_executor: Spot forex executor
            arb_executor: Arbitrage executor
        """
        self.binary_executor = binary_executor or BinaryExecutor()
        self.spot_executor = spot_executor or MT5SpotExecutor()
        self.arb_executor = arb_executor or ArbitrageExecutor()
    
    def execute(self, decision: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade via appropriate executor.
        
        Args:
            decision: Trading decision with engine_type
            ctx: Execution context
        
        Returns:
            Execution result
        """
        engine_type = decision.get("engine_type", "none")
        
        if engine_type == "binary":
            return self.binary_executor.execute(decision, ctx)
        elif engine_type == "spot":
            return self.spot_executor.execute(decision, ctx)
        elif engine_type == "arbitrage":
            return self.arb_executor.execute(decision, ctx)
        else:
            return {
                "success": False,
                "error": "Unknown engine type",
                "pnl": 0.0,
                "mode": "NONE"
            }


class ShadowExecutionHub(RealTimeExecutionHub):
    """Shadow execution hub for simulation.
    
    Mirrors RealTimeExecutionHub interface but doesn't place real orders.
    Returns simulated results for testing and validation.
    """
    
    def execute(self, decision: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Execute trade in shadow mode (simulation only).
        
        Args:
            decision: Trading decision
            ctx: Execution context
        
        Returns:
            Simulated execution result
        """
        engine_type = decision.get("engine_type", "none")
        
        # Simulate different outcomes based on engine type
        if engine_type == "binary":
            # Simulate 60% win rate for binary
            import random
            win = random.random() < 0.6
            pnl = decision.get("stake", 1.0) * 0.8 if win else -decision.get("stake", 1.0)
            
            return {
                "success": True,
                "trade_id": "SHADOW_BIN",
                "pnl": pnl,
                "mode": "SHADOW"
            }
        
        elif engine_type == "spot":
            # Simulate average profit
            import random
            pnl = random.gauss(0, decision.get("tp", 0.01) * 0.5)
            
            return {
                "success": True,
                "order_id": "SHADOW_SPOT",
                "pnl": pnl,
                "mode": "SHADOW"
            }
        
        elif engine_type == "arbitrage":
            # Simulate small profit
            import random
            pnl = random.uniform(0, 0.01)
            
            return {
                "success": True,
                "route": decision.get("route_id", "default"),
                "pnl": pnl,
                "mode": "SHADOW"
            }
        
        return {
            "success": False,
            "error": "Unknown engine type",
            "pnl": 0.0,
            "mode": "SHADOW"
        }
