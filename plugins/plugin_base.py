"""
Plugin Base Class - Template for creating custom agents/plugins
"""
from abc import ABC, abstractmethod
from agents.memory import MemorySystem

class AgentPlugin(ABC):
    """
    Base class for all agent plugins
    Inherit from this to create custom agents
    """
    
    def __init__(self, llm):
        self.llm = llm
        self.memory = MemorySystem()
        self.name = "BasePlugin"
        self.description = "Base plugin description"
        self.capabilities = []
    
    @abstractmethod
    def execute(self, task: str, **kwargs) -> str:
        """
        Execute the plugin's main function
        Must be implemented by subclass
        """
        pass
    
    def can_handle(self, task: str) -> bool:
        """
        Determine if this plugin can handle the given task
        Override for custom logic
        """
        return any(keyword in task.lower() for keyword in self.capabilities)
    
    def get_service_config(self, service_name: str) -> dict:
        """Get configuration for external service from memory"""
        return self.memory.get_service_config(service_name)
    
    def save_to_memory(self, key: str, value: any):
        """Save data to persistent memory"""
        self.memory.set_context(f"{self.name}_{key}", value)
    
    def get_from_memory(self, key: str, default=None):
        """Retrieve data from persistent memory"""
        return self.memory.get_context(f"{self.name}_{key}", default)


# Example plugin implementations:

class WordPressPlugin(AgentPlugin):
    """
    WordPress management plugin
    Handles SEO analysis, post management, etc.
    """
    
    def __init__(self, llm):
        super().__init__(llm)
        self.name = "WordPress"
        self.description = "WordPress site management and SEO"
        self.capabilities = ['wordpress', 'wp', 'seo', 'post', 'page']
        
        # Get WordPress credentials from memory
        self.wp_config = self.get_service_config('wordpress')
    
    def execute(self, task: str, **kwargs) -> str:
        """Execute WordPress-related tasks"""
        if 'seo' in task.lower():
            return self.analyze_seo()
        elif 'post' in task.lower():
            return self.manage_posts(task)
        else:
            return self.general_wp_task(task)
    
    def analyze_seo(self) -> str:
        """Analyze WordPress site SEO"""
        site_url = self.wp_config.get('site_url', 'Not configured')
        
        prompt = f"""Analyze the SEO for WordPress site: {site_url}

Provide recommendations for:
1. Meta tags
2. Content optimization
3. Performance improvements
4. Schema markup"""
        
        response = self.llm.invoke(prompt)
        return f"🔍 SEO Analysis for {site_url}\n\n{response.content}"
    
    def manage_posts(self, task: str) -> str:
        """Manage WordPress posts"""
        # In a real implementation, this would use WP REST API
        return f"📝 WordPress Post Management\n\nTask: {task}\n\nNote: Configure WordPress API in .env to enable full functionality"
    
    def general_wp_task(self, task: str) -> str:
        """Handle general WordPress tasks"""
        prompt = f"""You are a WordPress expert. Help with this task:

{task}

Provide detailed guidance."""
        
        response = self.llm.invoke(prompt)
        return response.content


class PhotographyPlugin(AgentPlugin):
    """
    Photography business assistant plugin
    Handles photo metadata, SEO keywords, client management
    """
    
    def __init__(self, llm):
        super().__init__(llm)
        self.name = "Photography"
        self.description = "Photography business assistant"
        self.capabilities = ['photo', 'image', 'camera', 'exif', 'portfolio', 'client']
    
    def execute(self, task: str, **kwargs) -> str:
        """Execute photography-related tasks"""
        image_path = kwargs.get('image_path')
        
        if 'metadata' in task.lower() or 'exif' in task.lower():
            return self.analyze_metadata(image_path)
        elif 'seo' in task.lower() or 'keyword' in task.lower():
            return self.suggest_seo_keywords(task, image_path)
        elif 'client' in task.lower():
            return self.client_management(task)
        else:
            return self.general_photography_task(task)
    
    def analyze_metadata(self, image_path: str) -> str:
        """Analyze photo EXIF metadata"""
        if not image_path:
            return "❌ No image provided for metadata analysis"
        
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS
            
            img = Image.open(image_path)
            exif = img._getexif()
            
            if not exif:
                return "No EXIF data found in image"
            
            metadata = {}
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                metadata[tag] = str(value)
            
            # Format nicely
            result = "📷 Photo Metadata:\n\n"
            for key, value in sorted(metadata.items()):
                result += f"- **{key}**: {value}\n"
            
            return result
        except Exception as e:
            return f"❌ Error analyzing metadata: {str(e)}"
    
    def suggest_seo_keywords(self, task: str, image_path: str = None) -> str:
        """Suggest SEO keywords for photography"""
        context = ""
        if image_path:
            context = f"\nImage file: {image_path}"
        
        prompt = f"""You are an SEO expert for photography websites. 

Task: {task}{context}

Provide:
1. SEO-optimized title
2. Alt text for accessibility
3. Meta description
4. 10 relevant keywords
5. Long-tail keyword suggestions

Focus on: photography, portraits, family photos, professional photography"""
        
        response = self.llm.invoke(prompt)
        return f"🎯 SEO Recommendations\n\n{response.content}"
    
    def client_management(self, task: str) -> str:
        """Handle client-related tasks"""
        prompt = f"""You are a photography business assistant. Help with this client-related task:

{task}

Provide professional, friendly response."""
        
        response = self.llm.invoke(prompt)
        return f"👥 Client Management\n\n{response.content}"
    
    def general_photography_task(self, task: str) -> str:
        """Handle general photography tasks"""
        prompt = f"""You are a professional photography consultant. Help with:

{task}"""
        
        response = self.llm.invoke(prompt)
        return response.content


class APIConnectorPlugin(AgentPlugin):
    """
    Generic API connector plugin
    Connect to any REST API
    """
    
    def __init__(self, llm):
        super().__init__(llm)
        self.name = "APIConnector"
        self.description = "Connect to external APIs"
        self.capabilities = ['api', 'rest', 'http', 'webhook']
    
    def execute(self, task: str, **kwargs) -> str:
        """Execute API-related tasks"""
        import requests
        
        # This is a template - customize based on your needs
        api_name = kwargs.get('api_name', 'generic')
        config = self.get_service_config(api_name)
        
        if not config:
            return f"❌ API '{api_name}' not configured. Add to .env or register in memory."
        
        # Example API call
        try:
            # response = requests.get(config['endpoint'], headers={'Authorization': f"Bearer {config['api_key']}"})
            # data = response.json()
            # Process with LLM...
            
            return f"🔌 API Connector\n\nConnected to: {api_name}\n\nNote: Customize this plugin for your specific API"
        except Exception as e:
            return f"❌ API Error: {str(e)}"
