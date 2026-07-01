import sqlite3

conn = sqlite3.connect("calorie_app.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT UNIQUE
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
    quantity REAL,
    date TEXT,
    input_method TEXT
)
""")

cursor.execute("CREATE INDEX IF NOT EXISTS idx_entries_user_date ON entries(user_id, date)")

conn.commit()
conn.close()

print("Database created successfully.")