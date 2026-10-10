"""Tests for the training script."""

import tempfile
import os
from pathlib import Path
import sys

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.train_model import load_and_validate_data, extract_features_batch


def test_load_and_validate_data():
    """Test loading and validating our test dataset."""
    # Use the test dataset we created
    csv_path = Path(__file__).parent.parent / "test_dataset.csv"

    df = load_and_validate_data(csv_path)

    # Check we have the right number of rows
    assert len(df) == 10

    # Check columns - should be 'URL' and 'label' after processing
    assert "URL" in df.columns
    assert "label" in df.columns

    # Check labels are 0 and 1
    assert set(df["label"].unique()) == {0, 1}

    # Check we have 5 of each (based on our test data)
    assert df["label"].value_counts()[0] == 5
    assert df["label"].value_counts()[1] == 5


def test_extract_features_batch():
    """Test feature extraction on a batch of URLs."""
    urls = [
        "https://example.com",
        "http://192.168.1.1",
        "https://paypa1.com/login"
    ]

    # Convert to pandas Series for the function
    import pandas as pd
    url_series = pd.Series(urls)

    features = extract_features_batch(url_series)

    # Should return a 3x27 array (27 features)
    assert features.shape == (3, 27)

    # Check first URL (https://example.com) for the original 8 features
    # url_length, scheme(1), has_ip(0), has_punycode(0), percent_encoding(0), hyphen_count(0), digit_count(0), subdomain_count(0)
    assert features[0][0] == len("https://example.com")  # url_length
    assert features[0][1] == 1  # scheme
    assert features[0][2] == 0  # has_ip
    assert features[0][3] == 0  # has_punycode
    assert features[0][4] == 0  # percent_encoding
    assert features[0][5] == 0  # hyphen_count
    assert features[0][6] == 0  # digit_count
    assert features[0][7] == 0  # subdomain_count

    # Check second URL (http://192.168.1.1) for has_ip flag
    assert features[1][2] == 1  # has_ip should be 1 for IP address
    assert features[1][1] == 1  # scheme should be 1 for http

    # Check third URL (https://paypa1.com/login) for hyphen count and percent encoding
    # https://paypa1.com/login has 0 hyphens and no percent encoding
    assert features[2][5] == 0  # hyphen_count
    assert features[2][4] == 0  # percent_encoding (no % signs in this URL)