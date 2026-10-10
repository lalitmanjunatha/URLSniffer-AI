"""Model loading and prediction utilities for URLSniffer.

This module provides a singleton class to load the trained model and scaler
from disk and make predictions on new URLs. It handles the case where the
model file does not yet exist (before training) by providing a clear error.
"""

from __future__ import annotations

import pickle
import threading
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

# Import our feature extraction modules
from .feature_extractor import extract_features_from_url, FEATURE_NAMES


class ModelPredictor:
    """Singleton class to load and use the trained model."""

    _instance: Optional["ModelPredictor"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "ModelPredictor":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._model: Optional[RandomForestClassifier] = None
                cls._instance._scaler: Optional[StandardScaler] = None
                cls._instance._metadata: Optional[Dict[str, Any]] = None
                cls._instance._loaded = False
        return cls._instance

    def load_model(self, model_path: str | Path) -> None:
        """Load the model and scaler from a pickle file.

        Parameters
        ----------
        model_path: str | Path
            Path to the pickle file containing the model, scaler, and metadata.

        Raises
        ------
        FileNotFoundError
            If the model file does not exist.
        RuntimeError
            If the file does not contain the expected objects or if the feature schema is incompatible.
        """
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found: {model_path}")

        try:
            with open(model_path, "rb") as f:
                data = pickle.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to load model file: {e}") from e

        # Validate the loaded data
        if not isinstance(data, dict):
            raise RuntimeError("Model file does not contain the expected dictionary.")

        required_keys = {"model", "scaler", "metadata"}
        if not required_keys.issubset(data.keys()):
            missing = required_keys - data.keys()
            raise RuntimeError(f"Model file is missing required keys: {missing}")

        # Validate the model and scaler types
        if not isinstance(data["model"], RandomForestClassifier):
            raise RuntimeError("Loaded model is not a RandomForestClassifier.")
        if not isinstance(data["scaler"], StandardScaler):
            raise RuntimeError("Loaded scaler is not a StandardScaler.")

        # Validate metadata
        metadata = data["metadata"]
        if not isinstance(metadata, dict):
            raise RuntimeError("Model metadata is not a dictionary.")
        if "feature_names" not in metadata:
            raise RuntimeError("Model metadata is missing feature_names.")

        # For backward compatibility, derive feature_count from feature_names if not present
        feature_count = metadata.get("feature_count", len(metadata["feature_names"]))

        # Check that the feature names match the canonical order
        expected_features = FEATURE_NAMES
        if metadata["feature_names"] != expected_features:
            raise RuntimeError(
                f"Feature schema mismatch. Expected {expected_features}, got {metadata['feature_names']}"
            )

        # Check that the feature count matches
        if feature_count != len(expected_features):
            raise RuntimeError(
                f"Feature count mismatch. Expected {len(expected_features)}, got {feature_count}"
            )

        # Assign the loaded objects
        self._model = data["model"]
        self._scaler = data["scaler"]
        self._metadata = metadata
        self._loaded = True

    def is_loaded(self) -> bool:
        """Return True if the model and scaler have been loaded."""
        return self._loaded

    def predict_url(self, url: str) -> Dict[str, Any]:
        """Predict whether a URL is phishing or legitimate.

        Parameters
        ----------
        url: str
            The URL to analyze.

        Returns
        -------
        dict
            Dictionary with keys:
            - ``is_phishing``: bool, True if the model predicts phishing.
            - ``probability``: float, probability of being phishing (if model supports predict_proba).
            - ``features``: dict, the extracted features for transparency.

        Raises
        ------
        RuntimeError
            If the model has not been loaded.
        ValueError
            If the URL is invalid (according to our validator).
        """
        if not self._loaded:
            raise RuntimeError("Model has not been loaded. Call load_model first.")

        # Validate URL
        from .url_validator import is_valid_url
        from app.core.logging_utils import sanitize_url_for_logging

        if not is_valid_url(url):
            # Sanitize URL for error message to avoid logging sensitive data
            sanitized_url = sanitize_url_for_logging(url)
            raise ValueError(f"Invalid URL: {sanitized_url}")

        # Extract features
        features = extract_features_from_url(url)
        feature_vector = np.array(
            [
                [
                    features[name] for name in FEATURE_NAMES
                ]
            ]
        )

        # Scale features
        assert self._scaler is not None  # for mypy
        feature_vector_scaled = self._scaler.transform(feature_vector)

        # Predict
        assert self._model is not None  # for mypy
        pred = self._model.predict(feature_vector_scaled)[0]
        # Try to get probability if available
        try:
            prob = self._model.predict_proba(feature_vector_scaled)[0][1]  # class 1 = phishing
        except AttributeError:
            # If the model doesn't have predict_proba, set to None
            prob = None

        return {
            "is_phishing": bool(pred),
            "probability": prob if prob is not None else None,
            "features": features,
        }


# Global singleton instance
model_predictor = ModelPredictor()


def load_model(model_path: str | Path) -> None:
    """Convenience function to load the model using the global predictor.

    Parameters
    ----------
    model_path: str | Path
        Path to the model pickle file.
    """
    model_predictor.load_model(Path(model_path))


def predict_url(url: str) -> Dict[str, Any]:
    """Convenience function to predict using the global predictor.

    Parameters
    ----------
    url: str
        The URL to analyze.

    Returns
    -------
    dict
        Prediction result.
    """
    return model_predictor.predict_url(url)