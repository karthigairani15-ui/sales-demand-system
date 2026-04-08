# =============================================================
# location.py — Location-Based Demand Patterns
# =============================================================

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import LOCATION_TYPES

# =============================================================
# LOCATION MULTIPLIERS
# =============================================================
LOCATION_IMPACT = {
    "Office_Area" : 1.20,   # High lunch demand
    "Residential" : 1.15,   # High dinner demand
    "College"     : 1.10,   # Steady demand
    "Market"      : 1.05    # Mixed demand
}

# Time slot specific multipliers per location
LOCATION_TIMESLOT_IMPACT = {
    "Office_Area" : {
        "Lunch"  : 1.30,    # Office lunch peak
        "Dinner" : 0.70     # Low after office hours
    },
    "Residential" : {
        "Lunch"  : 0.90,
        "Dinner" : 1.25     # Family dinner peak
    },
    "College" : {
        "Lunch"  : 1.15,
        "Dinner" : 1.05
    },
    "Market" : {
        "Lunch"  : 1.10,
        "Dinner" : 1.10
    }
}

# =============================================================
# GET LOCATION MULTIPLIER
# =============================================================
def get_location_multiplier(location_type):
    """
    Returns overall demand multiplier for location.

    Args:
        location_type : str

    Returns:
        float : multiplier
    """
    if location_type not in LOCATION_IMPACT:
        print(f"⚠️  Unknown location '{location_type}' → using 1.0")
        return 1.0

    multiplier = LOCATION_IMPACT[location_type]
    print(f"📍 Location '{location_type}' → multiplier: {multiplier}")
    return multiplier

# =============================================================
# GET LOCATION + TIME SLOT MULTIPLIER
# =============================================================
def get_location_timeslot_multiplier(location_type, time_slot):
    """
    Returns combined location + time slot multiplier.

    Args:
        location_type : str
        time_slot     : str (Lunch/Dinner)

    Returns:
        float : multiplier
    """
    if location_type in LOCATION_TIMESLOT_IMPACT:
        slots = LOCATION_TIMESLOT_IMPACT[location_type]
        multiplier = slots.get(time_slot, 1.0)
        print(f"📍 {location_type} + {time_slot} → multiplier: {multiplier}")
        return multiplier

    return get_location_multiplier(location_type)

# =============================================================
# LOCATION SUMMARY
# =============================================================
def get_location_summary():
    """
    Prints a summary of all location impacts.
    """
    print("\n" + "="*50)
    print("  LOCATION DEMAND SUMMARY")
    print("="*50)
    for loc, slots in LOCATION_TIMESLOT_IMPACT.items():
        print(f"\n  📍 {loc}")
        for slot, impact in slots.items():
            bar    = "█" * int(impact * 15)
            effect = "🔺 Boost" if impact > 1 else "🔻 Drop"
            print(f"     {slot:<8} {bar:<25} {impact:.2f}  {effect}")
    print("="*50)
    
    """Office lunch peak +30%
    Residential dinner peak +25%
    Combined location+timeslot logic"""