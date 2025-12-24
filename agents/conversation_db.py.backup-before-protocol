"""
Conversation Database - Store and retrieve chat history
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

class ConversationDB:
    """
    SQLite database for storing conversation history
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "..", "memory", "conversations.db")
            
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        
    def _init_db(self):
        """Create tables if they don't exist"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        self.conn.commit()
        
    def create_conversation(self, title: str = None) -> int:
        """Create a new conversation"""
        if title is None:
            title = f"Chat - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO conversations (title) VALUES (?)
        """, (title,))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_all_conversations(self, limit: int = 20):
        """Get all conversations ordered by most recent"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, title, updated_at 
            FROM conversations 
            ORDER BY updated_at DESC 
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
        
    def add_message(self, conversation_id: int, role: str, content: str, metadata: Dict = None):
        """Add a message to a conversation"""
        cursor = self.conn.cursor()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        cursor.execute("""
            INSERT INTO messages (conversation_id, role, content, metadata)
            VALUES (?, ?, ?, ?)
        """, (conversation_id, role, content, metadata_json))
        
        # Update conversation timestamp
        cursor.execute("""
            UPDATE conversations SET updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (conversation_id,))
        
        self.conn.commit()
        
    def get_conversation_messages(self, conversation_id: int) -> List[Dict[str, Any]]:
        """Get all messages from a conversation"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, role, content, timestamp, metadata
            FROM messages
            WHERE conversation_id = ?
            ORDER BY timestamp ASC
        """, (conversation_id,))
        
        messages = []
        for row in cursor.fetchall():
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            messages.append({
                'id': row['id'],
                'role': row['role'],
                'content': row['content'],
                'timestamp': row['timestamp'],
                'metadata': metadata
            })
            
        return messages
        
    def get_recent_conversations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get list of recent conversations"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.id, c.title, c.created_at, c.updated_at,
                   (SELECT COUNT(*) FROM messages WHERE conversation_id = c.id) as message_count,
                   (SELECT content FROM messages WHERE conversation_id = c.id ORDER BY timestamp ASC LIMIT 1) as first_message
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
                'message_count': row['message_count'],
                'preview': row['first_message'][:100] if row['first_message'] else ""
            })
            
        return conversations
        
    def update_conversation_title(self, conversation_id: int, title: str):
        """Update conversation title"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE conversations SET title = ? WHERE id = ?
        """, (title, conversation_id))
        self.conn.commit()
        
    def delete_conversation(self, conversation_id: int):
        """Delete a conversation and all its messages"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        self.conn.commit()
        
    def search_conversations(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search conversations by content"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT c.id, c.title, c.updated_at
            FROM conversations c
            JOIN messages m ON c.id = m.conversation_id
            WHERE m.content LIKE ? OR c.title LIKE ?
            ORDER BY c.updated_at DESC
            LIMIT ?
        """, (f'%{query}%', f'%{query}%', limit))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'title': row['title'],
                'updated_at': row['updated_at']
            })
            
        return results
        
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM conversations")
        conversation_count = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM messages")
        message_count = cursor.fetchone()['count']
        
        return {
            'conversations': conversation_count,
            'messages': message_count
        }
        
    def close(self):
        """Close database connection"""
        self.conn.close()

    def close(self):
        """Close database connection"""
        self.conn.close()

