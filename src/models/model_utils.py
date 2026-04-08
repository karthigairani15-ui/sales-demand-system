# =============================================================
# model_utils.py — Utility Functions for Model Load & Verify
# =============================================================

import os
import sys
import joblib

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import MODEL_PATH, ENCODER_PATH

# =============================================================
# LOAD MODEL
# =============================================================
def load_model():
    """
    Loads trained model from artifacts/model.pkl

    Returns:
        model : Trained RandomForestRegressor
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"❌ Model not found at: {MODEL_PATH}\n"
            f"   Please run train_model.py first."
        )

    model = joblib.load(MODEL_PATH)
    print(f"✅ Model loaded from: {MODEL_PATH}")
    return model

# =============================================================
# LOAD ENCODERS
# =============================================================
def load_encoders():
    """
    Loads fitted encoders from artifacts/encoder.pkl

    Returns:
        encoders : Dictionary of LabelEncoders
    """
    if not os.path.exists(ENCODER_PATH):
        raise FileNotFoundError(
            f"❌ Encoder not found at: {ENCODER_PATH}\n"
            f"   Please run feature_engineering.py first."
        )

    encoders = joblib.load(ENCODER_PATH)
    print(f"✅ Encoders loaded from: {ENCODER_PATH}")
    return encoders

# =============================================================
# VERIFY MODEL & ENCODER EXIST
# =============================================================
def verify_artifacts():
    """
    Checks if model.pkl and encoder.pkl exist.
    Prints status for each.

    Returns:
        bool : True if both exist, False otherwise
    """
    print("\n" + "="*50)
    print("  ARTIFACT VERIFICATION")
    print("="*50)

    model_exists   = os.path.exists(MODEL_PATH)
    encoder_exists = os.path.exists(ENCODER_PATH)

    print(f"  model.pkl   : {'✅ Found' if model_exists   else '❌ Missing'}")
    print(f"  encoder.pkl : {'✅ Found' if encoder_exists else '❌ Missing'}")
    print("="*50)

    return model_exists and encoder_exists

# =============================================================
# GET MODEL INFO
# =============================================================
def get_model_info(model):
    """
    Prints key info about the loaded model.

    Args:
        model : Trained RandomForestRegressor
    """
    print("\n" + "="*50)
    print("  MODEL INFO")
    print("="*50)
    print(f"  Type         : {type(model).__name__}")
    print(f"  N Estimators : {model.n_estimators}")
    print(f"  Max Depth    : {model.max_depth}")
    print(f"  N Features   : {model.n_features_in_}")
    print("="*50)



"""load_model()        → loads model.pkl
load_encoders()     → loads encoder.pkl
verify_artifacts()  → checks both files exist
get_model_info()    → prints model details"""