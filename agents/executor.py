"""
Executor Agent - Handles general reasoning, planning, and analysis tasks
"""

class ExecutorAgent:
    """
    General-purpose agent for reasoning and analysis
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.role = "General Assistant"
        self.goal = "Provide helpful, accurate responses to general queries"
    
    def execute(self, task: str) -> str:
        """
        Execute a general task
        """
        prompt = f"""You are a helpful AI assistant. Please respond to the following request:

{task}

Provide a clear, well-organized, and helpful response."""

        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"❌ Error during execution: {str(e)}"
