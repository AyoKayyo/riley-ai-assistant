"""
Deep Memory System (The Hippocampus)
Uses Vector Database (ChromaDB) to give Riley long-term, semantic recall.
"""
import chromadb
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional

class MemoryManager:
    """
    Manages long-term semantic memory for the Companion.
    Stores and retrieves memories based on meaning, not just keywords.
    """
    
    def __init__(self, persistence_path="./memory/db"):
        self.client = chromadb.PersistentClient(path=persistence_path)
        
        # Collection for general conversation memories
        self.memories = self.client.get_or_create_collection(
            name="companion_memories",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Collection for user facts/profile
        self.facts = self.client.get_or_create_collection(
            name="user_facts",
            metadata={"hnsw:space": "cosine"} 
        )

    def add_memory(self, text: str, source: str = "conversation", tags: List[str] = None):
        """Store a new memory fragment"""
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        self.memories.add(
            documents=[text],
            metadatas=[{
                "timestamp": timestamp,
                "source": source,
                "tags": ",".join(tags) if tags else ""
            }],
            ids=[memory_id]
        )
        return memory_id
        
    def add_fact(self, fact: str, category: str = "general"):
        """Store a core fact about the user (e.g., "Likes sci-fi")"""
        fact_id = str(uuid.uuid4())
        self.facts.add(
            documents=[fact],
            metadatas=[{
                "timestamp": datetime.now().isoformat(),
                "category": category
            }],
            ids=[fact_id]
        )

    def recall(self, query: str, n_results: int = 3) -> List[str]:
        """Retrieve relevant memories based on semantic meaning"""
        if not query:
            return []
            
        results = self.memories.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Flatten results
        return results['documents'][0] if results['documents'] else []

    def recall_facts(self, query: str = None) -> List[str]:
        """Retrieve relevant facts about the user"""
        if not query:
            # excessive, maybe random sample? For now return top 5
             return [] 

        results = self.facts.query(
            query_texts=[query],
            n_results=5
        )
        return results['documents'][0] if results['documents'] else []

    def get_context_string(self, current_input: str) -> str:
        """
        Builds a context string for the LLM prompt.
        Recalls relevant past memories + user facts.
        """
        relevant_memories = self.recall(current_input, n_results=3)
        relevant_facts = self.recall_facts(current_input)
        
        context = ""
        
        if relevant_facts:
            context += "KNOWN FACTS ABOUT USER:\n" + "\n".join([f"- {f}" for f in relevant_facts]) + "\n\n"
            
        if relevant_memories:
            context += "RELEVANT PAST MEMORIES:\n" + "\n".join([f"- {m}" for m in relevant_memories]) + "\n"
            
        return context

# Test if running standalone
if __name__ == "__main__":
    memory = MemoryManager()
    memory.add_fact("User is a software engineer named Mark.")
    memory.add_memory("We discussed the new architecture for the agent system.")
    
    print("Recall 'who is user':", memory.recall_facts("who is the user"))
    print("Recall 'system':", memory.recall("agent architecture"))
