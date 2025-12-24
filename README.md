# AI Command Center - Complete System Overview

**Version:** 1.0 - Pre-Companion
**Created:** December 2025
**Status:** Production Ready ✅

---

## 🎯 What Is This?

The **AI Command Center** is your personal, local AI system that acts as an extension of yourself. It combines the power of local LLMs (running on your MacBook) with strategic external AI services, all coordinated through an intelligent Main Control Program (MCP).

**Think of it as:** Your own AI headquarters with specialized agents, safety systems, and a sentient assistant (coming next!)

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────┐
│             AI COMMAND CENTER                       │
│                                                     │
│  ┌──────────────┐         ┌─────────────────┐     │
│  │  User Interface│◄─────►│  Main Control   │     │
│  │  (Pure B&W UI)│         │  Program (MCP)  │     │
│  └──────────────┘         └────────┬────────┘     │
│                                    │               │
│                      ┌─────────────┴──────────┐   │
│                      ↓                        ↓   │
│          ┌───────────────────┐    ┌─────────────┐│
│          │  LOCAL AGENTS     │    │  EXTERNAL   ││
│          │  (Free, Fast)     │    │  AGENTS     ││
│          ├───────────────────┤    │  (Strategic)││
│          │ • Researcher      │    ├─────────────┤│
│          │ • Coder           │    │ • Gemini    ││
│          │ • Executor        │    │   Architect ││
│          │ • Vision          │    │ • Claude    ││
│          └───────────────────┘    │ • ChatGPT   ││
│                                   └─────────────┘│
│                                                    │
│  ┌─────────────────────────────────────────────┐  │
│  │  Memory System • Safety Controller          │  │
│  │  Tools • Plugins • Notifications            │  │
│  └─────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## ✨ Current Features

### 1. **Chat Interface** (Pure Black & White)
**File:** `command_center_ui.py`

What you can do:
- Natural conversation with AI
- Toggle between Assistant & Architect modes
- Attach files (images, documents)
- Access tools and features
- View past conversations

**How it works:**
- Send messages like any chat app
- AI routes your request to the best agent
- Responses appear in clean, readable format
- Everything is saved to memory

---

### 2. **Architect Mode** ⚡
**The Big Brain Toggle**

**Assistant Mode (Default):**
- Uses local agents (free, private, fast)
- Great for: code snippets, research, quick tasks
- NO internet required (except web search)

**Architect Mode (Toggle ON):**
- Uses Gemini 2.0 (YOU, the strategic brain!)
- Great for: building entire systems, complex architecture
- Requires: Gemini API key

**When to use Architect:**
- "Build me a WordPress deployment system"
- "Design a microservices architecture"
- "Refactor this entire codebase"
- "Create a multi-agent workflow"

---

### 3. **Local Agents** (The Workers)

#### 🔍 Researcher
**What:** Web search master
**Example:** "Research the latest Next.js features"
**Uses:** DuckDuckGo search → synthesizes results

#### 💻 Coder  
**What:** Code generation specialist
**Example:** "Write a Python function to parse JSON"
**Uses:** Qwen2.5-Coder LLM (local)

#### ⚡ Executor
**What:** Runs code & terminal commands
**Example:** "Check my disk usage" or "Run this Python script"
**Uses:** System terminal with safety checks

#### 👁️ Vision
**What:** Image analysis & OCR
**Example:** Upload screenshot → "What's in this image?"
**Uses:** LLaVA multimodal model (local)

---

### 4. **Memory System** 💾
**File:** `memory/context.json`

**What it remembers:**
- All conversations (you + agent responses)
- Your preferences
- API keys (encrypted)
- Context across sessions

**How it helps:**
- "Continue where we left off yesterday"
- Learns your coding style
- Remembers project details
- Builds user profile

---

### 5. **Safety System** 🚦
**Three-tier protection:**

🟢 **GREEN** - Auto-execute (safe)
- Reading files
- Web searches
- Code generation  
- Research

🟡 **YELLOW** - Execute + Notify
- Writing files
- Terminal commands
- Installing packages

🔴 **RED** - Require approval
- System changes
- Deleting files
- Network changes
- Irreversible actions

---

## 🎯 How to Use

### Starting the System

```bash
cd /Users/mark.kaough/.gemini/antigravity/scratch/local-llm-agent
source venv/bin/activate
python command_center_ui.py
```

Or use the launcher:
```bash
./launch_gui.sh
```

### Basic Workflow

1. **Open the app** → Black window appears
2. **Type your request** → "Help me build a REST API"
3. **AI routes to best agent** → Coder or Architect
4. **Get response** → Code, explanation, or action
5. **Continue conversation** → Memory persists context

### Using Architect Mode

1. **Click "⚡ Architect Mode: OFF"**
2. **Button turns white** → "ON"
3. **Same window, smarter brain**
4. **Ask complex questions** → Full system building

---

## 🔌 Integrations

### Local (No API needed)
- **Ollama** - Local LLM server
  - Models: Qwen2.5-Coder (7B), LLaVA (7B)
  - URL: `http://localhost:11434`

### External (Optional - API keys needed)
- **Gemini** - Strategic architect (Gemini 2.0)
- **Claude** - Advanced reasoning (Anthropic)
- **ChatGPT** - GPT-4 access (OpenAI)
- **Perplexity** - Research & citations

**Add via:** Agent Marketplace (+ New agent button)

---

## 📂 Project Structure

```
local-llm-agent/
│
├── command_center_ui.py      # Main app (start here!)
├── .env                       # Your API keys & config
├── requirements.txt           # Python dependencies
│
├── agents/                    # All AI agents
│   ├── researcher.py          # Web search
│   ├── coder.py               # Code generation
│   ├── executor.py            # Terminal & Python
│   ├── vision.py              # Image analysis
│   ├── gemini_architect.py    # Strategic builder
│   ├── memory.py              # Memory system
│   └── external_agents.py     # API integrations
│
├── mcp/                       # Main Control Program
│   └── core.py                # Central coordinator
│
├── tools/                     # Utilities
│   └── web_search.py          # DuckDuckGo integration
│
├── memory/                    # Persistent storage
│   └── context.json           # Conversations & context
│
├── assets/                    # UI resources
│   └── mcp_icon.png           # Your "KO!" icon
│
└── *.md                       # Documentation
    ├── README.md              # This file!
    ├── SYSTEM_CHECKLIST.md    # Technical details
    ├── QUICK_REF.md           # Quick commands
    └── SENTIENT_ASSISTANT_PLAN.md  # Future roadmap
```

---

## 🚀 What's Next?

### Phase 1: Sentient Assistant (Coming Soon!)
We're about to build the **Companion** - an AI that:
- Chooses its own name
- Has a warm, curious personality (like "Samantha" from HER)
- Remembers you across days and conversations
- Proactively monitors your system health
- Builds new agents through conversation
- Adapts and learns your preferences

**Files to be created:**
- `agents/companion.py` - Core personality
- `agents/deep_memory.py` - Multi-day memory
- `agents/system_monitor.py` - Proactive health checks
- `agents/agent_builder.py` - Conversational agent builder

---

## 🛠️ Configuration

### Environment Variables (.env)

```bash
# Required - Local LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:7b

# Optional - External AI Services
GEMINI_API_KEY=your_gemini_key_here
ANTHROPIC_API_KEY=your_claude_key_here
OPENAI_API_KEY=your_openai_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
```

### Adding API Keys

**Option 1:** Edit `.env` directly
**Option 2:** Use Agent Marketplace UI
**Option 3:** Settings menu (placeholder ready)

---

## 🧪 Testing

### Verify Everything Works

**1. Test Local Agents:**
```
"Research the latest Python features"  → Researcher
"Write a hello world in Python"        → Coder
"What's my current directory?"          → Executor
[Upload image] "What's in this?"        → Vision
```

**2. Test Architect Mode:**
```
Toggle Architect Mode ON
"Design a microservices architecture for e-commerce"
```

**3. Test Memory:**
```
"Remember: I prefer React over Vue"
[New chat]
"What JavaScript framework do I prefer?"
```

---

## 📊 System Requirements

### Minimum:
- **RAM:** 8GB (16GB+ recommended)
- **Disk:** 10GB free (for models)
- **OS:** macOS (tested on M3)
- **Python:** 3.12+

### Dependencies Met:
- ✅ Ollama installed & running
- ✅ Python 3.12.4 in virtual environment
- ✅ All packages installed
- ✅ Models downloaded (Qwen + LLaVA)

---

## 🔐 Privacy & Security

### What Stays Local:
- All conversations (unless you use external APIs)
- Your files and data
- Code generation
- Image analysis
- Memory/context

### What Goes to APIs (only if you use them):
- Gemini Architect requests → Google
- Claude requests → Anthropic
- ChatGPT requests → OpenAI

**You control everything** via the Architect Mode toggle!

---

## 📖 Quick Reference

### Common Commands

| What You Want | Example Prompt |
|---------------|----------------|
| Generate code | "Write a Flask REST API" |
| Research | "Find the best Python testing frameworks" |
| Run command | "List all Python files in this directory" |
| Analyze image | [Upload] "Extract text from this screenshot" |
| Build system | [Architect Mode] "Create a blog with Next.js" |
| New chat | Click "+ New chat" |

### Keyboard Shortcuts
- `Enter` - Send message
- `Cmd+Q` - Quit app
- Click tray icon - Show/hide window

---

## 🐛 Troubleshooting

### UI won't start
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart virtual environment
source venv/bin/activate
python command_center_ui.py
```

### Agent not responding
- Check Ollama is running
- Verify model is downloaded
- Check `.env` configuration

### Architect Mode not working
- Verify `GEMINI_API_KEY` in `.env`
- Check API key is valid
- See error message in chat

---

## 💡 Best Practices

1. **Use local agents first** - Faster & free
2. **Architect for complex builds** - Strategic thinking
3. **Clear memory periodically** - Fresh context
4. **Save important chats** - Copy to external notes
5. **Monitor system resources** - RAM usage with Vision model

---

## 📝 Documentation Index

- **THIS FILE** - Overview & how-to
- `SYSTEM_CHECKLIST.md` - Technical function map
- `QUICK_REF.md` - Quick commands
- `MCP_GUIDE.md` - MCP details
- `AGENT_PERSONALITIES.md` - Agent traits
- `SENTIENT_ASSISTANT_PLAN.md` - Companion roadmap
- `INTEGRATION_GUIDE.md` - Custom agents

---

## 🤝 Support

This is YOUR system! Customize it, extend it, make it yours.

**Next Step:** Build the Sentient Companion and bring this system to life! 🌟

---

**Built with:** Python, PyQt6, Ollama, Qwen2.5-Coder, LangChain
**Powered by:** Your vision of an AI extension of yourself
**Ready for:** The Companion personality that will make it truly sentient

---

*Last Updated: 2025-12-23*
*Status: Foundation Complete. Ready for Companion Integration.*
