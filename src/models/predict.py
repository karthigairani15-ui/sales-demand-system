# =============================================================
# predict.py — Prediction Engine for Sales Demand System
# =============================================================

from operator import le

import pandas as pd
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import (
    FEATURE_COLS,
    CATEGORICAL_COLS,
    FOOD_ITEMS
)
from src.models.model_utils import load_model, load_encoders

# =============================================================
# BUILD INPUT ROW
# =============================================================
def build_input(
    item,
    weather_type,
    location_type,
    time_slot,
    festival,
    special_event,
    is_weekend,
    is_festival,
    is_nonveg_day,
    is_special_event,
    is_offer,
    previous_day_sales
):
    """
    Builds a single input row as DataFrame
    for prediction.

    Returns:
        pd.DataFrame : Single row ready for model
    """

    input_data = {
        "is_weekend"        : int(is_weekend),
        "is_festival"       : int(is_festival),
        "is_nonveg_day"     : int(is_nonveg_day),
        "is_special_event"  : int(is_special_event),
        "is_offer"          : int(is_offer),
        "previous_day_sales": float(previous_day_sales),
        "weather_type"      : str(weather_type),
        "location_type"     : str(location_type),
        "time_slot"         : str(time_slot),
        "festival"          : str(festival),
        "special_event"     : str(special_event),
        "item"              : str(item)
    }

    return pd.DataFrame([input_data])

# =============================================================
# ENCODE INPUT
# =============================================================
def encode_input(df, encoders):
    """
    Encodes categorical columns in input DataFrame
    using pre-fitted encoders.

    Args:
        df       : Input DataFrame
        encoders : Dictionary of fitted LabelEncoders

    Returns:
        df : Encoded DataFrame
    """
    df = df.copy()

    for col in CATEGORICAL_COLS:
        if col in df.columns and col in encoders:
            le = encoders[col]
            val = str(df[col].iloc[0])

            # Handle unseen labels safely
            if val not in le.classes_:
                # Try "None" first, else use first class
                val = "None" if "None" in le.classes_ else le.classes_[0]

            df[col] = le.transform([val])

    return df

# =============================================================
# PREDICT SINGLE ITEM
# =============================================================
def predict_single(
    item,
    weather_type,
    location_type,
    time_slot,
    festival        = "None",
    special_event   = "None",
    is_weekend      = 0,
    is_festival     = 0,
    is_nonveg_day   = 1,
    is_special_event= 0,
    is_offer        = 0,
    previous_day_sales = 0
):
    """
    Predicts sales for a single food item.

    Returns:
        dict : {item, predicted_sales}
    """

    model    = load_model()
    encoders = load_encoders()

    # Build input
    df = build_input(
        item, weather_type, location_type,
        time_slot, festival, special_event,
        is_weekend, is_festival, is_nonveg_day,
        is_special_event, is_offer, previous_day_sales
    )

    # Encode
    df_encoded = encode_input(df, encoders)

    # Ensure correct column order
    df_encoded = df_encoded[FEATURE_COLS]

    # Predict
    prediction = model.predict(df_encoded)[0]
    predicted  = max(0, round(float(prediction)))

    return {
        "item"            : item,
        "predicted_sales" : predicted
    }

# =============================================================
# PREDICT ALL ITEMS
# =============================================================
# =============================================================
# PREDICT ALL ITEMS
# =============================================================
def predict_all_items(
    weather_type,
    location_type,
    time_slot,
    festival         = "None",
    special_event    = "None",
    is_weekend       = 0,
    is_festival      = 0,
    is_nonveg_day    = 1,
    is_special_event = 0,
    is_offer         = 0,
    previous_day_sales = 0
):
    """
    Predicts sales for ALL food items.
    Loads model ONCE and reuses for all items.

    Returns:
        list : [{item, predicted_sales}, ...]
    """

    print("\n" + "="*50)
    print("  SALES PREDICTION — ALL ITEMS")
    print("="*50)

    # ✅ Load model & encoder ONCE only
    model    = load_model()
    encoders = load_encoders()

    results = []

    for item in FOOD_ITEMS:
        # Build input
        df = build_input(
            item, weather_type, location_type,
            time_slot, festival, special_event,
            is_weekend, is_festival, is_nonveg_day,
            is_special_event, is_offer, previous_day_sales
        )

        # Encode
        df_encoded = encode_input(df, encoders)

        # Ensure correct column order
        df_encoded = df_encoded[FEATURE_COLS]

        # Predict
        prediction = model.predict(df_encoded)[0]
        predicted  = max(0, round(float(prediction)))

        results.append({
            "item"            : item,
            "predicted_sales" : predicted
        })

        print(f"  {item:<12} → {predicted} units")

    print("="*50)
    return results

# =============================================================
# RUN DIRECTLY
# =============================================================
if __name__ == "__main__":

    predictions = predict_all_items(
        weather_type     = "Sunny",
        location_type    = "Office_Area",
        time_slot        = "Lunch",
        festival         = "None",
        special_event    = "None",
        is_weekend       = 0,
        is_festival      = 0,
        is_nonveg_day    = 1,
        is_special_event = 0,
        is_offer         = 1,
        previous_day_sales = 90
    )

""" build_input()       → creates input DataFrame
encode_input()      → converts text → numbers
predict_single()    → predicts 1 food item
predict_all_items() → predicts all 5 items"""
