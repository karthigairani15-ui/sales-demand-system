# =============================================================
# events.py — Special Events & Festival Impact
# =============================================================

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import FESTIVALS, SPECIAL_EVENTS

# =============================================================
# FESTIVAL IMPACT
# =============================================================
FESTIVAL_IMPACT = {
    "Pongal"    : 1.40,   # Major Tamil festival
    "Diwali"    : 1.45,   # Huge boost
    "Christmas" : 1.30,
    "New Year"  : 1.50,   # Biggest boost
    "Eid"       : 1.35,
    "None"      : 1.00
}

# =============================================================
# SPECIAL EVENT IMPACT
# =============================================================
EVENT_IMPACT = {
    "Cricket Match"  : 1.35,   # Big crowd
    "Local Festival" : 1.25,
    "College Event"  : 1.20,
    "None"           : 1.00
}

# =============================================================
# GET FESTIVAL MULTIPLIER
# =============================================================
def get_festival_multiplier(festival):
    """
    Returns sales multiplier for given festival.

    Args:
        festival : str

    Returns:
        float : multiplier
    """
    if festival not in FESTIVAL_IMPACT:
        print(f"⚠️  Unknown festival '{festival}' → using 1.0")
        return 1.0

    multiplier = FESTIVAL_IMPACT[festival]
    if multiplier > 1.0:
        print(f"🎉 Festival '{festival}' → boost: {multiplier}")
    return multiplier

# =============================================================
# GET EVENT MULTIPLIER
# =============================================================
def get_event_multiplier(special_event):
    """
    Returns sales multiplier for special event.

    Args:
        special_event : str

    Returns:
        float : multiplier
    """
    if special_event not in EVENT_IMPACT:
        print(f"⚠️  Unknown event '{special_event}' → using 1.0")
        return 1.0

    multiplier = EVENT_IMPACT[special_event]
    if multiplier > 1.0:
        print(f"🏆 Event '{special_event}' → boost: {multiplier}")
    return multiplier

# =============================================================
# GET COMBINED EVENT MULTIPLIER
# =============================================================
def get_combined_event_multiplier(festival, special_event):
    """
    Returns combined festival + event multiplier.
    Caps at 2.0 to avoid unrealistic predictions.

    Returns:
        float : combined multiplier (max 2.0)
    """
    fest_mult  = get_festival_multiplier(festival)
    event_mult = get_event_multiplier(special_event)

    combined = round(min(fest_mult * event_mult, 2.0), 2)
    print(f"🎯 Combined event multiplier → {combined}")
    return combined

# =============================================================
# EVENTS SUMMARY
# =============================================================
def get_events_summary():
    """
    Prints summary of all event impacts.
    """
    print("\n" + "="*50)
    print("  EVENTS IMPACT SUMMARY")
    print("="*50)
    print("\n  🎉 Festivals:")
    for fest, impact in FESTIVAL_IMPACT.items():
        bar = "█" * int(impact * 15)
        print(f"    {fest:<15} {bar:<25} {impact:.2f}")
    print("\n  🏆 Special Events:")
    for event, impact in EVENT_IMPACT.items():
        bar = "█" * int(impact * 15)
        print(f"    {event:<20} {bar:<25} {impact:.2f}")
    print("="*50)

    """New Year +50%, Diwali +45%
               Cricket Match +35%
               Combined festival+event (capped at 2.0x)
"""