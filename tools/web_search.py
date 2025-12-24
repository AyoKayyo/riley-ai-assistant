"""
Web Search Tool using DuckDuckGo
"""
from duckduckgo_search import DDGS

class DuckDuckGoSearch:
    """Tool for performing web searches without API keys"""
    
    def __init__(self):
        self.searcher = DDGS()
    
    def search(self, query: str, max_results: int = 5) -> str:
        """
        Perform a web search and return formatted results
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
        
        Returns:
            Formatted string with search results
        """
        try:
            results = list(self.searcher.text(query, max_results=max_results))
            
            if not results:
                return "No results found."
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                body = result.get('body', 'No description')
                url = result.get('href', '')
                
                formatted_results.append(f"{i}. {title}\n   {body}\n   URL: {url}\n")
            
            return "\n".join(formatted_results)
            
        except Exception as e:
            return f"Search error: {str(e)}"
