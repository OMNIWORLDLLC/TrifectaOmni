"""Logging and observability components."""

from typing import Dict, Any
from pathlib import Path
import json
from datetime import datetime


def _json_serializer(obj):
    """Custom JSON serializer for non-serializable objects.
    
    Args:
        obj: Object to serialize
    
    Returns:
        Serializable version of object
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    else:
        return str(obj)


class OmniLogger:
    """Centralized logger for ticks, trades, and system events.
    
    Writes JSONL (JSON Lines) format for easy parsing and analysis.
    """
    
    def __init__(self, log_dir: Path):
        """Initialize Omni logger.
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file paths
        self.ticks_file = self.log_dir / "ticks.jsonl"
        self.trades_file = self.log_dir / "trades.jsonl"
        self.events_file = self.log_dir / "events.jsonl"
    
    def log_tick(self, symbol: str, price: float, timestamp: datetime = None):
        """Log a price tick.
        
        Args:
            symbol: Trading symbol
            price: Price value
            timestamp: Timestamp (uses current time if None)
        """
        timestamp = timestamp or datetime.now()
        
        record = {
            "timestamp": timestamp.isoformat(),
            "symbol": symbol,
            "price": price
        }
        
        self._write_jsonl(self.ticks_file, record)
    
    def log_trade(self, trade_record: Dict[str, Any]):
        """Log a trade execution.
        
        Args:
            trade_record: Dictionary with trade information
        """
        if "timestamp" not in trade_record:
            trade_record["timestamp"] = datetime.now().isoformat()
        
        self._write_jsonl(self.trades_file, trade_record)
    
    def log_event(self, event_type: str, details: Dict[str, Any]):
        """Log a system event.
        
        Args:
            event_type: Type of event (e.g., "SAFETY_TRIGGERED", "MODEL_UPDATED")
            details: Event details
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        }
        
        self._write_jsonl(self.events_file, record)
    
    def _write_jsonl(self, filepath: Path, record: Dict[str, Any]):
        """Write a JSON record to file.
        
        Args:
            filepath: Path to log file
            record: Dictionary to write
        """
        with open(filepath, "a") as f:
            f.write(json.dumps(record, default=_json_serializer) + "\n")
    
    def get_recent_trades(self, limit: int = 100) -> list[Dict[str, Any]]:
        """Get recent trade records.
        
        Args:
            limit: Maximum number of trades to return
        
        Returns:
            List of trade records
        """
        if not self.trades_file.exists():
            return []
        
        trades = []
        with open(self.trades_file, "r") as f:
            for line in f:
                try:
                    trades.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        
        return trades[-limit:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from trade logs.
        
        Returns:
            Dictionary with performance metrics
        """
        trades = self.get_recent_trades(limit=1000)
        
        if not trades:
            return {
                "total_trades": 0,
                "total_pnl": 0.0,
                "win_rate": 0.0,
                "avg_pnl": 0.0
            }
        
        total_pnl = sum(t.get("pnl", 0.0) for t in trades)
        wins = sum(1 for t in trades if t.get("pnl", 0.0) > 0)
        
        return {
            "total_trades": len(trades),
            "total_pnl": total_pnl,
            "win_rate": wins / len(trades) if trades else 0.0,
            "avg_pnl": total_pnl / len(trades) if trades else 0.0
        }


class DecisionAuditTrail:
    """Audit trail for decision-making process.
    
    Tracks the complete decision chain for analysis and debugging.
    """
    
    def __init__(self, log_dir: Path):
        """Initialize decision audit trail.
        
        Args:
            log_dir: Directory for audit logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.audit_file = self.log_dir / "decision_audit.jsonl"
    
    def log_decision(
        self,
        decision: Dict[str, Any],
        regime_state: Any,
        fib_block: Dict[str, Any]
    ):
        """Log a complete decision with all contributing factors.
        
        Args:
            decision: Final decision
            regime_state: Regime state at decision time
            fib_block: Fibonacci analysis block
        """
        # Convert RegimeState to dict if needed
        if hasattr(regime_state, 'vol_score'):
            regime_dict = {
                "vol_score": regime_state.vol_score,
                "trend_strength": regime_state.trend_strength,
                "mean_reversion_score": regime_state.mean_reversion_score
            }
        else:
            regime_dict = None
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "decision": {
                k: v for k, v in decision.items() 
                if k != "regime_state"  # Skip non-serializable nested state
            },
            "regime_state": regime_dict,
            "fib_analysis": {
                "wave_state": fib_block.get("wave_state"),
                "volatility_score": fib_block.get("volatility_score"),
                "final_decision": fib_block.get("final_decision")
            }
        }
        
        with open(self.audit_file, "a") as f:
            f.write(json.dumps(record, default=_json_serializer) + "\n")


class PerformanceRecorder:
    """Performance metrics recorder.
    
    Tracks detailed performance metrics for analysis and optimization.
    """
    
    def __init__(self, log_dir: Path):
        """Initialize performance recorder.
        
        Args:
            log_dir: Directory for performance logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.perf_file = self.log_dir / "performance.jsonl"
    
    def record_metrics(
        self,
        balance: float,
        equity_curve: list[float],
        engine_stats: Dict[str, Any],
        safety_status: Dict[str, Any]
    ):
        """Record performance metrics snapshot.
        
        Args:
            balance: Current balance
            equity_curve: Recent equity curve points
            engine_stats: Engine performance statistics
            safety_status: Safety manager status
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "balance": balance,
            "equity_curve": equity_curve,
            "engine_stats": engine_stats,
            "safety_status": safety_status
        }
        
        with open(self.perf_file, "a") as f:
            f.write(json.dumps(record, default=_json_serializer) + "\n")
    
    def get_equity_curve(self) -> list[tuple[str, float]]:
        """Get equity curve from performance logs.
        
        Returns:
            List of (timestamp, balance) tuples
        """
        if not self.perf_file.exists():
            return []
        
        equity_curve = []
        with open(self.perf_file, "r") as f:
            for line in f:
                try:
                    record = json.loads(line)
                    equity_curve.append((
                        record["timestamp"],
                        record["balance"]
                    ))
                except (json.JSONDecodeError, KeyError):
                    continue
        
        return equity_curve
