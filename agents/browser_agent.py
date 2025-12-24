"""
God Mode Browser Agent - Autonomous Web Navigator
Uses browser-use + Playwright to control a real Chrome browser
Isolated module - if this crashes, Riley stays online
"""
import os
import asyncio
from browser_use import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class BrowserManager:
    """
    🌎 GOD MODE: Autonomous browser control
    Watches and controls a real Chrome browser to complete missions
    """
    
    def __init__(self):
        # Reuse existing Gemini API key (safe, already configured)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",  # Fast model for browser tasks
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.0  # Deterministic for reliable web navigation
        )
        print("✅ God Mode Browser initialized with Gemini 2.0 Flash")
    
    async def run_task(self, task_description: str):
        """
        Spawn autonomous browser agent to complete a mission
        
        Args:
            task_description: Natural language mission (e.g. "Find cheapest RTX 4090 on Amazon")
        
        Returns:
            Final result from browser agent
        """
        print(f"🌎 Browser Agent Mission: {task_description}")
        
        try:
            agent = Agent(
                task=task_description,
                llm=self.llm,
            )
            
            # headless=False means browser window is VISIBLE (God Mode)
            # User can watch the AI navigate in real-time
            result = await agent.run(headless=False)
            
            return result.final_result()
            
        except Exception as e:
            return f"❌ Browser mission failed: {str(e)}"
    
    def execute_sync(self, task: str) -> str:
        """
        Synchronous wrapper for PyQt integration
        Runs async browser agent from Qt event loop
        """
        try:
            return asyncio.run(self.run_task(task))
        except Exception as e:
            return f"❌ God Mode error: {str(e)}"


# Quick test function
if __name__ == "__main__":
    manager = BrowserManager()
    result = manager.execute_sync("Go to google.com and search for 'Playwright automation'")
    print(f"Result: {result}")
