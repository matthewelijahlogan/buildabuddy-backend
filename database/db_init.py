# backend/database/db_init.py

import sqlite3
import os

# -------------------------------------------------------------
# Database Initialization Script for Build-A-Buddy
# -------------------------------------------------------------
# This script sets up the local SQLite database using schema.sql
# Run this once (or whenever you need to reset your database)
# -------------------------------------------------------------

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "buildabuddy.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")

def initialize_database():
    """Creates or reinitializes the Build-A-Buddy SQLite database."""
    print("🚀 Initializing Build-A-Buddy database...")

    # Remove existing database (optional, for resets)
    if os.path.exists(DB_PATH):
        print("⚠️  Existing database found. Removing old file...")
        os.remove(DB_PATH)

    # Connect to the database
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    print("✅ Connected to database.")

    # Read schema
    if not os.path.exists(SCHEMA_PATH):
        print("❌ ERROR: schema.sql not found at:", SCHEMA_PATH)
        connection.close()
        return

    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()

    # Execute schema
    try:
        cursor.executescript(schema_sql)
        print("📜 Schema applied successfully.")
    except sqlite3.Error as e:
        print("❌ Error applying schema:", e)
        connection.close()
        return

    # Commit and close
    connection.commit()
    connection.close()
    print(f"🎉 Database initialized at: {DB_PATH}")

if __name__ == "__main__":
    initialize_database()
