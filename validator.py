def validate_nutrition(data):
    """
    Validates a nutrition result before saving to the database.
    Returns (is_valid, cleaned_data, errors) tuple.
    Works for any input method: ai_text, standard_geometric, barcode, photo.
    """
    errors = []
    cleaned = {}

    # Check required fields exist
    required_fields = ["food", "calories", "protein_g", "carbs_g", "fat_g"]
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing field: {field}")

    if errors:
        return False, None, errors

    # Validate food name
    cleaned["food"] = str(data["food"]).strip()
    if not cleaned["food"]:
        errors.append("Food name cannot be empty")

    # Validate numeric fields
    numeric_fields = ["calories", "protein_g", "carbs_g", "fat_g"]
    for field in numeric_fields:
        try:
            value = float(data[field])
            if value < 0:
                errors.append(f"{field} cannot be negative (got {value})")
            elif field == "calories" and value > 9000:
                errors.append(f"Calories value seems unrealistic: {value}")
            else:
                cleaned[field] = round(value, 1)
        except (TypeError, ValueError):
            errors.append(f"{field} must be a number (got {data[field]})")

    # Copy optional fields if present
    cleaned["source"] = data.get("source", "unknown")
    cleaned["portion_description"] = data.get("portion_description", "")
    cleaned["mass_g"] = data.get("mass_g", None)

    if errors:
        return False, None, errors

    return True, cleaned, []