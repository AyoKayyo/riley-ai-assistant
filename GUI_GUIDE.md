# 🎨 GUI Menu Bar App - Quick Guide

## 🚀 Launch the GUI

**Easiest way:**
```bash
cd /Users/mark.kaough/.gemini/antigravity/scratch/local-llm-agent
./launch_gui.sh
```

This will:
1. Show a 🤖 icon in your menu bar (top right)
2. Open a beautiful floating chat window
3. Let you chat with your AI agent!

## 💡 How to Use

### Menu Bar Icon
- **Click icon** → Show/hide chat window
- **Right-click icon** → Menu with options:
  - Show Chat
  - Hide Chat
  - Quit

### Chat Window
- Type your question in the input field
- Press Enter or click "Send"
- Wait for the agent to respond
- The status bar shows which sub-agent is working

### Features
- ✨ Beautiful modern macOS design
- 🎯 Auto-delegates to specialized agents (Researcher, Coder, Executor)
- ⚡ Non-blocking - window stays responsive
- 🔝 Stays on top for easy access
- 📝 Full chat history in the window

## 🎨 What It Looks Like

```
┌─────────────────────────────────────┐
│       🤖 Local AI Agent            │
│            Ready                    │
├─────────────────────────────────────┤
│                                     │
│  🤖 Agent: Hello! I can help with...│
│                                     │
│  👤 You: Write a hello world       │
│                                     │
│  🤖 Agent: Here's a Python func... │
│                                     │
├─────────────────────────────────────┤
│ Ask me anything...     [Send]       │
└─────────────────────────────────────┘
```

## 🛠️ Keep It Running

The app will keep running in the background with the menu bar icon. You can:
- Hide the window and bring it back anytime
- Keep working while the agent thinks
- Quit from the menu bar menu when done

## 🔧 Troubleshooting

**Icon not showing?**
```bash
# Make sure Ollama is running
brew services info ollama

# If not, start it
brew services start ollama
```

**Window won't open?**
- Check terminal for error messages
- Make sure virtual environment is activated
- Try: `source venv/bin/activate && python agent_gui.py`

## ⚙️ Customization

Edit `agent_gui.py` to:
- Change window size (line 66: `setGeometry`)
- Modify colors (search for hex colors like `#2563eb`)
- Adjust fonts (search for `QFont`)
- Change welcome message (line 79-84)

## 🎯 Next Level

Want this to auto-start on login?
1. Open "System Settings" → "General" → "Login Items"
2. Click "+" and add `launch_gui.sh`

Or create a proper macOS app with:
```bash
pip install py2app
# Then I can help you build a .app bundle!
```
