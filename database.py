import sqlite3

def init_db():
    conn = sqlite3.connect("calorie_app.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT,
        daily_calorie_goal REAL DEFAULT 2000,
        goal TEXT DEFAULT 'general',
        is_muslim INTEGER DEFAULT 0,
        age INTEGER,
        weight_kg REAL,
        height_cm REAL,
        language TEXT DEFAULT 'en'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS foods (
        id INTEGER PRIMARY KEY,
        name TEXT,
        calories REAL,
        protein_g REAL,
        carbs_g REAL,
        fat_g REAL,
        source TEXT,
        verified INTEGER DEFAULT 0
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        food_id INTEGER,
        quantity_g REAL,
        meal_type TEXT,
        input_method TEXT,
        date TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (food_id) REFERENCES foods(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favourites (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        food_id INTEGER,
        added_date TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (food_id) REFERENCES foods(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weight_log (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        weight_kg REAL,
        date TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_user_date ON entries(user_id, date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_meal_type ON entries(user_id, meal_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_favourites_user ON favourites(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_weight_user ON weight_log(user_id, date)")

    # Safe migration for existing databases
    safe_cols = [
        ("password_hash", "TEXT"),
        ("language", "TEXT DEFAULT 'en'"),
        ("goal", "TEXT DEFAULT 'general'"),
        ("is_muslim", "INTEGER DEFAULT 0"),
        ("age", "INTEGER"),
        ("weight_kg", "REAL"),
        ("height_cm", "REAL"),
    ]
    for col, definition in safe_cols:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
        except Exception:
            pass

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database ready.")