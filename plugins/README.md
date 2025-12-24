# 🔌 Plugin System - Quick Start

## Create Your Own Custom Agent in 5 Minutes

The plugin system makes it dead simple to add specialized capabilities to your AI.

## 🚀 Quick Example

### 1. Import the Base Class

```python
from plugins.plugin_base import AgentPlugin

class MyCustomAgent(AgentPlugin):
    def __init__(self, llm):
        super().__init__(llm)
        self.name = "MyAgent"
        self.description = "What your agent does"
        self.capabilities = ['keyword1', 'keyword2']  # Trigger words
    
    def execute(self, task: str, **kwargs) -> str:
        # Your logic here
        response = self.llm.invoke(f"Help with: {task}")
        return response.content
```

### 2. Register Your Agent

In `agents/orchestrator.py`:

```python
from plugins.plugin_base import MyCustomAgent

# In __init__:
self.sub_agents['my_agent'] = MyCustomAgent(llm)
```

### 3. Use It!

Just mention your trigger keywords:
```
You: "keyword1 do something cool"
Agent: *delegates to MyCustomAgent*
```

## 📦 Pre-Built Plugins

### WordPress Plugin
**File**: `plugins/plugin_base.py` → `WordPressPlugin`

**Capabilities**:
- SEO analysis
- Post management
- Site optimization

**Setup**:
```python
# In .env
WORDPRESS_URL=https://yoursite.com
WORDPRESS_API_KEY=your_key

# Register
memory.register_external_service('wordpress', {
    'site_url': os.getenv('WORDPRESS_URL'),
    'api_key': os.getenv('WORDPRESS_API_KEY')
})
```

**Usage**:
```
"Analyze my WordPress site SEO"
"Create a blog post about photography"
```

### Photography Plugin
**File**: `plugins/plugin_base.py` → `PhotographyPlugin`

**Capabilities**:
- Photo EXIF analysis
- SEO keyword generation
- Client management

**Usage**:
```
Upload photo → "Generate SEO keywords"
"Analyze this photo's metadata"
"Draft email to client about wedding shoot"
```

### API Connector Plugin
**File**: `plugins/plugin_base.py` → `APIConnectorPlugin`

**Customize for ANY API**:
- Notion
- Google Drive
- Airtable
- Custom APIs

## 🎨 Real-World Example: Email Plugin

```python
from plugins.plugin_base import AgentPlugin
import smtplib
from email.mime.text import MIMEText

class EmailPlugin(AgentPlugin):
    def __init__(self, llm):
        super().__init__(llm)
        self.name = "Email"
        self.description = "Email management and drafting"
        self.capabilities = ['email', 'send', 'draft', 'reply']
        
        # Get email config from memory
        self.email_config = self.get_service_config('email')
    
    def execute(self, task: str, **kwargs) -> str:
        if 'draft' in task.lower():
            return self.draft_email(task)
        elif 'send' in task.lower():
            return self.send_email(task)
        else:
            return "Email plugin ready!"
    
    def draft_email(self, task: str) -> str:
        prompt = f"""Draft a professional email:

{task}

Keep it friendly but professional."""
        
        response = self.llm.invoke(prompt)
        
        # Save draft to memory for later
        self.save_to_memory('last_draft', response.content)
        
        return f"📧 Email Draft:\n\n{response.content}\n\n(Saved to memory)"
    
    def send_email(self, task: str) -> str:
        # Get last draft from memory
        draft = self.get_from_memory('last_draft')
        
        if not draft:
            return "No draft found. Draft an email first!"
        
        # In real implementation, send via SMTP
        return f"✅ Email sent!\n\n{draft}"
```

## 🔧 Plugin Features

### Built-in Methods

Every plugin inherits:

```python
# Memory
self.save_to_memory(key, value)  # Persist data
self.get_from_memory(key)        # Retrieve data

# Services
self.get_service_config('service_name')  # Get API keys, etc.

# LLM Access
self.llm.invoke(prompt)  # Use the local model

# Capabilities
self.can_handle(task)  # Auto-detect if plugin should handle task
```

### Task Routing

Your orchestrator automatically routes tasks based on `capabilities`:

```python
self.capabilities = ['photo', 'image']
```

Any task containing "photo" or "image" → routes to your plugin!

## 🎯 Plugin Ideas for YOU

### 1. Social Media Plugin
```python
class SocialMediaPlugin(AgentPlugin):
    # Generate posts
    # Schedule content
    # Analyze engagement
```

### 2. Analytics Plugin
```python
class AnalyticsPlugin(AgentPlugin):
    # Pull Google Analytics data
    # Generate reports
    # Suggest optimizations
```

### 3. Calendar Plugin
```python
class CalendarPlugin(AgentPlugin):
    # Schedule meetings based on conversations
    # Set reminders
    # Check availability
```

### 4. File Organizer Plugin
```python
class FileOrganizerPlugin(AgentPlugin):
    # Auto-organize downloads
    # Rename photos by date
    # Backup important files
```

## 🚀 Activating Plugins

### Method 1: Direct Registration

```python
# In agent_gui.py or main.py
from plugins.plugin_base import WordPressPlugin, PhotographyPlugin

# Add to orchestrator
orchestrator.sub_agents['wordpress'] = WordPressPlugin(llm)
orchestrator.sub_agents['photography'] = PhotographyPlugin(llm)
```

### Method 2: Auto-Discovery (Advanced)

```python
# Auto-load all plugins from plugins/ directory
import os
import importlib

def load_plugins(orchestrator, llm):
    plugin_dir = 'plugins'
    for file in os.listdir(plugin_dir):
        if file.endswith('.py') and not file.startswith('_'):
            module = importlib.import_module(f'plugins.{file[:-3]}')
            # Load plugin classes...
```

## 🎁 Next Steps

1. **Try a pre-built plugin**
   - Enable WordPressPlugin
   - Test PhotographyPlugin

2. **Create your first custom plugin**
   - Copy the template
   - Add your logic
   - Register it

3. **Build a workflow**
   - Chain multiple plugins
   - Create automation

Your AI command center is NOW infinitely extensible! 🔥
