# =============================================================
# settings.py — Central Configuration for Sales Demand System
# FIX: Reduced production buffer to 2–5% 
#      Combined with pos.py sell ratio fix (93–97%),
#      this brings waste and loss to acceptable levels.
# =============================================================

import os

# -------------------------------------------------------------
# BASE PATHS
# -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_PATH    = os.path.join(BASE_DIR, "data",      "dataset.csv")
MODEL_PATH   = os.path.join(BASE_DIR, "artifacts", "model.pkl")
ENCODER_PATH = os.path.join(BASE_DIR, "artifacts", "encoder.pkl")

# -------------------------------------------------------------
# DATASET SETTINGS
# -------------------------------------------------------------
DATASET_ROWS = 2000

# -------------------------------------------------------------
# FOOD ITEMS & COST
# -------------------------------------------------------------
FOOD_ITEMS = ["Biryani", "Meals", "Parotta", "Noodles", "Dosa"]

ITEM_COST = {
    "Biryani"  : 120,
    "Meals"    : 80,
    "Parotta"  : 50,
    "Noodles"  : 70,
    "Dosa"     : 40
}

# -------------------------------------------------------------
# WEATHER TYPES
# -------------------------------------------------------------
WEATHER_TYPES = ["Sunny", "Rainy", "Cloudy", "Windy"]

# -------------------------------------------------------------
# LOCATION TYPES
# -------------------------------------------------------------
LOCATION_TYPES = ["Office_Area", "Residential", "Market", "College"]

# -------------------------------------------------------------
# TIME SLOTS
# -------------------------------------------------------------
TIME_SLOTS = ["Lunch", "Dinner"]

# -------------------------------------------------------------
# FESTIVALS
# -------------------------------------------------------------
FESTIVALS = ["Pongal", "Diwali", "Christmas", "New Year", "Eid", "None"]

# -------------------------------------------------------------
# SPECIAL EVENTS
# -------------------------------------------------------------
SPECIAL_EVENTS = ["Cricket Match", "Local Festival", "College Event", "None"]

# -------------------------------------------------------------
# PRODUCTION BUFFER
# FIX: Reduced from 10–20% → 2–5%
#
# How it works with the pos.py fix:
#   Prediction = 120 units
#   Buffer 2–5% → Produce 122–126 units
#   POS sells 93–97% of 122–126 = 113–122 units
#   Waste = 122–126 - 113–122 = 0–13 units (avg ~5)
#   vs OLD: waste was 16–29 units per item
# -------------------------------------------------------------
PRODUCTION_BUFFER_MIN = 0.02   
PRODUCTION_BUFFER_MAX = 0.05   

# -------------------------------------------------------------
# MODEL SETTINGS
# -------------------------------------------------------------
MODEL_SETTINGS = {
    "n_estimators"      : 500,
    "max_depth"         : 15,
    "min_samples_split" : 3,
    "min_samples_leaf"  : 1,
    "random_state"      : 42,
}

# -------------------------------------------------------------
# FLASK API SETTINGS
# -------------------------------------------------------------
FLASK_HOST  = "0.0.0.0"
FLASK_PORT  = 5000
FLASK_DEBUG = True

# -------------------------------------------------------------
# CATEGORICAL COLUMNS (for encoding)
# -------------------------------------------------------------
CATEGORICAL_COLS = [
    "weather_type",
    "location_type",
    "time_slot",
    "festival",
    "special_event",
    "item",
]

# -------------------------------------------------------------
# FEATURE COLUMNS (used for training)
# -------------------------------------------------------------
FEATURE_COLS = [
    "is_weekend",
    "is_festival",
    "is_nonveg_day",
    "is_special_event",
    "is_offer",
    "previous_day_sales",
    "weather_type",
    "location_type",
    "time_slot",
    "festival",
    "special_event",
    "item",
]

TARGET_COL = "actual_sales"