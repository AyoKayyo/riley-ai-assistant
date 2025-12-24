"""
Conversation Database - Store and retrieve chat history
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class ConversationDB:
    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(__file__))
            db_path = os.path.join(base_dir, "memory", "conversations.db")
            
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # FIXED: Complete SQL statement with proper closing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        """)
        self.conn.commit()

    def create_conversation(self, title: str = None) -> int:
        if title is None:
            title = f"Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO conversations (title) VALUES (?)", (title,))
        self.conn.commit()
        return cursor.lastrowid

    def add_message(self, conversation_id: int, role: str, content: str, metadata: Dict = None):
        cursor = self.conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content, metadata)
            VALUES (?, ?, ?, ?)
        """, (conversation_id, role, content, metadata_json))
        cursor.execute("UPDATE conversations SET updated_at = CURRENT_TIMESTAMP WHERE id = ?", (conversation_id,))
        self.conn.commit()

    def get_conversation_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM messages WHERE conversation_id = ? ORDER BY timestamp ASC", (conversation_id,))
        messages = []
        for row in cursor.fetchall():
            meta = json.loads(row['metadata']) if row['metadata'] else {}
            messages.append({'role': row['role'], 'content': row['content'], 'metadata': meta})
        return messages
    
    def get_recent_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get list of recent conversations"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.id, c.title, c.created_at, c.updated_at,
                   (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count
            FROM conversations c
            ORDER BY c.updated_at DESC
            LIMIT ?
        """, (limit,))
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'id': row['id'],
                'title': row['title'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'message_count': row['message_count']
            })
        return conversations

    def close(self):
        self.conn.close()
