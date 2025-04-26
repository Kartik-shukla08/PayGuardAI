import sqlite3

conn = sqlite3.connect("users_data.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS upi_reputation (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    upi_id TEXT NOT NULL,
    user_email TEXT,
    rating INTEGER CHECK(rating BETWEEN 1 AND 5),
    flag_reason TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

conn.commit()
conn.close()
