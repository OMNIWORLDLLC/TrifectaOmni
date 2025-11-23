"""Safety and governance components."""

from typing import Dict, Any
from datetime import datetime, timedelta
import os

from ..core.config import OmniConfig


class SafetyManager:
    """Safety manager enforcing risk limits and cooldown periods.
    
    Prevents excessive losses and enforces trading limits.
    """
    
    def __init__(
        self,
        max_daily_loss: float = 100.0,
        max_daily_trades: int = 50,
        max_loss_streak: int = 5,
        cooldown_duration: int = 3600
    ):
        """Initialize safety manager.
        
        Args:
            max_daily_loss: Maximum allowed daily loss
            max_daily_trades: Maximum trades per day
            max_loss_streak: Maximum consecutive losses
            cooldown_duration: Cooldown duration in seconds
        """
        self.max_daily_loss = max_daily_loss
        self.max_daily_trades = max_daily_trades
        self.max_loss_streak = max_loss_streak
        self.cooldown_duration = cooldown_duration
        
        # State tracking
        self.daily_pnl = 0.0
        self.trades_count = 0
        self.loss_streak = 0
        self.cooldown_until = None
        self.last_reset = datetime.now()
    
    def can_trade(self) -> bool:
        """Check if trading is allowed.
        
        Returns:
            True if trading is allowed, False otherwise
        """
        # Reset daily counters if new day
        self._check_daily_reset()
        
        # Check cooldown
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            return False
        
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            self._trigger_cooldown("daily_loss_exceeded")
            return False
        
        # Check daily trades limit
        if self.trades_count >= self.max_daily_trades:
            self._trigger_cooldown("daily_trades_exceeded")
            return False
        
        # Check loss streak
        if self.loss_streak >= self.max_loss_streak:
            self._trigger_cooldown("loss_streak_exceeded")
            return False
        
        return True
    
    def register_trade(self, pnl: float):
        """Register a completed trade.
        
        Args:
            pnl: Trade profit/loss
        """
        self.daily_pnl += pnl
        self.trades_count += 1
        
        if pnl < 0:
            self.loss_streak += 1
        else:
            self.loss_streak = 0
    
    def _check_daily_reset(self):
        """Check if daily counters should be reset."""
        now = datetime.now()
        if (now - self.last_reset).days >= 1:
            self.daily_pnl = 0.0
            self.trades_count = 0
            self.loss_streak = 0
            self.last_reset = now
    
    def _trigger_cooldown(self, reason: str):
        """Trigger cooldown period.
        
        Args:
            reason: Reason for cooldown
        """
        self.cooldown_until = datetime.now() + timedelta(seconds=self.cooldown_duration)
        print(f"SAFETY COOLDOWN TRIGGERED: {reason}")
        print(f"Trading suspended until {self.cooldown_until}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current safety status.
        
        Returns:
            Dictionary with safety status information
        """
        return {
            "can_trade": self.can_trade(),
            "daily_pnl": self.daily_pnl,
            "trades_count": self.trades_count,
            "loss_streak": self.loss_streak,
            "cooldown_active": bool(self.cooldown_until and datetime.now() < self.cooldown_until),
            "cooldown_until": self.cooldown_until
        }


class DeploymentChecklist:
    """Deployment readiness checker.
    
    Verifies all critical configuration and dependencies before live trading.
    """
    
    def __init__(self, config: OmniConfig):
        """Initialize deployment checklist.
        
        Args:
            config: System configuration
        """
        self.config = config
    
    def verify(self) -> Dict[str, Any]:
        """Verify deployment readiness.
        
        Returns:
            Dictionary with verification results
        """
        checks = {}
        
        # Check MT5 configuration
        checks["mt5_configured"] = self.config.validate_mt5()
        
        # Check binary options configuration
        checks["binary_configured"] = self.config.validate_binary()
        
        # Check DEX configuration
        checks["dex_configured"] = self.config.validate_dex()
        
        # Check log directory
        checks["log_dir_accessible"] = self.config.log_dir.exists()
        
        # Check ONNX model (optional)
        checks["onnx_model_exists"] = os.path.exists(self.config.seq_model_onnx)
        
        # Overall status
        checks["all_passed"] = all([
            checks["mt5_configured"] or checks["binary_configured"] or checks["dex_configured"],
            checks["log_dir_accessible"]
        ])
        
        return checks
    
    def print_report(self):
        """Print deployment readiness report."""
        checks = self.verify()
        
        print("\n=== DEPLOYMENT READINESS CHECKLIST ===")
        print(f"MT5 Configured: {'✓' if checks['mt5_configured'] else '✗'}")
        print(f"Binary Configured: {'✓' if checks['binary_configured'] else '✗'}")
        print(f"DEX Configured: {'✓' if checks['dex_configured'] else '✗'}")
        print(f"Log Directory: {'✓' if checks['log_dir_accessible'] else '✗'}")
        print(f"ONNX Model: {'✓' if checks['onnx_model_exists'] else '✗ (optional)'}")
        print(f"\nOverall Status: {'READY' if checks['all_passed'] else 'NOT READY'}")
        print("=" * 40 + "\n")
        
        return checks["all_passed"]


class EmergencyShutdownController:
    """Emergency shutdown controller.
    
    Provides mechanisms for immediate system shutdown in critical situations.
    """
    
    def __init__(self):
        """Initialize emergency shutdown controller."""
        self.shutdown_triggered = False
        self.shutdown_reason = None
    
    def trigger_shutdown(self, reason: str):
        """Trigger emergency shutdown.
        
        Args:
            reason: Reason for shutdown
        """
        self.shutdown_triggered = True
        self.shutdown_reason = reason
        print(f"\n{'='*50}")
        print(f"EMERGENCY SHUTDOWN TRIGGERED")
        print(f"Reason: {reason}")
        print(f"{'='*50}\n")
    
    def should_shutdown(self) -> bool:
        """Check if shutdown has been triggered.
        
        Returns:
            True if shutdown is active
        """
        return self.shutdown_triggered
    
    def reset(self):
        """Reset shutdown state (use with caution)."""
        self.shutdown_triggered = False
        self.shutdown_reason = None
