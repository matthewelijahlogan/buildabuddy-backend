# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

from backend.database.db_init import DB_PATH
from ml.llm import BuddyEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow requests from mobile app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache of BuddyEngine instances for performance
buddies = {}

# ---------------------------
# Pydantic models
# ---------------------------

class ChatRequest(BaseModel):
    buddy_id: str
    personality: str
    message: str

# ---------------------------
# Database utility functions
# ---------------------------

def save_conversation(buddy_id: str, user_message: str, buddy_reply: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO conversations (buddy_id, user_message, buddy_reply) VALUES (?, ?, ?)",
        (buddy_id, user_message, buddy_reply)
    )
    conn.commit()
    conn.close()

def get_history(buddy_id: str, limit: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT user_message, buddy_reply FROM conversations WHERE buddy_id=? ORDER BY timestamp DESC LIMIT ?",
        (buddy_id, limit)
    )
    rows = cur.fetchall()
    conn.close()
    return rows[::-1]  # oldest first

def ensure_buddy_in_db(buddy_id: str, personality: str):
    """
    Ensure the buddy exists in the DB; if not, insert with default personality vector.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT buddy_id FROM buddies WHERE buddy_id=?", (buddy_id,))
    row = cur.fetchone()
    if not row:
        cur.execute(
            "INSERT INTO buddies (buddy_id, personality_type, kindness, excitement, humor, current_mood) VALUES (?, ?, ?, ?, ?, ?)",
            (buddy_id, personality, 0.5, 0.5, 0.5, "neutral")
        )
        conn.commit()
    conn.close()

def update_mood_in_db(buddy_id: str, mood: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "UPDATE buddies SET current_mood=? WHERE buddy_id=?",
        (mood, buddy_id)
    )
    conn.commit()
    conn.close()

# ---------------------------
# API Routes
# ---------------------------

@app.get("/")
def home():
    return {"status": "Build-A-Buddy backend running"}

@app.post("/chat")
def chat(req: ChatRequest):
    # Ensure buddy exists in DB
    ensure_buddy_in_db(req.buddy_id, req.personality)

    # Initialize BuddyEngine if not in cache
    if req.buddy_id not in buddies:
        buddies[req.buddy_id] = BuddyEngine(req.buddy_id, req.personality)
    else:
        # Update personality if changed
        buddies[req.buddy_id].update_personality(req.personality)

    buddy_engine = buddies[req.buddy_id]

    # Get reply and mood from BuddyEngine
    mood, reply = buddy_engine.get_reply(req.message)

    # Save conversation
    save_conversation(req.buddy_id, req.message, reply)

    # Update mood in DB
    update_mood_in_db(req.buddy_id, mood)

    # Return last few messages to help frontend context
    history = get_history(req.buddy_id, limit=5)

    return {
        "buddy_id": req.buddy_id,
        "mood": mood,
        "reply": reply,
        "history": history
    }
