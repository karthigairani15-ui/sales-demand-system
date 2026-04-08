# =============================================================
# weather.py — Weather Impact on Food Sales
# =============================================================

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config.settings import WEATHER_TYPES

# =============================================================
# WEATHER IMPACT MULTIPLIERS
# =============================================================
WEATHER_IMPACT = {
    "Sunny"  : 1.10,   # More footfall
    "Rainy"  : 0.80,   # People stay home
    "Cloudy" : 0.95,   # Slightly less
    "Windy"  : 0.90    # Less outdoor movement
}

WEATHER_ITEM_IMPACT = {
    "Rainy" : {
        "Biryani" : 1.20,   # Hot food preferred
        "Noodles" : 1.15,   # Hot food preferred
        "Dosa"    : 1.10,
        "Meals"   : 0.90,
        "Parotta" : 1.05
    },
    "Sunny" : {
        "Dosa"    : 1.15,
        "Meals"   : 1.10,
        "Biryani" : 1.05,
        "Noodles" : 0.95,
        "Parotta" : 1.00
    }
}

# =============================================================
# GET WEATHER MULTIPLIER
# =============================================================
def get_weather_multiplier(weather_type):
    """
    Returns overall sales multiplier for given weather.

    Args:
        weather_type : str (Sunny/Rainy/Cloudy/Windy)

    Returns:
        float : multiplier
    """
    if weather_type not in WEATHER_IMPACT:
        print(f"⚠️  Unknown weather '{weather_type}' → using 1.0")
        return 1.0

    multiplier = WEATHER_IMPACT[weather_type]
    print(f"🌦️  Weather '{weather_type}' → multiplier: {multiplier}")
    return multiplier

# =============================================================
# GET ITEM-SPECIFIC WEATHER IMPACT
# =============================================================
def get_item_weather_impact(weather_type, item):
    """
    Returns item-specific weather multiplier.

    Args:
        weather_type : str
        item         : str (food item name)

    Returns:
        float : multiplier
    """
    if weather_type in WEATHER_ITEM_IMPACT:
        item_impacts = WEATHER_ITEM_IMPACT[weather_type]
        return item_impacts.get(item, 1.0)

    return get_weather_multiplier(weather_type)

# =============================================================
# WEATHER SUMMARY
# =============================================================
def get_weather_summary():
    """
    Prints a summary of all weather impacts.
    """
    print("\n" + "="*50)
    print("  WEATHER IMPACT SUMMARY")
    print("="*50)
    for weather, impact in WEATHER_IMPACT.items():
        bar    = "█" * int(impact * 20)
        effect = "🔺 Boost" if impact > 1 else "🔻 Drop"
        print(f"  {weather:<8} {bar:<25} {impact:.2f}  {effect}")
    print("="*50)

    """ Sunny +10%, Rainy -20%
        Item-specific weather impact
        e.g. Biryani sells more in Rain"""