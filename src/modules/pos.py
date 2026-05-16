# =============================================================
# pos.py — Point of Sale Module
# =============================================================

import json
import random
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import FOOD_ITEMS

# =============================================================
# SIMULATE SALES
# =============================================================
def simulate_sales(inventory, context):
    """
    Simulates real-time sales from inventory.
    Sales are between 80-95% of available stock.

    Args:
        inventory : dict {item: quantity}
        context   : dict {weather, location, etc.}

    Returns:
        list : POS records as JSON array
    """

    print("\n" + "="*50)
    print("  POS — SALES SIMULATION")
    print("="*50)

    pos_records = []

    for item, stock in inventory.items():
        # Simulate 80-95% of stock being sold
        sell_ratio = 0.95 
        sold_qty   = round(stock * sell_ratio)
        sold_qty   = max(0, min(sold_qty, stock))

        record = {
            "timestamp"    : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "item"         : item,
            "stock"        : stock,
            "sold_qty"     : sold_qty,
            "weather"      : context.get("weather_type",  "Sunny"),
            "location"     : context.get("location_type", "Office_Area"),
            "time_slot"    : context.get("time_slot",     "Lunch"),
            "is_offer"     : context.get("is_offer",      0),
            "special_event": context.get("special_event", "None"),
            "festival"     : context.get("festival",      "None")
        }

        pos_records.append(record)
        print(f"  {item:<12} Stock: {stock:<6} Sold: {sold_qty}")

    print("="*50)
    return pos_records

# =============================================================
# GET SALES DICT FROM POS
# =============================================================
def get_sales_dict(pos_records):
    """
    Converts POS records to simple {item: sold_qty} dict.

    Args:
        pos_records : list of POS records

    Returns:
        dict : {item: sold_qty}
    """
    return {
        record["item"]: record["sold_qty"]
        for record in pos_records
    }

# =============================================================
# GET POS SUMMARY
# =============================================================
def get_pos_summary(pos_records):
    """
    Returns POS summary as JSON string.

    Args:
        pos_records : list of POS records

    Returns:
        str : JSON string
    """
    summary = {
        "total_items_sold" : sum(
            r["sold_qty"] for r in pos_records
        ),
        "records"          : pos_records
    }

    return json.dumps(summary, indent=2)

"""pos.py         → Simulate 80-95% of stock sold
                → Captures context (weather/location)
"""