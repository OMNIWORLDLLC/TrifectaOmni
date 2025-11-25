"""Learning, persistence, and evolution components."""

from typing import Dict, Any, Callable, List
from pathlib import Path
import json
import shutil

from ..decision.rl_agents import RegimeSwitchingRL, ArbitrageRLAgent


class RLJSONStore:
    """JSON-based persistence for RL agents.
    
    Saves and loads RL state to/from JSON files.
    """
    
    def __init__(self, storage_dir: Path):
        """Initialize RL JSON store.
        
        Args:
            storage_dir: Directory for storing RL state files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
    
    def save_regime(self, regime_rl: RegimeSwitchingRL, filename: str = "regime_rl.json"):
        """Save regime switching RL state.
        
        Args:
            regime_rl: Regime switching RL agent
            filename: Output filename
        """
        filepath = self.storage_dir / filename
        
        state = {
            "q_table": regime_rl.q_table,
            "engine_performance": {
                k: v for k, v in regime_rl.engine_performance.items()
            },
            "learning_rate": regime_rl.learning_rate,
            "discount": regime_rl.discount,
            "epsilon": regime_rl.epsilon
        }
        
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)
    
    def load_regime(self, filename: str = "regime_rl.json") -> Dict[str, Any]:
        """Load regime switching RL state.
        
        Args:
            filename: Input filename
        
        Returns:
            Dictionary with RL state
        """
        filepath = self.storage_dir / filename
        
        if not filepath.exists():
            return {}
        
        with open(filepath, "r") as f:
            return json.load(f)
    
    def save_routes(self, arb_rl: ArbitrageRLAgent, filename: str = "arb_routes.json"):
        """Save arbitrage routes state.
        
        Args:
            arb_rl: Arbitrage RL agent
            filename: Output filename
        """
        filepath = self.storage_dir / filename
        
        state = {
            "route_scores": arb_rl.route_scores,
            "learning_rate": arb_rl.learning_rate
        }
        
        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)
    
    def load_routes(self, filename: str = "arb_routes.json") -> Dict[str, Any]:
        """Load arbitrage routes state.
        
        Args:
            filename: Input filename
        
        Returns:
            Dictionary with route scores
        """
        filepath = self.storage_dir / filename
        
        if not filepath.exists():
            return {}
        
        with open(filepath, "r") as f:
            return json.load(f)


class TrainingOrchestrator:
    """Orchestrates retraining and RL updates.
    
    Coordinates learning from trade logs and model retraining.
    """
    
    def __init__(self, log_dir: Path):
        """Initialize training orchestrator.
        
        Args:
            log_dir: Directory containing trade logs
        """
        self.log_dir = Path(log_dir)
    
    def update_rl_from_trades(
        self,
        regime_rl: RegimeSwitchingRL,
        arb_rl: ArbitrageRLAgent
    ) -> Dict[str, Any]:
        """Update RL agents from trade logs.
        
        Args:
            regime_rl: Regime switching RL agent
            arb_rl: Arbitrage RL agent
        
        Returns:
            Update statistics
        """
        trades_file = self.log_dir / "trades.jsonl"
        
        if not trades_file.exists():
            return {"trades_processed": 0, "errors": 0}
        
        trades_processed = 0
        total_pnl = 0.0
        errors = 0
        engine_pnl = {"binary": 0.0, "spot": 0.0, "arbitrage": 0.0}
        engine_counts = {"binary": 0, "spot": 0, "arbitrage": 0}
        
        with open(trades_file, "r") as f:
            for line in f:
                try:
                    trade = json.loads(line)
                    
                    # Extract relevant fields
                    engine = trade.get("engine_type")
                    pnl = trade.get("pnl", 0.0)
                    route_id = trade.get("route_id")
                    
                    # Skip if no engine type
                    if not engine:
                        continue
                    
                    # Update arbitrage RL if applicable
                    if engine == "arbitrage" and route_id:
                        arb_rl.update_route(route_id, pnl)
                    
                    # Track engine performance for regime RL
                    if engine in engine_pnl:
                        engine_pnl[engine] += pnl
                        engine_counts[engine] += 1
                        # Update regime RL performance tracking
                        regime_rl.engine_performance[engine].append(pnl)
                    
                    trades_processed += 1
                    total_pnl += pnl
                    
                except json.JSONDecodeError:
                    errors += 1
                    continue
                except Exception as e:
                    errors += 1
                    continue
        
        return {
            "trades_processed": trades_processed,
            "total_pnl": total_pnl,
            "avg_pnl": total_pnl / trades_processed if trades_processed > 0 else 0.0,
            "engine_pnl": engine_pnl,
            "engine_counts": engine_counts,
            "errors": errors
        }
    
    def retrain_sequence_model(
        self,
        trainer_callback: Callable[[List[float]], str]
    ) -> str:
        """Retrain sequence model from tick history.
        
        Args:
            trainer_callback: Callback function that trains model and returns new ONNX path
        
        Returns:
            Path to new ONNX model
        """
        ticks_file = self.log_dir / "ticks.jsonl"
        
        if not ticks_file.exists():
            raise FileNotFoundError("No tick history found for training")
        
        # Load tick prices
        prices = []
        with open(ticks_file, "r") as f:
            for line in f:
                try:
                    tick = json.loads(line)
                    prices.append(tick.get("price", 0.0))
                except json.JSONDecodeError:
                    continue
        
        if len(prices) < 1000:
            raise ValueError("Insufficient tick history for training (need at least 1000)")
        
        # Call external trainer
        new_model_path = trainer_callback(prices)
        
        return new_model_path
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get statistics on available training data.
        
        Returns:
            Dictionary with training data statistics
        """
        ticks_file = self.log_dir / "ticks.jsonl"
        trades_file = self.log_dir / "trades.jsonl"
        
        stats = {
            "ticks_available": 0,
            "trades_available": 0
        }
        
        if ticks_file.exists():
            with open(ticks_file, "r") as f:
                stats["ticks_available"] = sum(1 for _ in f)
        
        if trades_file.exists():
            with open(trades_file, "r") as f:
                stats["trades_available"] = sum(1 for _ in f)
        
        return stats


class ModelMutationController:
    """Controller for model evolution and mutation.
    
    Manages model versioning and controlled experimentation.
    """
    
    def __init__(self, models_dir: Path):
        """Initialize model mutation controller.
        
        Args:
            models_dir: Directory for storing model versions
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.current_version = 0
    
    def register_model(self, model_path: str, performance_score: float) -> str:
        """Register a new model version.
        
        Args:
            model_path: Path to model file
            performance_score: Performance metric
        
        Returns:
            Versioned model identifier
        """
        self.current_version += 1
        version_id = f"v{self.current_version}_{int(performance_score * 1000)}"
        
        # Copy model to versioned location
        dest_path = self.models_dir / f"model_{version_id}.onnx"
        shutil.copy(model_path, dest_path)
        
        # Save metadata
        metadata = {
            "version": self.current_version,
            "performance_score": performance_score,
            "timestamp": str(Path(model_path).stat().st_mtime)
        }
        
        metadata_path = self.models_dir / f"model_{version_id}.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        return version_id
    
    def get_best_model(self) -> str:
        """Get path to best performing model.
        
        Returns:
            Path to best model
        """
        # Find all model metadata files
        metadata_files = list(self.models_dir.glob("model_v*.json"))
        
        if not metadata_files:
            return None
        
        best_score = -float("inf")
        best_model = None
        
        for metadata_file in metadata_files:
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                score = metadata.get("performance_score", 0.0)
                
                if score > best_score:
                    best_score = score
                    best_model = str(metadata_file).replace(".json", ".onnx")
        
        return best_model
