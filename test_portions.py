from search import search_food
from portions import scale_nutrition, parse_quantity

# Test portion parsing
print("--- Portion parsing ---")
test_quantities = ["150", "medium", "2 tbsp", "1 bowl", "feuille msemen", "250g", "louche harira"]
for q in test_quantities:
    print(f"  '{q}' → {parse_quantity(q)}g")

# Test full pipeline: search + scale
print("\n--- Full pipeline: harira, 1 louche ---")
results = search_food("harira")
if results:
    harira = results[0]
    scaled = scale_nutrition(harira, "louche harira")
    print(f"  Food: {scaled['food']}")
    print(f"  Quantity: {scaled['quantity_g']}g")
    print(f"  Calories: {scaled['calories']} kcal")
    print(f"  Protein: {scaled['protein_g']}g | Carbs: {scaled['carbs_g']}g | Fat: {scaled['fat_g']}g")

print("\n--- Full pipeline: pizza, 200g ---")
results = search_food("pizza")
if results:
    pizza = results[0]
    scaled = scale_nutrition(pizza, 200)
    print(f"  Food: {scaled['food']}")
    print(f"  Quantity: {scaled['quantity_g']}g")
    print(f"  Calories: {scaled['calories']} kcal")