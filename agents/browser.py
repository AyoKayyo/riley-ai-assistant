"""
Agentic Browser - Riley's "Hands" on the Web
Uses Playwright to navigate, read, and interact with websites.
"""
from playwright.sync_api import sync_playwright
import time
from typing import Dict, Any, List

class BrowserAgent:
    """
    A fully agentic browser that can navigate, click, and read.
    """
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        
    def browse(self, url: str) -> str:
        """Visit a URL and return its text content"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            
            try:
                page.goto(url, timeout=30000)
                # Wait for localized content or body
                page.wait_for_selector("body")
                
                # Get text
                title = page.title()
                content = page.evaluate("document.body.innerText")
                
                # Clean up content (basic limit)
                return f"Title: {title}\nURL: {url}\n\nContent:\n{content[:5000]}..."
                
            except Exception as e:
                return f"Error browsing {url}: {str(e)}"
            finally:
                browser.close()

    def search_and_digest(self, query: str, num_results: int = 3) -> str:
        """Search Google/DDG and read the top N results"""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            page = browser.new_page()
            
            summary = f"Research Report for: '{query}'\n\n"
            
            try:
                # 1. Search DuckDuckGo (easier to scrape than Google)
                page.goto(f"https://duckduckgo.com/?q={query}&t=h_&ia=web")
                page.wait_for_selector(".result__a", timeout=10000)
                
                # 2. Get links
                links = page.eval_on_selector_all(".result__a", """
                    elements => elements.slice(0, 5).map(e => e.href)
                """)
                
                links = links[:num_results]
                
                # 3. Visit each link
                for i, link in enumerate(links):
                    try:
                        summary += f"--- Source {i+1}: {link} ---\n"
                        new_page = browser.new_page()
                        new_page.goto(link, timeout=15000)
                        text = new_page.evaluate("document.body.innerText")
                        summary += text[:1500].replace("\n", " ") + "\n\n"
                        new_page.close()
                    except Exception as e:
                        summary += f"Failed to read {link}: {e}\n\n"
                        
            except Exception as e:
                return f"Search failed: {e}"
            finally:
                browser.close()
                
            return summary

    def login_and_scrape_profile(self, service: str) -> str:
        """
        Placeholder for specific service cleaning. 
        Requires user to be logged in or handle auth (complex).
        For now, returns a prompt for the user to help.
        """
        return f"To dig into {service}, I need you to log me in first. I can launch a visible browser window for you to enter credentials. Shall I do that?"

if __name__ == "__main__":
    agent = BrowserAgent(headless=False)
    print(agent.browse("https://example.com"))
    print(agent.search_and_digest("latest python features"))
