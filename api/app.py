# =============================================================
# app.py — Flask API + UI for Sales Demand Prediction System
# FIX: normalize_consumption now uses "sold_qty" key (matches
#      pos.py record structure), not "sold" or "qty"
# =============================================================

import sys
import os
import json
from flask import Flask, request, jsonify, render_template

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models.predict        import predict_all_items
from src.modules.production    import generate_production_plan
from src.modules.inventory     import (
    initialize_inventory,
    update_inventory,
    get_inventory_status,
)
from src.modules.pos           import simulate_sales, get_sales_dict
from src.modules.consumption   import (
    convert_pos_to_consumption,
    get_consumption_summary,
)
from src.modules.waste         import calculate_waste, get_waste_summary
from src.modules.loss          import calculate_loss, generate_loss_report
from src.external.weather      import get_weather_multiplier
from src.external.location     import get_location_timeslot_multiplier
from src.external.events       import get_combined_event_multiplier
from src.external.offers       import get_offers_summary
from src.config.settings       import (
    FLASK_HOST, FLASK_PORT, FLASK_DEBUG, FOOD_ITEMS, ITEM_COST
)

# =============================================================
# FLASK APP INIT
# =============================================================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

print(f"[DEBUG] ROOT_DIR   : {ROOT_DIR}")
print(f"[DEBUG] templates/ : {os.path.join(ROOT_DIR, 'templates')}")
print(f"[DEBUG] static/    : {os.path.join(ROOT_DIR, 'static')}")

app = Flask(
    __name__,
    template_folder = os.path.join(ROOT_DIR, "templates"),
    static_folder   = os.path.join(ROOT_DIR, "static"),
)

# =============================================================
# DATA NORMALIZERS
# =============================================================

def normalize_consumption(pos_records, context):
    """
    Builds a clean list-of-lists from pos_records directly.
    FIX: uses "sold_qty" key (correct key from pos.py),
         not "sold" or "qty" (those keys don't exist).

    Each row: [item, qty_sold, timestamp, location, slot, weather]
    """
    rows = []
    for rec in pos_records:
        if isinstance(rec, dict):
            rows.append([
                rec.get("item",      ""),
                rec.get("sold_qty",  0),        # ← FIXED: was rec.get("sold", ...)
                rec.get("timestamp", ""),
                rec.get("location",  context.get("location_type", "")),
                rec.get("time_slot", context.get("time_slot",     "")),
                rec.get("weather",   context.get("weather_type",  "")),
            ])
        elif isinstance(rec, (list, tuple)) and len(rec) >= 2:
            row = list(rec)
            while len(row) < 6:
                row.append("")
            rows.append(row[:6])
    return rows


def normalize_waste(waste_summary):
    """
    Unwraps any wrapper and returns:
    list of {item, produced, sold, waste, waste_pct, status}
    """
    if isinstance(waste_summary, list):
        result = []
        for row in waste_summary:
            if isinstance(row, dict):
                result.append({
                    "item"     : row.get("item",      ""),
                    "produced" : row.get("produced",  row.get("production_qty", 0)),
                    "sold"     : row.get("sold",       0),
                    "waste"    : row.get("waste",      row.get("wasted", 0)),
                    "waste_pct": row.get("waste_pct",  row.get("waste_percent", 0)),
                    "status"   : row.get("status",     ""),
                })
        return result

    if isinstance(waste_summary, dict):
        for key in ("items", "summary", "data", "records", "waste_records"):
            if key in waste_summary:
                return normalize_waste(waste_summary[key])
        # Dict keyed by item name
        result = []
        for item_name, v in waste_summary.items():
            if isinstance(v, dict):
                result.append({
                    "item"     : item_name,
                    "produced" : v.get("produced",  0),
                    "sold"     : v.get("sold",       0),
                    "waste"    : v.get("waste",      v.get("wasted", 0)),
                    "waste_pct": v.get("waste_pct",  0),
                    "status"   : v.get("status",     ""),
                })
            else:
                result.append({
                    "item": item_name, "produced": 0,
                    "sold": 0, "waste": v, "waste_pct": 0, "status": "",
                })
        return result

    return []


def normalize_loss(loss_report, waste_rows):
    """
    Always returns:
    {total_loss, severity, loss_records: [{item, waste_qty, cost, loss}]}

    Severity thresholds (realistic for small restaurant):
      🟢 Low      : total_loss < 1500
      🟡 Medium   : total_loss < 4000
      🔴 High     : total_loss >= 4000
    """
    if isinstance(loss_report, dict) and "loss_records" in loss_report:
        records = []
        for rec in loss_report["loss_records"]:
            records.append({
                "item"     : rec.get("item",      ""),
                "waste_qty": rec.get("waste_qty",  rec.get("waste", 0)),
                "cost"     : rec.get("cost",       rec.get("cost_per_unit", 0)),
                "loss"     : rec.get("loss",       rec.get("total_loss", 0)),
            })
        total = loss_report.get("total_loss", sum(r["loss"] for r in records))
        severity = (
            "🟢 Low Loss"    if total < 1500 else
            "🟡 Medium Loss" if total < 4000 else
            "🔴 High Loss"
        )
        return {
            "total_loss"   : total,
            "severity"     : severity,
            "loss_records" : records,
        }

    # Rebuild from waste_rows + ITEM_COST as fallback
    records = []
    total   = 0
    for row in waste_rows:
        item     = row["item"]
        waste_qty= row["waste"]
        cost     = ITEM_COST.get(item, 0)
        loss_val = waste_qty * cost
        total   += loss_val
        records.append({
            "item"     : item,
            "waste_qty": waste_qty,
            "cost"     : cost,
            "loss"     : loss_val,
        })

    severity = (
        "🟢 Low Loss"    if total < 1500 else
        "🟡 Medium Loss" if total < 4000 else
        "🔴 High Loss"
    )
    return {"total_loss": total, "severity": severity, "loss_records": records}


def _parse_form(form):
    return {
        "weather_type"      : form.get("weather_type",       "Sunny"),
        "location_type"     : form.get("location_type",      "Office_Area"),
        "time_slot"         : form.get("time_slot",          "Lunch"),
        "festival"          : form.get("festival",           "None"),
        "special_event"     : form.get("special_event",      "None"),
        "is_weekend"        : int(form.get("is_weekend",         0)),
        "is_festival"       : int(form.get("is_festival",        0)),
        "is_nonveg_day"     : int(form.get("is_nonveg_day",      0)),
        "is_special_event"  : int(form.get("is_special_event",   0)),
        "is_offer"          : int(form.get("is_offer",           0)),
        "previous_day_sales": float(form.get("previous_day_sales", 0)),
    }


# =============================================================
# UI ROUTES
# =============================================================

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", error=None)


@app.route("/ui/predict", methods=["POST"])
def ui_predict():
    try:
        params        = _parse_form(request.form)
        predictions   = predict_all_items(**params)
        weather_mult  = get_weather_multiplier(params["weather_type"])
        location_mult = get_location_timeslot_multiplier(
            params["location_type"], params["time_slot"]
        )
        event_mult    = get_combined_event_multiplier(
            params["festival"], params["special_event"]
        )
        return render_template(
            "result.html",
            predictions   = predictions,
            params        = params,
            weather_mult  = weather_mult,
            location_mult = location_mult,
            event_mult    = event_mult,
            error         = None,
        )
    except Exception as e:
        return render_template("index.html", error=str(e))


@app.route("/ui/full-pipeline", methods=["POST"])
def ui_full_pipeline():
    try:
        params = _parse_form(request.form)

        context = {
            "weather_type"  : params["weather_type"],
            "location_type" : params["location_type"],
            "time_slot"     : params["time_slot"],
            "festival"      : params["festival"],
            "special_event" : params["special_event"],
            "is_offer"      : params["is_offer"],
        }

        # ── Step 1: Predict
        predictions = predict_all_items(**params)

        # ── Step 2: Production  (uses PRODUCTION_BUFFER from settings.py)
        production_plan = generate_production_plan(predictions)

        # ── Step 3: Inventory
        inventory = initialize_inventory(production_plan)

        # ── Step 4: POS  (uses sell_ratio 0.93–0.97 from pos.py)
        pos_records = simulate_sales(inventory, context)
        sales_dict  = get_sales_dict(pos_records)

        # ── Step 5: Update Inventory
        updated_inventory = update_inventory(inventory, sales_dict)

        # ── Step 6: Consumption
        # FIX: build from pos_records directly using "sold_qty" key
        consumption_summary = normalize_consumption(pos_records, context)

        # ── Step 7: Waste
        waste_records  = calculate_waste(production_plan, pos_records)
        raw_waste_json = json.loads(get_waste_summary(waste_records))
        waste_summary  = normalize_waste(raw_waste_json)

        # ── Step 8: Loss
        loss_records   = calculate_loss(waste_records)
        raw_loss_json  = json.loads(generate_loss_report(loss_records))
        loss_report    = normalize_loss(raw_loss_json, waste_summary)

        return render_template(
            "full_result.html",
            context             = context,
            predictions         = predictions,
            production_plan     = production_plan,
            inventory           = updated_inventory,
            consumption_summary = consumption_summary,
            waste_summary       = waste_summary,
            loss_report         = loss_report,
            error               = None,
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return render_template("index.html", error=str(e))


# =============================================================
# REST API ROUTES (unchanged — still work for curl/Postman)
# =============================================================

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "model": "loaded"})


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

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

        weather_mult  = get_weather_multiplier(weather_type)
        location_mult = get_location_timeslot_multiplier(location_type, time_slot)
        event_mult    = get_combined_event_multiplier(festival, special_event)
        predictions   = predict_all_items(
            weather_type=weather_type, location_type=location_type,
            time_slot=time_slot, festival=festival,
            special_event=special_event, is_weekend=is_weekend,
            is_festival=is_festival, is_nonveg_day=is_nonveg_day,
            is_special_event=is_special_event, is_offer=is_offer,
            previous_day_sales=previous_day_sales,
        )
        return jsonify({
            "status"     : "success",
            "multipliers": {"weather": weather_mult, "location": location_mult, "events": event_mult},
            "predictions": predictions,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/full-pipeline", methods=["POST"])
def full_pipeline():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

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

        context     = {
            "weather_type": weather_type, "location_type": location_type,
            "time_slot": time_slot, "festival": festival,
            "special_event": special_event, "is_offer": is_offer,
        }
        predictions        = predict_all_items(
            weather_type=weather_type, location_type=location_type,
            time_slot=time_slot, festival=festival,
            special_event=special_event, is_weekend=is_weekend,
            is_festival=is_festival, is_nonveg_day=is_nonveg_day,
            is_special_event=is_special_event, is_offer=is_offer,
            previous_day_sales=previous_day_sales,
        )
        production_plan     = generate_production_plan(predictions)
        inventory           = initialize_inventory(production_plan)
        pos_records         = simulate_sales(inventory, context)
        sales_dict          = get_sales_dict(pos_records)
        updated_inventory   = update_inventory(inventory, sales_dict)
        consumption_summary = normalize_consumption(pos_records, context)
        waste_records       = calculate_waste(production_plan, pos_records)
        raw_waste           = json.loads(get_waste_summary(waste_records))
        waste_summary       = normalize_waste(raw_waste)
        loss_records        = calculate_loss(waste_records)
        raw_loss            = json.loads(generate_loss_report(loss_records))
        loss_report         = normalize_loss(raw_loss, waste_summary)

        return jsonify({
            "status"         : "success",
            "context"        : context,
            "predictions"    : predictions,
            "production_plan": production_plan,
            "inventory"      : updated_inventory,
            "consumption"    : consumption_summary,
            "waste_summary"  : waste_summary,
            "loss_report"    : loss_report,
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/summary", methods=["GET"])
def summary():
    from src.external.weather  import WEATHER_IMPACT
    from src.external.location import LOCATION_IMPACT
    from src.external.events   import FESTIVAL_IMPACT, EVENT_IMPACT
    from src.external.offers   import OFFER_TYPES
    return jsonify({
        "weather_impact" : WEATHER_IMPACT,
        "location_impact": LOCATION_IMPACT,
        "festival_impact": FESTIVAL_IMPACT,
        "event_impact"   : EVENT_IMPACT,
        "offer_types"    : OFFER_TYPES,
    })


# =============================================================
# RUN APP
# =============================================================
if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)