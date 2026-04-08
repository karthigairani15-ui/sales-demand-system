# =============================================================
# data_generator.py — Generates Realistic Sales Dataset
# =============================================================

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import (
    DATASET_ROWS, FOOD_ITEMS, WEATHER_TYPES,
    LOCATION_TYPES, TIME_SLOTS, FESTIVALS,
    SPECIAL_EVENTS, DATA_PATH
)

# -------------------------------------------------------------
# SEED FOR REPRODUCIBILITY
# -------------------------------------------------------------
random.seed(42)
np.random.seed(42)

# -------------------------------------------------------------
# HELPER: Generate One Row of Data
# -------------------------------------------------------------
def generate_row(date, item):
    """
    Generates one realistic row of sales data
    based on all intelligence factors.
    """

    day_of_week   = date.weekday()           # 0=Monday, 6=Sunday
    is_weekend    = 1 if day_of_week >= 5 else 0
    festival      = random.choice(FESTIVALS)
    is_festival   = 0 if festival == "None" else 1
    weather_type  = random.choice(WEATHER_TYPES)
    location_type = random.choice(LOCATION_TYPES)
    time_slot     = random.choice(TIME_SLOTS)
    special_event = random.choice(SPECIAL_EVENTS)
    is_special    = 0 if special_event == "None" else 1
    is_offer      = random.choice([0, 1])

    # Non-veg restriction days (Monday, Thursday = 0)
    is_nonveg_day = 0 if day_of_week in [0, 3] else 1

    # -------------------------------------------------------------
    # BASE SALES (per item)
    # -------------------------------------------------------------
    base_sales = {
        "Biryani" : 80,
        "Meals"   : 100,
        "Parotta" : 90,
        "Noodles" : 70,
        "Dosa"    : 85
    }

    sales = base_sales[item]

    # -------------------------------------------------------------
    # INTELLIGENCE FACTOR ADJUSTMENTS
    # -------------------------------------------------------------

    # Weekend boost
    if is_weekend:
        sales *= 1.25

    # Festival boost
    if is_festival:
        sales *= 1.35

    # Weather impact
    if weather_type == "Rainy":
        sales *= 0.80   # people stay home
    elif weather_type == "Sunny":
        sales *= 1.10   # more footfall
    elif weather_type == "Cloudy":
        sales *= 0.95
    elif weather_type == "Windy":
        sales *= 0.90

    # Location impact
    if location_type == "Office_Area":
        sales *= 1.20 if time_slot == "Lunch" else 0.75
    elif location_type == "Residential":
        sales *= 1.15 if time_slot == "Dinner" else 0.85
    elif location_type == "College":
        sales *= 1.10
    elif location_type == "Market":
        sales *= 1.05

    # Non-veg day impact (Biryani, Parotta affected)
    if item in ["Biryani", "Parotta"] and not is_nonveg_day:
        sales *= 0.70

    # Special event boost
    if is_special:
        sales *= 1.20

    # Offer boost
    if is_offer:
        sales *= 1.15

    # Time slot impact
    if time_slot == "Lunch":
        sales *= 1.10
    else:
        sales *= 0.95

    # Add realistic random noise
    noise = random.uniform(-8, 8)
    sales = max(10, int(sales + noise))

    return {
        "date"              : date.strftime("%Y-%m-%d"),
        "day_of_week"       : day_of_week,
        "item"              : item,
        "is_weekend"        : is_weekend,
        "festival"          : festival,
        "is_festival"       : is_festival,
        "weather_type"      : weather_type,
        "location_type"     : location_type,
        "time_slot"         : time_slot,
        "special_event"     : special_event,
        "is_special_event"  : is_special,
        "is_offer"          : is_offer,
        "is_nonveg_day"     : is_nonveg_day,
        "actual_sales"      : sales
    }

# -------------------------------------------------------------
# MAIN: Generate Full Dataset
# -------------------------------------------------------------
def generate_dataset():
    """
    Generates full dataset with previous_day_sales feature.
    Saves to data/dataset.csv
    """

    print("🔄 Generating dataset...")

    rows      = []
    start_date = datetime(2023, 1, 1)

    # Calculate days needed
    days_needed = DATASET_ROWS // len(FOOD_ITEMS)

    for day_offset in range(days_needed):
        date = start_date + timedelta(days=day_offset)
        for item in FOOD_ITEMS:
            row = generate_row(date, item)
            rows.append(row)

    df = pd.DataFrame(rows)

    # -------------------------------------------------------------
    # ADD PREVIOUS DAY SALES FEATURE
    # -------------------------------------------------------------
    df = df.sort_values(["item", "date"]).reset_index(drop=True)

    df["previous_day_sales"] = (
        df.groupby("item")["actual_sales"]
        .shift(1)
        .fillna(0)
        .astype(int)
    )

    # -------------------------------------------------------------
    # SAVE TO CSV
    # -------------------------------------------------------------
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    df.to_csv(DATA_PATH, index=False)

    print(f"✅ Dataset generated: {len(df)} rows")
    print(f"📁 Saved to: {DATA_PATH}")
    print(f"\n📊 Sample Data:")
    print(df.head(3).to_string())

    return df

# -------------------------------------------------------------
# RUN DIRECTLY
# -------------------------------------------------------------
if __name__ == "__main__":
    generate_dataset()


"""📊 Generates 2000 rows of realistic data
🍽️  5 food items × multiple days
🧠  Applies all intelligence factors:
    → Weekend boost      +25%
    → Festival boost     +35%
    → Rainy weather      -20%
    → Office lunch peak  +20%
    → Offer applied      +15%
    → Special event      +20%
🎲  Adds random noise (realistic)
💾  Saves to data/dataset.csv    """