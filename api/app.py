# =============================================================
# app.py — Flask API for Sales Demand Prediction System
# =============================================================

import sys
import os
import json
from flask import Flask, request, jsonify

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.predict        import predict_all_items
from src.modules.production    import generate_production_plan
from src.modules.inventory     import (
    initialize_inventory,
    update_inventory,
    get_inventory_status
)
from src.modules.pos           import simulate_sales, get_sales_dict
from src.modules.consumption   import (
    convert_pos_to_consumption,
    get_consumption_summary
)
from src.modules.waste         import calculate_waste, get_waste_summary
from src.modules.loss          import calculate_loss, generate_loss_report
from src.external.weather      import get_weather_multiplier
from src.external.location     import get_location_timeslot_multiplier
from src.external.events       import get_combined_event_multiplier
from src.external.offers       import get_offers_summary
from src.config.settings       import FLASK_HOST, FLASK_PORT, FLASK_DEBUG

# =============================================================
# INITIALIZE FLASK APP
# =============================================================
app = Flask(__name__)

# =============================================================
# ROOT ENDPOINT
# =============================================================
@app.route("/", methods=["GET"])
def home():
    """
    Root endpoint — API health check.
    """
    return jsonify({
        "status"  : "✅ Running",
        "message" : "Sales Demand Prediction API",
        "version" : "1.0.0",
        "endpoints": {
            "POST /predict"    : "Predict sales for all items",
            "POST /full-pipeline": "Run full pipeline end-to-end",
            "GET  /health"     : "Health check",
            "GET  /summary"    : "External factors summary"
        }
    })

# =============================================================
# HEALTH CHECK
# =============================================================
@app.route("/health", methods=["GET"])
def health():
    """
    Health check endpoint.
    """
    return jsonify({
        "status" : "healthy",
        "model"  : "loaded"
    })

# =============================================================
# PREDICT ENDPOINT
# =============================================================
@app.route("/predict", methods=["POST"])
def predict():
    """
    Predicts sales for all food items.

    Expected JSON input:
    {
        "weather_type"      : "Sunny",
        "location_type"     : "Office_Area",
        "time_slot"         : "Lunch",
        "festival"          : "None",
        "special_event"     : "None",
        "is_weekend"        : 0,
        "is_festival"       : 0,
        "is_nonveg_day"     : 1,
        "is_special_event"  : 0,
        "is_offer"          : 1,
        "previous_day_sales": 90
    }

    Returns:
        JSON with predictions for all items
    """

    try:
        # -------------------------------------------------------
        # PARSE INPUT
        # -------------------------------------------------------
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No input data provided"
            }), 400

        # -------------------------------------------------------
        # EXTRACT PARAMETERS WITH DEFAULTS
        # -------------------------------------------------------
        weather_type       = data.get("weather_type",       "Sunny")
        location_type      = data.get("location_type",      "Office_Area")
        time_slot          = data.get("time_slot",          "Lunch")
        festival           = data.get("festival",           "None")
        special_event      = data.get("special_event",      "None")
        is_weekend         = int(data.get("is_weekend",         0))
        is_festival        = int(data.get("is_festival",        0))
        is_nonveg_day      = int(data.get("is_nonveg_day",      1))
        is_special_event   = int(data.get("is_special_event",   0))
        is_offer           = int(data.get("is_offer",           0))
        previous_day_sales = float(data.get("previous_day_sales", 0))

        # -------------------------------------------------------
        # GET EXTERNAL FACTOR MULTIPLIERS
        # -------------------------------------------------------
        weather_mult  = get_weather_multiplier(weather_type)
        location_mult = get_location_timeslot_multiplier(
            location_type, time_slot
        )
        event_mult    = get_combined_event_multiplier(
            festival, special_event
        )

        # -------------------------------------------------------
        # PREDICT SALES
        # -------------------------------------------------------
        predictions = predict_all_items(
            weather_type       = weather_type,
            location_type      = location_type,
            time_slot          = time_slot,
            festival           = festival,
            special_event      = special_event,
            is_weekend         = is_weekend,
            is_festival        = is_festival,
            is_nonveg_day      = is_nonveg_day,
            is_special_event   = is_special_event,
            is_offer           = is_offer,
            previous_day_sales = previous_day_sales
        )

        # -------------------------------------------------------
        # RETURN RESPONSE
        # -------------------------------------------------------
        return jsonify({
            "status"      : "success",
            "input"       : {
                "weather_type"  : weather_type,
                "location_type" : location_type,
                "time_slot"     : time_slot,
                "festival"      : festival,
                "special_event" : special_event,
                "is_weekend"    : is_weekend,
                "is_offer"      : is_offer
            },
            "multipliers" : {
                "weather"  : weather_mult,
                "location" : location_mult,
                "events"   : event_mult
            },
            "predictions" : predictions
        })

    except Exception as e:
        return jsonify({
            "status" : "error",
            "message": str(e)
        }), 500

# =============================================================
# FULL PIPELINE ENDPOINT
# =============================================================
@app.route("/full-pipeline", methods=["POST"])
def full_pipeline():
    """
    Runs the complete pipeline:
    Predict → Production → Inventory →
    POS → Consumption → Waste → Loss

    Same input as /predict endpoint.

    Returns:
        JSON with complete pipeline results
    """

    try:
        # -------------------------------------------------------
        # PARSE INPUT
        # -------------------------------------------------------
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No input data provided"
            }), 400

        # -------------------------------------------------------
        # EXTRACT PARAMETERS
        # -------------------------------------------------------
        weather_type       = data.get("weather_type",       "Sunny")
        location_type      = data.get("location_type",      "Office_Area")
        time_slot          = data.get("time_slot",          "Lunch")
        festival           = data.get("festival",           "None")
        special_event      = data.get("special_event",      "None")
        is_weekend         = int(data.get("is_weekend",         0))
        is_festival        = int(data.get("is_festival",        0))
        is_nonveg_day      = int(data.get("is_nonveg_day",      1))
        is_special_event   = int(data.get("is_special_event",   0))
        is_offer           = int(data.get("is_offer",           0))
        previous_day_sales = float(data.get("previous_day_sales", 0))

        context = {
            "weather_type"  : weather_type,
            "location_type" : location_type,
            "time_slot"     : time_slot,
            "festival"      : festival,
            "special_event" : special_event,
            "is_offer"      : is_offer
        }

        # -------------------------------------------------------
        # STEP 1: PREDICT
        # -------------------------------------------------------
        predictions = predict_all_items(
            weather_type       = weather_type,
            location_type      = location_type,
            time_slot          = time_slot,
            festival           = festival,
            special_event      = special_event,
            is_weekend         = is_weekend,
            is_festival        = is_festival,
            is_nonveg_day      = is_nonveg_day,
            is_special_event   = is_special_event,
            is_offer           = is_offer,
            previous_day_sales = previous_day_sales
        )

        # -------------------------------------------------------
        # STEP 2: PRODUCTION
        # -------------------------------------------------------
        production_plan = generate_production_plan(predictions)

        # -------------------------------------------------------
        # STEP 3: INVENTORY
        # -------------------------------------------------------
        inventory = initialize_inventory(production_plan)

        # -------------------------------------------------------
        # STEP 4: POS
        # -------------------------------------------------------
        pos_records = simulate_sales(inventory, context)
        sales_dict  = get_sales_dict(pos_records)

        # -------------------------------------------------------
        # STEP 5: UPDATE INVENTORY
        # -------------------------------------------------------
        updated_inventory = update_inventory(inventory, sales_dict)

        # -------------------------------------------------------
        # STEP 6: CONSUMPTION
        # -------------------------------------------------------
        consumption        = convert_pos_to_consumption(pos_records)
        consumption_summary = get_consumption_summary(consumption)

        # -------------------------------------------------------
        # STEP 7: WASTE
        # -------------------------------------------------------
        waste_records = calculate_waste(production_plan, pos_records)
        waste_summary = json.loads(get_waste_summary(waste_records))

        # -------------------------------------------------------
        # STEP 8: LOSS
        # -------------------------------------------------------
        loss_records = calculate_loss(waste_records)
        loss_report  = json.loads(generate_loss_report(loss_records))

        # -------------------------------------------------------
        # RETURN FULL RESPONSE
        # -------------------------------------------------------
        return jsonify({
            "status"          : "success",
            "context"         : context,
            "predictions"     : predictions,
            "production_plan" : production_plan,
            "inventory"       : updated_inventory,
            "consumption"     : consumption_summary,
            "waste_summary"   : waste_summary,
            "loss_report"     : loss_report
        })

    except Exception as e:
        return jsonify({
            "status" : "error",
            "message": str(e)
        }), 500

# =============================================================
# SUMMARY ENDPOINT
# =============================================================
@app.route("/summary", methods=["GET"])
def summary():
    """
    Returns summary of all external factors.
    """
    from src.external.weather  import WEATHER_IMPACT
    from src.external.location import LOCATION_IMPACT
    from src.external.events   import FESTIVAL_IMPACT, EVENT_IMPACT
    from src.external.offers   import OFFER_TYPES

    return jsonify({
        "weather_impact"  : WEATHER_IMPACT,
        "location_impact" : LOCATION_IMPACT,
        "festival_impact" : FESTIVAL_IMPACT,
        "event_impact"    : EVENT_IMPACT,
        "offer_types"     : OFFER_TYPES
    })

# =============================================================
# RUN APP
# =============================================================
if __name__ == "__main__":
    app.run(
        host  = FLASK_HOST,
        port  = FLASK_PORT,
        debug = FLASK_DEBUG
    )


    """ Client sends JSON
      ↓
Flask receives input
      ↓
predict_all_items()     → ML predictions
      ↓
generate_production_plan() → +buffer
      ↓
initialize_inventory()  → stock setup
      ↓
simulate_sales()        → POS records
      ↓
update_inventory()      → deduct sold
      ↓
convert_pos_to_consumption() → track usage
      ↓
calculate_waste()       → produced - sold
      ↓
generate_loss_report()  → waste × cost
      ↓
Return full JSON response"""