"""Advanced Order Management System (OMS) for tracking positions and P&L."""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIAL = "partial"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class OrderType(Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class OrderSide(Enum):
    """Order side enumeration for trade direction."""
    BUY = "buy"
    SELL = "sell"
    LONG = "long"
    SHORT = "short"


@dataclass
class Order:
    """Order representation."""
    order_id: str
    symbol: str
    side: str
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    average_fill_price: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    filled_timestamp: Optional[datetime] = None
    commission: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert order to dictionary."""
        return {
            'order_id': self.order_id,
            'symbol': self.symbol,
            'side': self.side,
            'order_type': self.order_type.value,
            'quantity': self.quantity,
            'price': self.price,
            'stop_price': self.stop_price,
            'status': self.status.value,
            'filled_quantity': self.filled_quantity,
            'average_fill_price': self.average_fill_price,
            'timestamp': self.timestamp.isoformat(),
            'filled_timestamp': self.filled_timestamp.isoformat() if self.filled_timestamp else None,
            'commission': self.commission,
            'metadata': self.metadata
        }


@dataclass
class Position:
    """Position representation."""
    symbol: str
    side: str
    quantity: float
    entry_price: float
    current_price: float
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    open_timestamp: datetime = field(default_factory=datetime.now)
    orders: List[Order] = field(default_factory=list)
    
    def update_price(self, current_price: float):
        """Update current price and recalculate unrealized P&L."""
        self.current_price = current_price
        
        if self.side == 'BUY' or self.side == 'LONG':
            self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
        else:
            self.unrealized_pnl = (self.entry_price - current_price) * self.quantity
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert position to dictionary."""
        return {
            'symbol': self.symbol,
            'side': self.side,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'unrealized_pnl': self.unrealized_pnl,
            'realized_pnl': self.realized_pnl,
            'open_timestamp': self.open_timestamp.isoformat(),
            'orders': [order.to_dict() for order in self.orders]
        }


class OrderManagementSystem:
    """Advanced Order Management System."""
    
    def __init__(self):
        """Initialize OMS."""
        self.orders: Dict[str, Order] = {}
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Dict[str, Any]] = []
        self.order_counter = 0
    
    def generate_order_id(self) -> str:
        """Generate unique order ID."""
        self.order_counter += 1
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"ORD-{timestamp}-{self.order_counter:06d}"
    
    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: OrderType,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Order:
        """Create new order."""
        order_id = self.generate_order_id()
        
        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            metadata=metadata or {}
        )
        
        self.orders[order_id] = order
        return order
    
    def fill_order(
        self,
        order_id: str,
        fill_price: float,
        fill_quantity: Optional[float] = None,
        commission: float = 0.0
    ):
        """Mark order as filled and update positions."""
        if order_id not in self.orders:
            raise ValueError(f"Order {order_id} not found")
        
        order = self.orders[order_id]
        fill_quantity = fill_quantity or order.quantity
        
        order.filled_quantity += fill_quantity
        order.average_fill_price = (
            (order.average_fill_price * (order.filled_quantity - fill_quantity) + 
             fill_price * fill_quantity) / order.filled_quantity
        )
        order.commission += commission
        order.filled_timestamp = datetime.now()
        
        if order.filled_quantity >= order.quantity:
            order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.PARTIAL
        
        self._update_position(order, fill_price, fill_quantity)
        
        self.trade_history.append({
            'timestamp': datetime.now().isoformat(),
            'order_id': order_id,
            'symbol': order.symbol,
            'side': order.side,
            'quantity': fill_quantity,
            'price': fill_price,
            'commission': commission
        })
    
    def _update_position(self, order: Order, fill_price: float, fill_quantity: float):
        """Update position based on filled order."""
        symbol = order.symbol
        
        if symbol in self.positions:
            position = self.positions[symbol]
            
            if (order.side == 'BUY' and position.side == 'BUY') or \
               (order.side == 'SELL' and position.side == 'SELL'):
                total_quantity = position.quantity + fill_quantity
                position.entry_price = (
                    (position.entry_price * position.quantity + 
                     fill_price * fill_quantity) / total_quantity
                )
                position.quantity = total_quantity
            
            elif (order.side == 'SELL' and position.side == 'BUY') or \
                 (order.side == 'BUY' and position.side == 'SELL'):
                if fill_quantity >= position.quantity:
                    realized_pnl = (fill_price - position.entry_price) * position.quantity
                    if position.side == 'SELL':
                        realized_pnl = -realized_pnl
                    
                    position.realized_pnl += realized_pnl
                    
                    remaining = fill_quantity - position.quantity
                    if remaining > 0:
                        position.side = order.side
                        position.quantity = remaining
                        position.entry_price = fill_price
                    else:
                        del self.positions[symbol]
                else:
                    realized_pnl = (fill_price - position.entry_price) * fill_quantity
                    if position.side == 'SELL':
                        realized_pnl = -realized_pnl
                    
                    position.realized_pnl += realized_pnl
                    position.quantity -= fill_quantity
            
            if symbol in self.positions:
                position.orders.append(order)
        
        else:
            position = Position(
                symbol=symbol,
                side=order.side,
                quantity=fill_quantity,
                entry_price=fill_price,
                current_price=fill_price,
                orders=[order]
            )
            self.positions[symbol] = position
    
    def cancel_order(self, order_id: str):
        """Cancel pending order."""
        if order_id not in self.orders:
            raise ValueError(f"Order {order_id} not found")
        
        order = self.orders[order_id]
        if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
            return
        
        order.status = OrderStatus.CANCELLED
    
    def get_position(self, symbol: str) -> Optional[Position]:
        """Get current position for symbol."""
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> List[Position]:
        """Get all open positions."""
        return list(self.positions.values())
    
    def update_market_price(self, symbol: str, current_price: float):
        """Update market price for position."""
        if symbol in self.positions:
            self.positions[symbol].update_price(current_price)
    
    def get_total_unrealized_pnl(self) -> float:
        """Get total unrealized P&L across all positions."""
        return sum(pos.unrealized_pnl for pos in self.positions.values())
    
    def get_total_realized_pnl(self) -> float:
        """Get total realized P&L from closed positions."""
        return sum(pos.realized_pnl for pos in self.positions.values())
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all open orders, optionally filtered by symbol."""
        orders = [
            order for order in self.orders.values()
            if order.status in [OrderStatus.PENDING, OrderStatus.PARTIAL]
        ]
        
        if symbol:
            orders = [order for order in orders if order.symbol == symbol]
        
        return orders
    
    def get_filled_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get all filled orders, optionally filtered by symbol."""
        orders = [
            order for order in self.orders.values()
            if order.status == OrderStatus.FILLED
        ]
        
        if symbol:
            orders = [order for order in orders if order.symbol == symbol]
        
        return orders
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get comprehensive portfolio summary."""
        total_unrealized = self.get_total_unrealized_pnl()
        total_realized = self.get_total_realized_pnl()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'open_positions': len(self.positions),
            'total_unrealized_pnl': total_unrealized,
            'total_realized_pnl': total_realized,
            'total_pnl': total_unrealized + total_realized,
            'positions': [pos.to_dict() for pos in self.positions.values()],
            'open_orders': len(self.get_open_orders()),
            'filled_orders': len(self.get_filled_orders()),
            'total_trades': len(self.trade_history)
        }
    
    def calculate_position_metrics(self, symbol: str) -> Dict[str, Any]:
        """Calculate detailed metrics for a position."""
        position = self.get_position(symbol)
        if not position:
            return {}
        
        filled_orders = [
            order for order in position.orders
            if order.status == OrderStatus.FILLED
        ]
        
        if not filled_orders:
            return {}
        
        total_commission = sum(order.commission for order in filled_orders)
        
        hold_duration = (datetime.now() - position.open_timestamp).total_seconds() / 3600
        
        pnl_percentage = (position.unrealized_pnl / (position.entry_price * position.quantity)) * 100 if position.entry_price * position.quantity > 0 else 0
        
        return {
            'symbol': symbol,
            'pnl': position.unrealized_pnl + position.realized_pnl,
            'pnl_percentage': pnl_percentage,
            'total_commission': total_commission,
            'hold_duration_hours': hold_duration,
            'number_of_trades': len(filled_orders),
            'average_entry_price': position.entry_price,
            'current_price': position.current_price
        }
    
    def export_trade_history(self, filepath: str):
        """Export trade history to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.trade_history, f, indent=2)
    
    def export_portfolio_snapshot(self, filepath: str):
        """Export current portfolio snapshot to JSON file."""
        summary = self.get_portfolio_summary()
        with open(filepath, 'w') as f:
            json.dump(summary, f, indent=2)
