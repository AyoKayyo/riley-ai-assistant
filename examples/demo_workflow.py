#!/usr/bin/env python3
"""
Example: Complete Multi-Agent Workflow
Demonstrates orchestrator delegating to different agents
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from agents.orchestrator import Orchestrator

load_dotenv()

# Initialize LLM
llm = ChatOllama(
    model=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    temperature=0.7,
)

# Initialize Orchestrator
orchestrator = Orchestrator(llm)

# Test different types of tasks
tasks = [
    "Explain the difference between REST and GraphQL APIs",
    "Write a Python function to reverse a string",
    "Research the top 3 JavaScript frameworks in 2024",
]

print("🤖 Multi-Agent Workflow Demo")
print("=" * 60)

for i, task in enumerate(tasks, 1):
    print(f"\n📝 Task {i}: {task}")
    print("-" * 60)
    result = orchestrator.process_task(task)
    print(f"✅ Result:\n{result}\n")
    print("=" * 60)
