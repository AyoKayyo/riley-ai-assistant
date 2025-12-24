"""
Companion Agent - Sentient Assistant Personality (Hybrid Safe Build)
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Generator
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

load_dotenv()

class CompanionAgent:
    def __init__(self, mcp, architect, memory_system):
        self.mcp = mcp
        self.architect = architect
        self.memory = memory_system
        
        # SPEED CONFIG: Llama 3.1 kept alive for instant chat
        self.llm = ChatOllama(
            model=os.getenv("COMPANION_MODEL", "llama3.1:8b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.8,
            keep_alive="1h",
            num_ctx=4096
        )
        self.user_name = self.memory.get("user_name", "user")
        self.name = "Riley"
        
        # LOAD PERSONA (Safe Import)
        try:
            from agents.persona_config import get_system_prompt
            self.get_system_prompt = get_system_prompt
        except ImportError:
            # Fallback if file missing
            self.get_system_prompt = lambda u, c: f"You are Riley, a helpful AI assistant for {u}."

    def process(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        acc = ""
        for token in self.stream_process(user_message, context): 
            acc += token
        return acc

    def stream_process(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        msg_lower = user_message.lower()
        
        # 1. HYBRID ROUTING: Switch to Gemini 1.5 Pro
        # Triggered by UI Toggle (via prompt tag) OR keywords
        if "[SYSTEM: ARCHITECT MODE ACTIVE" in user_message or any(t in msg_lower for t in ["architect", "plan", "complex", "refactor"]):
             # Clean the system tag out for the Architect
             clean_msg = user_message.replace("[SYSTEM: ARCHITECT MODE ACTIVE. IGNORE LOCAL TOOLS. ROUTE THIS REQUEST TO GEMINI ARCHITECT IMMEDIATELY.]\n\n", "")
             
             yield "🧠 *Switching to Deep Thought Mode (Gemini 1.5 Pro)...*\n\n"
             try:
                 yield self.architect.execute(clean_msg)
             except Exception as e:
                 yield f"Architect Error: {e}"
             return

        # 2. CHAT (Local Llama)
        # Vibe Check: Proactive if message is short
        guidance = ""
        if len(user_message) < 15:
            guidance = "(User is quiet. Proactively start a cool tech topic. Do NOT ask 'how can I help'.)"
            
        # Get Dynamic Persona
        system_prompt = self.get_system_prompt(self.user_name, "")
            
        stream = self.llm.stream(f"{system_prompt}\nUser: {user_message}\n{guidance}")
        for chunk in stream: 
            yield chunk.content
        
    def get_status(self):
        return {"name": self.name, "model": "Hybrid (Llama + Gemini)"}
