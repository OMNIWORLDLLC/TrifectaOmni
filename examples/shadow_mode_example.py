#!/usr/bin/env python3
"""Example: Running the Omni-Trifecta system in shadow mode.

This script demonstrates running the system with simulated price data
in shadow mode (no real trades).
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from omni_trifecta.core.config import OmniConfig
from omni_trifecta.data.price_feeds import SimulatedPriceFeedAdapter
from omni_trifecta.decision.master_governor import MasterGovernorX100
from omni_trifecta.execution.executors import ShadowExecutionHub
from omni_trifecta.learning.orchestrator import RLJSONStore
from omni_trifecta.safety.managers import SafetyManager, DeploymentChecklist
from omni_trifecta.runtime.logging import OmniLogger, DecisionAuditTrail, PerformanceRecorder
from omni_trifecta.runtime.orchestration import OmniRuntime, omni_main_loop

import numpy as np


def generate_synthetic_prices(n_ticks: int = 1000, start_price: float = 1.1000) -> list[float]:
    """Generate synthetic price data for testing.
    
    Args:
        n_ticks: Number of price ticks to generate
        start_price: Starting price
    
    Returns:
        List of synthetic prices
    """
    prices = [start_price]
    
    for _ in range(n_ticks - 1):
        # Random walk with slight upward bias
        change = np.random.normal(0.0001, 0.0005)
        new_price = prices[-1] + change
        prices.append(max(new_price, 0.01))  # Prevent negative prices
    
    return prices


def main():
    """Main function to run shadow mode example."""
    print("=" * 70)
    print("OMNI-TRIFECTA QUANT ENGINE - Shadow Mode Example")
    print("=" * 70)
    
    # Load configuration
    config = OmniConfig()
    
    # Run deployment checklist
    checker = DeploymentChecklist(config)
    print("\nRunning deployment checklist...")
    checker.print_report()
    
    # Initialize components
    print("\nInitializing system components...")
    
    # Governor
    governor = MasterGovernorX100(base_stake=1.0, max_stake=10.0)
    
    # Shadow execution (no real trades)
    execution_hub = ShadowExecutionHub()
    
    # Persistence
    rl_store = RLJSONStore(config.log_dir / "rl_state")
    
    # Logging
    logger = OmniLogger(config.log_dir)
    audit_trail = DecisionAuditTrail(config.log_dir)
    perf_recorder = PerformanceRecorder(config.log_dir)
    
    # Safety manager
    safety_manager = SafetyManager(
        max_daily_loss=50.0,
        max_daily_trades=100,
        max_loss_streak=5
    )
    
    # Runtime
    runtime = OmniRuntime(
        governor=governor,
        execution_hub=execution_hub,
        rl_store=rl_store,
        logger=logger,
        audit_trail=audit_trail,
        perf_recorder=perf_recorder
    )
    
    # Generate synthetic price data
    print("\nGenerating synthetic price data...")
    prices = generate_synthetic_prices(n_ticks=500, start_price=1.1000)
    
    # Create price feed adapter
    price_feed = SimulatedPriceFeedAdapter(
        symbol="EURUSD",
        prices=prices,
        delay=0.01  # Fast simulation
    )
    
    # Run main loop
    print("\nStarting shadow mode execution...\n")
    
    omni_main_loop(
        price_feed=price_feed,
        symbol="EURUSD",
        runtime=runtime,
        safety_manager=safety_manager,
        starting_balance=1000.0,
        window_size=256
    )
    
    # Print performance summary
    print("\nPerformance Summary:")
    perf_summary = logger.get_performance_summary()
    print(f"  Total Trades: {perf_summary['total_trades']}")
    print(f"  Total PnL: ${perf_summary['total_pnl']:.2f}")
    print(f"  Win Rate: {perf_summary['win_rate']*100:.1f}%")
    print(f"  Average PnL: ${perf_summary['avg_pnl']:.4f}")
    
    # Print engine statistics
    print("\nEngine Statistics:")
    engine_stats = governor.regime_rl.get_stats()
    for engine, stats in engine_stats.items():
        print(f"  {engine.upper()}:")
        print(f"    Trades: {stats['count']}")
        print(f"    Total PnL: ${stats['total']:.2f}")
        print(f"    Avg PnL: ${stats['mean']:.4f}")
    
    print("\n" + "=" * 70)
    print("Shadow mode execution completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
