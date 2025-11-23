#!/usr/bin/env python3
"""Production-ready example with real broker and exchange integrations.

This demonstrates the full Trifecta system configured for real trading.
Start with shadow mode, then enable real execution when ready.
"""

import sys
import getpass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from omni_trifecta.core.config import OmniConfig
from omni_trifecta.data.price_feeds import create_price_feed
from omni_trifecta.decision.master_governor import MasterGovernorX100
from omni_trifecta.execution.executors import (
    BinaryExecutor,
    MT5SpotExecutor,
    ArbitrageExecutor,
    RealTimeExecutionHub,
    ShadowExecutionHub
)
from omni_trifecta.execution.brokers import create_broker_bridge
from omni_trifecta.learning.orchestrator import RLJSONStore
from omni_trifecta.safety.managers import SafetyManager, DeploymentChecklist
from omni_trifecta.runtime.logging import OmniLogger, DecisionAuditTrail, PerformanceRecorder
from omni_trifecta.runtime.orchestration import OmniRuntime, omni_main_loop


def main():
    """Main function for production execution."""
    print("=" * 70)
    print("OMNI-TRIFECTA QUANT ENGINE - Production Configuration")
    print("=" * 70)
    
    config = OmniConfig()
    
    checker = DeploymentChecklist(config)
    print("\nDeployment Readiness:")
    checker.print_report()
    
    print("\n" + "=" * 70)
    print("CONFIGURATION OPTIONS")
    print("=" * 70)
    
    print("\nData Sources Available:")
    print("  1. Binance (crypto spot/futures)")
    print("  2. CCXT (100+ exchanges)")
    print("  3. Alpaca (stocks, crypto)")
    print("  4. Oanda (forex)")
    print("  5. Polygon.io (stocks, forex, crypto)")
    print("  6. Forex.com (forex)")
    print("  7. Simulated (testing)")
    
    print("\nBroker Integrations Available:")
    print("  1. CCXT (universal exchange trading)")
    print("  2. Oanda (forex broker)")
    print("  3. Alpaca (stock/crypto broker)")
    print("  4. Binary Options (Pocket Option, IQ Option)")
    print("  5. Web3 (DEX arbitrage, flashloans)")
    
    print("\n" + "=" * 70)
    print("EXECUTION MODE SELECTION")
    print("=" * 70)
    
    mode = input("\nSelect mode (shadow/live): ").lower().strip()
    
    if mode not in ['shadow', 'live']:
        print("Invalid mode. Using shadow mode for safety.")
        mode = 'shadow'
    
    data_source = input("Select data source (binance/alpaca/oanda/simulated): ").lower().strip()
    
    if data_source not in ['binance', 'alpaca', 'oanda', 'simulated']:
        print("Invalid source. Using simulated.")
        data_source = 'simulated'
    
    symbol = input("Enter trading symbol (e.g., BTC/USDT, EUR_USD, AAPL): ").strip()
    if not symbol:
        symbol = "BTC/USDT"
    
    print("\n" + "=" * 70)
    print("INITIALIZING SYSTEM")
    print("=" * 70)
    
    print(f"\nMode: {mode.upper()}")
    print(f"Data Source: {data_source}")
    print(f"Symbol: {symbol}")
    
    governor = MasterGovernorX100(base_stake=1.0, max_stake=10.0)
    
    if mode == 'shadow':
        execution_hub = ShadowExecutionHub()
        print("✓ Shadow execution hub initialized (no real trades)")
    else:
        print("\nWARNING: LIVE MODE REQUIRES BROKER CONFIGURATION")
        print("Configure brokers in .env file with valid credentials")
        
        broker_type = input("Select broker (ccxt/oanda/alpaca): ").lower().strip()
        
        if broker_type == 'ccxt':
            exchange_id = input("Exchange ID (binance/kraken/etc): ").strip()
            api_key = getpass.getpass("API Key: ").strip()
            api_secret = getpass.getpass("API Secret: ").strip()
            
            broker_config = {
                'exchange_id': exchange_id,
                'api_key': api_key,
                'api_secret': api_secret,
                'testnet': True
            }
            broker = create_broker_bridge('ccxt', broker_config)
        
        elif broker_type == 'oanda':
            api_key = getpass.getpass("Oanda API Key: ").strip()
            account_id = input("Oanda Account ID: ").strip()
            
            broker_config = {
                'api_key': api_key,
                'account_id': account_id,
                'practice': True
            }
            broker = create_broker_bridge('oanda', broker_config)
        
        elif broker_type == 'alpaca':
            api_key = getpass.getpass("Alpaca API Key: ").strip()
            api_secret = getpass.getpass("Alpaca API Secret: ").strip()
            
            broker_config = {
                'api_key': api_key,
                'api_secret': api_secret,
                'paper': True
            }
            broker = create_broker_bridge('alpaca', broker_config)
        
        else:
            print("Invalid broker. Using shadow mode.")
            mode = 'shadow'
            execution_hub = ShadowExecutionHub()
        
        if mode == 'live':
            spot_executor = MT5SpotExecutor(mt5_bridge=broker)
            execution_hub = RealTimeExecutionHub(spot_executor=spot_executor)
            print("✓ Live execution hub initialized")
    
    rl_store = RLJSONStore(config.log_dir / "rl_state")
    logger = OmniLogger(config.log_dir)
    audit_trail = DecisionAuditTrail(config.log_dir)
    perf_recorder = PerformanceRecorder(config.log_dir)
    
    safety_manager = SafetyManager(
        max_daily_loss=50.0,
        max_daily_trades=100,
        max_loss_streak=5
    )
    
    runtime = OmniRuntime(
        governor=governor,
        execution_hub=execution_hub,
        rl_store=rl_store,
        logger=logger,
        audit_trail=audit_trail,
        perf_recorder=perf_recorder
    )
    
    if data_source == 'simulated':
        import numpy as np
        prices = [1.0 + i * 0.001 + np.random.normal(0, 0.005) for i in range(500)]
        feed_config = {'prices': prices, 'delay': 0.01}
    elif data_source == 'binance':
        feed_config = {}
    elif data_source == 'alpaca':
        api_key = input("Alpaca API Key (for data): ").strip()
        api_secret = input("Alpaca API Secret: ").strip()
        feed_config = {'api_key': api_key, 'api_secret': api_secret}
    elif data_source == 'oanda':
        api_key = input("Oanda API Key: ").strip()
        account_id = input("Oanda Account ID: ").strip()
        feed_config = {'api_key': api_key, 'account_id': account_id, 'practice': True}
    else:
        feed_config = {}
    
    price_feed = create_price_feed(data_source, symbol, feed_config)
    
    print("\n" + "=" * 70)
    print("STARTING EXECUTION")
    print("=" * 70)
    print("\nPress Ctrl+C to stop\n")
    
    omni_main_loop(
        price_feed=price_feed,
        symbol=symbol,
        runtime=runtime,
        safety_manager=safety_manager,
        starting_balance=1000.0,
        window_size=256
    )
    
    print("\n" + "=" * 70)
    print("SESSION COMPLETED")
    print("=" * 70)
    print(f"\nLogs saved to: {config.log_dir}")
    print(f"RL state saved to: {config.log_dir / 'rl_state'}")


if __name__ == "__main__":
    main()
