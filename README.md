# Velora — AI-Powered Nutrition Intelligence

A full-stack nutrition tracking app built with Python, Mistral AI, and Streamlit.
Four input methods · Moroccan food database · Halal scanner · Multilingual (EN/FR/AR)

---

## What it does

Velora lets you log meals and track your daily nutrition using four input methods:

- **Text / AI** — describe any food in any language, AI estimates calories and macros per 100g
- **Photo** — upload a photo of your meal, vision AI identifies the food and estimates nutrition
- **Barcode** — enter a product barcode, fetches real label data from Open Food Facts (3M+ products)
- **Geometric** — measure food dimensions, app calculates mass using geometry and density tables

## Key features

- Moroccan food database with 25+ verified local dishes (harira, msemen, couscous, tagine...)
- Halal scanner — checks barcode products for haram and doubtful ingredients automatically
- Multilingual — works in English, French, and Arabic natively
- Daily log with calorie goal progress ring and macro donut chart
- Meal history with trend charts (7 days free, full history Premium)
- AI nutrition advice based on recent eating patterns (Premium)
- Weight tracker with history chart
- Favourites for one-tap logging of frequent foods
- Secure email + password authentication (SHA-256 hashing)
- Premium tier with extended limits

---

## Tech stack

- Language: Python 3.14
- AI / LLM: Mistral AI API (mistral-small-latest + pixtral-12b for vision)
- Frontend: Streamlit
- Database: SQLite
- Food data: Open Food Facts API (barcode lookup)
- Charts: Plotly
- Version control: Git / GitHub

---

## Project structure

- app.py — Main Streamlit application
- database.py — Database schema and initialization
- search.py — Unified food search with fallback chain
- ai_text_estimation.py — Text to nutrition via Mistral AI
- photo_estimation.py — Image to nutrition via Mistral vision
- barcode.py — Barcode to nutrition via Open Food Facts
- halal_checker.py — Ingredient halal/haram analysis
- geometry.py — Geometric mass estimation (cylinder, cuboid, sphere, ellipsoid)
- nutrition.py — AI nutrition lookup per 100g
- moroccan_foods.py — Moroccan food database
- portions.py — Portion size parsing and nutrition scaling
- tracking.py — Meal logging, daily summary, history
- validator.py — Nutrition data validation

---

## Getting started

Requirements: Python 3.10+ and a Mistral AI API key (free tier available at console.mistral.ai)

```bash
git clone https://github.com/justttleyla-bot/ai-calorie-estimator.git
cd ai-calorie-estimator
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a .env file:
MISTRAL_API_KEY=your_mistral_api_key_here

Run:
```bash
python database.py
python moroccan_foods.py
streamlit run app.py
```

---

## How the search fallback chain works

1. Check Moroccan database first (fastest, verified local foods)
2. Fall back to Mistral AI text estimation (handles any food in any language)

Users never see a "not found" error — the app always returns a result.

---

## Halal scanner classification

- Halal — no flagged ingredients detected
- Doubtful — ingredients with scholarly disagreement (E322, gelatin of unknown origin, insect-derived colorants)
- Haram — confirmed forbidden ingredients (pork, alcohol, porcine gelatin)

Includes a disclaimer that this is a helper tool, not a religious ruling.

---

## Free vs Premium

| Feature | Free | Premium |
|---------|------|---------|
| Text / AI estimation | Unlimited | Unlimited |
| Barcode scanning | Unlimited | Unlimited |
| Moroccan food database | Unlimited | Unlimited |
| Halal scanner | Unlimited | Unlimited |
| Daily log | Unlimited | Unlimited |
| Favourites | Up to 10 | Unlimited |
| Meal history | 7 days | Full history |
| Photo estimation | 3 per day | Unlimited |
| Trend charts | 7 days | Full |
| AI nutrition advice | No | Yes |

---

## Roadmap

- Deploy to Render (live public URL)
- Payment integration for Premium tier
- Ramadan mode (suhoor/iftar tracking)
- Cycle-synced nutrition recommendations
- Micronutrient breakdown
- PDF/CSV export
- Mobile-optimized UI

---

## Built by

Leïla — first-year IDSI engineering student at FST Mohammedia, Hassan II University.
Built as a summer portfolio project to learn Python, AI APIs, and full-stack development from scratch.

GitHub: https://github.com/justttleyla-bot