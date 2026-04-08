# =============================================================
# production.py — Production Planning Module
# =============================================================

import json
import random
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import (
    PRODUCTION_BUFFER_MIN,
    PRODUCTION_BUFFER_MAX,
    FOOD_ITEMS
)

# =============================================================
# CALCULATE PRODUCTION QUANTITY
# =============================================================
def calculate_production(predicted_sales):
    """
    Adds 10-20% buffer to predicted sales
    to avoid stockouts.

    Args:
        predicted_sales : dict {item: sales}

    Returns:
        dict : {item: production_quantity}
    """
    production = {}

    for item, sales in predicted_sales.items():
        buffer   = random.uniform(
            PRODUCTION_BUFFER_MIN,
            PRODUCTION_BUFFER_MAX
        )
        quantity = round(sales * (1 + buffer))
        production[item] = quantity

    return production

# =============================================================
# GENERATE PRODUCTION PLAN
# =============================================================
def generate_production_plan(predictions):
    """
    Generates full production plan from predictions.

    Args:
        predictions : list [{item, predicted_sales}]

    Returns:
        list : production plan as JSON array
    """

    print("\n" + "="*50)
    print("  PRODUCTION PLAN")
    print("="*50)

    production_plan = []

    for pred in predictions:
        item           = pred["item"]
        predicted      = pred["predicted_sales"]
        buffer         = random.uniform(
            PRODUCTION_BUFFER_MIN,
            PRODUCTION_BUFFER_MAX
        )
        produce_qty    = round(predicted * (1 + buffer))

        record = {
            "item"             : item,
            "predicted_sales"  : predicted,
            "buffer_percent"   : round(buffer * 100, 1),
            "production_qty"   : produce_qty
        }

        production_plan.append(record)

        print(f"  {item:<12} "
              f"Predicted: {predicted:<6} "
              f"Buffer: {record['buffer_percent']}%  "
              f"Produce: {produce_qty}")

    print("="*50)
    return production_plan

# =============================================================
# GET PRODUCTION SUMMARY
# =============================================================
def get_production_summary(production_plan):
    """
    Returns production summary as JSON string.

    Args:
        production_plan : list of production records

    Returns:
        str : JSON string
    """
    summary = {
        "total_items"      : len(production_plan),
        "total_production" : sum(
            p["production_qty"] for p in production_plan
        ),
        "plan"             : production_plan
    }

    return json.dumps(summary, indent=2)
""" production.py  → Predicted sales + 10-20% buffer
                    → JSON production plan"""