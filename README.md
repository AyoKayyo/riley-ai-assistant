# Riley AI Assistant 🤖

> **Local LLM-powered AI companion with a tech-savvy roommate personality**

[![Status](https://img.shields.io/badge/status-stable-green.svg)](https://github.com/AyoKayyo/riley-ai-assistant)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Riley is a conversational AI assistant that runs **100% locally** on your Mac using Ollama and open-source LLMs. She acts like a tech-savvy roommate rather than a corporate assistant - casual, opinionated, and genuinely helpful.

---

## ✨ Features

### 🧠 **AI Companion with Personality**
- **Riley** - Powered by `llama3.1:8b`, she talks like a friend, not a bot
- No corporate speak ("How can I help?") - just natural conversation
- Remembers your preferences and conversation history
- **Response time:** 3-4 seconds (instant feedback)

### 🛠️ **Powerful Local Agents**
- **Code Generator** - 8 languages with syntax highlighting
- **Research Tool** - Web search with markdown export
- **Terminal** - Execute commands with history (↑/↓ arrows)
- **Vision** - Analyze images (LLaVA model)
- **Browser Agent** - Automated web tasks

### 🎨 **Clean, Modern UI**
- Pure black & white design
- Chat-style interface
- File attachments (PDF, images, text)
- Settings panel for configuration
- System monitor (CPU, RAM, Disk)

### 🔒 **Privacy-First**
- Runs 100% offline (except optional cloud agents)
- All data stays on your Mac
- No telemetry, no tracking
- Optional Gemini "Architect" mode for strategic tasks

---

## 🚀 Quick Start

### Prerequisites
- macOS (tested on M-series Macs)
- Python 3.12+
- [Ollama](https://ollama.com) installed

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/AyoKayyo/riley-ai-assistant.git
cd riley-ai-assistant
```

2. **Set up Python environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Download AI models:**
```bash
ollama pull llama3.1:8b      # Riley's brain
ollama pull qwen2.5-coder:7b # Coding expert
ollama pull llava:7b         # Vision (optional)
```

4. **Configure environment:**
```bash
cp .env-example .env
# Edit .env if you want to add Gemini API key (optional)
```

5. **Launch Riley:**
```bash
python command_center_ui.py
```

That's it! Riley should appear in a clean black window.

---

## 📖 Usage Guide

### Basic Chat
Just type naturally:
```
You: hey
Riley: sup. it's getting late, you still coding?

You: write me a fibonacci function
Riley: [generates Python code with explanation]
```

### Code Generator
1. Click **Code Generator** in sidebar
2. Select language (Python, JavaScript, etc.)
3. Describe what you want
4. Copy or save the generated code

### Research Tool
1. Click **Research**
2. Enter search query
3. Get web results with citations
4. Export as Markdown

### Terminal
1. Click **Python/Terminal**
2. Type commands (e.g., `ls -la`)
3. View output in green terminal
4. Use ↑/↓ for command history

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│        Riley AI Assistant           │
├─────────────────────────────────────┤
│                                     │
│  ┌──────────┐      ┌────────────┐  │
│  │   Riley  │◄────►│    MCP     │  │
│  │ (llama)  │      │ (Router)   │  │
│  └──────────┘      └──────┬─────┘  │
│                           │         │
│         ┌─────────────────┴──────┐ │
│         ↓                        ↓ │
│  ┌─────────────┐      ┌──────────┐│
│  │Local Agents │      │ Optional ││
│  ├─────────────┤      │ Cloud    ││
│  │• Coder      │      ├──────────┤│
│  │• Researcher │      │• Gemini  ││
│  │• Executor   │      │  Architect│
│  │• Vision     │      └──────────┘│
│  └─────────────┘                  │
│                                    │
│  [Memory] [Settings] [UI]         │
└────────────────────────────────────┘
```

---

## 🎯 What Makes Riley Different?

### NOT Your Typical AI Assistant
- ❌ No "How can I assist you today?"
- ❌ No overly formal responses
- ❌ No listing options robotically
- ✅ Casual, authentic conversation
- ✅ Has opinions and personality
- ✅ Proactive when you're quiet

### Example Conversation:
**Generic AI:**
> "I understand you'd like assistance with coding. I can help with Python, JavaScript, Java, C++, and many other languages. Which would you prefer?"

**Riley:**
> "yeah I can code. what language? I usually go with Python for quick stuff but your call"

---

## 📦 Project Structure

```
riley-ai-assistant/
├── command_center_ui.py       # Main application
├── agents/
│   ├── companion.py            # Riley's personality
│   ├── coder.py                # Code generation
│   ├── researcher.py           # Web search
│   ├── executor.py             # Command execution
│   └── gemini_architect.py     # Optional cloud agent
├── ui/
│   ├── code_generator.py       # Code gen UI
│   ├── research_panel.py       # Research UI
│   ├── terminal_widget.py      # Terminal UI
│   └── settings_dialog.py      # Settings
├── mcp/
│   └── core.py                 # Central router
├── tools/
│   └── web_search.py           # DuckDuckGo integration
└── memory/
    └── conversations.db        # Chat history (SQLite)
```

---

## ⚙️ Configuration

### Environment Variables (`.env`)
```bash
# Local LLM (Required)
OLLAMA_BASE_URL=http://localhost:11434
COMPANION_MODEL=llama3.1:8b
CODER_MODEL=qwen2.5-coder:7b

# Optional Cloud Agent
GEMINI_API_KEY=your_key_here   # For complex architecture tasks
```

### Models Used
| Model | Purpose | Size | When |
|-------|---------|------|------|
| `llama3.1:8b` | Riley (conversation) | 4.9GB | Always |
| `qwen2.5-coder:7b` | Code generation | 4.7GB | Code tasks |
| `llava:7b` | Image analysis | 4.7GB | Optional |

---

## 🐛 Troubleshooting

### "Model not found" error
```bash
# Download missing model
ollama pull llama3.1:8b
ollama list  # Verify it's there
```

### App won't start
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Restart virtual environment
source venv/bin/activate
python command_center_ui.py
```

### Slow responses (~20+ seconds)
- Check if deep memory (ChromaDB) is enabled
- Currently disabled by default for speed
- Response time should be 3-4 seconds

---

## 🔮 Roadmap

### Current Features ✅
- [x] Conversational AI with personality
- [x] Code generation (8 languages)
- [x] Web research with export
- [x] Terminal execution
- [x] Chat history database
- [x] Settings panel
- [x] File attachments

### Coming Soon 🚧
- [ ] Optimize deep memory (ChromaDB)
- [ ] Keyboard shortcuts (Cmd+K, Cmd+Enter)
- [ ] Drag-drop file upload
- [ ] Export conversations as Markdown
- [ ] Custom agent marketplace
- [ ] Voice input/output

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details

---

## 🤝 Contributing

This is a personal project, but suggestions and feedback are welcome! Open an issue if you find bugs or have ideas.

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM infrastructure
- **Qwen2.5-Coder** - Code generation model
- **Llama 3.1** - Conversational model
- **PyQt6** - UI framework
- **LangChain** - AI agent orchestration

---

## 📧 Contact

**Author:** Mark Kaough  
**Username:** [@AyoKayyo](https://github.com/AyoKayyo)

---

*Built with ❤️ for developers who want AI that feels human*
