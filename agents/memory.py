"""
Memory System - Persistent context and external service integration
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any

class MemorySystem:
    """
    Manages context, memories, and external service integrations
    Acts as the agent's long-term memory and knowledge base
    """
    
    def __init__(self, memory_file="memory/context.json"):
        self.memory_file = memory_file
        self.context = {}
        self.conversations = []
        self.external_services = {}
        self.load_memory()
    
    def load_memory(self):
        """Load memory from disk"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    self.context = data.get('context', {})
                    self.conversations = data.get('conversations', [])
        except Exception as e:
            print(f"Could not load memory: {e}")
    
    def save_memory(self):
        """Save memory to disk"""
        try:
            with open(self.memory_file, 'w') as f:
                json.dump({
                    'context': self.context,
                    'conversations': self.conversations[-100:],  # Keep last 100
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Could not save memory: {e}")
    
    def get(self, key: str, default=None):
        """Get a value from context"""
        return self.context.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a value in context and save"""
        self.context[key] = value
        self.save_memory()
    
    def add_conversation(self, user_message: str, agent_response: str, agent_type: str):
        """Store a conversation turn"""
        self.conversations.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_message,
            'agent': agent_response,
            'agent_type': agent_type
        })
        self.save_memory()
    
    def set_context(self, key: str, value: Any):
        """Set a context value"""
        self.context[key] = value
        self.save_memory()
    
    def get_context(self, key: str, default=None) -> Any:
        """Get a context value"""
        return self.context.get(key, default)
    
    def get_recent_context(self, n: int = 5) -> str:
        """Get recent conversation context as formatted string"""
        if not self.conversations:
            return "No previous conversations."
        
        recent = self.conversations[-n:]
        context_str = ""
        for conv in recent:
            user_msg = conv.get('user', '')
            agent_msg = conv.get('agent', '')
            context_str += f"User: {user_msg}\nAssistant: {agent_msg}\n\n"
        
        return context_str.strip()
    
    def get_recent_conversations(self, limit: int = 5) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversations[-limit:]
    
    def register_external_service(self, name: str, config: Dict):
        """
        Register an external AI service or API
        
        Example:
            memory.register_external_service('notion', {
                'api_key': 'xxx',
                'database_id': 'yyy'
            })
        """
        self.external_services[name] = config
        self.set_context(f'service_{name}', config)
    
    def get_service_config(self, name: str) -> Dict:
        """Get configuration for an external service"""
        return self.external_services.get(name) or self.get_context(f'service_{name}', {})
    
    def search_memories(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search through conversation history
        Simple keyword search for now
        """
        results = []
        query_lower = query.lower()
        
        for conv in reversed(self.conversations):
            if (query_lower in conv['user'].lower() or 
                query_lower in conv['agent'].lower()):
                results.append(conv)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_context_for_prompt(self, current_task: str) -> str:
        """
        Build context string to include in prompts
        Makes the agent aware of previous conversations and context
        """
        recent = self.get_recent_conversations(3)
        if not recent:
            return ""
        
        context_str = "\n\nRecent context:\n"
        for conv in recent:
            context_str += f"- User asked: {conv['user'][:100]}...\n"
        
        return context_str
