from geometry import estimate_cylinder, diameter_to_radius, DENSITY_TABLE
from nutrition import estimate_nutrition_from_mass

radius = diameter_to_radius(15)
mass = estimate_cylinder(radius, 3, DENSITY_TABLE["khobz"])

result = estimate_nutrition_from_mass("khobz", mass)

print(f"Food: {result['food']}")
print(f"Mass: {result['mass_g']}g")
print(f"Calories: {result['calories']} kcal")
print(f"Protein: {result['protein_g']}g")
print(f"Carbs: {result['carbs_g']}g")
print(f"Fat: {result['fat_g']}g")
print(f"Source: {result['source']}")