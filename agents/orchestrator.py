"""
Orchestrator Agent - Manages and delegates tasks to sub-agents
"""
from typing import Dict, Any
from agents.researcher import ResearchAgent
from agents.coder import CoderAgent
from agents.executor import ExecutorAgent
from agents.vision import VisionAgent

class Orchestrator:
    """
    Main orchestrator that analyzes tasks and delegates to specialized sub-agents
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.sub_agents = {
            'researcher': ResearchAgent(llm),
            'coder': CoderAgent(llm),
            'executor': ExecutorAgent(llm),
            'vision': VisionAgent(llm),
        }
        
    def analyze_task(self, task: str) -> str:
        """
        Analyze the task and determine which sub-agent(s) should handle it
        """
        analysis_prompt = f"""You are an intelligent task orchestrator. Analyze the following task and determine which agent should handle it:

Available agents:
- researcher: For web searches, information gathering, and research tasks
- coder: For writing code, fixing bugs, or creating scripts
- executor: For general reasoning, planning, and analysis tasks

Task: {task}

Respond with ONLY ONE WORD - either 'researcher', 'coder', or 'executor'."""

        try:
            response = self.llm.invoke(analysis_prompt)
            agent_type = response.content.strip().lower()
            
            # Validate response
            if agent_type in self.sub_agents:
                return agent_type
            else:
                # Default to executor for general tasks
                return 'executor'
        except Exception as e:
            print(f"⚠️  Error analyzing task: {e}")
            return 'executor'  # Default fallback
    
    def process_task(self, task: str) -> str:
        """
        Process a task by delegating to the appropriate sub-agent
        """
        # Analyze which agent should handle this
        agent_type = self.analyze_task(task)
        agent = self.sub_agents[agent_type]
        
        print(f"🎯 Delegating to: {agent_type.capitalize()} Agent")
        
        # Execute with the selected agent
        result = agent.execute(task)
        
        return result
    
    def create_custom_agent(self, name: str, role: str, goal: str):
        """
        Create a custom sub-agent with specific role and goal
        This allows for dynamic agent creation
        """
        # Placeholder for custom agent creation
        # In a full implementation, this would dynamically create new agent types
        print(f"📝 Creating custom agent: {name}")
        print(f"   Role: {role}")
        print(f"   Goal: {goal}")
        return f"Custom agent '{name}' created successfully"
