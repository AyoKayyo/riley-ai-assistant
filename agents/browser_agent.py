import os
import asyncio
from browser_use import Agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class BrowserManager:
    def __init__(self):
        # FORCE GEMINI 1.5 PRO
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-latest",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.0,
        )

    async def run_task(self, task_description: str):
        print(f"🌎 Browser Agent Starting: {task_description}")
        try:
            # Explicitly pass the LLM to the Agent
            agent = Agent(
                task=task_description,
                llm=self.llm,
            )
            # headless=False means you SEE the browser open
            result = await agent.run()
            return result.final_result()
        except Exception as e:
            return f"Browser Agent Error: {str(e)}"

    def execute_sync(self, task):
        """Helper to run async code from PyQt safely"""
        return asyncio.run(self.run_task(task))
