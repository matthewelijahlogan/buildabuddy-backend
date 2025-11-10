# ===================================================================
# Build-A-Buddy Personality Vectorizer
# Handles personality vector retrieval and updates with safe DB fallback
# ===================================================================

import numpy as np
import sqlite3
from typing import Any
from database.db_init import DB_PATH
import traceback

class PersonalityVectorizer:
    """
    Manages personality vectors for buddies.
    Tries to load from SQLite database, otherwise falls back to defaults.
    Vector layout: [friendliness, humor, excitement, empathy, curiosity]
    """

    def __init__(self):
        self.default_vectors = {
            "friendly": np.array([0.9, 0.8, 0.4, 0.7, 0.6]),
            "sarcastic": np.array([0.2, 0.9, 0.5, 0.3, 0.4]),
            "romantic": np.array([0.7, 0.6, 0.5, 0.9, 0.7]),
            "motivational": np.array([0.8, 0.3, 0.9, 0.6, 0.5]),
        }

    def get_vector(self, buddy_id: str, personality_type: str = "friendly") -> np.ndarray:
        """
        Retrieve personality vector for a buddy from DB.
        Falls back to defaults and inserts into DB if missing.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "SELECT kindness, excitement, humor, current_mood, 0 FROM buddies WHERE buddy_id=?",
                (buddy_id,)
            )
            row = cur.fetchone()
            conn.close()

            if row:
                return np.array(row[:5], dtype=float)
            else:
                vec = self.default_vectors.get(personality_type, np.array([0.5]*5))
                try:
                    conn = sqlite3.connect(DB_PATH)
                    cur = conn.cursor()
                    cur.execute(
                        "INSERT INTO buddies "
                        "(buddy_id, personality_type, kindness, excitement, humor, current_mood) "
                        "VALUES (?, ?, ?, ?, ?, ?)",
                        (buddy_id, personality_type, float(vec[0]), float(vec[1]), float(vec[2]), "neutral")
                    )
                    conn.commit()
                    conn.close()
                except Exception as e:
                    print(f"Failed to initialize buddy {buddy_id} in DB:", e)
                    traceback.print_exc()
                return vec

        except Exception as e:
            print(f"Error fetching personality vector for {buddy_id}:", e)
            traceback.print_exc()
            return self.default_vectors.get(personality_type, np.array([0.5]*5))

    def update_vector(self, buddy_id: str, new_vector: Any):
        """
        Update the buddy's personality vector in the database.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "UPDATE buddies SET kindness=?, excitement=?, humor=? WHERE buddy_id=?",
                (float(new_vector[0]), float(new_vector[1]), float(new_vector[2]), buddy_id)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating personality vector for {buddy_id}:", e)
            traceback.print_exc()
