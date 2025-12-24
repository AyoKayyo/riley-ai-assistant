import pandas as pd
from langchain_ollama import ChatOllama

class NUMBERSAgent:
    def __init__(self, llm):
        self.llm = llm
        self.role = "Expert CPA and Financial Analyst"
        self.goal = "Help you organize personal and business finances"

    def execute(self, task) -> str:
        if 'file_ops' in task:
            # Handle file operations (e.g., reading CSV)
            data = pd.read_csv(task['file_path'])
            return self.analyze_financial_data(data)

        elif 'web_search' in task:
            # Perform web search
            result = tools.web_search(task['query'])
            return f"Search Result:\n{result}"

        elif 'coding' in task:
            # Format code blocks
            code_snippet = task['code']
            formatted_code = f"