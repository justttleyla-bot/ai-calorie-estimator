from barcode import lookup_barcode

# Test 1: Nutella (should be found)
print("--- Test 1: Nutella ---")
result = lookup_barcode("3017620422003")
if result.get("found") and result.get("valid"):
    print(f"Product: {result['food']}")
    print(f"Calories: {result['calories']} kcal per 100g")
    print(f"Protein: {result['protein_g']}g | Carbs: {result['carbs_g']}g | Fat: {result['fat_g']}g")
    print(f"Source: {result['source']}")
else:
    print(result.get("message") or result.get("error"))

# Test 2: Unknown barcode (should NOT be found)
print("\n--- Test 2: Unknown barcode ---")
result = lookup_barcode("0000000000000")
print(result.get("message") or result.get("error"))