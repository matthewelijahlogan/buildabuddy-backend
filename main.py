# backend/main.py

import sys
import os
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from typing import List, Optional

# ---------------------------
# Fix imports for local folder structure
# ---------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from database.db_init import DB_PATH
from ml.llm import BuddyEngine

# ---------------------------
# FastAPI app
# ---------------------------
app = FastAPI(title="Build-A-Buddy Backend")

# ---------------------------
# CORS Middleware (allow dev frontend)
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins for dev; adjust for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# BuddyEngine cache
# ---------------------------
buddies = {}

# ---------------------------
# Models
# ---------------------------
class ChatRequest(BaseModel):
    username: str
    buddy_id: str
    personality: str
    message: str

class InitBuddyRequest(BaseModel):
    username: str
    buddy_id: str
    personality: str = "friendly"

# ---------------------------
# Database utilities
# ---------------------------
def get_connection():
    """Safe SQLite connection factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_user_in_db(username: str):
    """Ensure a user exists in the users table."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        if not row:
            cur.execute("INSERT INTO users (username) VALUES (?)", (username,))
            conn.commit()
            cur.execute("SELECT id FROM users WHERE username=?", (username,))
            row = cur.fetchone()
        return row["id"]
    except Exception as e:
        print(f"DB error in ensure_user_in_db: {e}")
        return None
    finally:
        conn.close()

def ensure_buddy_in_db(buddy_id: str, personality: str):
    """Ensure a buddy exists in the buddies table."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT buddy_id FROM buddies WHERE buddy_id=?", (buddy_id,))
        row = cur.fetchone()
        if not row:
            cur.execute(
                """
                INSERT INTO buddies (buddy_id, personality_type, kindness, excitement, humor, current_mood)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (buddy_id, personality, 0.5, 0.5, 0.5, "neutral"),
            )
            conn.commit()
    except Exception as e:
        print(f"DB error in ensure_buddy_in_db: {e}")
    finally:
        conn.close()

def update_mood_in_db(buddy_id: str, mood: str):
    """Update the current mood of a buddy."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE buddies SET current_mood=? WHERE buddy_id=?", (mood, buddy_id))
        conn.commit()
    except Exception as e:
        print(f"DB error in update_mood_in_db: {e}")
    finally:
        conn.close()

def save_conversation(user_id: int, buddy_id: str, user_message: str, buddy_reply: str):
    """Persist a conversation to the database."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO conversations (buddy_id, user_message, buddy_reply)
            VALUES (?, ?, ?)
            """,
            (buddy_id, user_message, buddy_reply),
        )
        cur.execute(
            """
            INSERT INTO messages (user_id, sender, message, mood)
            VALUES (?, 'user', ?, ?)
            """,
            (user_id, user_message, None)
        )
        cur.execute(
            """
            INSERT INTO messages (user_id, sender, message, mood)
            VALUES (?, 'buddy', ?, ?)
            """,
            (user_id, buddy_reply, None)
        )
        conn.commit()
    except Exception as e:
        print(f"DB error in save_conversation: {e}")
    finally:
        conn.close()

def get_history(buddy_id: str, limit: int = 10) -> List[tuple]:
    """Fetch recent conversation history for a buddy."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT user_message, buddy_reply
            FROM conversations
            WHERE buddy_id=?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (buddy_id, limit),
        )
        rows = cur.fetchall()
        return rows[::-1]  # oldest first
    except Exception as e:
        print(f"DB error in get_history: {e}")
        return []
    finally:
        conn.close()

# ---------------------------
# API Endpoints
# ---------------------------
@app.get("/")
def root():
    return {"status": "✅ Build-A-Buddy backend running"}

@app.get("/health")
def health_check():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"ok": True, "status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat-history")
def chat_history(buddy_id: str, limit: int = 20):
    history = get_history(buddy_id, limit)
    return [{"user_message": msg, "buddy_reply": reply} for msg, reply in history]

@app.post("/init")
def init_buddy(req: InitBuddyRequest):
    """Initialize or reset a buddy in DB and memory."""
    user_id = ensure_user_in_db(req.username)
    if user_id is None:
        raise HTTPException(status_code=500, detail="Failed to create or fetch user.")
    
    ensure_buddy_in_db(req.buddy_id, req.personality)

    try:
        buddies[req.buddy_id] = BuddyEngine(req.buddy_id, req.personality)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BuddyEngine init failed: {e}")

    return {"message": f"User '{req.username}' and buddy '{req.buddy_id}' initialized with personality '{req.personality}'."}

@app.post("/chat")
def chat(req: ChatRequest):
    """Send a message to a buddy and return response."""
    user_id = ensure_user_in_db(req.username)
    if user_id is None:
        raise HTTPException(status_code=500, detail="Failed to create or fetch user.")
    
    ensure_buddy_in_db(req.buddy_id, req.personality)

    # Initialize or update buddy engine
    if req.buddy_id not in buddies:
        try:
            buddies[req.buddy_id] = BuddyEngine(req.buddy_id, req.personality)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"BuddyEngine init failed: {e}")
    else:
        buddies[req.buddy_id].update_personality(req.personality)

    buddy_engine = buddies[req.buddy_id]

    # Generate response safely
    try:
        mood, reply = buddy_engine.get_reply(req.message)
        if not reply:
            reply = "Hmm... I didn't understand that. Can you rephrase?"
        if not mood:
            mood = "neutral"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"BuddyEngine reply failed: {e}")

    # Persist conversation
    save_conversation(user_id, req.buddy_id, req.message, reply)
    update_mood_in_db(req.buddy_id, mood)
    history = get_history(req.buddy_id, limit=5)

    return {
        "buddy_id": req.buddy_id,
        "username": req.username,
        "mood": mood,
        "reply": reply,
        "history": history,
    }
