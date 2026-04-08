# =============================================================
# waste.py — Waste Calculation Module
# =============================================================

import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# =============================================================
# CALCULATE WASTE
# =============================================================
def calculate_waste(production_plan, pos_records):
    """
    Calculates waste = produced - sold.

    Args:
        production_plan : list of production records
        pos_records     : list of POS records

    Returns:
        list : waste records
    """

    print("\n" + "="*50)
    print("  WASTE CALCULATION")
    print("="*50)

    # Build lookup dicts
    produced = {
        p["item"]: p["production_qty"]
        for p in production_plan
    }
    sold = {
        r["item"]: r["sold_qty"]
        for r in pos_records
    }

    waste_records = []

    for item in produced:
        produced_qty = produced.get(item, 0)
        sold_qty     = sold.get(item, 0)
        waste_qty    = max(0, produced_qty - sold_qty)
        waste_pct    = round(
            (waste_qty / produced_qty * 100)
            if produced_qty > 0 else 0, 1
        )

        status = (
            "🟢 Low"    if waste_pct < 10 else
            "🟡 Medium" if waste_pct < 20 else
            "🔴 High"
        )

        record = {
            "item"        : item,
            "produced"    : produced_qty,
            "sold"        : sold_qty,
            "waste"       : waste_qty,
            "waste_pct"   : waste_pct,
            "status"      : status
        }

        waste_records.append(record)
        print(f"  {item:<12} "
              f"Produced: {produced_qty:<6} "
              f"Sold: {sold_qty:<6} "
              f"Waste: {waste_qty:<6} "
              f"({waste_pct}%)  {status}")

    print("="*50)
    return waste_records

# =============================================================
# GET WASTE SUMMARY
# =============================================================
def get_waste_summary(waste_records):
    """
    Returns waste summary as JSON string.

    Args:
        waste_records : list of waste records

    Returns:
        str : JSON string
    """
    total_produced = sum(r["produced"] for r in waste_records)
    total_sold     = sum(r["sold"]     for r in waste_records)
    total_waste    = sum(r["waste"]    for r in waste_records)
    overall_pct    = round(
        (total_waste / total_produced * 100)
        if total_produced > 0 else 0, 1
    )

    summary = {
        "total_produced"  : total_produced,
        "total_sold"      : total_sold,
        "total_waste"     : total_waste,
        "overall_waste_pct": overall_pct,
        "records"         : waste_records
    }

    print(f"\n📊 Overall Waste: {total_waste} units ({overall_pct}%)")
    return json.dumps(summary, indent=2)

"""waste.py       → Produced - Sold = Waste
            → 🟢 Low / 🟡 Medium / 🔴 High"""