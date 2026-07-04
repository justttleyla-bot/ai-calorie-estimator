from moroccan_foods import search_moroccan_food
from ai_text_estimation import estimate_from_text
from validator import validate_nutrition

def search_food(query):
    """
    Unified food search with fallback chain:
    1. Moroccan database (fastest, verified, local foods)
    2. AI text estimation (fallback for everything else)
    
    Returns a list of results, always at least one.
    """
    results = []

    # Step 1: Check Moroccan database first
    moroccan_results = search_moroccan_food(query)
    if moroccan_results:
        for item in moroccan_results:
            item["input_method"] = "database"
            results.append(item)
        return results

    # Step 2: Fall back to AI text estimation
    ai_result = estimate_from_text(query)
    if "error" not in ai_result:
        is_valid, cleaned, errors = validate_nutrition(ai_result)
        if is_valid:
            cleaned["input_method"] = "ai_text"
            cleaned["verified"] = False
            results.append(cleaned)
            return results

    # Step 3: If everything fails, return a helpful message
    return [{
        "food": query,
        "error": "Could not estimate nutrition for this food. Try describing it differently.",
        "input_method": "failed"
    }]