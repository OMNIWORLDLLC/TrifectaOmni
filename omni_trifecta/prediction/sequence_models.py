"""Predictive sequence intelligence models."""

from typing import List, Optional
import numpy as np


class SequenceModelEngine:
    """Base sequence model for directional and volatility prediction.
    
    Uses momentum-based logic for predictions. Can be extended with
    ONNX models for neural network predictions.
    """
    
    def __init__(self):
        """Initialize sequence model engine."""
        pass
    
    def predict_direction(self, window: List[float]) -> float:
        """Predict probability of upward movement.
        
        Args:
            window: List of recent prices
        
        Returns:
            Probability of upward movement [0.0, 1.0]
        """
        if len(window) < 2:
            return 0.5  # Neutral if insufficient data
        
        # Simple momentum-based probability
        momentum = window[-1] - window[0]
        std = np.std(window) if len(window) > 1 else 1.0
        
        # Normalize momentum to probability range
        normalized = 0.5 + (momentum / (2 * std + 1e-8))
        return np.clip(normalized, 0.0, 1.0)
    
    def predict_volatility(self, window: List[float]) -> float:
        """Predict volatility estimate.
        
        Args:
            window: List of recent prices
        
        Returns:
            Volatility estimate (standard deviation)
        """
        if len(window) < 2:
            return 0.0
        
        return float(np.std(window))


class ONNXSequenceAdapter(SequenceModelEngine):
    """ONNX Runtime adapter for neural sequence models.
    
    Extends SequenceModelEngine to use ONNX models for predictions.
    Falls back to base implementation if ONNX model fails.
    """
    
    def __init__(self, model_path: str):
        """Initialize ONNX adapter.
        
        Args:
            model_path: Path to ONNX model file
        """
        super().__init__()
        self.model_path = model_path
        self.session = None
        self._load_model()
    
    def _load_model(self):
        """Load ONNX model session."""
        try:
            import onnxruntime as ort
            self.session = ort.InferenceSession(self.model_path)
        except ImportError:
            print("Warning: onnxruntime not installed, using base model")
            self.session = None
        except Exception as e:
            print(f"Warning: Failed to load ONNX model: {e}")
            self.session = None
    
    def predict_direction(self, window: List[float]) -> float:
        """Predict direction using ONNX model.
        
        Args:
            window: List of recent prices
        
        Returns:
            Probability of upward movement [0.0, 1.0]
        """
        if self.session is None:
            return super().predict_direction(window)
        
        try:
            # Prepare input for ONNX model
            input_array = np.array(window, dtype=np.float32).reshape(1, -1)
            
            # Get input name from model
            input_name = self.session.get_inputs()[0].name
            
            # Run inference
            outputs = self.session.run(None, {input_name: input_array})
            
            # Assume first output is direction probability
            prob = float(outputs[0][0])
            return np.clip(prob, 0.0, 1.0)
        except Exception as e:
            print(f"ONNX prediction error: {e}, falling back to base model")
            return super().predict_direction(window)
    
    def predict_volatility(self, window: List[float]) -> float:
        """Predict volatility.
        
        For simplicity, uses base implementation. Can be extended to use
        ONNX model output if available.
        
        Args:
            window: List of recent prices
        
        Returns:
            Volatility estimate
        """
        return super().predict_volatility(window)


class DirectionPredictor:
    """Specialized direction predictor with confidence scoring."""
    
    def __init__(self, model: SequenceModelEngine):
        """Initialize direction predictor.
        
        Args:
            model: Sequence model engine
        """
        self.model = model
    
    def predict_with_confidence(self, window: List[float]) -> tuple[str, float, float]:
        """Predict direction with confidence score.
        
        Args:
            window: List of recent prices
        
        Returns:
            Tuple of (direction, probability, confidence)
        """
        prob = self.model.predict_direction(window)
        
        # Direction is UP if prob > 0.5, else DOWN
        direction = "UP" if prob > 0.5 else "DOWN"
        
        # Confidence is distance from neutral (0.5)
        confidence = abs(prob - 0.5) * 2.0
        
        return direction, prob, confidence
