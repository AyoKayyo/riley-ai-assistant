"""
Agent Generator - Uses Gemini Architect to build new local agents
"""
import os
import re
from typing import Dict, Any, Optional

class AgentGenerator:
    """
    Generates code for new local agents based on user description.
    Uses the Architect (Gemini) to ensure high-quality, bug-free code.
    """
    
    def __init__(self, architect_agent, local_llm=None):
        self.architect = architect_agent
        self.local_llm = local_llm
        self.output_dir = os.path.join(os.path.dirname(__file__), "..", "agents")
        
    def generate_agent(self, name: str, description: str, capabilities: list, model: str = "qwen2.5-coder:7b") -> Dict[str, str]:
        """
        Generate the Full Agent Code
        
        Returns:
            {
                "filename": "agents/my_agent.py",
                "code": "...",
                "class_name": "MyAgent",
                "tool_name": "my_agent"
            }
        """
        
        prompt = f"""You are an Expert Python Developer specializing in AI Agents.
        
TASK: Create a new Python file for a local AI Agent named '{name}'.

REQUIREMENTS:
1.  **Class Name**: {name.replace(' ', '')}Agent
2.  **Inheritance**: It usually doesn't need to inherit, but follows the pattern: `__init__(self, llm)` and `execute(self, task)`.
3.  **Dependencies**: 
    - `from langchain_ollama import ChatOllama` (if needed, though usually passed in)
    - Any standard library tools needed for `{description}`.
    - If external tools are needed (like `duckduckgo`), assume they might need install, but try to use standard libs or existing tools if possible.
4.  **Structure**:
    - `__init__(self, llm)`: Stores the LLM. Sets self.role and self.goal.
    - `execute(self, task) -> str`: The main entry point. 
5.  **Logic**:
    - It should construct a prompt for the LLM based on the task.
    - If `{capabilities}` implies web search, use `tools.web_search`.
    - If it implies coding, it should format code blocks.
    - Return a string response.

CONTEXT:
This agent is part of a local MCP system.
Description: {description}
Capabilities: {capabilities}
Model Hint: {model}

OUTPUT FORMAT:
Return ONLY the raw Python code. No markdown or explanation.
"""
        
        response = ""
        used_source = "Architect"
        
        # 1. Try Architect (Cloud)
        try:
            print(f"DEBUG: Generating agent '{name}' w/ Architect...")
            response = self.architect.execute(prompt)
            
            # Check for API Error strings masquerading as response
            if "Error:" in response or "400 Client Error" in response or "not configured" in response:
                raise Exception(f"Architect returned error: {response}")
                
        except Exception as e:
            print(f"WARN: Architect failed ({e}). Falling back to Local LLM.")
            used_source = "Local LLM"
            
            if self.local_llm:
                try:
                    # 2. Fallback to Local LLM
                    msg = self.local_llm.invoke(prompt)
                    response = msg.content
                except Exception as local_e:
                    raise Exception(f"Both Architect and Local LLM failed: {local_e}")
            else:
                raise Exception("Architect failed and no Local LLM provided.")
        
        # Clean response (remove markdown if present)
        code = self._clean_code(response)
        
        # VALIDATION: Ensure it looks like Python
        if "class " not in code or "def __init__" not in code:
             raise Exception(f"Generated text does not look like valid Python code. Source: {used_source}\nResponse: {response[:100]}...")
        
        # Determine filename
        safe_name = name.lower().replace(" ", "_").replace("-", "_")
        filename = f"{safe_name}.py"
        filepath = os.path.join(self.output_dir, filename)
        class_name = f"{name.replace(' ', '')}Agent"
        
        return {
            "name": name,
            "filename": filename,
            "filepath": filepath,
            "code": code,
            "class_name": class_name,
            "tool_name": safe_name
        }

    def save_agent(self, agent_data: Dict[str, str]) -> bool:
        """Save the generated code to disk"""
        try:
            with open(agent_data["filepath"], "w") as f:
                f.write(agent_data["code"])
            return True
        except Exception as e:
            print(f"Error saving agent: {e}")
            return False

    def _clean_code(self, text: str) -> str:
        """Strip markdown code blocks"""
        if "**ARCHITECT MODE**" in text:
            text = text.split("**ARCHITECT MODE**")[1]
            
        match = re.search(r"```python(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
            
        match = re.search(r"```(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
            
        return text.strip()
