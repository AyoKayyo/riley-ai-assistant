# 🔌 External Service Integration Guide

## Making Your Agent an Extension of YOU

Your AI Command Center can now connect to ANY external service or AI system. Here's how to integrate your existing tools and memories.

## 🧠 Built-in Memory System

Your agent now remembers:
- ✅ All conversations (last 100 stored)
- ✅ Context between sessions
- ✅ Patterns in your requests
- ✅ Custom configurations

### View Memory
Click the 💾 button in the app or ask: "What did we talk about earlier?"

## 🔗 Connect External Services

### Method 1: Add API Keys to Memory

```python
# Example: Connect to Notion
from agents.memory import MemorySystem

memory = MemorySystem()
memory.register_external_service('notion', {
    'api_key': 'your_notion_api_key',
    'database_id': 'your_database_id'
})
```

### Method 2: Create Custom Agents

Want to connect to WordPress, photography apps, or business tools?

**Example: WordPress Agent**

```python
# agents/wordpress_agent.py
import requests

class WordPressAgent:
    def __init__(self, llm):
        self.llm = llm
        self.memory = MemorySystem()
        
        # Get WP credentials from memory
        wp_config = self.memory.get_service_config('wordpress')
        self.site_url = wp_config.get('site_url')
        self.api_key = wp_config.get('api_key')
    
    def execute(self, task: str) -> str:
        # Analyze SEO, update posts, fetch analytics
        if 'seo' in task.lower():
            return self.analyze_seo()
        elif 'post' in task.lower():
            return self.create_post(task)
        # ... more  capabilities
```

## 🎯 Pre-Built Integration Examples

### 1. Connect to Claude/ChatGPT for Enhanced Analysis

```python
# agents/integrations/claude_integration.py
import anthropic

class ClaudeMemoryBridge:
    """Pull memories from Claude conversations"""
    def __init__(self, api_key):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def import_conversation(self, conversation_id):
        # Fetch conversation from Claude
        # Store in local memory
        pass
```

### 2. Photo Metadata Agent (for your business!)

```python
# agents/photo_agent.py
from PIL import Image
from PIL.ExifTags import TAGS

class PhotoAgent:
    """Analyze photo EXIF, suggest metadata, SEO keywords"""
    
    def execute(self, task: str, image_path: str) -> str:
        img = Image.open(image_path)
        exif = img._getexif()
        
        # Extract camera settings, dates, etc.
        metadata = {}
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            metadata[tag] = value
        
        # Use LLM to suggest SEO keywords
        prompt = f"""Based on this photo metadata:
{metadata}

Suggest SEO-friendly title, alt text, and keywords for a photography portfolio."""
        
        return self.llm.invoke(prompt).content
```

### 3. Google Drive / Cloud Storage

```python
# Store in .env
GOOGLE_DRIVE_API_KEY=your_key
GOOGLE_DRIVE_FOLDER_ID=your_folder

# agents/storage_agent.py
class StorageAgent:
    def upload_to_drive(file_path, folder='AI-Generated'):
        # Auto-organize your generated code/content
        pass
```

## 🌐 API Service Templates

### Add to `.env` file:

```env
# WordPress
WORDPRESS_URL=https://yoursite.com
WORDPRESS_API_KEY=wp_xxx

# Notion
NOTION_API_KEY=secret_xxx
NOTION_DATABASE_ID=xxx

# Claude
ANTHROPIC_API_KEY=sk-ant-xxx

# Any other service
SERVICE_NAME_API_KEY=xxx
```

### Register in Runtime:

```python
# In main.py or agent_gui.py
from agents.memory import MemorySystem

def setup_services():
    memory = MemorySystem()
    
    # WordPress
    memory.register_external_service('wordpress', {
        'url': os.getenv('WORDPRESS_URL'),
        'api_key': os.getenv('WORDPRESS_API_KEY')
    })
    
    # Your photography database
    memory.register_external_service('portfolio', {
        'photos_path': '/path/to/photos',
        'metadata_db': '/path/to/metadata.db'
    })
```

## 🎨 Use Cases for YOUR Business

### Photography Business Automation

1. **SEO Analysis Agent**
   - Scans your WordPress site
   - Analyzes competitors
   - Suggests improvements
  
2. **Photo Metadata Agent**
   - Batch-processes photos
   - Generates SEO-friendly descriptions
   - Suggests keywords

3. **Client Communication Agent**
   - Drafts email responses
   - Schedules follow-ups
   - Remembers client preferences

### Implementation Example

```python
# agents/photography_assistant.py
class PhotographyAssistant:
    """Your personal photography business assistant"""
    
    def __init__(self, llm):
        self.llm = llm
        self.memory = MemorySystem()
        self.wp_agent = WordPressAgent(llm)
        self.photo_agent = PhotoAgent(llm)
    
    def execute(self, task: str) -> str:
        # Delegate to specialized agents
        if 'seo' in task.lower():
            return self.wp_agent.analyze_seo()
        elif 'photo' in task.lower() or 'image' in task.lower():
            return self.photo_agent.process_photos()
        # ... more capabilities
```

## 🚀 Next Steps

1. **Register Your Services**
   - Add API keys to `.env`
   - Register in memory system

2. **Create Custom Agents**
   - Copy an existing agent as template
   - Add your specific logic
   - Register in orchestrator

3. **Build Workflows**
   - Chain multiple agents
   - Create automation scripts
   - Schedule recurring tasks

## 🔐 Security Note

- API keys stored in `.env` (gitignored)
- Memory file stored locally (`memory/context.json`)
- No data leaves your Mac unless you explicitly send it to external APIs

## 💡 Ideas for Integration

- **Email**: Auto-respond, draft emails
- **Calendar**: Schedule based on conversations
- **CRM**: Update client notes
- **Analytics**: Pull data, generate reports
- **Cloud Storage**: Auto-organize files
- **Social Media**: Draft posts, analyze engagement
- **Payment Processing**: Track invoices
- **Any REST API**: Integrate with HTTP requests

Your agent is now infinitely extensible! 🎉
