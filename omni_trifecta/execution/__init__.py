"""Execution layer module."""

from .executors import (
    ExecutorBase,
    BinaryExecutor,
    MT5SpotExecutor,
    ArbitrageExecutor,
    ForexExecutor,
    RealTimeExecutionHub,
    ShadowExecutionHub,
)
from .brokers import (
    BrokerBridge,
    CCXTBrokerBridge,
    OandaBrokerBridge,
    AlpacaBrokerBridge,
    BinaryOptionsBridge,
    Web3ArbitrageBridge,
    create_broker_bridge,
)
from .arbitrage_calculator import (
    MultiHopArbitrageCalculator,
    UniversalArbitrageCalculator,
    Exchange,
    TradingPair,
    ArbitrageRoute,
    FlashLoanParams,
    UniversalArbitrageResult,
    RouteType,
    CalculatorType,
    format_arbitrage_report,
    format_comparison_report,
)

__all__ = [
    # Executors
    "ExecutorBase",
    "BinaryExecutor",
    "MT5SpotExecutor",
    "ArbitrageExecutor",
    "RealTimeExecutionHub",
    "ShadowExecutionHub",
    # Brokers
    "BrokerBridge",
    "CCXTBrokerBridge",
    "OandaBrokerBridge",
    "AlpacaBrokerBridge",
    "BinaryOptionsBridge",
    "Web3ArbitrageBridge",
    "create_broker_bridge",
    # Arbitrage Calculators
    "MultiHopArbitrageCalculator",
    "UniversalArbitrageCalculator",
    "Exchange",
    "TradingPair",
    "ArbitrageRoute",
    "FlashLoanParams",
    "UniversalArbitrageResult",
    "RouteType",
    "CalculatorType",
    "format_arbitrage_report",
    "format_comparison_report",
]
