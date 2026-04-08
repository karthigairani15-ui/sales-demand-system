
# 🍽️ Sales Demand Prediction System

An AI-powered food sales demand prediction system that integrates
weather, location, festivals, events, time slots, and offers
to predict demand and manage production, inventory, waste, and loss.

---

## 🏗️ Project Structure
sales-demand-system/
├── notebook/
│   └── main.ipynb              # Full pipeline notebook
├── src/
│   ├── config/
│   │   └── settings.py         # Central configuration
│   ├── data/
│   │   └── data_generator.py   # Dataset generation
│   ├── features/
│   │   └── feature_engineering.py
│   ├── models/
│   │   ├── train_model.py
│   │   ├── predict.py
│   │   └── model_utils.py
│   ├── modules/
│   │   ├── production.py
│   │   ├── inventory.py
│   │   ├── pos.py
│   │   ├── consumption.py
│   │   ├── waste.py
│   │   └── loss.py
│   └── external/
│       ├── weather.py
│       ├── location.py
│       ├── events.py
│       └── offers.py
├── api/
│   └── app.py                  # Flask REST API
├── data/
│   └── dataset.csv
├── artifacts/
│   ├── model.pkl
│   └── encoder.pkl
├── requirements.txt
├── README.md
└── .gitignore

---

## 🧠 Intelligence Factors

| Factor | Impact |
|--------|--------|
| Weekend | +25% sales boost |
| Festival (Diwali) | +45% boost |
| Rainy Weather | -20% drop |
| Office Lunch | +30% boost |
| Cricket Match | +35% boost |
| Offer/Discount | +15% boost |

---

## ⚙️ Setup Instructions

### 1. Create GitHub Repository
- Go to github.com → New Repository
- Name: `sales-demand-system`
- Click Create

### 2. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/sales-demand-system.git
cd sales-demand-system
```

### 3. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Requirements
```bash
pip install -r requirements.txt
```

### 5. Register Jupyter Kernel
```bash
python3 -m ipykernel install --user \
  --name=sales-demand-venv \
  --display-name "Sales Demand (venv)"
```

### 6. Run Notebook
```bash
cd notebook
jupyter notebook main.ipynb
```

### 7. Run Flask API
```bash
python api/app.py
```

---

## 🚀 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API info |
| GET | `/health` | Health check |
| GET | `/summary` | Factor multipliers |
| POST | `/predict` | Predict sales |
| POST | `/full-pipeline` | Full pipeline |

---

## 📬 Sample API Request
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

---

## 📬 Sample API Response
```json
{
  "status": "success",
  "predictions": [
    {"item": "Biryani",  "predicted_sales": 112},
    {"item": "Meals",    "predicted_sales": 134},
    {"item": "Parotta",  "predicted_sales": 118},
    {"item": "Noodles",  "predicted_sales": 95},
    {"item": "Dosa",     "predicted_sales": 108}
  ]
}
```

---

## 🔄 Git Commands
```bash
git init
git add .
git commit -m "initial commit"
git branch -M main
git remote add origin <repo_url>
git push -u origin main
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.12 | Core language |
| pandas | Data handling |
| scikit-learn | ML model |
| Flask | REST API |
| Jupyter | Notebook |
| joblib | Model saving |

---

## 👩‍💻 Author
Built with ❤️ as an internship-ready ML project.
Save → Ctrl + S

