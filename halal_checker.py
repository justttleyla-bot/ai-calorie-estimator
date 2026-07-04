HARAM_INGREDIENTS = {
    "lard": "❌ Contains lard (pork fat)",
    "pork": "❌ Contains pork",
    "pig": "❌ Contains pig-derived ingredient",
    "bacon": "❌ Contains bacon",
    "ham": "❌ Contains ham",
    "gelatin porcine": "❌ Contains porcine gelatin (pork-derived)",
}

ALCOHOL_INGREDIENTS = {
    "alcohol": "❌ Contains alcohol",
    "ethanol": "❌ Contains alcohol (ethanol)",
    "wine": "❌ Contains wine",
    "beer": "❌ Contains beer",
    "liqueur": "❌ Contains liqueur",
}

DOUBTFUL_INGREDIENTS = {
    "gelatin": "⚠️ Gelatin detected — source unknown (may be pork or non-halal animal)",
    "carmine": "⚠️ Carmine/E120 — insect-derived colorant (scholars disagree on permissibility)",
    "cochineal": "⚠️ Cochineal — insect-derived colorant (scholars disagree on permissibility)",
    "e120": "⚠️ E120 — Carmine, insect-derived (scholars disagree on permissibility)",
    "e322": "⚠️ E322 — Soy lecithin (extraction process debated by some scholars)",
    "e441": "⚠️ E441 — Gelatin, animal origin unknown",
    "e542": "⚠️ E542 — Bone phosphate, animal origin",
    "e904": "⚠️ E904 — Shellac, insect-derived (scholars disagree on permissibility)",
    "e471": "⚠️ E471 — Mono/diglycerides, may be animal-derived",
    "e472": "⚠️ E472 — Fatty acid esters, may be animal-derived",
    "e473": "⚠️ E473 — Sucrose esters, may be animal-derived",
    "e474": "⚠️ E474 — Sucroglycerides, may be animal-derived",
    "e475": "⚠️ E475 — Polyglycerol esters, may be animal-derived",
    "e422": "⚠️ E422 — Glycerol, may be animal-derived",
}

DISCLAIMER = (
    "⚠️ This checker is a helper tool only, not a fatwa or religious ruling. "
    "Scholarly opinions differ on some ingredients. "
    "Always verify with a certified halal authority for certainty."
)

def check_halal(ingredients_text, ingredients_tags=None):
    """
    Checks a product's ingredients for haram or doubtful items.
    Uses both raw ingredients text AND standardized tags for accuracy.
    Tags are always in English regardless of product country of origin.
    """
    flags = []
    text_lower = ingredients_text.lower() if ingredients_text else ""

    # Check confirmed haram ingredients in text
    for keyword, message in HARAM_INGREDIENTS.items():
        if keyword in text_lower:
            flags.append(message)

    # Check alcohol in text
    for keyword, message in ALCOHOL_INGREDIENTS.items():
        if keyword in text_lower:
            if keyword == "alcohol" and "sugar alcohol" in text_lower:
                flags.append("⚠️ Contains sugar alcohol (halal) — verify no other alcohol present")
            else:
                flags.append(message)

    # Check doubtful ingredients in text
    for keyword, message in DOUBTFUL_INGREDIENTS.items():
        if keyword in text_lower:
            if keyword == "gelatin" and any("porcine" in f for f in flags):
                continue
            flags.append(message)

    # Check standardized tags (always English — more reliable than text)
    if ingredients_tags:
        tags_lower = [tag.lower() for tag in ingredients_tags]

        # Confirmed haram tags
        if "en:pork" in tags_lower and not any("pork" in f for f in flags):
            flags.append("❌ Contains pork (confirmed by database tag)")
        if "en:alcohol" in tags_lower and not any("alcohol" in f for f in flags):
            flags.append("❌ Contains alcohol (confirmed by database tag)")

        # Doubtful tags
        if "en:gelatin" in tags_lower and not any("gelatin" in f.lower() for f in flags):
            flags.append("⚠️ Gelatin detected — source unknown (may be pork or non-halal animal)")
        if "en:e120" in tags_lower and not any("E120" in f for f in flags):
            flags.append("⚠️ E120 — Carmine, insect-derived (scholars disagree on permissibility)")
        if "en:e322" in tags_lower and not any("E322" in f for f in flags):
            flags.append("⚠️ E322 — Soy lecithin (extraction process debated by some scholars)")
        if "en:e322i" in tags_lower and not any("E322" in f for f in flags):
            flags.append("⚠️ E322i — Soy lecithin variant (extraction process debated by some scholars)")
        if "en:e471" in tags_lower and not any("E471" in f for f in flags):
            flags.append("⚠️ E471 — Mono/diglycerides, may be animal-derived")
        if "en:e472" in tags_lower and not any("E472" in f for f in flags):
            flags.append("⚠️ E472 — Fatty acid esters, may be animal-derived")
        if "en:e904" in tags_lower and not any("E904" in f for f in flags):
            flags.append("⚠️ E904 — Shellac, insect-derived (scholars disagree on permissibility)")
        if "en:e441" in tags_lower and not any("E441" in f for f in flags):
            flags.append("⚠️ E441 — Gelatin, animal origin unknown")
        if "en:emulsifier" in tags_lower and not any("emulsifier" in f.lower() for f in flags):
            flags.append("⚠️ Contains emulsifier(s) — source not specified, verify origin")

    # Determine overall status
    haram_flags = [f for f in flags if f.startswith("❌")]
    doubtful_flags = [f for f in flags if f.startswith("⚠️")]

    if haram_flags:
        status = "haram"
        message = "❌ This product contains haram ingredients."
    elif doubtful_flags:
        status = "doubtful"
        message = "⚠️ This product contains doubtful ingredients. Verify before consuming."
    else:
        status = "halal"
        message = "✅ No haram or doubtful ingredients detected."

    return {
        "status": status,
        "flags": flags,
        "message": message,
        "disclaimer": DISCLAIMER
    }