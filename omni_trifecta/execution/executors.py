"""Execution engines for different trading modes."""

from typing import Dict, Any, Callable, Optional, TYPE_CHECKING
from abc import ABC, abstractmethod
import random
import logging

# Type hints for OMS integration
if TYPE_CHECKING:
    from .oms import OrderManagementSystem, OrderType, OrderStatus

# Get logger for this module
logger = logging.getLogger(__name__)


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
    Integrates with Order Management System for position tracking.
    """
    
    def __init__(
        self,
        binary_executor: Optional[BinaryExecutor] = None,
        spot_executor: Optional[MT5SpotExecutor] = None,
        arb_executor: Optional[ArbitrageExecutor] = None,
        oms: Optional['OrderManagementSystem'] = None
    ):
        """Initialize execution hub.
        
        Args:
            binary_executor: Binary options executor
            spot_executor: Spot forex executor
            arb_executor: Arbitrage executor
            oms: Order Management System for position tracking
        """
        self.binary_executor = binary_executor or BinaryExecutor()
        self.spot_executor = spot_executor or MT5SpotExecutor()
        self.arb_executor = arb_executor or ArbitrageExecutor()
        self.oms = oms
    
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
            result = self.binary_executor.execute(decision, ctx)
        elif engine_type == "spot":
            result = self.spot_executor.execute(decision, ctx)
        elif engine_type == "arbitrage":
            result = self.arb_executor.execute(decision, ctx)
        else:
            return {
                "success": False,
                "error": "Unknown engine type",
                "pnl": 0.0,
                "mode": "NONE"
            }
        
        # Update OMS if available and trade was successful
        if self.oms and result.get("success"):
            self._update_oms(decision, result)
        
        return result
    
    def _update_oms(self, decision: Dict[str, Any], result: Dict[str, Any]):
        """Update Order Management System with trade result.
        
        Args:
            decision: Trading decision
            result: Execution result
        """
        try:
            from .oms import OrderType
            
            symbol = decision.get("symbol", "UNKNOWN")
            engine_type = decision.get("engine_type")
            
            if engine_type == "spot":
                direction = decision.get("direction", "BUY")
                volume = decision.get("volume", 0.01)
                
                # Create and fill order
                order = self.oms.create_order(
                    symbol=symbol,
                    side=direction,
                    order_type=OrderType.MARKET,
                    quantity=volume,
                    metadata={"engine_type": engine_type}
                )
                
                if result.get("success"):
                    self.oms.fill_order(
                        order_id=order.order_id,
                        fill_price=decision.get("entry_price", 0),
                        commission=0.0
                    )
        except ImportError as e:
            logger.debug(f"OMS import not available: {e}")
        except ValueError as e:
            logger.warning(f"OMS order validation failed: {e}")
        except Exception as e:
            # OMS update is non-critical, log and continue
            logger.debug(f"OMS update failed (non-critical): {e}")


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
            pnl = random.gauss(0, decision.get("tp", 0.01) * 0.5)
            
            return {
                "success": True,
                "order_id": "SHADOW_SPOT",
                "pnl": pnl,
                "mode": "SHADOW"
            }
        
        elif engine_type == "arbitrage":
            # Simulate small profit
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


class ArbitrageExecutor(ExecutorBase):
    """Arbitrage trade executor for paper trading."""
    
    def __init__(self, oms=None, risk_manager=None, mode='paper'):
        """Initialize arbitrage executor.
        
        Args:
            oms: Order management system
            risk_manager: Risk manager
            mode: Execution mode ('paper' or 'live')
        """
        self.oms = oms
        self.risk_manager = risk_manager
        self.mode = mode
    
    async def execute_paper_trade(self, route: str, asset: str, capital: float, 
                                  expected_profit: float, buy_exchange: str = None, 
                                  sell_exchange: str = None) -> Dict[str, Any]:
        """Execute paper arbitrage trade.
        
        Args:
            route: Route type (2-HOP, 3-HOP, BRIDGE)
            asset: Asset symbol
            capital: Capital to use
            expected_profit: Expected profit
            buy_exchange: Buy exchange name
            sell_exchange: Sell exchange name
        
        Returns:
            Execution result with PnL
        """
        # Simulate execution with small variance
        actual_profit = expected_profit * random.uniform(0.85, 1.0)
        
        return {
            'success': True,
            'execution_id': f"ARB_{random.randint(10000, 99999)}",
            'route': route,
            'asset': asset,
            'capital': capital,
            'pnl': actual_profit,
            'buy_exchange': buy_exchange,
            'sell_exchange': sell_exchange,
            'mode': self.mode
        }
    
    def execute(self, decision: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Execute arbitrage trade (sync version).
        
        Args:
            decision: Trading decision
            ctx: Execution context
        
        Returns:
            Execution result
        """
        # Simulate small profit
        pnl = random.uniform(0, 0.01) * decision.get('capital', 10000.0)
        
        return {
            'success': True,
            'route': decision.get('route', 'default'),
            'pnl': pnl,
            'mode': self.mode
        }


class ForexExecutor(ExecutorBase):
    """Forex trade executor for paper trading."""
    
    def __init__(self, oms=None, risk_manager=None, mode='paper'):
        """Initialize forex executor.
        
        Args:
            oms: Order management system
            risk_manager: Risk manager
            mode: Execution mode ('paper' or 'live')
        """
        self.oms = oms
        self.risk_manager = risk_manager
        self.mode = mode
    
    async def execute_paper_trade(self, pair: str, signal: str, entry_price: float,
                                  take_profit: float, stop_loss: float, 
                                  size: float) -> Dict[str, Any]:
        """Execute paper forex trade.
        
        Args:
            pair: Currency pair
            signal: BUY or SELL
            entry_price: Entry price
            take_profit: Take profit level
            stop_loss: Stop loss level
            size: Position size
        
        Returns:
            Execution result with PnL
        """
        # Simulate outcome based on risk/reward
        risk = abs(entry_price - stop_loss)
        reward = abs(take_profit - entry_price)
        
        # 60% win rate simulation
        win = random.random() < 0.6
        
        if win:
            pnl = size * (reward / entry_price)
        else:
            pnl = -size * (risk / entry_price)
        
        return {
            'success': True,
            'execution_id': f"FX_{random.randint(10000, 99999)}",
            'pair': pair,
            'signal': signal,
            'entry': entry_price,
            'size': size,
            'pnl': pnl,
            'outcome': 'WIN' if win else 'LOSS',
            'mode': self.mode
        }
    
    def execute(self, decision: Dict[str, Any], ctx: Dict[str, Any]) -> Dict[str, Any]:
        """Execute forex trade (sync version).
        
        Args:
            decision: Trading decision
            ctx: Execution context
        
        Returns:
            Execution result
        """
        # Simulate outcome
        size = decision.get('size', 10000.0)
        risk_pct = decision.get('risk', 0.02)
        
        # 60% win rate
        win = random.random() < 0.6
        pnl = size * risk_pct * (2.0 if win else -1.0)
        
        return {
            'success': True,
            'pair': decision.get('pair', 'UNKNOWN'),
            'pnl': pnl,
            'mode': self.mode
        }
