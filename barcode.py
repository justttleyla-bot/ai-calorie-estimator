import requests
from validator import validate_nutrition

def lookup_barcode(barcode):
    """
    Looks up a product by barcode using the Open Food Facts API.
    Returns clean nutrition data or an error message.
    Works with any barcode worldwide — including Moroccan products.
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"

    try:
        headers = {
            "User-Agent": "AI-Calorie-Estimator/1.0 (learning project; contact@example.com)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()

        # Check if product was found
        if data.get("status") != 1:
            return {
                "found": False,
                "barcode": barcode,
                "message": "Product not found. Please scan the nutrition label to add it."
            }

        product = data["product"]
        nutriments = product.get("nutriments", {})

        # Extract nutrition per 100g
        raw = {
            "food": product.get("product_name", "Unknown product"),
            "calories": nutriments.get("energy-kcal_100g"),
            "protein_g": nutriments.get("proteins_100g"),
            "carbs_g": nutriments.get("carbohydrates_100g"),
            "fat_g": nutriments.get("fat_100g"),
            "source": "barcode"
        }

        # Validate before returning
        is_valid, cleaned, errors = validate_nutrition(raw)

        if not is_valid:
            return {
                "found": True,
                "barcode": barcode,
                "valid": False,
                "errors": errors,
                "message": "Product found but nutrition data is incomplete."
            }

        cleaned["found"] = True
        cleaned["barcode"] = barcode
        cleaned["valid"] = True
        return cleaned

    except requests.exceptions.Timeout:
        return {"found": False, "error": "Request timed out. Check your connection."}
    except Exception as e:
        return {"found": False, "error": str(e)}