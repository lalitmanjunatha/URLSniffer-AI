# URLSniffer Feature Extractor Update Summary

## Overview
The feature extractor in `app/ml/feature_extractor.py` has been enhanced with additional features to improve phishing detection capabilities. The training and inference pipelines now use a canonical 27-feature schema. Existing 8-feature model artifacts are incompatible with the new schema and will be rejected by the model loader to prevent silent failures.

Support for downloading and preprocessing the UCI PhiUSIIL Phishing URL Dataset has been added via `scripts/download_uci_dataset.py`.

## Canonical 27-Feature Schema (Ordered)
The following features are extracted in this exact order:

### Original Features (Preserved)
1. `url_length`: Total character count of the URL
2. `scheme`: Binary flag for HTTP/HTTPS scheme
3. `has_ip`: Binary flag for IPv4 address in host
4. `has_punycode`: Binary flag for punycode labels
5. `percent_encoding`: Binary flag for percent-encoded sequences
6. `hyphen_count`: Count of '-' characters
7. `digit_count`: Count of digits
8. `subdomain_count`: Number of sub-domain components

### New Features Added
9. `hostname_length`: Length of hostname component
10. `path_length`: Length of path component
11. `query_length`: Length of query component
12. `fragment_length`: Length of fragment component
13. `tld_length`: Length of top-level domain
14. `hostname_dot_count`: Number of dots in hostname
15. `path_dot_count`: Number of dots in path
16. `query_param_count`: Number of query parameters (separated by &)
17. `has_at_sign`: Binary flag for @ symbol (possible embedded credentials)
18. `tilde_count`: Count of '~' characters
19. `underscore_count`: Count of '_' characters
20. `colon_count`: Count of ':' characters
21. `semicolon_count`: Count of ';' characters
22. `bracket_count`: Count of '[' and ']' characters
23. `brace_count`: Count of '{' and '}' characters
24. `parenthesis_count`: Count of '(' and ')' characters
25. `single_quote_count`: Count of ''' characters
26. `double_quote_count`: Count of '"' characters
27. `backtick_count`: Count of '`' characters

## Pipeline Changes
- **Training**: `scripts/train_model.py` now extracts all 27 features using the canonical order from `FEATURE_NAMES`. It supports both the legacy format and the UCI PhiUSIIL dataset format.
- **Inference**: `app/ml/model.py` now constructs feature vectors using all 27 features in the canonical order.
- **Model Loading**: The model loader validates that the feature names and count in the artifact metadata match the canonical 27-feature schema. Legacy 8-feature artifacts will raise a clear `RuntimeError` about feature schema mismatch.
- **Dataset Download**: `scripts/download_uci_dataset.py` downloads and extracts the UCI PhiUSIIL Phishing URL Dataset from the official UCI Machine Learning Repository.

## UCI PhiUSIIL Phishing URL Dataset
- **Source**: https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset
- **Size**: 235,795 instances
- **Format**: CSV file with columns including 'URL' and 'Label'
- **Label Definition**: Label 1 = legitimate URL, Label 0 = phishing URL
- **License**: Please check the UCI repository for the specific license and provide appropriate attribution if using this dataset.

The dataset is not automatically downloaded or included in the repository. Users must explicitly download it using the provided script.

## Dataset Preprocessing
The training pipeline includes the following preprocessing steps:
1. **Format Detection**: Automatically detects whether the CSV is in UCI PhiUSIIL format ('URL', 'Label') or legacy format ('url', 'label')
2. **Label Mapping**: For UCI dataset, converts Label 1->0 (legitimate) and Label 0->1 (phishing) to match URLSniffer's convention (0=legitimate, 1=phishing)
3. **URL Validation**: Filters out syntactically invalid URLs using the offline `is_valid_url` function (no network requests)
4. **Missing Value Removal**: Removes rows with missing URLs or labels
5. **Label Validation**: Ensures labels are binary (0 or 1)
6. **Class Distribution Reporting**: Reports final counts of legitimate and phishing URLs
7. **Train/Test Split**: Uses stratified 80/20 split with fixed random seed (42) for reproducibility
8. **Feature Scaling**: Fits StandardScaler on training data only, applies to both train and test sets

## Legacy Artifact Incompatibility
All existing `.pkl` model artifacts (e.g., `model.pkl`, `test_model_updated.pkl`) were trained with only the original 8 features. These artifacts are now **incompatible** with the updated code and will produce an error when loaded:
```
RuntimeError: Feature schema mismatch. Expected [list of 27 features], got ['url_length', 'scheme', 'has_ip', 'has_punycode', 'percent_encoding', 'hyphen_count', 'digit_count', 'subdomain_count']
```

To use the new features, you must train a new model using the updated training script.

## Training a New Model
To train a model with the 27-feature schema:
```bash
python scripts/train_model.py --data /path/to/dataset.csv --model-output /path/to/model.pkl
```

### For UCI Dataset:
1. First download the dataset: `python scripts/download_uci_dataset.py`
2. Then train: `python scripts/train_model.py --data data/raw/dataset.csv --model-output model.pkl`

The script will:
1. Load and validate the CSV dataset (supports both UCI and legacy formats)
2. Extract all 27 features for each URL
3. Split the data into training and test sets (80/20 by default, stratified)
4. Train a RandomForestClassifier with a StandardScaler preprocessing step
5. Evaluate the model on the test set and print metrics (including ROC-AUC)
6. Save the model, scaler, and metadata (including the 27 feature names) to the specified output path

### Important Notes on Evaluation
- Performance metrics should be interpreted with caution. Even with a large dataset like UCI PhiUSIIL, historical performance does not guarantee detection of novel phishing URLs in the wild.
- The model should be regularly retrained with fresh data to maintain effectiveness against evolving phishing tactics.
- For production deployment, consider additional validation techniques and monitoring for concept drift.

## Running Tests
The backend test suite validates the feature extractor, training pipeline, model loading, and API endpoints. Run all tests with:
```bash
python -m pytest tests/ -v
```
All tests should pass, including:
- Feature extractor tests
- Health endpoint tests
- Model loading and prediction tests (including compatibility checks)
- Scan endpoint tests
- Training script tests
- URL validator tests

## Next Milestone
The next step is to actually download and train on the UCI PhiUSIIL dataset to evaluate the performance of the 27-feature model on a real-world dataset. After training, proper evaluation should be conducted to assess the model's effectiveness and determine appropriate thresholds for deployment.

## Verification
After updating the code, the following should hold:
1. The extractor returns exactly 27 features in the canonical order.
2. Batch extraction returns the same feature schema.
3. The trainer uses all 27 features and supports UCI dataset format.
4. A compatible 27-feature artifact loads and predicts successfully.
5. An 8-feature legacy artifact is rejected explicitly with a clear error message.
6. Missing, corrupt, or incompatible artifacts produce the expected error behavior.
7. Invalid URLs are rejected without any network requests.
8. The scan endpoint returns a clear error when no compatible model is available.
9. Existing authentication, health, validation, and scan tests continue to pass.
10. The UCI dataset download script works correctly and extracts the expected CSV file.