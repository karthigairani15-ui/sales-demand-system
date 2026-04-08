# =============================================================
# offers.py — Offer & Discount Impact on Sales
# =============================================================

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import FOOD_ITEMS

# =============================================================
# OFFER TYPES & MULTIPLIERS
# =============================================================
OFFER_TYPES = {
    "Discount_10"  : 1.10,   # 10% discount
    "Discount_20"  : 1.20,   # 20% discount
    "Combo_Meal"   : 1.25,   # Combo deal
    "Buy1_Get1"    : 1.40,   # BOGO offer
    "No_Offer"     : 1.00    # No offer
}

# Item-specific offer sensitivity
ITEM_OFFER_SENSITIVITY = {
    "Biryani" : 1.20,   # Very sensitive to offers
    "Meals"   : 1.10,
    "Parotta" : 1.15,
    "Noodles" : 1.25,   # Most sensitive
    "Dosa"    : 1.10
}

# =============================================================
# GET OFFER MULTIPLIER
# =============================================================
def get_offer_multiplier(offer_type):
    """
    Returns sales multiplier for given offer type.

    Args:
        offer_type : str

    Returns:
        float : multiplier
    """
    if offer_type not in OFFER_TYPES:
        print(f"⚠️  Unknown offer '{offer_type}' → using 1.0")
        return 1.0

    multiplier = OFFER_TYPES[offer_type]
    if multiplier > 1.0:
        print(f"💰 Offer '{offer_type}' → boost: {multiplier}")
    return multiplier

# =============================================================
# GET ITEM OFFER IMPACT
# =============================================================
def get_item_offer_impact(item, is_offer):
    """
    Returns offer impact for specific item.

    Args:
        item     : str (food item)
        is_offer : int (0 or 1)

    Returns:
        float : multiplier
    """
    if not is_offer:
        return 1.0

    sensitivity = ITEM_OFFER_SENSITIVITY.get(item, 1.10)
    print(f"💰 '{item}' offer sensitivity → {sensitivity}")
    return sensitivity

# =============================================================
# APPLY OFFER TO PREDICTION
# =============================================================
def apply_offer_to_prediction(predicted_sales, item, is_offer):
    """
    Applies offer multiplier to predicted sales.

    Args:
        predicted_sales : float
        item            : str
        is_offer        : int (0 or 1)

    Returns:
        float : adjusted sales
    """
    multiplier     = get_item_offer_impact(item, is_offer)
    adjusted_sales = round(predicted_sales * multiplier)

    if is_offer:
        print(f"  {item:<12} {predicted_sales} → {adjusted_sales} (offer applied)")

    return adjusted_sales

# =============================================================
# OFFERS SUMMARY
# =============================================================
def get_offers_summary():
    """
    Prints summary of all offer impacts.
    """
    print("\n" + "="*50)
    print("  OFFERS IMPACT SUMMARY")
    print("="*50)
    print("\n  💰 Offer Types:")
    for offer, impact in OFFER_TYPES.items():
        bar    = "█" * int(impact * 15)
        effect = "🔺 Boost" if impact > 1 else "➖ None"
        print(f"    {offer:<15} {bar:<25} {impact:.2f}  {effect}")
    print("\n  🍽️  Item Sensitivity:")
    for item, sens in ITEM_OFFER_SENSITIVITY.items():
        bar = "█" * int(sens * 15)
        print(f"    {item:<12} {bar:<25} {sens:.2f}")
    print("="*50)

    """BOGO +40%, Combo +25%
        Noodles most offer-sensitive +25%
        Applies offer to any prediction"""