#!/usr/bin/env python3
"""
Example: Using the Research Agent
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from agents.researcher import ResearchAgent

load_dotenv()

# Initialize LLM
llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    temperature=0.7,
)

# Initialize Research Agent
researcher = ResearchAgent(llm)

# Test research task
print("🔍 Testing Research Agent")
print("=" * 60)
result = researcher.execute("What are the latest trends in AI for 2024?")
print(f"\n📊 Research Result:\n{result}")
