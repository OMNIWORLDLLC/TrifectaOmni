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
        
        # Check if in cooldown
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            return False
        
        # Check daily trade limit
        if self.trades_count >= self.max_daily_trades:
            return False
        
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            return False
        
        # Check loss streak
        if self.loss_streak >= self.max_loss_streak:
            return False
        
        return True
    
    def register_trade(self, pnl: float):
        """Register a completed trade and update tracking state.
        
        Args:
            pnl: Profit/loss from the trade
        """
        self._check_daily_reset()
        
        # Update trade count
        self.trades_count += 1
        
        # Update daily PnL
        self.daily_pnl += pnl
        
        # Update loss streak
        if pnl < 0:
            self.loss_streak += 1
        else:
            self.loss_streak = 0
        
        # Trigger cooldown if limits exceeded
        if (self.daily_pnl <= -self.max_daily_loss or 
            self.loss_streak >= self.max_loss_streak or
            self.trades_count >= self.max_daily_trades):
            self.cooldown_until = datetime.now() + timedelta(seconds=self.cooldown_duration)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current safety manager status.
        
        Returns:
            Dictionary with current safety status
        """
        self._check_daily_reset()
        
        return {
            'can_trade': self.can_trade(),
            'daily_pnl': self.daily_pnl,
            'trades_count': self.trades_count,
            'loss_streak': self.loss_streak,
            'max_daily_loss': self.max_daily_loss,
            'max_daily_trades': self.max_daily_trades,
            'max_loss_streak': self.max_loss_streak,
            'cooldown_until': self.cooldown_until.isoformat() if self.cooldown_until else None,
            'in_cooldown': self.cooldown_until is not None and datetime.now() < self.cooldown_until,
            'last_reset': self.last_reset.isoformat()
        }
    
    def check_trade_approval(
        self,
        asset: str,
        size: float,
        direction: str,
        current_portfolio_value: float
    ) -> Dict[str, Any]:
        """Check if trade meets risk requirements.
        
        Args:
            asset: Asset to trade
            size: Trade size in base currency
            direction: 'long' or 'short'
            current_portfolio_value: Current portfolio value
        
        Returns:
            Approval decision with approved flag and reason
        """
        # Check daily resets
        self._check_daily_reset()
        
        # Check if in cooldown
        if self.cooldown_until and datetime.now() < self.cooldown_until:
            return {
                'approved': False,
                'reason': f'In cooldown until {self.cooldown_until.strftime("%H:%M:%S")}',
                'risk_level': 'BLOCKED'
            }
        
        # Check daily trade limit
        if self.trades_count >= self.max_daily_trades:
            return {
                'approved': False,
                'reason': f'Daily trade limit reached: {self.trades_count}/{self.max_daily_trades}',
                'risk_level': 'BLOCKED'
            }
        
        # Check daily loss limit
        if self.daily_pnl <= -self.max_daily_loss:
            return {
                'approved': False,
                'reason': f'Daily loss limit reached: ${self.daily_pnl:.2f}',
                'risk_level': 'BLOCKED'
            }
        
        # Check loss streak
        if self.loss_streak >= self.max_loss_streak:
            return {
                'approved': False,
                'reason': f'Loss streak limit reached: {self.loss_streak} consecutive losses',
                'risk_level': 'BLOCKED'
            }
        
        # Check position size vs portfolio
        position_pct = (size / current_portfolio_value) * 100 if current_portfolio_value > 0 else 100
        if position_pct > 25.0:  # Max 25% per position
            return {
                'approved': False,
                'reason': f'Position size too large: {position_pct:.1f}% of portfolio',
                'risk_level': 'HIGH'
            }
        
        # Determine risk level
        if position_pct > 15.0 or self.loss_streak > 2:
            risk_level = 'HIGH'
        elif position_pct > 10.0 or self.loss_streak > 1:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        return {
            'approved': True,
            'reason': f'Trade approved - Risk: {risk_level}, Position: {position_pct:.1f}%',
            'risk_level': risk_level
        }
    
    def _check_daily_reset(self):
        """Check if daily counters need reset."""
        now = datetime.now()
        if now.date() > self.last_reset.date():
            self.daily_pnl = 0.0
            self.trades_count = 0
            self.loss_streak = 0
            self.cooldown_until = None
            self.last_reset = now


# Create alias for backward compatibility
# Create alias for backward compatibility
RiskManager = SafetyManager


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
