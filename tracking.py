import sqlite3
from datetime import date

DB_PATH = "calorie_app.db"

def log_entry(user_id, food_name, calories, protein_g, carbs_g, fat_g,
              quantity_g, meal_type, input_method, source):
    """
    Saves a food entry to the database.
    First saves the food to foods table if not already there,
    then creates the entry linking user to food.
    meal_type: "breakfast", "lunch", "dinner", or "snack"
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = date.today().isoformat()

    # Insert food if it doesn't exist yet
    cursor.execute("""
        INSERT OR IGNORE INTO foods (name, calories, protein_g, carbs_g, fat_g, source, verified)
        SELECT ?, ?, ?, ?, ?, ?, 0
        WHERE NOT EXISTS (SELECT 1 FROM foods WHERE name = ?)
    """, (food_name, calories, protein_g, carbs_g, fat_g, source, food_name))

    # Get the food's id
    cursor.execute("SELECT id FROM foods WHERE name = ?", (food_name,))
    food_id = cursor.fetchone()[0]

    # Log the entry
    cursor.execute("""
        INSERT INTO entries (user_id, food_id, quantity_g, meal_type, input_method, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, food_id, quantity_g, meal_type, input_method, today))

    conn.commit()
    conn.close()
    return True


def get_daily_summary(user_id, target_date=None):
    """
    Returns today's nutrition summary for a user.
    Includes total calories, macros, and breakdown by meal type.
    """
    if target_date is None:
        target_date = date.today().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get user's daily goal
    cursor.execute("SELECT daily_calorie_goal FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    daily_goal = row[0] if row else 2000

    # Get all entries for today
    cursor.execute("""
        SELECT foods.name, entries.quantity_g, entries.meal_type,
               foods.calories, foods.protein_g, foods.carbs_g, foods.fat_g,
               entries.id
        FROM entries
        JOIN foods ON entries.food_id = foods.id
        WHERE entries.user_id = ? AND entries.date = ?
        ORDER BY entries.meal_type
    """, (user_id, target_date))

    rows = cursor.fetchall()
    conn.close()

    # Build summary
    meals = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
    totals = {"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0}

    for row in rows:
        name, qty, meal_type, cal, prot, carb, fat, entry_id = row
        ratio = qty / 100
        entry = {
            "food": name,
            "quantity_g": qty,
            "calories": round(cal * ratio, 1),
            "protein_g": round(prot * ratio, 1),
            "carbs_g": round(carb * ratio, 1),
            "fat_g": round(fat * ratio, 1),
            "entry_id": entry_id,
        }
        if meal_type in meals:
            meals[meal_type].append(entry)
        totals["calories"] += entry["calories"]
        totals["protein_g"] += entry["protein_g"]
        totals["carbs_g"] += entry["carbs_g"]
        totals["fat_g"] += entry["fat_g"]

    # Round totals
    for key in totals:
        totals[key] = round(totals[key], 1)

    remaining = round(daily_goal - totals["calories"], 1)
    progress_pct = round((totals["calories"] / daily_goal) * 100, 1)

    return {
        "date": target_date,
        "daily_goal": daily_goal,
        "totals": totals,
        "remaining_calories": remaining,
        "progress_percent": progress_pct,
        "meals": meals
    }


def add_favourite(user_id, food_name):
    """Saves a food to user's favourites."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    today = date.today().isoformat()

    cursor.execute("SELECT id FROM foods WHERE name = ?", (food_name,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    food_id = row[0]

    # Avoid duplicates
    cursor.execute("""
        INSERT OR IGNORE INTO favourites (user_id, food_id, added_date)
        SELECT ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM favourites WHERE user_id = ? AND food_id = ?
        )
    """, (user_id, food_id, today, user_id, food_id))

    conn.commit()
    conn.close()
    return True


def get_favourites(user_id):
    """Returns a user's saved favourite foods with nutrition data."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT foods.name, foods.calories, foods.protein_g,
               foods.carbs_g, foods.fat_g, foods.source
        FROM favourites
        JOIN foods ON favourites.food_id = foods.id
        WHERE favourites.user_id = ?
        ORDER BY favourites.added_date DESC
    """, (user_id,))

    results = []
    for row in cursor.fetchall():
        results.append({
            "food": row[0],
            "calories": row[1],
            "protein_g": row[2],
            "carbs_g": row[3],
            "fat_g": row[4],
            "source": row[5]
        })

    conn.close()
    return results


def delete_entry(entry_id, user_id):
    """
    Deletes a logged food entry.
    user_id check prevents deleting other users' entries.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM entries WHERE id = ? AND user_id = ?",
        (entry_id, user_id)
    )
    conn.commit()
    conn.close()


def get_history(user_id, days=30):
    """
    Returns meal entries grouped by date for the past N days.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT entries.date,
               foods.name, entries.quantity_g, entries.meal_type,
               foods.calories, foods.protein_g, foods.carbs_g, foods.fat_g,
               entries.id
        FROM entries
        JOIN foods ON entries.food_id = foods.id
        WHERE entries.user_id = ?
        ORDER BY entries.date DESC, entries.meal_type
        LIMIT 500
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()

    history = {}
    for row in rows:
        date_str, name, qty, meal_type, cal, prot, carb, fat, entry_id = row
        ratio = qty / 100
        if date_str not in history:
            history[date_str] = {
                "date": date_str,
                "totals": {"calories":0,"protein_g":0,"carbs_g":0,"fat_g":0},
                "entries": []
            }
        entry = {
            "food": name, "quantity_g": qty, "meal_type": meal_type,
            "calories": round(cal*ratio,1), "protein_g": round(prot*ratio,1),
            "carbs_g": round(carb*ratio,1), "fat_g": round(fat*ratio,1),
            "entry_id": entry_id
        }
        history[date_str]["entries"].append(entry)
        history[date_str]["totals"]["calories"] += entry["calories"]
        history[date_str]["totals"]["protein_g"] += entry["protein_g"]
        history[date_str]["totals"]["carbs_g"] += entry["carbs_g"]
        history[date_str]["totals"]["fat_g"] += entry["fat_g"]

    for d in history:
        for k in history[d]["totals"]:
            history[d]["totals"][k] = round(history[d]["totals"][k], 1)

    return dict(sorted(history.items(), reverse=True))