"""
Coder Agent - Handles code generation, debugging, and code-related tasks
"""

class CoderAgent:
    """
    Specialized agent for coding and programming tasks
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.role = "Software Engineer"
        self.goal = "Write clean, efficient, and well-documented code"
    
    def execute(self, task: str) -> str:
        """
        Execute a coding task
        """
        coding_prompt = f"""You are an expert software engineer. Complete the following coding task:

Task: {task}

Provide:
1. Clean, well-commented code
2. Explanation of how it works
3. Usage examples if applicable

Format your response with code blocks using ```language``` syntax."""

        try:
            response = self.llm.invoke(coding_prompt)
            return response.content
        except Exception as e:
            return f"❌ Error during code generation: {str(e)}"
