import sqlite3

conn = sqlite3.connect("users_data.db")
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    date TEXT NOT NULL,
    transaction_type TEXT,
    payment_gateway TEXT,
    transaction_state TEXT,
    merchant_category TEXT,
    amount REAL,
    is_fraud INTEGER
)
''')

conn.commit()
conn.close()
