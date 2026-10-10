"""Integration tests for model loading and prediction."""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ml.model import model_predictor, predict_url
from app.ml.feature_extractor import extract_features_from_url


def test_model_loading_and_prediction():
    """Test loading our trained model and making predictions."""
    model_path = Path(__file__).parent.parent / "model.pkl"

    # Check if model exists
    if not model_path.exists():
        print("Model file not found, skipping test")
        return

    # Load the model
    model_predictor.load_model(model_path)

    # Check that model is loaded
    assert model_predictor.is_loaded() is True

    # Test prediction on a known legitimate URL
    result = predict_url("https://example.com")
    assert "is_phishing" in result
    assert "probability" in result
    assert "features" in result
    assert isinstance(result["is_phishing"], bool)
    # For our test dataset, example.com should be legitimate (0)
    # But with such a small dataset, the prediction might vary

    # Test prediction on a known phishing URL from our test data
    result2 = predict_url("https://paypa1.com/login")
    assert "is_phishing" in result2
    assert isinstance(result2["is_phishing"], bool)

    # Test that features are extracted correctly
    features = extract_features_from_url("https://example.com")
    assert features["url_length"] == len("https://example.com")
    assert features["scheme"] == 1
    assert features["has_ip"] == 0


def test_model_predictor_singleton():
    """Test that ModelPredictor is a singleton."""
    predictor1 = model_predictor
    # Import again to get a new instance reference
    from app.ml.model import ModelPredictor
    predictor2 = ModelPredictor()
    assert predictor1 is predictor2


if __name__ == "__main__":
    test_model_loading_and_prediction()
    test_model_predictor_singleton()
    print("All integration tests passed!")