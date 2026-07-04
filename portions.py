# Standard portion sizes for common serving descriptions
# Values are in grams
PORTION_PRESETS = {
    # General
    "small": 80,
    "medium": 150,
    "large": 250,
    "extra large": 350,

    # Spoons
    "teaspoon": 5,
    "tsp": 5,
    "tablespoon": 15,
    "tbsp": 15,
    "cuillère à café": 5,
    "cuillère à soupe": 15,

    # Cups and bowls
    "cup": 240,
    "half cup": 120,
    "bowl": 300,
    "small bowl": 200,
    "large bowl": 400,
    "bol": 300,
    "petit bol": 200,
    "grand bol": 400,

    # Moroccan/North African specific
    "tagine portion": 350,
    "assiette": 300,
    "verre": 200,
    "pain rond entier": 200,
    "demi pain": 100,
    "feuille msemen": 90,
    "portion couscous": 250,
    "louche harira": 250,

    # Pieces
    "piece": 100,
    "slice": 60,
    "tranche": 60,
}

def parse_quantity(quantity_input):
    """
    Converts a quantity description into grams.
    Accepts:
    - A number (assumed to be grams): 150 → 150g
    - A string preset: "medium" → 150g
    - A string with unit: "2 tbsp" → 30g
    Returns quantity in grams as a float.
    """
    if isinstance(quantity_input, (int, float)):
        return float(quantity_input)

    text = str(quantity_input).strip().lower()

    # Try direct preset match first
    if text in PORTION_PRESETS:
        return float(PORTION_PRESETS[text])

    # Try "number + unit" format (e.g. "2 tbsp", "3 pieces")
    parts = text.split()
    if len(parts) == 2:
        try:
            number = float(parts[0])
            unit = parts[1]
            if unit in PORTION_PRESETS:
                return number * PORTION_PRESETS[unit]
        except ValueError:
            pass

    # Try to extract a plain number
    try:
        return float(text.replace("g", "").replace("gr", "").strip())
    except ValueError:
        pass

    # Default fallback
    print(f"⚠️ Could not parse quantity '{quantity_input}', defaulting to 100g")
    return 100.0


def scale_nutrition(nutrition_per_100g, quantity_input):
    """
    Scales nutrition values from per-100g to the actual quantity eaten.

    nutrition_per_100g: dict with calories, protein_g, carbs_g, fat_g
    quantity_input: grams as number, or description like "medium", "2 tbsp"

    Returns scaled nutrition dict with quantity_g included.
    """
    quantity_g = parse_quantity(quantity_input)
    ratio = quantity_g / 100

    return {
        "food": nutrition_per_100g.get("food", ""),
        "quantity_g": round(quantity_g, 1),
        "calories": round(nutrition_per_100g["calories"] * ratio, 1),
        "protein_g": round(nutrition_per_100g["protein_g"] * ratio, 1),
        "carbs_g": round(nutrition_per_100g["carbs_g"] * ratio, 1),
        "fat_g": round(nutrition_per_100g["fat_g"] * ratio, 1),
        "source": nutrition_per_100g.get("source", ""),
        "input_method": nutrition_per_100g.get("input_method", ""),
        "verified": nutrition_per_100g.get("verified", False)
    }