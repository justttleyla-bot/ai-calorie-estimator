from moroccan_foods import search_moroccan_food

queries = ["harira", "msemen", "couscous", "pizza"]

for query in queries:
    results = search_moroccan_food(query)
    print(f"\n--- Search: '{query}' ---")
    if results:
        for r in results:
            verified = "✅ Verified" if r["verified"] else "⚠️ Unverified"
            print(f"  {r['food']} — {r['calories']} kcal/100g | {verified}")
    else:
        print("  Not found in Moroccan database.")