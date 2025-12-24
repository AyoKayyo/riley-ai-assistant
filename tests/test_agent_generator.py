
import os
import sys
from agents.gemini_architect import GeminiArchitectAgent
from agents.agent_generator import AgentGenerator

# Fake Architect for testing (mocks the LLM response)
class MockArchitect:
    def execute(self, prompt):
        return """
Here is the code:
```python
from langchain_ollama import ChatOllama

class TestAgent:
    def __init__(self, llm):
        self.llm = llm
        self.role = "Tester"
        self.goal = "To test things"
        
    def execute(self, task):
        return "Test complete"
```
"""

print("DEBUG: Testing AgentGenerator backend...")

# Use mock if no API key, or real if available
# For this test, we just want to prove the parsing logic works
architect = MockArchitect()
generator = AgentGenerator(architect)

result = generator.generate_agent(
    name="Test Agent",
    description="A simple test agent",
    capabilities=["none"]
)

print(f"DEBUG: Generated filename: {result['filename']}")
print(f"DEBUG: Generated class: {result['class_name']}")
print("DEBUG: Code snippet:")
print(result['code'][:100] + "...")

if "class TestAgent:" in result['code']:
    print("SUCCESS: Code parsing worked.")
else:
    print("FAILURE: Code parsing failed.")
