# =============================================================
# inventory.py — Inventory Management Module
# =============================================================

import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import FOOD_ITEMS

# =============================================================
# INITIALIZE INVENTORY
# =============================================================
def initialize_inventory(production_plan):
    """
    Initializes inventory from production plan.

    Args:
        production_plan : list of production records

    Returns:
        dict : {item: quantity}
    """
    inventory = {}

    for record in production_plan:
        item     = record["item"]
        quantity = record["production_qty"]
        inventory[item] = quantity

    print("\n" + "="*50)
    print("  INVENTORY INITIALIZED")
    print("="*50)
    for item, qty in inventory.items():
        print(f"  {item:<12} → {qty} units")
    print("="*50)

    return inventory

# =============================================================
# UPDATE INVENTORY AFTER SALES
# =============================================================
def update_inventory(inventory, sales_data):
    """
    Deducts sold quantities from inventory.

    Args:
        inventory  : dict {item: quantity}
        sales_data : dict {item: sold_qty}

    Returns:
        dict : updated inventory
    """
    updated = inventory.copy()

    print("\n" + "="*50)
    print("  INVENTORY UPDATE")
    print("="*50)

    for item, sold in sales_data.items():
        if item in updated:
            before          = updated[item]
            updated[item]   = max(0, before - sold)
            remaining       = updated[item]
            status          = "✅" if remaining > 0 else "⚠️  OUT OF STOCK"
            print(f"  {item:<12} "
                  f"Before: {before:<6} "
                  f"Sold: {sold:<6} "
                  f"Remaining: {remaining}  {status}")

    print("="*50)
    return updated

# =============================================================
# GET INVENTORY STATUS
# =============================================================
def get_inventory_status(inventory):
    """
    Returns full inventory status as JSON.

    Args:
        inventory : dict {item: quantity}

    Returns:
        str : JSON string
    """
    status = {
        "inventory"   : inventory,
        "total_stock" : sum(inventory.values()),
        "out_of_stock": [
            item for item, qty in inventory.items()
            if qty == 0
        ]
    }

    return json.dumps(status, indent=2)

# =============================================================
# CHECK LOW STOCK
# =============================================================
def check_low_stock(inventory, threshold=10):
    """
    Identifies items with low stock.

    Args:
        inventory : dict {item: quantity}
        threshold : int (default 10)

    Returns:
        list : low stock items
    """
    low_stock = [
        item for item, qty in inventory.items()
        if qty <= threshold
    ]

    if low_stock:
        print(f"\n⚠️  LOW STOCK ALERT: {low_stock}")

    return low_stock

"""Inventory.py   → Initialize stock from production
            → Deduct after sales
            → Low stock alerts
"""