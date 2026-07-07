import os
import json
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()
client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

def get_nutrition_per_100g(food_name):
    """
    Asks the AI for nutrition values per 100g of a given food.
    Returns a dictionary with calories, protein, carbs, fat.
    Works in any language — just pass the food name as-is.
    """
    try:
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[
                {"role": "system", "content": (
                    "You are a nutrition database assistant. "
                    "Given a food name in any language, return ONLY valid JSON "
                    "with nutrition values PER 100G only — not for any described portion. "
                    "Return ALL values per 100g. "
                    "Use this exact format: "
                    '{"calories": number, "protein_g": number, "carbs_g": number, "fat_g": number} '
                    "No explanations, no extra text, just the JSON."
                )},
                {"role": "user", "content": food_name}
            ]
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        return json.loads(raw)
    except Exception as e:
        return {"error": str(e)}


def estimate_nutrition_from_mass(food_name, mass_g):
    """
    Given a food name and its mass in grams,
    returns the full nutrition for that exact amount.
    """
    per_100g = get_nutrition_per_100g(food_name)

    if "error" in per_100g:
        return per_100g

    ratio = mass_g / 100

    return {
        "food": food_name,
        "mass_g": round(mass_g, 2),
        "calories": round(per_100g["calories"] * ratio, 1),
        "protein_g": round(per_100g["protein_g"] * ratio, 1),
        "carbs_g": round(per_100g["carbs_g"] * ratio, 1),
        "fat_g": round(per_100g["fat_g"] * ratio, 1),
        "source": "standard_geometric"
    }