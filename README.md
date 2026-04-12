# 🍽️ Sales Demand Prediction System

> An AI-powered food sales demand prediction and management system that integrates weather, location, festivals, events, time slots, and offers to predict demand and automate production, inventory, waste, and loss calculation — with a smart dashboard UI.

![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0.3-black?style=flat-square&logo=flask)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4.2-orange?style=flat-square&logo=scikit-learn)
![RandomForest](https://img.shields.io/badge/Model-RandomForest-green?style=flat-square)
![R²](https://img.shields.io/badge/Accuracy-83.8%25%20R²-brightgreen?style=flat-square)
![Status](https://img.shields.io/badge/Status-Complete-success?style=flat-square)

---

## 📌 Project Overview

This system predicts food demand for a restaurant or canteen using machine learning. It takes intelligent inputs like weather, location, day type, festival, and promotional offers — and outputs a complete operational plan including production quantity, inventory tracking, waste calculation, and financial loss reporting.

The system includes a **smart dashboard** with two input modes:
- **Auto Mode** — enter a date, and the system detects weekend, festival, weather, and location automatically
- **Manual Mode** — full control over all prediction inputs

---

## 🧠 Intelligence Factors

| Factor | Impact |
|---|---|
| Weekend | +25% sales boost |
| Festival (Diwali) | +45% boost |
| Festival (New Year) | +50% boost |
| Rainy Weather | −20% drop |
| Sunny Weather | +10% boost |
| Office Area + Lunch | +30% boost |
| Residential + Dinner | +25% boost |
| Cricket Match | +35% boost |
| Offer / Discount | +15% boost |
| Non-Veg Restriction Day | −30% for Biryani/Parotta |

---

## 🏗️ Project Structure

```
sales-demand-system/
│
├── notebook/
│   └── main.ipynb                  ← Full ML pipeline notebook (10 cells)
│
├── src/
│   ├── config/
│   │   └── settings.py             ← Central configuration
│   ├── data/
│   │   └── data_generator.py       ← Generates 2000-row dataset
│   ├── features/
│   │   └── feature_engineering.py  ← Encodes features, saves encoder
│   ├── models/
│   │   ├── train_model.py          ← Trains RandomForest model
│   │   ├── predict.py              ← Prediction engine
│   │   └── model_utils.py          ← Load/verify model artifacts
│   ├── modules/
│   │   ├── production.py           ← Buffer-based production planning
│   │   ├── inventory.py            ← Stock tracking
│   │   ├── pos.py                  ← Simulates real-time sales
│   │   ├── consumption.py          ← Tracks item consumption
│   │   ├── waste.py                ← Calculates waste (produced − sold)
│   │   └── loss.py                 ← Calculates financial loss (waste × cost)
│   └── external/
│       ├── weather.py              ← Weather impact multipliers
│       ├── location.py             ← Location + time slot demand
│       ├── events.py               ← Festival and event boosts
│       └── offers.py               ← Discount and offer impact
│
├── api/
│   ├── app.py                      ← Flask REST API + dashboard
│   ├── templates/
│   │   └── index.html              ← Smart dashboard UI
│   └── static/
│       └── style.css               ← Dashboard styling
│
├── data/
│   └── dataset.csv                 ← Generated training data (2000 rows)
│
├── artifacts/
│   ├── model.pkl                   ← Trained RandomForest model
│   └── encoder.pkl                 ← Fitted label encoders
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 📊 ML Model Performance

| Metric | Value |
|---|---|
| Algorithm | RandomForestRegressor |
| Training Rows | 1600 |
| Test Rows | 400 |
| Total Dataset | 2000 rows |
| Trees (n_estimators) | 500 |
| Max Depth | 15 |
| MAE | 14.31 |
| RMSE | 18.47 |
| R² Score | **0.8380 (83.8%)** |

### Feature Importance

| Rank | Feature | Importance |
|---|---|---|
| 1 | is_weekend | 0.1638 |
| 2 | location_type | 0.1465 |
| 3 | item | 0.1250 |
| 4 | previous_day_sales | 0.0991 |
| 5 | weather_type | 0.0839 |
| 6 | time_slot | 0.0827 |
| 7 | festival | 0.0778 |

---

## 🚀 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/sales-demand-system.git
cd sales-demand-system
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Register Jupyter Kernel
```bash
python3 -m ipykernel install --user \
  --name=sales-demand-venv \
  --display-name "Sales Demand (venv)"
```

### 5. Run the Notebook (Train Model)
```bash
cd notebook
jupyter notebook main.ipynb
```
Run all 11 cells in order — this generates the dataset, trains the model, and saves artifacts.

### 6. Run the Flask Dashboard
```bash
python api/app.py
```
Open your browser → `http://localhost:5000`

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Smart dashboard UI |
| GET | `/health` | API health check |
| GET | `/summary` | All factor multipliers |
| POST | `/predict` | Predict sales for all items |
| POST | `/full-pipeline` | Full pipeline: predict → production → inventory → POS → consumption → waste → loss |

---

## 📬 Sample API Request

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "weather_type"       : "Sunny",
    "location_type"      : "Office_Area",
    "time_slot"          : "Lunch",
    "festival"           : "None",
    "special_event"      : "None",
    "is_weekend"         : 0,
    "is_festival"        : 0,
    "is_nonveg_day"      : 1,
    "is_special_event"   : 0,
    "is_offer"           : 1,
    "previous_day_sales" : 90
  }'
```

### Sample Response

```json
{
  "status": "success",
  "multipliers": {
    "weather": 1.1,
    "location": 1.3,
    "events": 1.0
  },
  "predictions": [
    { "item": "Biryani",  "predicted_sales": 133 },
    { "item": "Meals",    "predicted_sales": 164 },
    { "item": "Parotta",  "predicted_sales": 153 },
    { "item": "Noodles",  "predicted_sales": 141 },
    { "item": "Dosa",     "predicted_sales": 149 }
  ]
}
```

---

## 🍽️ Food Items & Pricing

| Item | Base Price (₹) | Base Sales/Day |
|---|---|---|
| Biryani | ₹120 | 80 units |
| Meals | ₹80 | 100 units |
| Parotta | ₹50 | 90 units |
| Noodles | ₹70 | 70 units |
| Dosa | ₹40 | 85 units |

---

## 💡 Key Features

- **Smart Date Input** — Auto-detects weekend, festival, weather from date
- **Dual Input Mode** — Auto (date-based) or Manual (full control)
- **Full Pipeline** — From prediction to loss calculation in one API call
- **Loss Optimisation** — Smart buffer logic reduced loss by 38.1% (₹7210 → ₹4460)
- **Clean Dashboard** — Tables, progress bars, severity indicators, no raw JSON
- **Modular Architecture** — Each module is independent and reusable
- **No External APIs** — Fully offline, no internet dependency

---

## 📓 Notebook Pipeline

| Cell | Description | Output |
|---|---|---|
| 1 | Imports | ✅ Ready |
| 2 | Generate Dataset | 2000 rows saved to CSV |
| 3 | Explore Dataset | Stats by item, weather |
| 4 | Feature Engineering | X: (2000,12), y: (2000,) |
| 5 | Train Model | R² = 0.8380 |
| 6 | Verify Artifacts | model.pkl + encoder.pkl |
| 7 | Test Predictions | 3 real-world scenarios |
| 8 | External Modules | Weather/Location/Events/Offers |
| 9 | Full Pipeline | Production → Loss |
| 10 | Final Report | Summary dashboard |
| 11 | Loss Improvement | 38.1% loss reduction |

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.12 | Core language |
| pandas | 2.2.2 | Data handling |
| numpy | 1.26.4 | Numerical ops |
| scikit-learn | 1.4.2 | ML model |
| joblib | 1.4.2 | Model persistence |
| Flask | 3.0.3 | REST API + UI |
| Jupyter | 1.0.0 | Notebook |
| HTML/CSS | — | Dashboard UI |

---

## 🔄 Git Setup

```bash
git init
git add .
git commit -m "initial commit: complete sales demand prediction system"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/sales-demand-system.git
git push -u origin main
```

---

## 👩‍💻 Author

**Karthiga**
Built as an internship-ready, industry-structured ML project demonstrating end-to-end demand prediction, production planning, and loss optimisation for a food service business.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
