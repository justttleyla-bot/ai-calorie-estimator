from validator import validate_nutrition

test_cases = [
    # Valid result from AI text estimation
    {
        "food": "harira",
        "calories": 250,
        "protein_g": 12,
        "carbs_g": 35,
        "fat_g": 7,
        "source": "ai_text",
        "portion_description": "un bol de harira"
    },
    # Missing calories field
    {
        "food": "banana",
        "protein_g": 1.3,
        "carbs_g": 27,
        "fat_g": 0.3
    },
    # Negative protein value
    {
        "food": "apple",
        "calories": 95,
        "protein_g": -5,
        "carbs_g": 25,
        "fat_g": 0.3
    },
    # Unrealistic calorie value
    {
        "food": "lettuce leaf",
        "calories": 15000,
        "protein_g": 0.5,
        "carbs_g": 1,
        "fat_g": 0.1
    },
    # Non-numeric value
    {
        "food": "egg",
        "calories": "unknown",
        "protein_g": 6,
        "carbs_g": 0.6,
        "fat_g": 5
    }
]

for i, test in enumerate(test_cases):
    is_valid, cleaned, errors = validate_nutrition(test)
    print(f"\n--- Test {i+1}: {test.get('food', '?')} ---")
    if is_valid:
        print(f"✓ Valid: {cleaned['calories']} kcal, {cleaned['protein_g']}g protein")
    else:
        print(f"✗ Invalid: {errors}")