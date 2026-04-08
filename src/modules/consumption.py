# =============================================================
# consumption.py — Consumption Tracking Module
# =============================================================

import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# =============================================================
# CONVERT POS TO CONSUMPTION
# =============================================================
def convert_pos_to_consumption(pos_records):
    """
    Converts POS records into consumption
    tracking format (JSON array-of-arrays).

    Args:
        pos_records : list of POS records

    Returns:
        list : array-of-arrays consumption data
    """

    print("\n" + "="*50)
    print("  CONSUMPTION TRACKING")
    print("="*50)

    # Array-of-arrays format:
    # [item, sold_qty, timestamp, location, time_slot]
    consumption = []

    for record in pos_records:
        row = [
            record["item"],
            record["sold_qty"],
            record["timestamp"],
            record["location"],
            record["time_slot"],
            record["weather"],
            record["is_offer"]
        ]
        consumption.append(row)
        print(f"  {record['item']:<12} → {record['sold_qty']} units consumed")

    print("="*50)
    return consumption

# =============================================================
# GET CONSUMPTION SUMMARY
# =============================================================
def get_consumption_summary(consumption):
    """
    Returns consumption summary.

    Args:
        consumption : list of arrays

    Returns:
        dict : summary
    """
    total = sum(row[1] for row in consumption)

    summary = {
        "total_consumed" : total,
        "item_count"     : len(consumption),
        "consumption"    : consumption
    }

    print(f"\n📊 Total Consumed: {total} units")
    return summary

# =============================================================
# SYNC WITH INVENTORY
# =============================================================
def sync_with_inventory(consumption, inventory):
    """
    Verifies consumption matches inventory deductions.

    Args:
        consumption : list of arrays
        inventory   : dict {item: remaining_qty}

    Returns:
        dict : sync status per item
    """
    print("\n" + "="*50)
    print("  CONSUMPTION ↔ INVENTORY SYNC")
    print("="*50)

    sync_status = {}

    for row in consumption:
        item     = row[0]
        consumed = row[1]
        stock    = inventory.get(item, 0)

        status = "✅ Synced" if stock >= 0 else "⚠️  Mismatch"
        sync_status[item] = {
            "consumed"  : consumed,
            "remaining" : stock,
            "status"    : status
        }
        print(f"  {item:<12} Consumed: {consumed:<6} "
            f"Remaining: {stock:<6} {status}")

    print("="*50)
    return sync_status

"""consumption.py → POS → array-of-arrays format
                → Syncs with inventory"""