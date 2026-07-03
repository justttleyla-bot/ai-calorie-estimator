from photo_estimation import estimate_from_photo

result = estimate_from_photo("test_food.jpg")

if "error" in result:
    print(f"Error: {result['error']}")
else:
    print(f"Food identified: {result['food']}")
    print(f"Portion: {result['portion_description']}")
    print(f"Calories: {result['calories']} kcal")
    print(f"Protein: {result['protein_g']}g | Carbs: {result['carbs_g']}g | Fat: {result['fat_g']}g")
    print(f"Source: {result['source']}")