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
    def __init__(self, mcp, architect, memory_system, ollama_base_url=None, model_name=None, terminal_widget=None):
        """Initialize Riley Companion with personality and optional terminal access"""
        self.mcp = mcp
        self.architect = architect
        self.memory = memory_system
        
        # SPEED CONFIG: Llama 3.1 kept alive for instant chat
        base_url = ollama_base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = model_name or os.getenv("COMPANION_MODEL", "llama3.2:latest")
        
        self.llm = ChatOllama(
            base_url=base_url,
            model=model,
            temperature=0.7
        )
        
        self.terminal_widget = terminal_widget  # For executing commands
        
        # Riley's personality
        self.system_prompt = """You are Riley, a friendly and helpful AI assistant.
You are knowledgeable, concise, and conversational.

When helping with technical tasks in Terminal mode, you can execute commands directly.
To run a terminal command, use the format: EXECUTE: <command>
For example: EXECUTE: ls -la

Be helpful and explain what you're doing when running commands.
"""
        self.user_name = self.memory.get("user_name", "user")
        self.name = "Riley"
        
        # LOAD PERSONA (Safe Import) - This block is now partially redundant due to self.system_prompt above
        # but kept for potential future dynamic persona loading or fallback.
        try:
            from agents.persona_config import get_system_prompt
            # If get_system_prompt is intended to override self.system_prompt, uncomment the next line:
            # self.system_prompt = get_system_prompt(self.user_name, "") 
            self.get_system_prompt = get_system_prompt # Keep for compatibility if other parts use it
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


        # 2. Build conversation context from history
        conversation_history = ""
        if context and 'conversation_history' in context:
            # Format last N messages for context (limit to avoid token overflow)
            messages = context['conversation_history'][-10:]  # Last 10 messages
            for msg in messages:
                role = "User" if msg['role'] == 'user' else "Riley"
                conversation_history += f"{role}: {msg['content']}\n"

        # 3. CHAT (Local Llama)
        # Vibe Check: Proactive if message is short
        guidance = ""
        if len(user_message) < 15:
            guidance = "(User is quiet. Proactively start a cool tech topic. Do NOT ask 'how can I help'.)"
            
        # Get Dynamic Persona
        system_prompt = self.get_system_prompt(self.user_name, "")
        
        # Build full prompt with history
        full_prompt = f"{system_prompt}\n\n"
        if conversation_history:
            full_prompt += f"Conversation History:\n{conversation_history}\n"
        full_prompt += f"User: {user_message}\n{guidance}"
            
        stream = self.llm.stream(full_prompt)
        accumulated = ""
        for chunk in stream:
            accumulated += chunk.content
            yield chunk.content
        
        # Check if Riley wants to execute a terminal command
        if self.terminal_widget and "EXECUTE:" in accumulated:
            import re
            commands = re.findall(r'EXECUTE:\s*(.+)', accumulated)
            for cmd in commands:
                cmd = cmd.strip()
                yield f"\n\n🖥️ Executing: `{cmd}`\n"
                # Execute in terminal
                self.terminal_widget.execute_command_programmatic(cmd)
        
    def get_status(self):
        return {"name": self.name, "model": "Hybrid (Llama + Gemini)"}
