"""Training pipeline for URLSniffer phishing detection model.

This script provides a simple training pipeline that:
1. Loads a CSV dataset with URLs and labels (supports both UCI PhiUSIIL format and the legacy format)
2. Extracts features using the deterministic feature extractor
3. Trains a scikit-learn classifier
4. Evaluates the model
5. Saves the trained model and feature information

The script is designed to work with a CSV file that has at least two columns:
- For UCI PhiUSIIL dataset: 'URL' and 'label' (where label 1 = legitimate, 0 = phishing)
- For legacy format: 'url' and 'label' (where label 0 = legitimate, 1 = phishing)

The script automatically handles the label mapping for the UCI dataset.

Usage:
    python train_model.py --data path/to/dataset.csv --model-output path/to/model.pkl

The script creates:
- A trained model (pickle file)
- Metadata about the features used
"""

from __future__ import annotations

import argparse
import json
import pickle
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Import our feature extraction modules
sys.path.append(str(Path(__file__).parent.parent))
from app.ml.feature_extractor import extract_features_from_url, FEATURE_NAMES
from app.ml.url_validator import is_valid_url


def load_and_validate_data(csv_path: Path) -> pd.DataFrame:
    """Load and validate the dataset CSV.

    Parameters
    ----------
    csv_path: Path
        Path to the CSV file containing URL and label columns.

    Returns
    -------
    pd.DataFrame
        DataFrame with validated URLs and labels (columns: 'URL', 'label').
        Label: 0 for legitimate, 1 for phishing.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {csv_path}")

    # Read CSV
    df = pd.read_csv(csv_path)

    # Check for UCI PhiUSIIL format: columns 'URL' and 'label' (note: label is lowercase)
    if 'URL' in df.columns and 'label' in df.columns:
        # UCI dataset: label 1 = legitimate, 0 = phishing
        # We need to convert to our format: 0 = legitimate, 1 = phishing
        df = df[['URL', 'label']].copy()
        # Label is already 0=phishing, 1=legitimate in UCI format, but we want 0=legitimate, 1=phishing
        # So we need to invert: 1->0, 0->1
        df['label'] = df['label'].apply(lambda x: 1 - int(x))  # invert: 1->0, 0->1
        df = df[['URL', 'label']]
        # URL column is already named correctly
    # Check for legacy format: columns 'url' and 'label'
    elif 'url' in df.columns and 'label' in df.columns:
        df = df[['url', 'label']].copy()
        df = df.rename(columns={'url': 'URL'})
        # Ensure label is integer and in {0,1}
        df['label'] = df['label'].astype(int)
    else:
        raise ValueError(
            "CSV must have either 'URL' and 'label' (UCI format) or 'url' and 'label' (legacy format)"
        )

    # Validate URLs: keep only syntactically valid URLs (without network requests)
    # Note: is_valid_url does not make network calls, it only checks syntax
    valid_mask = df['URL'].apply(is_valid_url)
    removed_invalid = (~valid_mask).sum()
    if removed_invalid > 0:
        print(f"Removed {removed_invalid} rows with invalid URLs")
        df = df[valid_mask].reset_index(drop=True)

    # Check for missing values
    missing_urls = df['URL'].isna().sum()
    missing_labels = df['label'].isna().sum()
    if missing_urls > 0 or missing_labels > 0:
        print(f"Removed {missing_urls + missing_labels} rows with missing values")
        df = df.dropna(subset=['URL', 'label']).reset_index(drop=True)

    # Ensure labels are binary (0 or 1)
    invalid_labels = (~df['label'].isin([0, 1])).sum()
    if invalid_labels > 0:
        print(f"Removed {invalid_labels} rows with invalid labels (not 0 or 1)")
        df = df[df['label'].isin([0, 1])].reset_index(drop=True)

    # Report class distribution
    label_counts = df['label'].value_counts().sort_index()
    print(f"Label distribution after cleaning:")
    print(f"  Legitimate (0): {label_counts.get(0, 0)}")
    print(f"  Phishing (1):   {label_counts.get(1, 0)}")

    return df


def extract_features_batch(urls: pd.Series) -> np.ndarray:
    """Extract features for a batch of URLs.

    Parameters
    ----------
    urls: pd.Series
        Series of URL strings.

    Returns
    -------
    np.ndarray
        Feature matrix of shape (n_samples, n_features).
    """
    feature_list = []
    for url in urls:
        features = extract_features_from_url(url)
        # Convert to list in canonical order
        feature_list.append([features[name] for name in FEATURE_NAMES])
    return np.array(feature_list)


def train_model(
    X: np.ndarray, y: np.ndarray
) -> Tuple[RandomForestClassifier, StandardScaler]:
    """Train a Random Forest classifier with feature scaling.

    Parameters
    ----------
    X: np.ndarray
        Feature matrix.
    y: np.ndarray
        Target labels.

    Returns
    -------
    Tuple[RandomForestClassifier, StandardScaler]
        Trained classifier and fitted scaler.
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",  # Handle potential imbalance
    )
    model.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = model.predict(X_test_scaled)
    y_proba = model.predict_proba(X_test_scaled)[:, 1]  # probability of phishing class
    print("\n=== Model Evaluation ===")
    print(classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))
    # Calculate ROC-AUC if both classes are present in y_test
    if len(np.unique(y_test)) == 2:
        roc_auc = roc_auc_score(y_test, y_proba)
        print(f"ROC-AUC: {roc_auc:.4f}")
    else:
        print("ROC-AUC: Not defined (only one class present in test set)")

    return model, scaler


def save_model(
    model: RandomForestClassifier,
    scaler: StandardScaler,
    model_path: Path,
    feature_names: List[str],
    dataset_info: Dict[str, Any]
) -> None:
    """Save the model, scaler, and metadata to a pickle file.

    Parameters
    ----------
    model: RandomForestClassifier
        Trained model.
    scaler: StandardScaler
        Fitted scaler.
    model_path: Path
        Path to save the pickle file.
    feature_names: List[str]
        List of feature names in canonical order.
    dataset_info: Dict[str, Any]
        Information about the dataset used for training.
    """
    data = {
        'model': model,
        'scaler': scaler,
        'metadata': {
            'feature_names': feature_names,
            'feature_count': len(feature_names),
            'model_type': 'RandomForestClassifier',
            'training_samples': dataset_info.get('training_samples'),
            'positive_samples': dataset_info.get('positive_samples'),
            'negative_samples': dataset_info.get('negative_samples'),
            'dataset_source': dataset_info.get('dataset_source'),
            'label_mapping': dataset_info.get('label_mapping'),
            'removed_invalid_urls': dataset_info.get('removed_invalid_urls'),
            'removed_missing_values': dataset_info.get('removed_missing_values'),
            'removed_invalid_labels': dataset_info.get('removed_invalid_labels'),
            'sklearn_version': dataset_info.get('sklearn_version'),
        }
    }
    with open(model_path, 'wb') as f:
        pickle.dump(data, f)
    print(f"\nModel saved to {model_path}")


def main() -> None:
    """Main training pipeline."""
    parser = argparse.ArgumentParser(description="Train URLSniffer phishing detection model")
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Path to the CSV dataset (UCI PhiUSIIL or legacy format)"
    )
    parser.add_argument(
        "--model-output",
        type=str,
        required=True,
        help="Path to save the trained model pickle file"
    )
    args = parser.parse_args()

    csv_path = Path(args.data)
    model_path = Path(args.model_output)

    # Load and validate data
    print("Loading and validating dataset...")
    df = load_and_validate_data(csv_path)

    # Extract features
    print("Extracting features...")
    X = extract_features_batch(df['URL'])
    y = df['label'].values

    # Train model
    print("Training model...")
    model, scaler = train_model(X, y)

    # Prepare dataset info for metadata
    dataset_info = {
        'training_samples': len(df),
        'positive_samples': int(df['label'].sum()),  # phishing count
        'negative_samples': int(len(df) - df['label'].sum()),  # legitimate count
        'dataset_source': str(csv_path.resolve()),
        'label_mapping': '0=legitimate, 1=phishing (after UCI inversion if applicable)',
        'removed_invalid_urls': None,  # we don't have this count from load_and_validate_data yet
        'removed_missing_values': None,
        'removed_invalid_labels': None,
        'sklearn_version': __import__('sklearn').__version__,
    }
    # Note: We could return the removal counts from load_and_validate_data, but for simplicity we'll skip.

    # Save model
    save_model(model, scaler, model_path, FEATURE_NAMES, dataset_info)


if __name__ == "__main__":
    main()