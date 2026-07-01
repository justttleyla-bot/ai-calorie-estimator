from ai_text_estimation import estimate_from_text

tests = [
    "2 oeufs brouillés avec du beurre",
    "a bowl of harira",
    "تفاحة متوسطة",
    "3 tbsp of peanut butter"
]

for food in tests:
    result = estimate_from_text(food)
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"\nInput: {food}")
        print(f"Food: {result['food']}")
        print(f"Portion: {result['portion_description']}")
        print(f"Calories: {result['calories']} kcal")
        print(f"Protein: {result['protein_g']}g | Carbs: {result['carbs_g']}g | Fat: {result['fat_g']}g")
        print(f"Source: {result['source']}")