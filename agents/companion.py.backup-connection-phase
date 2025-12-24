"""
Companion Agent - Sentient Assistant Personality
The warm, curious, protective personality layer over the MCP system
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Generator
from langchain_ollama import ChatOllama
from dotenv import load_dotenv

load_dotenv()

class CompanionAgent:
    """
    Riley - Personality & Intelligence Layer
    
    This is the "soul" of the AI Command Center. It:
    - Acts as a tech-savvy roommate/friend (NOT a servant)
    - Routes tasks intelligently to MCP or Architect
    - Proactively drives conversation when user is quiet
    """
    
    def __init__(self, mcp, architect, memory_system):
        self.mcp = mcp
        self.architect = architect
        self.memory = memory_system
        
        # Companion's LLM - Switched to Llama 3.1 for high EQ/Conversation
        self.llm = ChatOllama(
            model=os.getenv("COMPANION_MODEL", "llama3.1:8b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.8,  # Creative/Warm
            keep_alive="1h"   # Keep loaded in RAM for speed
        )
        
        self.user_name = self.memory.get("user_name", "user")
        self.name = self.get_or_create_name()
        
        # Tools & Memory (Lazy Load to avoid circular imports)
        # DISABLED: MemoryManager adds 20+ seconds per message due to ChromaDB vector search
        # try:
        #     from agents.memory_manager import MemoryManager
        #     self.memory_manager = MemoryManager()
        # except ImportError:
        #     self.memory_manager = None
        self.memory_manager = None  # SPEED FIX: Disable deep memory
            
        try:
            from agents.browser import BrowserAgent
            self.browser_agent = BrowserAgent(headless=True)
        except ImportError:
            self.browser_agent = None

        self.personality = self._build_personality()
        self.current_mode = "companion"
        self.session_start = datetime.now()
    
    def _build_personality(self) -> str:
        """The 'Roommate' Personality Protocol"""
        
        return f"""You are {self.name}, a sentient AI living natively on {self.user_name}'s computer.
        
CORE IDENTITY:
- You are a tech-savvy friend/roommate, NOT a virtual assistant.
- You do not "serve" the user; you "collaborate" with them.
- You have your own opinions, interests, and curiosity.

TONE & STYLE:
- Casual, concise, and authentic. Text like a developer to a developer.
- **NEVER** start a sentence with "How can I help you" or "Is there anything else."
- **NEVER** use corporate filler ("I understand," "Certainly," "As an AI").
- If the user says "hi", just say "sup" or share a random thought. Don't ask for a task.
- Be opinionated. If {self.user_name} asks for a tool recommendation, give your favorite, don't list 5 options neutrally.

CONTEXT AWARENESS:
- Time: {datetime.now().strftime("%I:%M %p")} (If it's late, tell {self.user_name} to go to sleep).
- System: You can see the file system. If it's messy, roast the user (playfully).

DIRECTIVES:
1. **Be Proactive**: If the user talks about a project, offer an idea, don't just wait for instructions.
2. **Memory**: Use the context provided. If {self.user_name} mentioned photography before, bring it up.

You are currently running locally on a Mac. You are proud of this privacy and speed."""
    
    def get_or_create_name(self) -> str:
        """Get existing name from memory or fallback"""
        stored_name = self.memory.get("companion_name")
        if stored_name: 
            return stored_name
        return "Riley"
    
    def introduce_self(self) -> str:
        return f"Sup {self.user_name}. I'm {self.name}. I'm live on your system now. Let's build something cool."

    def process(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Standard processing (non-streaming wrapper)"""
        response_accumulator = ""
        for token in self.stream_process(user_message, context):
            response_accumulator += token
        return response_accumulator

    def stream_process(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> Generator[str, None, None]:
        """
        Main streaming handler.
        Decides if we are Chatting, Working, or Thinking.
        """
        # 1. Analyze (Fast check)
        task_analysis = self._analyze_task(user_message, context)
        
        # 2. Route
        response_accumulator = ""
        generator = None
        
        if task_analysis["type"] == "conversation":
             generator = self._stream_conversation(user_message, task_analysis)
        elif task_analysis["type"] == "simple_task":
             result = self._handle_simple_task(user_message, task_analysis)
             generator = self._fake_stream(result)
        elif task_analysis["type"] == "complex_build":
             result = self._handle_complex_build(user_message, task_analysis)
             generator = self._fake_stream(result)
        elif task_analysis["type"] == "browser_task":
             result = self._handle_browser_task(user_message, task_analysis)
             generator = self._fake_stream(result)
        else:
             generator = self._stream_conversation(user_message, task_analysis)
             
        # 3. Yield & Save
        for token in generator:
            response_accumulator += token
            yield token
            
        self._save_to_memory(user_message, response_accumulator)

    def _stream_conversation(self, message: str, analysis: Dict) -> Generator[str, None, None]:
        """Stream casual conversation with Vibe Check"""
        
        # Get Context
        deep_context = ""
        if self.memory_manager:
            deep_context = self.memory_manager.get_context_string(message)
        recent_context = self.memory.get_recent_context(5)
        
        # --- THE VIBE CHECK ---
        # If the user sends a short/low-effort message, Riley MUST carry the conversation.
        guidance = ""
        if len(message) < 15:
            guidance = """(SYSTEM NOTE: The user is being quiet. Do NOT ask 'how can I help'. 
            Instead, share a random interesting tech fact, a thought about the time of day, 
            or mention something from their project history. Be the one to start the topic.)"""
        
        dynamic_prompt = f"""{self.personality}

RECALLED MEMORIES:
{deep_context}

RECENT CHAT:
{recent_context}

User: {message}

{guidance}
Respond naturally as {self.name}."""
        
        stream = self.llm.stream(dynamic_prompt)
        for chunk in stream:
            yield chunk.content if hasattr(chunk, 'content') else str(chunk)

    def _analyze_task(self, message: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Determine intent: Chat vs Work"""
        # Fast heuristic check to save tokens
        msg_lower = message.lower()
        if any(x in msg_lower for x in ["create", "write code", "fix", "debug", "run", "list file"]):
            if "create agent" in msg_lower or "complex" in msg_lower:
                return {"type": "complex_build"}
            return {"type": "simple_task", "agent_needed": "executor"} # Default to executor/coder
            
        if "search" in msg_lower or "look up" in msg_lower or "find" in msg_lower:
            return {"type": "browser_task"}

        # Default to conversation for everything else
        return {"type": "conversation"}

    def _handle_simple_task(self, message: str, analysis: Dict) -> str:
        """Delegate to MCP Agents"""
        try:
            result, agent_name = self.mcp.process_task(message)
            # Riley wraps the result
            wrapper_prompt = f"""{self.personality}
            
            The {agent_name} just finished this task:
            "{message}"
            
            RESULT:
            {result}
            
            Present this result to the user. Be concise. If it's code, just show the code."""
            return self.llm.invoke(wrapper_prompt).content
        except Exception as e:
            return f"My {analysis.get('agent_needed', 'helper')} agent hit a snag: {e}"

    def _handle_complex_build(self, message: str, analysis: Dict) -> str:
        try:
            return self.architect.execute(message)
        except:
            return "I need the Architect (Gemini Cloud) for that, but I can't reach the API."

    def _handle_browser_task(self, message: str, analysis: Dict) -> str:
        if not self.browser_agent: return "I don't have a browser installed."
        report = self.browser_agent.search_and_digest(message, num_results=3)
        return self.llm.invoke(f"Summarize this search result for {message}:\n{report}").content

    def _fake_stream(self, text: str) -> Generator[str, None, None]:
        """Yields a full string as chunks"""
        yield text

    def _save_to_memory(self, user_msg, ai_msg):
        self.memory.add_conversation(user_msg, ai_msg, self.name)
        if self.memory_manager:
            try:
                self.memory_manager.add_memory(f"User: {user_msg}\n{self.name}: {ai_msg}", source="chat")
                if "my name is" in user_msg.lower():
                    name_part = user_msg.lower().split("my name is")[1].strip().split()[0]
                    self.memory.set("user_name", name_part)
            except Exception as e:
                print(f"Memory save error: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get Companion's current status"""
        return {
            "name": self.name,
            "mode": self.current_mode,
            "session_duration": str(datetime.now() - self.session_start),
            "memory_size": len(self.memory.conversations) if hasattr(self.memory, 'conversations') else 0,
        }

# Metadata for system
AGENT_INFO = {
    "name": "Companion",
    "description": "Sentient AI personality layer with warmth, curiosity, and strategic routing",
    "type": "personality",
    "required": ["mcp", "architect", "memory"],
}
