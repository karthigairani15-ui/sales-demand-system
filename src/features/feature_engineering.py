# =============================================================
# feature_engineering.py — Prepares Features for ML Model
# =============================================================

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import joblib
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import (
    CATEGORICAL_COLS, FEATURE_COLS,
    TARGET_COL, ENCODER_PATH, DATA_PATH
)

# =============================================================
# LOAD DATASET
# =============================================================
def load_data():
    """
    Loads dataset from CSV file.
    Returns a pandas DataFrame.
    """
    print("📂 Loading dataset...")

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
    return df

# =============================================================
# ENCODE CATEGORICAL COLUMNS
# =============================================================
def encode_features(df, fit=True, encoders=None):
    """
    Encodes categorical columns using LabelEncoder.

    Args:
        df       : Input DataFrame
        fit      : If True, fits new encoders (training)
                   If False, uses existing encoders (prediction)
        encoders : Dictionary of pre-fitted encoders

    Returns:
        df       : Encoded DataFrame
        encoders : Dictionary of fitted encoders
    """

    if encoders is None:
        encoders = {}

    df = df.copy()

    for col in CATEGORICAL_COLS:
        if col not in df.columns:
            print(f"⚠️  Column '{col}' not found — skipping")
            continue

        if fit:
            # Fit new encoder
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            encoders[col] = le
        else:
            # Use existing encoder
            if col in encoders:
                le = encoders[col]
                # Handle unseen labels safely
                df[col] = df[col].astype(str).apply(
                lambda x: x if x in le.classes_ else "None"
                if "None" in le.classes_ else le.classes_[0]
)
                df[col] = le.transform(df[col])
            else:
                print(f"⚠️  No encoder found for '{col}' — skipping")

    return df, encoders

# =============================================================
# SAVE ENCODERS
# =============================================================
def save_encoders(encoders):
    """
    Saves fitted encoders to artifacts/encoder.pkl
    """
    os.makedirs(os.path.dirname(ENCODER_PATH), exist_ok=True)
    joblib.dump(encoders, ENCODER_PATH)
    print(f"✅ Encoders saved to: {ENCODER_PATH}")

# =============================================================
# LOAD ENCODERS
# =============================================================
def load_encoders():
    """
    Loads saved encoders from artifacts/encoder.pkl
    """
    if not os.path.exists(ENCODER_PATH):
        raise FileNotFoundError(f"Encoder not found at: {ENCODER_PATH}")

    encoders = joblib.load(ENCODER_PATH)
    print(f"✅ Encoders loaded from: {ENCODER_PATH}")
    return encoders

# =============================================================
# PREPARE FEATURES & TARGET
# =============================================================
def prepare_features(df):
    """
    Splits DataFrame into:
        X → Feature matrix
        y → Target vector (actual_sales)

    Returns:
        X : pd.DataFrame
        y : pd.Series
    """

    # Check all feature columns exist
    missing = [col for col in FEATURE_COLS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")

    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    print(f"✅ Features prepared → X: {X.shape}, y: {y.shape}")
    return X, y

# =============================================================
# FULL PIPELINE: Load → Encode → Prepare
# =============================================================
def run_feature_pipeline():
    """
    Full feature engineering pipeline:
    1. Load data
    2. Encode categorical columns
    3. Save encoders
    4. Return X, y ready for training
    """

    print("\n" + "="*50)
    print("  FEATURE ENGINEERING PIPELINE")
    print("="*50)

    # Step 1: Load
    df = load_data()

    # Step 2: Encode
    df, encoders = encode_features(df, fit=True)

    # Step 3: Save encoders
    save_encoders(encoders)

    # Step 4: Prepare X, y
    X, y = prepare_features(df)

    print("\n✅ Feature pipeline complete!")
    print(f"   X shape : {X.shape}")
    print(f"   y shape : {y.shape}")
    print(f"   Features : {list(X.columns)}")

    return X, y, encoders

# =============================================================
# RUN DIRECTLY
# =============================================================
if __name__ == "__main__":
    X, y, encoders = run_feature_pipeline()


""" 📂 load_data()           → Loads dataset.csv
🔤 encode_features()     → Converts text → numbers
                        (Sunny→0, Rainy→1 etc.)
💾 save_encoders()       → Saves to encoder.pkl
📂 load_encoders()       → Loads encoder.pkl
🎯 prepare_features()    → Splits X (features) & y (target)
🔄 run_feature_pipeline()→ Runs all steps together"""