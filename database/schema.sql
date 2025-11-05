-- ==========================================================
-- Build-A-Buddy Database Schema
-- ==========================================================
-- This schema is optimized for mobile (SQLite) deployments.
-- Stores users, chat messages, moods, and memory data.
-- ==========================================================

PRAGMA foreign_keys = ON;

-- ==========================================================
-- USERS TABLE
-- ==========================================================
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE,
    password_hash TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- ==========================================================
-- CHAT MESSAGES
-- ==========================================================
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    sender TEXT NOT NULL,  -- 'user' or 'buddy'
    message TEXT NOT NULL,
    mood TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ==========================================================
-- MOOD TRACKING
-- ==========================================================
CREATE TABLE IF NOT EXISTS moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    mood TEXT NOT NULL,
    confidence REAL DEFAULT 0.0,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ==========================================================
-- VECTOR MEMORY (for embeddings / context recall)
-- ==========================================================
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    embedding BLOB,            -- Serialized vector from ml/vectorizer.py
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ==========================================================
-- SETTINGS / PREFERENCES
-- ==========================================================
CREATE TABLE IF NOT EXISTS preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    theme TEXT DEFAULT 'light',
    language TEXT DEFAULT 'en',
    notifications_enabled INTEGER DEFAULT 1,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- ==========================================================
-- INDEXES FOR PERFORMANCE
-- ==========================================================
CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id);
CREATE INDEX IF NOT EXISTS idx_moods_user ON moods(user_id);
CREATE INDEX IF NOT EXISTS idx_memory_user ON memory(user_id);

-- ==========================================================

-- ==========================================================
-- BUDDIES TABLE
-- ==========================================================
CREATE TABLE IF NOT EXISTS buddies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buddy_id TEXT UNIQUE NOT NULL,
    personality_type TEXT,
    kindness REAL,
    excitement REAL,
    humor REAL,
    current_mood TEXT DEFAULT 'neutral'
);

-- ==========================================================
-- CONVERSATIONS TABLE
-- ==========================================================
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buddy_id TEXT NOT NULL,
    user_message TEXT NOT NULL,
    buddy_reply TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (buddy_id) REFERENCES buddies(buddy_id) ON DELETE CASCADE
);

-- ==========================================================