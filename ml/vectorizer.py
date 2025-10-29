# backend/ml/vectorizer.py
import numpy as np
import sqlite3
from backend.database.db_init import DB_PATH

class PersonalityVectorizer:
    def __init__(self):
        self.default_vectors = {
            "friendly": np.array([0.9, 0.8, 0.4]),
            "sarcastic": np.array([0.2, 0.1, 0.9]),
            "romantic": np.array([0.7, 0.9, 0.6]),
            "motivational": np.array([0.8, 0.4, 0.7]),
        }

    def get_vector(self, buddy_id: str, personality_type: str = "friendly"):
        # Try loading from DB
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT kindness, excitement, humor FROM buddies WHERE buddy_id=?", (buddy_id,))
        row = cur.fetchone()
        conn.close()

        if row:
            return np.array(row)
        else:
            # Initialize in DB
            vec = self.default_vectors.get(personality_type, np.array([0.5, 0.5, 0.5]))
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO buddies (buddy_id, personality_type, kindness, excitement, humor, current_mood) VALUES (?, ?, ?, ?, ?, ?)",
                (buddy_id, personality_type, float(vec[0]), float(vec[1]), float(vec[2]), "neutral")
            )
            conn.commit()
            conn.close()
            return vec

    def update_vector(self, buddy_id: str, new_vector):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "UPDATE buddies SET kindness=?, excitement=?, humor=? WHERE buddy_id=?",
            (float(new_vector[0]), float(new_vector[1]), float(new_vector[2]), buddy_id)
        )
        conn.commit()
        conn.close()
