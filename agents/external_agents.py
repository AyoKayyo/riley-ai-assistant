"""
External Agent Integrations
Connect to Claude, ChatGPT, Gemini, and any API
"""
import os
from abc import ABC, abstractmethod
import requests

class ExternalAgent(ABC):
    """Base class for external AI service agents"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.name = "External"
        self.cost_per_1k_tokens = 0
        self.usage_count = 0
    
    @abstractmethod
    def execute(self, task: str, **kwargs) -> str:
        pass
    
    def track_usage(self):
        """Track how many times this agent is used"""
        self.usage_count += 1


class ClaudeAgent(ExternalAgent):
    """
    Anthropic Claude integration
    Best for: Deep reasoning, coding, analysis
    """
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.name = "Claude"
        self.model = "claude-3-5-sonnet-20241022"
        self.cost_per_1k_tokens = 0.003  # $3 per million tokens
        self.endpoint = "https://api.anthropic.com/v1/messages"
    
    def execute(self, task: str, **kwargs) -> str:
        """Execute with Claude"""
        self.track_usage()
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        data = {
            "model": self.model,
            "max_tokens": kwargs.get('max_tokens', 4096),
            "messages": [
                {"role": "user", "content": task}
            ]
        }
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['content'][0]['text']
        except Exception as e:
            return f"❌ Claude Error: {str(e)}\nCheck your API key in Settings."


class ChatGPTAgent(ExternalAgent):
    """
    OpenAI ChatGPT integration
    Best for: Fast responses, general tasks
    """
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.name = "ChatGPT"
        self.model = "gpt-4o"
        self.cost_per_1k_tokens = 0.005
        self.endpoint = "https://api.openai.com/v1/chat/completions"
    
    def execute(self, task: str, **kwargs) -> str:
        """Execute with ChatGPT"""
        self.track_usage()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": task}
            ],
            "max_tokens": kwargs.get('max_tokens', 4096)
        }
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"❌ ChatGPT Error: {str(e)}\nCheck your API key in Settings."


class PerplexityAgent(ExternalAgent):
    """
    Perplexity AI integration
    Best for: Research with citations, up-to-date info
    """
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.name = "Perplexity"
        self.model = "llama-3.1-sonar-large-128k-online"
        self.cost_per_1k_tokens = 0.001
        self.endpoint = "https://api.perplexity.ai/chat/completions"
    
    def execute(self, task: str, **kwargs) -> str:
        """Execute with Perplexity"""
        self.track_usage()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": task}
            ]
        }
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            
            # Perplexity returns citations
            answer = result['choices'][0]['message']['content']
            citations = result.get('citations', [])
            
            if citations:
                answer += "\n\n📚 **Sources:**\n"
                for i, citation in enumerate(citations[:5], 1):
                    answer += f"{i}. {citation}\n"
            
            return answer
        except Exception as e:
            return f"❌ Perplexity Error: {str(e)}\nCheck your API key in Settings."


class GeminiAgent(ExternalAgent):
    """
    Google Gemini integration
    Best for: Multimodal (text + images), Google ecosystem
    """
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.name = "Gemini"
        self.model = "gemini-2.0-flash-exp"
        self.cost_per_1k_tokens = 0.00025
        self.endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
    
    def execute(self, task: str, **kwargs) -> str:
        """Execute with Gemini"""
        self.track_usage()
        
        url = f"{self.endpoint}?key={self.api_key}"
        
        data = {
            "contents": [{
                "parts": [{"text": task}]
            }]
        }
        
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            return f"❌ Gemini Error: {str(e)}\nCheck your API key in Settings."


class CustomAPIAgent(ExternalAgent):
    """
    Custom API integration
    For any other service
    """
    
    def __init__(self, api_key: str, endpoint: str, name: str = "Custom"):
        super().__init__(api_key)
        self.name = name
        self.endpoint = endpoint
    
    def execute(self, task: str, **kwargs) -> str:
        """Execute with custom API"""
        self.track_usage()
        
        # Generic implementation - customize per service
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "prompt": task,
            **kwargs
        }
        
        try:
            response = requests.post(self.endpoint, headers=headers, json=data)
            response.raise_for_status()
            return response.text
        except Exception as e:
            return f"❌ {self.name} Error: {str(e)}"


# Agent registry
AVAILABLE_AGENTS = {
    'architect': {
        'class': None,  # Special - loaded separately
        'name': '🏗️ Gemini Architect',
        'description': 'YOUR personal system architect. Builds entire features, makes architecture decisions, and handles complex multi-file projects with strategic thinking. This is Gemini integrated with full authority!',
        'icon': '🏗️',
        'requires': ['api_key'],
        'env_key': 'GEMINI_API_KEY',
        'special': True,  # Elevated permissions
        'safety_level': 'yellow'  # Execute + notify
    },
    'claude': {
        'class': ClaudeAgent,
        'name': 'Claude (Anthropic)',
        'description': 'Best for deep reasoning, coding, and complex analysis',
        'icon': '🧠',
        'requires': ['api_key'],
        'env_key': 'ANTHROPIC_API_KEY'
    },
    'chatgpt': {
        'class': ChatGPTAgent,
        'name': 'ChatGPT (OpenAI)',
        'description': 'Fast, reliable, great for general tasks',
        'icon': '💬',
        'requires': ['api_key'],
        'env_key': 'OPENAI_API_KEY'
    },
    'perplexity': {
        'class': PerplexityAgent,
        'name': 'Perplexity AI',
        'description': 'Research with citations and up-to-date information',
        'icon': '🔍',
        'requires': ['api_key'],
        'env_key': 'PERPLEXITY_API_KEY'
    },
    'gemini': {
        'class': GeminiAgent,
        'name': 'Gemini (Google)',
        'description': 'Multimodal AI, great for images and Google integration',
        'icon': '✨',
        'requires': ['api_key'],
        'env_key': 'GOOGLE_API_KEY'
    },
    'custom': {
        'class': CustomAPIAgent,
        'name': 'Custom API',
        'description': 'Connect any custom API endpoint',
        'icon': '🔌',
        'requires': ['api_key', 'endpoint', 'name'],
        'env_key': None
    }
}

