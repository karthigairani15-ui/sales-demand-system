# =============================================================
# loss.py — Loss Calculation Module
# =============================================================

import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import ITEM_COST

# =============================================================
# CALCULATE LOSS
# =============================================================
def calculate_loss(waste_records):
    """
    Calculates financial loss from waste.
    Loss = waste_qty * item_cost

    Args:
        waste_records : list of waste records

    Returns:
        list : loss records
    """

    print("\n" + "="*50)
    print("  LOSS CALCULATION")
    print("="*50)

    loss_records = []

    for record in waste_records:
        item      = record["item"]
        waste_qty = record["waste"]
        cost      = ITEM_COST.get(item, 0)
        loss      = waste_qty * cost

        loss_record = {
            "item"      : item,
            "waste_qty" : waste_qty,
            "cost"      : cost,
            "loss"      : loss
        }

        loss_records.append(loss_record)
        print(f"  {item:<12} "
              f"Waste: {waste_qty:<6} × "
              f"₹{cost:<6} = "
              f"₹{loss}")

    print("="*50)
    return loss_records

# =============================================================
# GENERATE LOSS REPORT
# =============================================================
def generate_loss_report(loss_records):
    """
    Generates full loss report as JSON string.

    Args:
        loss_records : list of loss records

    Returns:
        str : JSON string
    """
    total_loss = sum(r["loss"] for r in loss_records)

    print(f"\n💸 TOTAL LOSS: ₹{total_loss}")

    severity = (
        "🟢 Acceptable" if total_loss < 500  else
        "🟡 Moderate"   if total_loss < 1500 else
        "🔴 High Loss"
    )
    print(f"   Severity  : {severity}")

    report = {
        "total_loss"    : total_loss,
        "severity"      : severity,
        "currency"      : "INR",
        "loss_records"  : loss_records
    }

    return json.dumps(report, indent=2)


"""loss.py        → Waste × Cost = Loss in ₹
            → Loss severity report"""