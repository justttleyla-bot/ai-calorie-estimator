import sqlite3

MOROCCAN_FOODS = [
    # (name, calories_per_100g, protein_g, carbs_g, fat_g, source, verified)
    ("Khobz (pain marocain rond)", 265, 8.5, 52.0, 2.5, "moroccan_database", 1),
    ("Msemen", 320, 7.8, 48.0, 11.5, "moroccan_database", 1),
    ("Harcha", 380, 7.2, 50.0, 16.0, "moroccan_database", 1),
    ("Batbout", 255, 8.0, 50.0, 2.0, "moroccan_database", 1),
    ("Harira (soupe)", 75, 4.5, 10.0, 2.0, "moroccan_database", 1),
    ("Bissara", 120, 7.5, 18.0, 2.5, "moroccan_database", 1),
    ("Couscous (cuit)", 112, 3.8, 23.0, 0.6, "moroccan_database", 1),
    ("Tagine poulet citron", 165, 18.0, 8.0, 7.5, "moroccan_database", 1),
    ("Kefta (boulette)", 220, 17.0, 3.0, 15.5, "moroccan_database", 1),
    ("Pastilla poulet", 280, 14.0, 28.0, 12.0, "moroccan_database", 1),
    ("Zaalouk (caviar d'aubergine)", 85, 2.0, 8.0, 5.5, "moroccan_database", 1),
    ("Taktouka (salade tomate poivron)", 65, 1.5, 7.0, 3.5, "moroccan_database", 1),
    ("Chebakia", 420, 6.5, 58.0, 19.0, "moroccan_database", 1),
    ("Briwat au fromage", 290, 9.0, 28.0, 16.0, "moroccan_database", 1),
    ("Sellou (sfouf)", 480, 12.0, 55.0, 24.0, "moroccan_database", 1),
    ("Argan oil", 884, 0.0, 0.0, 100.0, "moroccan_database", 1),
    ("Amlou (pâte amande argan)", 580, 14.0, 18.0, 52.0, "moroccan_database", 1),
    ("Belboula (orge concassé cuit)", 95, 3.5, 19.5, 0.8, "moroccan_database", 1),
    ("Rfissa (msemen au poulet)", 185, 14.0, 22.0, 5.0, "moroccan_database", 1),
    ("Tanjia marrakchia", 245, 28.0, 2.0, 14.0, "moroccan_database", 1),
    ("Lben (lait fermenté)", 40, 3.5, 4.5, 1.0, "moroccan_database", 1),
    ("Arissa (harissa marocaine)", 45, 1.5, 6.0, 2.0, "moroccan_database", 1),
    ("Smen (beurre fermenté)", 720, 0.5, 0.0, 80.0, "moroccan_database", 1),
    ("Chermoula", 95, 1.5, 4.0, 8.0, "moroccan_database", 1),
    ("Mrouzia (tagine agneau miel)", 310, 22.0, 18.0, 16.0, "moroccan_database", 1),
]

def populate_moroccan_database():
    """
    Populates the foods table with verified Moroccan food data.
    Uses INSERT OR IGNORE to avoid duplicates on repeated runs.
    """
    conn = sqlite3.connect("calorie_app.db")
    cursor = conn.cursor()

    inserted = 0
    skipped = 0

    for food in MOROCCAN_FOODS:
        name, calories, protein, carbs, fat, source, verified = food

        cursor.execute("""
            INSERT OR IGNORE INTO foods (name, calories, protein_g, carbs_g, fat_g, source, verified)
            SELECT ?, ?, ?, ?, ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM foods WHERE name = ?
            )
        """, (name, calories, protein, carbs, fat, source, verified, name))

        if cursor.rowcount > 0:
            inserted += 1
        else:
            skipped += 1

    conn.commit()
    conn.close()

    print(f"✅ Moroccan database populated: {inserted} foods added, {skipped} already existed.")

def search_moroccan_food(query):
    """
    Searches the Moroccan food database for a matching food.
    Case-insensitive partial match — so "harira" finds "Harira (soupe)".
    Returns a list of matches with full nutrition data.
    """
    conn = sqlite3.connect("calorie_app.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, calories, protein_g, carbs_g, fat_g, source, verified
        FROM foods
        WHERE LOWER(name) LIKE LOWER(?)
        AND source = 'moroccan_database'
    """, (f"%{query}%",))

    results = []
    for row in cursor.fetchall():
        results.append({
            "food": row[0],
            "calories": row[1],
            "protein_g": row[2],
            "carbs_g": row[3],
            "fat_g": row[4],
            "source": row[5],
            "verified": bool(row[6])
        })

    conn.close()
    return results

if __name__ == "__main__":
    populate_moroccan_database()