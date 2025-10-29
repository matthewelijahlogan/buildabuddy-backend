# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from ml.vectorizer import PersonalityVectorizer
from ml.mood_engine import MoodEngine
from ml.responder import Responder
import sqlite3
import os

# Path to SQLite database
from backend.database.db_init import DB_PATH

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow requests from mobile app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory cache of buddy engines (optional for performance)
buddies = {}

# Pydantic model for chat requests
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
    # Initialize buddy if new
    if req.buddy_id not in buddies:
        buddies[req.buddy_id] = {
            "vectorizer": PersonalityVectorizer(),
            "mood_engine": MoodEngine(),
        }

    vec = buddies[req.buddy_id]["vectorizer"]
    mood_engine = buddies[req.buddy_id]["mood_engine"]

    # Load or initialize personality vector from DB
    personality_vector = vec.get_vector(req.buddy_id, req.personality)

    # Update mood based on incoming message
    mood = mood_engine.update_mood(req.message)
    update_mood_in_db(req.buddy_id, mood)

    # Generate reply using personality vector and current mood
    responder = Responder(personality_vector, mood)
    reply = responder.generate_response(req.message)

    # Save conversation in DB
    save_conversation(req.buddy_id, req.message, reply)

    # Optional: return last few messages to help frontend context
    history = get_history(req.buddy_id, limit=5)

    return {
        "buddy_id": req.buddy_id,
        "mood": mood,
        "reply": reply,
        "history": history
    }
