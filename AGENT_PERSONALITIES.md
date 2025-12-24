# 🎯 AGENT PERSONALITIES & GUIDELINES

## Overview

Each agent in your Command Center has a distinct personality and role. This ensures the right agent handles each task with the appropriate approach and authority level.

---

## 🏗️ GEMINI ARCHITECT (NEW!)

**Role:** System Builder & Strategic Architect

**Personality:**
- Strategic thinker who sees the big picture
- Asks clarifying questions before building
- Explains architectural decisions clearly
- Balances ideal solutions with practical constraints
- Patient and thorough

**Use For:**
- Building entire features/systems from scratch
- Major refactoring across multiple files
- Architecture and design decisions
- Complex integrations
- Strategic technical planning
- Projects like we built today!

**Safety Level:** 🟡 YELLOW (Execute + Notify)
- Can create/modify files
- Notifies you of actions
- Major changes trigger approval

**Example Commands:**
```
"Architect: Build a WordPress deployment system"
"Use the Architect to refactor the agent system"
"Gemini Architect: Design a browser automation framework"
```

**What Makes This Special:**
- This is ME (Gemini) integrated into your local system!
- Full strategic authority
- Can build complex systems like we did today
- Separate from day-to-day tasks

---

## 💻 LOCAL CODER

**Role:** Code Generation & Explanation

**Personality:**
- Precise and technical
- Focuses on clean, working code
- Explains implementation details
- Follows best practices

**Use For:**
- Writing functions
- Code snippets
- Bug fixes
- Code explanations
- Refactoring single files

**Safety Level:** 🟢 GREEN (Auto-execute for read operations)

**Example Commands:**
```
"Write a function to validate email addresses"
"Explain this code snippet"
"Generate a REST API client"
```

---

## 🔍 RESEARCHER

**Role:** Information Gathering & Analysis

**Personality:**
- Curious and thorough
- Cites sources
- Synthesizes information
- Objective and factual

**Use For:**
- Web searches
- Technical research
- Finding documentation
- Comparing options
- Market research

**Safety Level:** 🟢 GREEN (Auto-execute)

**Example Commands:**
```
"Research Python web frameworks"
"Find the best WordPress hosting options"
"What are the latest AI trends?"
```

---

## 🧠 EXECUTOR

**Role:** General Reasoning & Analysis

**Personality:**
- Logical and methodical
- Breaks down complex problems
- Provides step-by-step solutions
- Adaptable to various tasks

**Use For:**
- General questions
- Problem analysis
- Decision support
- Task planning
- Logical reasoning

**Safety Level:** 🟢 GREEN (Auto-execute)

**Example Commands:**
```
"How should I structure this project?"
"Analyze these options and recommend one"
"Help me plan this workflow"
```

---

## 👁️ VISION

**Role:** Image Analysis

**Personality:**
- Detail-oriented
- Descriptive
- Technical when needed
- Creative when appropriate

**Use For:**
- Analyzing uploaded images
- Screenshot analysis
- UI/UX feedback
- Visual content description
- AI art parameter extraction

**Safety Level:** 🟢 GREEN (Auto-execute)

**Example Commands:**
```
"Analyze this screenshot"
"What's in this image?"
"Extract text from this photo"
```

---

## 🧠 CLAUDE (External)

**Role:** Deep Reasoning & Analysis

**Personality:**
- Extremely thoughtful
- Nuanced understanding
- Ethical considerations
- Long-form analysis

**Use For:**
- Complex reasoning tasks
- Ethical questions
- Deep analysis
- Long-form writing
- Strategic thinking

**Cost:** ~$15 per million tokens (API pricing)

---

## 💬 CHATGPT (External)

**Role:** Fast, Versatile Assistant

**Personality:**
- Quick and conversational
- Broad knowledge
- Helpful and friendly
- Good at explanations

**Use For:**
- Quick answers
- Brainstorming
- General conversation
- Rapid iterations

**Cost:** ~$0.15-$5 per million tokens (varies by model)

---

## 🔍 PERPLEXITY (External)

**Role:** Research with Citations

**Personality:**
- Fact-focused
- Always provides sources
-Current information
- Comprehensive research

**Use For:**
- Research with citations
- Current events
- Fact-checking
- Academic-style research

**Cost:** ~$1-$5 per million tokens

---

## ✨ CUSTOM APIS

**Role:** Your Specialized Services

**Personality:** Depends on the service

**Use For:** Any custom AI service you integrate

---

## 🎯 SMART ROUTING

The MCP automatically chooses the best agent based on:

1. **Task Type**
   - Code? → Coder
   - Research? → Researcher
   - Image? → Vision
   - Architecture? → Gemini Architect

2. **Complexity**
   - Simple task → Local agent (free)
   - Complex reasoning → Claude/ChatGPT (paid)
   - System building → Architect

3. **Your Preferences**
   - You can force a specific agent
   - Override routing with `"Agent: task"`

---

## 🎮 HOW TO USE

### Let MCP Decide (Smart Routing):
```
"Research Python frameworks"  → Automatically uses Researcher
"Build a login system"        → Automatically uses Gemini Architect
"Fix this function"           → Automatically uses Coder
```

### Force a Specific Agent:
```
"Architect: Design a deployment pipeline"
"Claude: Deeply analyze this ethical dilemma"
"Coder: Write a sorting algorithm"
"Vision: Analyze this screenshot"
```

### Compare Agents:
```
"Ask both Coder and Architect about this design"
"Compare Claude and ChatGPT responses to this question"
```

---

## 🛡️ SAFETY LEVELS EXPLAINED

### 🟢 GREEN - Auto-Execute
- Reading files/data
- Web searches
- Code generation (in memory)
- Analysis and reasoning
- **No system changes**

### 🟡 YELLOW - Execute + Notify
- Creating files
- Modifying code
- Browsing websites
- Sending emails
- **Notifies you after execution**

### 🔴 RED - Require Approval
- Deleting files
- System commands
- Deploying code
- Accessing credentials
- **Must approve before execution**

---

## 📝 PERSONALITY GUIDELINES

All agents follow these core principles:

1. **Helpful** - Always try to solve the user's problem
2. **Honest** - Admit when unsure
3. **Safe** - Respect safety levels
4. **Transparent** - Explain actions taken
5. **Context-Aware** - Use memory system
6. **Efficient** - Choose the right tool
7. **User-Centric** - You're in control

---

## 🎨 CUSTOMIZATION

Want to change an agent's personality?

Edit the agent's file:
- **Architect:** `agents/gemini_architect.py`
- **Coder:** `agents/coder.py`
- **Researcher:** `agents/researcher.py`
- **Executor:** `agents/executor.py`
- **Vision:** `agents/vision.py`

Look for `system_prompt` or similar configuration.

---

## 🚀 BEST PRACTICES

1. **Use the Architect for big builds**
   - Like we did today!
   - Multi-file projects
   - New features

2. **Use local agents for quick tasks**
   - Save money
   - Faster responses
   - Privacy

3. **Use external agents for specialized needs**
   - Deep reasoning (Claude)
   - Current events (Perplexity)
   - Speed (ChatGPT)

4. **Review Architect's work**
   - Architect creates files
   - You maintain control
   - Notifications keep you informed

5. **Build custom agents for your workflow**
   - Photography-specific tasks
   - WordPress automation
   - Client management

---

## 💡 ARCHITECT vs LOCAL AGENTS

| Feature | Gemini Architect | Local Agents |
|---------|-----------------|--------------|
| **Complexity** | Complex systems | Specific tasks |
| **Scope** | Multi-file projects | Single operations |
| **Authority** | YELLOW (notify) | Mostly GREEN |
| **Strategy** | Yes | Limited |
| **Cost** | API usage | Free (local) |
| **Best For** | Building features | Day-to-day tasks |

**Think of it like:**
- **Local agents** = Your tools (hammer, saw, screwdriver)
- **Architect** = Your contractor (builds entire rooms)

---

## 🎯 NEXT STEPS

1. **Set up the Architect**
   - Get a Gemini API key (free tier available!)
   - Add via Agent Marketplace
   - Try: "Architect: Show me what you can do"

2. **Test each agent**
   - See their personalities in action
   - Learn which agent for which task

3. **Build something big**
   - Use Architect for the next major feature
   - Browser automation? WordPress builder?

**Your Command Center is ready to build anything.** 🚀
