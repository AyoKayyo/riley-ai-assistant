"""
Smart Orchestrator - Routes tasks to best available agent (local or external)
"""
from typing import Dict, Any, Optional
from agents.researcher import ResearchAgent
from agents.coder import CoderAgent
from agents.executor import ExecutorAgent
from agents.vision import VisionAgent
from agents.memory import MemorySystem


class SmartOrchestrator:
    """
    Intelligent orchestrator that picks the best agent for each task
    Supports both local and external agents
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.memory = MemorySystem()
        
        # Local agents (always available)
        self.local_agents = {
            'researcher': ResearchAgent(llm),
            'coder': CoderAgent(llm),
            'executor': ExecutorAgent(llm),
            'vision': VisionAgent(llm),
        }
        
        # External agents (loaded from memory)
        self.external_agents = {}
        self.load_external_agents()
    
    def load_external_agents(self):
        """Load external agents from memory"""
        from agents.external_agents import AVAILABLE_AGENTS
        
        for agent_id in AVAILABLE_AGENTS.keys():
            config = self.memory.get_service_config(f'agent_{agent_id}')
            if config and config.get('api_key'):
                try:
                    agent_class = AVAILABLE_AGENTS[agent_id]['class']
                    
                    if agent_id == 'custom':
                        self.external_agents[config.get('name', agent_id)] = agent_class(
                            config['api_key'],
                            config.get('endpoint', ''),
                            config.get('name', 'Custom')
                        )
                    else:
                        self.external_agents[agent_id] = agent_class(config['api_key'])
                    
                    print(f"✅ Loaded external agent: {agent_id}")
                except Exception as e:
                    print(f"⚠️ Could not load {agent_id}: {e}")
    
    def reload_agents(self):
        """Reload external agents (after adding new ones)"""
        self.external_agents = {}
        self.load_external_agents()
    
    def analyze_task(self, task: str) -> tuple[str, bool]:
        """
        Analyze task and return (agent_type, is_external)
        
        Returns:
            - ('coder', False) for local coder
            - ('claude', True) for external Claude
        """
        task_lower = task.lower()
        
        # Check if specific agent requested
        for ext_agent in self.external_agents.keys():
            if ext_agent in task_lower:
                return (ext_agent, True)
        
        # Intelligent routing based on task characteristics
        
        # Complex reasoning → Claude (if available)
        if any(word in task_lower for word in ['analyze', 'explain', 'reas on', 'complex', 'detail']):
            if 'claude' in self.external_agents:
                return ('claude', True)
        
        # Research with sources → Perplexity (if available)
        if any(word in task_lower for word in ['research', 'find', 'search', 'source', 'latest']):
            if 'perplexity' in self.external_agents:
                return ('perplexity', True)
            return ('researcher', False)
        
        # Coding tasks → local (fast) or ChatGPT
        if any(word in task_lower for word in ['code', 'function', 'script', 'program', 'debug', 'fix']):
            # Use local for privacy and speed
            return ('coder', False)
        
        # Default to fastest available
        if 'chatgpt' in self.external_agents:
            return ('chatgpt', True)
        
        return ('executor', False)
    
    def get_agent(self, agent_type: str, is_external: bool):
        """Get the actual agent instance"""
        if is_external:
            return self.external_agents.get(agent_type)
        else:
            return self.local_agents.get(agent_type)
    
    def process_task(self, task: str, **kwargs) -> tuple[str, str]:
        """
        Process task with best agent
        
        Returns:
            (result, agent_name)
        """
        agent_type, is_external = self.analyze_task(task)
        agent = self.get_agent(agent_type, is_external)
        
        if not agent:
            # Fallback to local executor
            agent = self.local_agents['executor']
            agent_type = 'executor'
            is_external = False
        
        agent_name = agent.name if hasattr(agent, 'name') else agent_type.capitalize()
        
        print(f"🎯 Using: {agent_name} ({'☁️ External' if is_external else '💻 Local'})")
        
        try:
            result = agent.execute(task, **kwargs)
            return (result, agent_name)
        except Exception as e:
            return (f"❌ Error with {agent_name}: {str(e)}", agent_name)
    
    def list_available_agents(self) -> Dict[str, str]:
        """List all available agents"""
        agents = {}
        
        # Local agents
        for name in self.local_agents.keys():
            agents[f"{name} (local)"] = "💻 Always available"
        
        # External agents
        for name, agent in self.external_agents.items():
            agents[f"{name} (external)"] = f"☁️ {agent.name}"
        
        return agents
