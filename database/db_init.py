# backend/database/db_init.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "buddies.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    with open(os.path.join(os.path.dirname(__file__), "schema.sql"), "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
