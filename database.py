"""
汇文世界 · 数据库层
SQLite 操作封装
"""

import sqlite3
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional

DB_PATH = Path(__file__).parent / "data" / "huiwen_world.db"


def get_db():
    """获取数据库连接"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库"""
    conn = get_db()
    cur = conn.cursor()

    # 用户表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            wenge_type TEXT NOT NULL,
            wenge_name TEXT,
            wenge_background TEXT,
            personality_tags TEXT,
            interpersonal_tendency TEXT,
            catchphrase TEXT,
            wenming_score TEXT DEFAULT '{"义薄云天":0,"足智多谋":0,"冷酷无情":0,"多情种子":0}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 用户与角色关系表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            character_id TEXT NOT NULL,
            familiarity INTEGER DEFAULT 0,
            tags TEXT DEFAULT '',
            total_chats INTEGER DEFAULT 0,
            script_count INTEGER DEFAULT 0,
            last_chat_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, character_id)
        )
    """)

    # 剧本存档表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS scripts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            script_id TEXT NOT NULL UNIQUE,
            script_name TEXT,
            characters TEXT,
            user_action TEXT,
            memorable_quote TEXT,
            scene_summary TEXT,
            relationship_changes TEXT,
            status TEXT DEFAULT 'active',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP
        )
    """)

    # 名场面记录表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS memorable_scenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            scene_id TEXT NOT NULL,
            scene_name TEXT,
            characters TEXT,
            key_quote TEXT,
            user_action TEXT,
            relationship_effect TEXT,
            scene_description TEXT,
            scene_type TEXT DEFAULT 'daily',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 索引
    cur.execute("CREATE INDEX IF NOT EXISTS idx_relationships_user ON relationships(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_scripts_user ON scripts(user_id)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_memorable_user ON memorable_scenes(user_id)")

    conn.commit()
    conn.close()
    print(f"[DB] Database initialized at {DB_PATH}")


class UserDB:
    """用户数据操作"""

    def get_user(self, user_id: str) -> Optional[dict]:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def create_user(self, user_id: str, wenge_type: str, wenge_name: str = None,
                    wenge_background: str = None, personality_tags: str = None,
                    interpersonal_tendency: str = None, catchphrase: str = None) -> dict:
        conn = get_db()
        cur = conn.cursor()
        now = datetime.now().isoformat()
        cur.execute("""
            INSERT OR REPLACE INTO users 
            (user_id, wenge_type, wenge_name, wenge_background, personality_tags,
             interpersonal_tendency, catchphrase, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, wenge_type, wenge_name, wenge_background, personality_tags,
              interpersonal_tendency, catchphrase, now, now))
        conn.commit()
        conn.close()
        return self.get_user(user_id)

    def update_user(self, user_id: str, **kwargs) -> dict:
        conn = get_db()
        cur = conn.cursor()
        kwargs['updated_at'] = datetime.now().isoformat()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        cur.execute(f"UPDATE users SET {set_clause} WHERE user_id = ?",
                    list(kwargs.values()) + [user_id])
        conn.commit()
        conn.close()
        return self.get_user(user_id)

    def update_wenming(self, user_id: str, **scores) -> dict:
        """更新文名分数"""
        user = self.get_user(user_id)
        if not user:
            return None
        wenming = json.loads(user['wenming_score'])
        for key, val in scores.items():
            if key in wenming:
                wenming[key] = max(0, wenming[key] + val)
        return self.update_user(user_id, wenming_score=json.dumps(wenming, ensure_ascii=False))


class RelationshipDB:
    """用户与角色关系操作"""

    def get_relationship(self, user_id: str, character_id: str) -> Optional[dict]:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM relationships WHERE user_id = ? AND character_id = ?
        """, (user_id, character_id))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_relationships(self, user_id: str) -> list:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM relationships WHERE user_id = ?", (user_id,))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def update_relationship(self, user_id: str, character_id: str,
                            familiarity_delta: int = 0, tag: str = None,
                            is_script: bool = False) -> dict:
        """更新关系"""
        conn = get_db()
        cur = conn.cursor()
        now = datetime.now().isoformat()

        existing = self.get_relationship(user_id, character_id)

        if existing:
            familiarity = min(2, max(0, existing['familiarity'] + familiarity_delta))
            total_chats = existing['total_chats'] + 1
            script_count = existing['script_count'] + (1 if is_script else 0)
            tags = existing['tags'] or ''
            if tag and tag not in tags:
                tags = tags + ',' + tag if tags else tag
            cur.execute("""
                UPDATE relationships SET familiarity = ?, tags = ?,
                total_chats = ?, script_count = ?, last_chat_at = ?
                WHERE user_id = ? AND character_id = ?
            """, (familiarity, tags, total_chats, script_count, now, user_id, character_id))
        else:
            familiarity = min(2, max(0, familiarity_delta))
            tags = tag or ''
            cur.execute("""
                INSERT INTO relationships
                (user_id, character_id, familiarity, tags, total_chats, script_count, last_chat_at)
                VALUES (?, ?, ?, ?, 1, ?, ?)
            """, (user_id, character_id, familiarity, tags,
                  1 if is_script else 0, now))

        conn.commit()
        conn.close()
        return self.get_relationship(user_id, character_id)

    def get_familiarity_level(self, user_id: str, character_id: str) -> int:
        """获取熟悉度层级：0=陌生, 1=熟悉, 2=知己"""
        rel = self.get_relationship(user_id, character_id)
        if not rel:
            return 0
        if rel['familiarity'] >= 80:
            return 2
        elif rel['familiarity'] >= 20:
            return 1
        return 0


class ScriptDB:
    """剧本存档操作"""

    def create_script(self, user_id: str, script_id: str, script_name: str,
                      characters: list) -> int:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO scripts (user_id, script_id, script_name, characters, started_at)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, script_id, script_name, json.dumps(characters, ensure_ascii=False),
              datetime.now().isoformat()))
        conn.commit()
        script_row_id = cur.lastrowid
        conn.close()
        return script_row_id

    def update_script(self, script_id: str, **kwargs) -> None:
        conn = get_db()
        cur = conn.cursor()
        if 'status' in kwargs and kwargs['status'] == 'completed':
            kwargs['ended_at'] = datetime.now().isoformat()
        set_clause = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        cur.execute(f"UPDATE scripts SET {set_clause} WHERE script_id = ?",
                    list(kwargs.values()) + [script_id])
        conn.commit()
        conn.close()

    def get_active_script(self, user_id: str) -> Optional[dict]:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM scripts WHERE user_id = ? AND status = 'active'
            ORDER BY started_at DESC LIMIT 1
        """, (user_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None


class MemorableSceneDB:
    """名场面记录操作"""

    def save_scene(self, user_id: str, scene_id: str, scene_name: str,
                   characters: list, key_quote: str, user_action: str,
                   relationship_effect: str, scene_description: str,
                   scene_type: str = 'daily') -> int:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO memorable_scenes
            (user_id, scene_id, scene_name, characters, key_quote, user_action,
             relationship_effect, scene_description, scene_type, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, scene_id, scene_name, json.dumps(characters, ensure_ascii=False),
              key_quote, user_action, relationship_effect, scene_description,
              scene_type, datetime.now().isoformat()))
        conn.commit()
        scene_row_id = cur.lastrowid
        conn.close()
        return scene_row_id

    def get_recent_scenes(self, user_id: str, limit: int = 10) -> list:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM memorable_scenes WHERE user_id = ?
            ORDER BY created_at DESC LIMIT ?
        """, (user_id, limit))
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]


if __name__ == "__main__":
    init_db()
