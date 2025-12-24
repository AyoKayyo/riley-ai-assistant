# 🎯 MCP - Main Control Program

## Your AI Assistant's Brain

The MCP is the central command system that:
- Controls all sub-agents safely
- Prevents accidental damage
- Notifies you when needed
- Logs all actions

---

## 🛡️ Safety System

Every action your assistant takes is categorized:

### 🟢 GREEN - Auto-Execute
Safe actions that run automatically:
- Read files
- Search the web
- Analyze text
- Generate code
- Chat responses

### 🟡 YELLOW - Execute + Notify
Actions that run but notify you:
- Create files
- Browse websites  
- Send emails
- Modify files

### 🔴 RED - Require Approval
Dangerous actions that need your permission:
- Delete files/folders
- Run system commands
- Deploy websites
- Install software
- Access credentials

---

## 📱 Notification System

### iMessage Setup

1. **Set Your Phone Number:**
```python
# In your chat:
"Set my phone number to +1234567890"
```

2. **Enable iMessage:**
```python
"Enable iMessage notifications"
```

3. **Test It:**
```python
"Send me a test message"
```

### What You'll Get Notified About:

**GUI Notifications** (always on):
- Task completions
- Errors/warnings
- Approval requests

**iMessage** (optional):
- Critical approvals needed
- Long-running task completions
- Errors when you're away

---

## 🎮 Using the MCP

### Check Status
```
"What's your status?"
"Show me recent actions"
"Any pending approvals?"
```

### Configure Notifications
```
"Disable GUI notifications"
"Enable iMessage for errors only"
"Show me your configuration"
```

### Approve Actions
When you get an approval request:
```
"Approve action 0"
"Deny all pending"
"Show pending approvals"
```

### View Action Log
```
"Show last 10 actions"
"What did you do today?"
"Action history"
```

---

## 🔧 Configuration

### Config File: `memory/context.json`

```json
{
  "mcp_config": {
    "auto_notify_yellow": true,
    "auto_notify_complete": true,
    "gui_notifications": true,
    "imessage_notifications": false
  },
  "phone_number": "+1234567890"
}
```

### Change Settings:
```python
# In the GUI or use the command center
mcp.configure(
    auto_notify_yellow=False,  # Don't notify for yellow actions
    imessage_notifications=True  # Enable iMessage
)
```

---

## 🏗️ Architecture

```
MCP (Main Control Program)
│
├─ Safety Controller
│   ├─ Action Classifier (GREEN/YELLOW/RED)
│   ├─ Approval Queue
│   └─ Action Logger
│
├─ Notification System
│   ├─ iMessage (via AppleScript)
│   ├─ GUI Notifications
│   └─ In-App Alerts
│
└─ Sub-Agent Registry
    ├─ Browser Agent
    ├─ WordPress Builder
    ├─ Image Analyzer
    ├─ Code Generator
    ├─ Researcher
    └─ External Agents (Claude, ChatGPT, etc.)
```

---

## 🔥 Example Workflows

### Safe Workflow (All GREEN):
```
You: "Research Python web frameworks"
MCP: ✅ Auto-executes (GREEN)
     → Uses Researcher agent
     → Returns results
```

### Notification Workflow (YELLOW):
```
You: "Create a new file called test.py"
MCP: ✅ Executes
     🔔 Notifies you via GUI
     → File created
```

### Approval Workflow (RED):
```
You: "Delete all .log files"
MCP: 🔴 REQUIRES APPROVAL
     📱 Sends iMessage (if enabled)
     🔔 GUI notification
     ❓ "This will delete 47 files. Approve?"

You: "Approve"
MCP: ✅ Executes
     🔔 "47 files deleted"
```

---

## 🎯 Safety Examples

### What's Protected:

**File System:**
- ❌ Can't delete folders automatically
- ❌ Can't move important files
- ✅ Can create files with notification
- ✅ Can read any file

**System:**
- ❌ Can't run sudo commands
- ❌ Can't install software
- ❌ Can't modify system files
- ✅ Can check system status

**Network:**
- ❌ Can't deploy without approval
- ❌ Can't access credentials automatically
- ✅ Can browse websites with notification
- ✅ Can search web freely

**Your Data:**
- ❌ Can't delete database records
- ❌ Can't wipe memory
- ✅ Can add to memory
- ✅ Can query data

---

## 📊 Action Log

Everything is logged:

```python
{
  "action_type": "create_file",
  "description": "Created test.py",
  "safety_level": "notify",
  "timestamp": "2024-12-23T15:30:00",
  "approved": true,
  "executed": true
}
```

View history:
```
"Show me what you did in the last hour"
"Did you create any files today?"
"What actions needed approval this week?"
```

---

## 🚀 Next Steps

1. **Set your phone number** for iMessage
2. **Test the notification system**
3. **Review the action log** to understand what runs automatically
4. **Customize safety rules** if needed (advanced)

The MCP ensures your assistant is:
- ✅ Helpful
- ✅ Safe
- ✅ Transparent
- ✅ Under your control

**You're in charge. Always.** 🎯
