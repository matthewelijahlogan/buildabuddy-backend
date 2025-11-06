# backend/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os

from database.db_init import DB_PATH
from ml.llm import BuddyEngine

app = FastAPI(title="Build-A-Buddy Backend")

# Allow mobile + local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For Render + local testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache of running BuddyEngine instances
buddies = {}

# ---------------------------
# Models
# ---------------------------

class ChatRequest(BaseModel):
    buddy_id: str
    personality: str
    message: str

class InitBuddyRequest(BaseModel):
    buddy_id: str
    personality: str = "friendly"

# ---------------------------
# Database utils
# ---------------------------

def get_connection():
    """Safe SQLite connection factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_buddy_in_db(buddy_id: str, personality: str):
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
    conn.close()

def update_mood_in_db(buddy_id: str, mood: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE buddies SET current_mood=? WHERE buddy_id=?",
        (mood, buddy_id),
    )
    conn.commit()
    conn.close()

def save_conversation(buddy_id: str, user_message: str, buddy_reply: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO conversations (buddy_id, user_message, buddy_reply)
        VALUES (?, ?, ?)
        """,
        (buddy_id, user_message, buddy_reply),
    )
    conn.commit()
    conn.close()

def get_history(buddy_id: str, limit: int = 10):
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
    conn.close()
    return rows[::-1]  # Return oldest first

# ---------------------------
# API Endpoints
# ---------------------------

@app.get("/")
def root():
    return {"status": "✅ Build-A-Buddy backend running on Render"}

@app.get("/health")
def health_check():
    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
        return {"ok": True, "status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/init")
def init_buddy(req: InitBuddyRequest):
    """Initialize or reset a buddy in DB and memory."""
    ensure_buddy_in_db(req.buddy_id, req.personality)
    buddies[req.buddy_id] = BuddyEngine(req.buddy_id, req.personality)
    return {"message": f"Buddy {req.buddy_id} initialized with {req.personality} personality."}

@app.post("/chat")
def chat(req: ChatRequest):
    # Ensure buddy exists
    ensure_buddy_in_db(req.buddy_id, req.personality)

    # Create or update engine
    if req.buddy_id not in buddies:
        buddies[req.buddy_id] = BuddyEngine(req.buddy_id, req.personality)
    else:
        buddies[req.buddy_id].update_personality(req.personality)

    buddy_engine = buddies[req.buddy_id]

    # Generate response
    try:
        mood, reply = buddy_engine.get_reply(req.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model error: {e}")

    # Persist conversation
    save_conversation(req.buddy_id, req.message, reply)
    update_mood_in_db(req.buddy_id, mood)
    history = get_history(req.buddy_id, limit=5)

    return {
        "buddy_id": req.buddy_id,
        "mood": mood,
        "reply": reply,
        "history": history,
    }
