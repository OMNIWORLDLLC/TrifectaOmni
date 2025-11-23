"""Configuration management for Omni-Trifecta system."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv


class OmniConfig:
    """Central configuration manager for the Omni-Trifecta system.
    
    Loads configuration from environment variables and .env file.
    Provides centralized access to all system configuration parameters.
    """
    
    def __init__(self, env_path: Optional[str] = None):
        """Initialize configuration.
        
        Args:
            env_path: Optional path to .env file. If None, searches in current directory.
        """
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()
        
        # MT5 Configuration
        self.mt5_login = os.getenv("MT5_LOGIN")
        self.mt5_server = os.getenv("MT5_SERVER")
        self.mt5_password = os.getenv("MT5_PASSWORD")
        
        # Binary Options Platform
        self.pocket_token = os.getenv("POCKET_TOKEN")
        self.pocket_base_url = os.getenv("POCKET_BASE_URL", "https://api.po.trade")
        
        # DEX/Blockchain
        self.dex_rpc = os.getenv("DEX_RPC")
        self.dex_privkey = os.getenv("DEX_PRIVKEY")
        self.mev_relay_url = os.getenv("MEV_RELAY_URL")
        
        # Logging & Models
        self.log_dir = Path(os.getenv("OMNI_LOG_DIR", "runtime/logs"))
        self.seq_model_onnx = os.getenv("SEQ_MODEL_ONNX", "models/sequence_model.onnx")
        
        # Safety Limits
        self.max_daily_loss = float(os.getenv("MAX_DAILY_LOSS", "100.0"))
        self.max_daily_trades = int(os.getenv("MAX_DAILY_TRADES", "50"))
        self.max_loss_streak = int(os.getenv("MAX_LOSS_STREAK", "5"))
        
        # Ensure log directory exists
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_mt5(self) -> bool:
        """Check if MT5 configuration is complete."""
        return all([self.mt5_login, self.mt5_server, self.mt5_password])
    
    def validate_binary(self) -> bool:
        """Check if binary options configuration is complete."""
        return bool(self.pocket_token)
    
    def validate_dex(self) -> bool:
        """Check if DEX/blockchain configuration is complete."""
        return all([self.dex_rpc, self.dex_privkey])
    
    def validate_all(self) -> bool:
        """Check if all critical configuration is present."""
        return self.validate_mt5() and self.validate_binary() and self.validate_dex()
