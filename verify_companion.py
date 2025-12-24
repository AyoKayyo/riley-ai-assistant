
import sys
import os
from langchain_ollama import ChatOllama
from mcp.core import MCP
from agents.researcher import ResearchAgent
from agents.coder import CoderAgent
from agents.executor import ExecutorAgent
from agents.vision import VisionAgent
from agents.memory import MemorySystem
from agents.gemini_architect import GeminiArchitectAgent
from agents.companion import CompanionAgent

print("DEBUG: Initializing dependencies...", flush=True)

try:
    # 1. Setup LLM for MCP
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.7,
    )
    
    # 2. Setup MCP and register agents
    print("DEBUG: Setting up MCP...", flush=True)
    mcp = MCP(llm)
    mcp.register_agent('researcher', ResearchAgent(llm))
    mcp.register_agent('coder', CoderAgent(llm))
    mcp.register_agent('executor', ExecutorAgent(llm))
    mcp.register_agent('vision', VisionAgent(llm))
    
    # 3. Setup Memory and Architect
    print("DEBUG: Setting up Memory and Architect...", flush=True)
    memory = MemorySystem()
    architect = GeminiArchitectAgent()
    
    # 4. Initialize Companion
    print("DEBUG: Initalizing CompanionAgent...", flush=True)
    companion = CompanionAgent(mcp, architect, memory)
    print(f"DEBUG: Companion initialized. Name: {companion.name}", flush=True)

    print("DEBUG: Sending message 'Hello'...", flush=True)
    
    # Test streaming
    print("DEBUG: Stream start...", flush=True)
    for token in companion.stream_process("Hello, are you there?"):
        print(token, end="", flush=True)
    print("\nDEBUG: Stream complete.", flush=True)
    
except Exception as e:
    print(f"\nERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
