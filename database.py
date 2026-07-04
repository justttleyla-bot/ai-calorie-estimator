import sqlite3

conn = sqlite3.connect("calorie_app.db")
cursor = conn.cursor()

# Users table — now includes daily calorie goal
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    daily_calorie_goal REAL DEFAULT 2000
)
""")

# Foods table — unchanged
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

# Entries table — now includes meal_type and quantity_g
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

# Favourites table — new
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

# Indexes
cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_user_date ON entries(user_id, date)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_meal_type ON entries(user_id, meal_type)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_favourites_user ON favourites(user_id)")

conn.commit()
conn.close()

print("Database schema updated successfully.")