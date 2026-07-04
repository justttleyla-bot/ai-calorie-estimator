import sqlite3
from tracking import log_entry, get_daily_summary, add_favourite, get_favourites
from search import search_food
from portions import scale_nutrition

# Create a test user
conn = sqlite3.connect("calorie_app.db")
cursor = conn.cursor()
cursor.execute("""
    INSERT OR IGNORE INTO users (username, email, daily_calorie_goal)
    VALUES ('leyla', 'leyla@test.com', 1800)
""")
conn.commit()
cursor.execute("SELECT id FROM users WHERE username = 'leyla'")
user_id = cursor.fetchone()[0]
conn.close()

print(f"Test user ID: {user_id}")

# Log breakfast
harira = search_food("harira")[0]
scaled = scale_nutrition(harira, "louche harira")
log_entry(user_id, scaled["food"], scaled["calories"],
          scaled["protein_g"], scaled["carbs_g"], scaled["fat_g"],
          scaled["quantity_g"], "breakfast", "database", "moroccan_database")
print("✅ Logged harira for breakfast")

# Log lunch
msemen = search_food("msemen")[0]
scaled2 = scale_nutrition(msemen, "feuille msemen")
log_entry(user_id, scaled2["food"], scaled2["calories"],
          scaled2["protein_g"], scaled2["carbs_g"], scaled2["fat_g"],
          scaled2["quantity_g"], "lunch", "database", "moroccan_database")
print("✅ Logged msemen for lunch")

# Add harira to favourites
add_favourite(user_id, "Harira (soupe)")
print("✅ Added harira to favourites")

# Get daily summary
summary = get_daily_summary(user_id)
print(f"\n--- Daily Summary ---")
print(f"Goal: {summary['daily_goal']} kcal")
print(f"Consumed: {summary['totals']['calories']} kcal")
print(f"Remaining: {summary['remaining_calories']} kcal")
print(f"Progress: {summary['progress_percent']}%")
print(f"\nProtein: {summary['totals']['protein_g']}g")
print(f"Carbs: {summary['totals']['carbs_g']}g")
print(f"Fat: {summary['totals']['fat_g']}g")

print(f"\n--- Meals ---")
for meal_type, entries in summary['meals'].items():
    if entries:
        print(f"\n{meal_type.capitalize()}:")
        for e in entries:
            print(f"  {e['food']} ({e['quantity_g']}g) — {e['calories']} kcal")

print(f"\n--- Favourites ---")
favs = get_favourites(user_id)
for f in favs:
    print(f"  ⭐ {f['food']} — {f['calories']} kcal/100g")