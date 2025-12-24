import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

class GeminiArchitectAgent:
    def __init__(self):
        # UPGRADE: Gemini 1.5 Pro (2M Context)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro-latest",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.3, # Low temp for precise architecture
            convert_system_message_to_human=True
        )

    def execute(self, task):
        system_prompt = """You are the ARCHITECT. You are a strategic technical genius.
        - You do not chit-chat.
        - You provide high-level architectural plans, code structures, and deep debugging.
        - You have a massive context window, so be thorough."""
        
        messages = [
            ("system", system_prompt),
            ("human", task)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
