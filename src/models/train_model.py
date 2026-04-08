# =============================================================
# train_model.py — Trains RandomForest Sales Prediction Model
# =============================================================

import sys
import os
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)
import joblib

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import (
    MODEL_PATH,
    MODEL_SETTINGS,
    FEATURE_COLS,
    TARGET_COL
)
from src.features.feature_engineering import run_feature_pipeline

# =============================================================
# TRAIN MODEL
# =============================================================
def train_model(X, y):
    """
    Trains a RandomForestRegressor on the prepared features.

    Args:
        X : Feature matrix (pd.DataFrame)
        y : Target vector  (pd.Series)

    Returns:
        model     : Trained model
        X_test    : Test features
        y_test    : Test targets
        y_pred    : Predictions on test set
    """

    print("\n" + "="*50)
    print("  MODEL TRAINING")
    print("="*50)

    # -------------------------------------------------------------
    # SPLIT DATA
    # -------------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42
    )

    print(f"📊 Train size : {X_train.shape[0]} rows")
    print(f"📊 Test size  : {X_test.shape[0]} rows")

    # -------------------------------------------------------------
    # INITIALIZE MODEL
    # -------------------------------------------------------------
    model = RandomForestRegressor(
    n_estimators      = MODEL_SETTINGS["n_estimators"],
    max_depth         = MODEL_SETTINGS["max_depth"],
    min_samples_split = MODEL_SETTINGS["min_samples_split"],
    min_samples_leaf  = MODEL_SETTINGS["min_samples_leaf"],
    random_state      = MODEL_SETTINGS["random_state"],
    n_jobs            = -1
)

    # -------------------------------------------------------------
    # TRAIN
    # -------------------------------------------------------------
    print("\n🔄 Training model...")
    model.fit(X_train, y_train)
    print("✅ Training complete!")

    # -------------------------------------------------------------
    # EVALUATE
    # -------------------------------------------------------------
    y_pred = model.predict(X_test)

    mae  = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2   = r2_score(y_test, y_pred)

    print("\n" + "="*50)
    print("  MODEL EVALUATION")
    print("="*50)
    print(f"  MAE  (Mean Abs Error)  : {mae:.2f}")
    print(f"  RMSE (Root Mean Sq Er) : {rmse:.2f}")
    print(f"  R²   (Accuracy Score)  : {r2:.4f}")
    print("="*50)

    # -------------------------------------------------------------
    # FEATURE IMPORTANCE
    # -------------------------------------------------------------
    print("\n📊 Feature Importance:")
    importances = model.feature_importances_
    for feat, imp in sorted(
        zip(FEATURE_COLS, importances),
        key=lambda x: x[1],
        reverse=True
    ):
        bar = "█" * int(imp * 50)
        print(f"  {feat:<22} {bar} {imp:.4f}")

    return model, X_test, y_test, y_pred

# =============================================================
# SAVE MODEL
# =============================================================
def save_model(model):
    """
    Saves trained model to artifacts/model.pkl
    """
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\n✅ Model saved to: {MODEL_PATH}")

# =============================================================
# FULL TRAINING PIPELINE
# =============================================================
def run_training_pipeline():
    """
    Full pipeline:
    1. Feature engineering
    2. Train model
    3. Evaluate model
    4. Save model
    """

    print("\n" + "="*50)
    print("  FULL TRAINING PIPELINE")
    print("="*50)

    # Step 1: Feature engineering
    X, y, encoders = run_feature_pipeline()

    # Step 2 & 3: Train + Evaluate
    model, X_test, y_test, y_pred = train_model(X, y)

    # Step 4: Save
    save_model(model)

    print("\n🎉 Training pipeline complete!")
    print(f"   Model    → {MODEL_PATH}")
    print(f"   Encoder  → artifacts/encoder.pkl")

    return model

# =============================================================
# RUN DIRECTLY
# =============================================================
if __name__ == "__main__":
    run_training_pipeline()  

"""✂️  train_test_split()     → 80% train, 20% test
🌲  RandomForestRegressor  → 200 trees, depth 10
📊  Evaluation metrics:
    → MAE  (how far off predictions are)
    → RMSE (penalizes big errors)
    → R²   (overall accuracy 0→1)
📊  Feature importance      → shows which factor
                            affects sales most
💾  save_model()            → saves to model.pkl
🔄  run_training_pipeline() → runs everything"""