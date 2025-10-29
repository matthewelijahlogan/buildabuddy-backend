-- Schema for Buddy Chat Application 
-- backend/database/schema.sql

-- Buddy table: stores personality vectors & current mood
CREATE TABLE IF NOT EXISTS buddies (
    buddy_id TEXT PRIMARY KEY,
    personality_type TEXT,
    kindness REAL,
    excitement REAL,
    humor REAL,
    current_mood TEXT
);

-- Conversation table: stores chat history
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buddy_id TEXT,
    user_message TEXT,
    buddy_reply TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(buddy_id) REFERENCES buddies(buddy_id)
);
-- Buddy table: stores personality vectors & current mood
CREATE TABLE IF NOT EXISTS buddies (
    buddy_id TEXT PRIMARY KEY,
    personality_type TEXT,
    kindness REAL,
    excitement REAL,
    humor REAL,
    current_mood TEXT
);

-- Conversation table: stores chat history
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buddy_id TEXT,
    user_message TEXT,
    buddy_reply TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(buddy_id) REFERENCES buddies(buddy_id)
);
