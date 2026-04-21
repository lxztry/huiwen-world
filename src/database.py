"""
汇文世界 · 数据库层
SQLite implementation for user data, sessions, and memorable scenes.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any


DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "huiwen.db")


def get_conn():
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            wen_ge_type TEXT,
            name TEXT,
            background TEXT,
            personality TEXT,
            relationships TEXT DEFAULT '{}',
            wenming TEXT DEFAULT '',
            mode TEXT DEFAULT 'daily',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            mode TEXT DEFAULT 'daily',
            scene TEXT,
            characters TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memorable_scenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            user_id TEXT,
            scene_type TEXT,
            description TEXT,
            participants TEXT DEFAULT '[]',
            tags TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def create_user(user_id: str, wen_ge_type: str, name: str, background: str, personality: str) -> bool:
    """Create a new user with their wen_ge profile."""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO users (user_id, wen_ge_type, name, background, personality, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, wen_ge_type, name, background, personality, datetime.now().isoformat()))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating user: {e}")
        return False
    finally:
        conn.close()


def get_user(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user by ID."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


def update_user_wenming(user_id: str, wenming: str) -> bool:
    """Update user's wenming (文名)."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET wenming = ? WHERE user_id = ?", (wenming, user_id))
    conn.commit()
    conn.close()
    return True


def update_user_relationship(user_id: str, character_id: str, level: str, tag: str) -> bool:
    """Update relationship with a character."""
    user = get_user(user_id)
    if not user:
        return False
    rels = json.loads(user.get("relationships", "{}"))
    if character_id not in rels:
        rels[character_id] = {"level": level, "tags": []}
    else:
        if tag not in rels[character_id]["tags"]:
            rels[character_id]["tags"].append(tag)
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET relationships = ? WHERE user_id = ?", (json.dumps(rels), user_id))
    conn.commit()
    conn.close()
    return True


def update_user_mode(user_id: str, mode: str) -> bool:
    """Update user's current mode (daily/script)."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET mode = ? WHERE user_id = ?", (mode, user_id))
    conn.commit()
    conn.close()
    return True


def create_session(session_id: str, user_id: str, mode: str = "daily", scene: str = "") -> bool:
    """Create a new session."""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO sessions (session_id, user_id, mode, scene, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (session_id, user_id, mode, scene, datetime.now().isoformat(), datetime.now().isoformat()))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating session: {e}")
        return False
    finally:
        conn.close()


def update_session_scene(session_id: str, scene: str, characters: List[str]) -> bool:
    """Update session scene info."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE sessions SET scene = ?, characters = ?, updated_at = ? WHERE session_id = ?
    """, (scene, json.dumps(characters), datetime.now().isoformat(), session_id))
    conn.commit()
    conn.close()
    return True


def add_memorable_scene(session_id: str, user_id: str, scene_type: str, description: str,
                        participants: List[str], tags: List[str]) -> bool:
    """Record a memorable scene."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO memorable_scenes (session_id, user_id, scene_type, description, participants, tags, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (session_id, user_id, scene_type, description, json.dumps(participants), json.dumps(tags),
          datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return True


def get_memorable_scenes(user_id: str) -> List[Dict[str, Any]]:
    """Get all memorable scenes for a user."""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM memorable_scenes WHERE user_id = ? ORDER BY created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


if __name__ == "__main__":
    init_db()
    print("Database initialized.")
