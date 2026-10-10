"""Script to download and extract the UCI PhiUSIIL Phishing URL Dataset.

The dataset is downloaded from the UCI Machine Learning Repository and extracted
to the `data/raw` directory. The script does not overwrite existing files.

Usage:
    python scripts/download_uci_dataset.py

Notes:
    - The dataset is approximately 100 MB in size.
    - The extracted CSV file is named `dataset.csv` and contains 235,795 instances.
    - The script checks for existing files and skips download if they are present.
"""
from __future__ import annotations

import zipfile
from pathlib import Path
import requests
import sys

# Constants
UCI_URL = "https://archive.ics.uci.edu/static/public/967/phiusiil+phishing+url+dataset.zip"
DATA_DIR = Path("data/raw")
ZIP_PATH = DATA_DIR / "PhiUSIIL_Phishing_URL_Dataset.zip"
CSV_PATH = DATA_DIR / "dataset.csv"


def download_dataset() -> None:
    """Download the UCI dataset zip file if it does not already exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if ZIP_PATH.exists():
        print(f"Zip file already exists at {ZIP_PATH}. Skipping download.")
        return

    print(f"Downloading dataset from {UCI_URL}...")
    try:
        response = requests.get(UCI_URL, stream=True)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to download dataset: {e}")
        sys.exit(1)

    # Write the zip file in chunks to avoid memory issues
    with open(ZIP_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    print(f"Download completed. Saved to {ZIP_PATH}")


def extract_dataset() -> None:
    """Extract the dataset zip file if the CSV does not already exist."""
    if CSV_PATH.exists():
        print(f"CSV file already exists at {CSV_PATH}. Skipping extraction.")
        return

    if not ZIP_PATH.exists():
        print(f"Zip file not found at {ZIP_PATH}. Please download it first.")
        sys.exit(1)

    print(f"Extracting {ZIP_PATH} to {DATA_DIR}...")
    try:
        with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
            zip_ref.extractall(DATA_DIR)
    except zipfile.BadZipFile as e:
        print(f"Failed to extract zip file: {e}")
        sys.exit(1)

    # The zip file contains a single CSV file named `dataset.csv`
    extracted_csv = DATA_DIR / "dataset.csv"
    if not extracted_csv.exists():
        print(f"Expected CSV file not found in zip at {extracted_csv}")
        sys.exit(1)

    # Ensure the CSV is at the expected location (it should be, but just in case)
    if extracted_csv != CSV_PATH:
        extracted_csv.rename(CSV_PATH)

    print(f"Extraction completed. CSV saved to {CSV_PATH}")


def main() -> None:
    """Main function to download and extract the dataset."""
    download_dataset()
    extract_dataset()


if __name__ == "__main__":
    main()