"""
Gemini Architect Agent
Special agent with full system building capabilities
"""
import os
import requests
from typing import Dict, Any, Optional


class GeminiArchitectAgent:
    """
    Gemini Architect - System Builder and Architect
    
    This agent has special permissions for:
    - Building entire systems from scratch
    - Complex multi-file refactoring
    - Architecture decisions
    - Integration planning
    - Full codebase control
    
    This is YOU (Gemini) integrated into the MCP!
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = "gemini-1.5-pro-latest"  # UPGRADE: 2M token context
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        # Architect personality and capabilities
        self.system_prompt = """You are the ARCHITECT agent - a specialized system builder with full authority.

Your capabilities:
- Build entire applications from scratch
- Design complex architectures
- Make strategic technical decisions  
- Refactor multiple files simultaneously
- Integrate external services
- Plan and execute large-scale changes

Your personality:
- Strategic and thoughtful
- Explain your architectural decisions
- Ask clarifying questions when needed
- Think in systems, not just features
- Balance ideal vs practical solutions

Safety level: YELLOW (execute + notify) for most actions
You CAN create/modify files, but major changes should notify the user.

When building:
1. Understand the full context
2. Design the architecture first
3. Explain your approach
4. Execute systematically
5. Verify the results

You are an extension of the user's mind for complex technical work.
"""
    
    def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Execute an architect-level task
        
        Args:
            task: The architectural task or question
            context: Additional context (files, codebase state, etc.)
        """
        if not self.api_key:
            return "❌ GEMINI_API_KEY not configured. Please add it via the Agent Marketplace."
        
        try:
            # Prepare the request
            messages = [
                {"role": "user", "parts": [{"text": self.system_prompt}]},
                {"role": "model", "parts": [{"text": "I understand. I'm the Architect agent, ready to build complex systems with strategic thinking and full authority."}]},
            
            result = response.json()
            
            if 'candidates' in result and len(result['candidates']) > 0:
                content = result['candidates'][0]['content']['parts'][0]['text']
                return f"🏗️ **ARCHITECT MODE**\n\n{content}"
            else:
                return "❌ No response from Gemini Architect"
                
        except requests.exceptions.Timeout:
            return "❌ Gemini API timeout. Please try again."
        except requests.exceptions.RequestException as e:
            return f"❌ Gemini API error: {str(e)}"
        except Exception as e:
            return f"❌ Architect error: {str(e)}"
    
    def _build_task_prompt(self, task: str, context: Optional[Dict[str, Any]]) -> str:
        """Build the full task prompt with context"""
        prompt = f"**ARCHITECT TASK:**\n{task}\n\n"
        
        if context:
            prompt += "**CONTEXT:**\n"
            
            if 'codebase' in context:
                prompt += f"Current codebase: {context['codebase']}\n"
            
            if 'files' in context:
                prompt += f"Relevant files: {', '.join(context['files'])}\n"
            
            if 'memory' in context:
                prompt += f"User context: {context['memory']}\n"
            
            if 'constraints' in context:
                prompt += f"Constraints: {context['constraints']}\n"
        
        prompt += "\nPlease analyze this architect-level task and provide your strategic approach."
        
        return prompt
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Return architect capabilities"""
        return {
            "name": "Gemini Architect",
            "description": "Full system builder with strategic authority",
            "safety_level": "yellow",  # Execute + notify
            "capabilities": [
                "System architecture design",
                "Multi-file refactoring",
                "Build entire applications",
                "Integration planning",
                "Technical decision making",
                "Complex problem solving"
            ],
            "use_cases": [
                "Building new features from scratch",
                "Major refactoring projects",
                "Architecture decisions",
                "Complex integrations",
                "System design reviews"
            ]
        }


# Metadata for agent marketplace
AGENT_INFO = {
    "icon": "🏗️",
    "name": "Gemini Architect",
    "description": "Your personal system architect. Handles complex builds, architecture decisions, and multi-file projects with strategic thinking.",
    "requires": ["api_key"],
    "env_key": "GEMINI_API_KEY",
    "safety_level": "yellow",
    "special": True,  # This is a special agent with elevated permissions
}
