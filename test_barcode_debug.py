import requests

headers = {
    "User-Agent": "AI-Calorie-Estimator/1.0 (learning project; contact@example.com)"
}

response = requests.get(
    "https://world.openfoodfacts.org/api/v0/product/3017620422003.json",
    headers=headers
)

data = response.json()
product = data["product"]

print("Ingredients text:")
print(product.get("ingredients_text", "NOT FOUND"))
print("\nIngredients tags:")
print(product.get("ingredients_tags", []))