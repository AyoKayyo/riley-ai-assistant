#!/usr/bin/env python3
"""
Main entry point for the Local LLM Agent System
"""
import os
import sys
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from agents.orchestrator import Orchestrator

load_dotenv()

def main():
    """Main function to run the agent system"""
    
    # Initialize the LLM
    llm = ChatOllama(
        model=os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b"),
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        temperature=0.7,
    )
    
    # Initialize the orchestrator
    orchestrator = Orchestrator(llm)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive" or sys.argv[1] == "-i":
            # Interactive mode
            print("🤖 Local LLM Agent System - Interactive Mode")
            print("=" * 60)
            print("Type 'exit', 'quit', or 'q' to quit")
            print("Type 'help' for usage information")
            print("=" * 60)
            
            while True:
                try:
                    user_input = input("\n👤 You: ").strip()
                    
                    if user_input.lower() in ['exit', 'quit', 'q']:
                        print("\n👋 Goodbye!")
                        break
                    
                    if user_input.lower() == 'help':
                        print("\n📚 Usage:")
                        print("  - Ask anything and the orchestrator will delegate to sub-agents")
                        print("  - Example: 'Research the top 3 Python web frameworks'")
                        print("  - Example: 'Create a Python script to sort a list'")
                        print("  - Example: 'Tell me about quantum computing'")
                        continue
                    
                    if not user_input:
                        continue
                    
                    # Process the task
                    print("\n🔄 Processing...")
                    result = orchestrator.process_task(user_input)
                    print(f"\n🤖 Agent: {result}")
                    
                except KeyboardInterrupt:
                    print("\n\n👋 Goodbye!")
                    break
                except Exception as e:
                    print(f"\n❌ Error: {str(e)}")
        
        elif sys.argv[1] == "--task" or sys.argv[1] == "-t":
            # Single task mode
            if len(sys.argv) < 3:
                print("❌ Error: Please provide a task")
                print("Usage: python main.py --task 'your task here'")
                sys.exit(1)
            
            task = " ".join(sys.argv[2:])
            print(f"🔄 Processing task: {task}")
            result = orchestrator.process_task(task)
            print(f"\n✅ Result:\n{result}")
        
        else:
            print("❌ Unknown option. Use --interactive or --task")
            print("Usage:")
            print("  python main.py --interactive")
            print("  python main.py --task 'your task here'")
            sys.exit(1)
    else:
        # Default: show usage
        print("🤖 Local LLM Agent System")
        print("\nUsage:")
        print("  Interactive mode: python main.py --interactive (or -i)")
        print("  Single task:      python main.py --task 'your task' (or -t)")
        print("\nExamples:")
        print("  python main.py -i")
        print("  python main.py -t 'Research quantum computing and summarize'")

if __name__ == "__main__":
    main()
