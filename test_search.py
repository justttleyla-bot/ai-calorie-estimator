from search import search_food

queries = ["harira", "msemen", "pizza", "grilled salmon", "تفاحة"]

for query in queries:
    print(f"\n--- Search: '{query}' ---")
    results = search_food(query)
    for r in results:
        if "error" in r:
            print(f"  ❌ {r['error']}")
        else:
            verified = "✅ Verified" if r.get("verified") else "≈ AI estimate"
            print(f"  {r['food']} — {r['calories']} kcal/100g [{verified}]")
            print(f"  Source: {r['input_method']}")