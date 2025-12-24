"""
Research Agent - Handles web searches and information gathering
"""
from tools.web_search import DuckDuckGoSearch

class ResearchAgent:
    """
    Specialized agent for research and information gathering tasks
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.search_tool = DuckDuckGoSearch()
        self.role = "Research Specialist"
        self.goal = "Gather accurate information from the web and provide comprehensive summaries"
    
    def execute(self, task: str) -> str:
        """
        Execute a research task
        """
        # First, perform web search
        print("🔍 Searching the web...")
        search_results = self.search_tool.search(task, max_results=5)
        
        # Then, use LLM to synthesize the information
        synthesis_prompt = f"""You are a research specialist. Based on the following web search results, provide a comprehensive answer to the task.

Task: {task}

Search Results:
{search_results}

Provide a clear, well-organized answer based on the search results."""

        try:
            response = self.llm.invoke(synthesis_prompt)
            return response.content
        except Exception as e:
            return f"❌ Error during research: {str(e)}\n\nRaw search results:\n{search_results}"
