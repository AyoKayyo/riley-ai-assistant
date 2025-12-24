# PRE-COMPANION CHECKLIST
**Final Check Before Building Sentient Assistant**
**Date:** 2025-12-23 17:08

---

## ✅ VERIFIED & WORKING

### UI ✅
- [x] Pure black & white theme
- [x] Attachment button (+)
- [x] Tools menu button (⋯)
- [x] White send button
- [x] Architect mode toggle
- [x] All features wired
- [x] No green colors

### Core Systems ✅
- [x] MCP initialized
- [x] All 4 local agents registered
- [x] Gemini Architect ready
- [x] Memory system exists
- [x] Safety controller active

---

## ⚠️ CRITICAL TESTS NEEDED

### 1. **Test All Local Agents** 🔴 MUST DO
```
Test Coder: "Write a hello world function"
Test Researcher: "Search for Python tutorials"  
Test Executor: "What's my current directory?"
Test Vision: [Upload screenshot] "What's in this?"
```
**Why:** Ensure agents actually respond before companion depends on them

### 2. **Test Memory Persistence** 🔴 MUST DO
```
1. Send message: "Remember: I prefer Python"
2. Restart app
3. Check memory/context.json has saved data
```
**Why:** Companion needs persistent memory to work

### 3. **Test Architect Mode Switch** 🔴 MUST DO
```
1. Toggle Architect ON
2. Send test message
3. Toggle OFF
4. Send another message
```
**Why:** Companion will use this mode switching

### 4. **Verify Ollama Connection** 🔴 MUST DO
```bash
curl http://localhost:11434/api/tags
```
**Why:** All local agents fail without Ollama

---

## 🛠️ RECOMMENDED FIXES

### 1. **Add Error Handling** ⚠️ Important
**Issue:** If Ollama crashes, UI will freeze
**Fix:** Add try/catch in AgentThread with user-friendly errors

### 2. **Add "Thinking..." Indicator** 💡 Nice-to-have
**Issue:** No feedback while agent processes
**Fix:** Show "Thinking..." in chat while waiting

### 3. **Memory Auto-Save** ⚠️ Important
**Issue:** Memory only saves on specific events
**Fix:** Auto-save after each message

### 4. **Companion Integration Point** 🔴 CRITICAL
**Decision needed:**
- Option A: Companion = New agent in MCP
- Option B: Companion = Wrapper around MCP
- Option C: Companion = Separate system

**Recommendation:** Option A - Register as special agent

---

## 🔧 QUICK FIXES I RECOMMEND NOW

### Fix 1: Add Ollama Health Check (2 min)
Add startup check to verify Ollama is running

### Fix 2: Better Error Messages (3 min)
Instead of "Error: ...", show helpful guidance

### Fix 3: Loading State (2 min)
Disable input + show "..." while processing

### Fix 4: Memory Auto-Save (2 min)
Save context.json after every exchange

**Total time: ~10 minutes**

---

## 🎯 COMPANION INTEGRATION PLAN

### Where Companion Will Live:
```
agents/companion.py
```

### How It Connects:
```python
# In command_center_ui.py, after line 66:
self.companion = CompanionAgent(self.mcp, self.architect)

# Companion has access to:
- self.mcp (all local agents)
- self.architect (strategic brain)
- self.memory (persistence)
```

### Companion's Role:
- Personality layer OVER existing agents
- Decides which agent to use
- Adds warmth, memory, proactivity
- NOT a replacement, an enhancement

---

## 🚨 POTENTIAL BLOCKERS

### 1. Ollama Not Running
**Symptom:** All local agents fail
**Test:** `curl http://localhost:11434/api/tags`
**Fix:** Start Ollama

### 2. Memory File Permissions
**Symptom:** Context not saving
**Test:** Check `memory/context.json` writeable
**Fix:** `chmod 644 memory/context.json`

### 3. PyQt6 Event Loop
**Symptom:** UI freezes during long responses
**Test:** Send complex task, try clicking
**Fix:** Already using QThread ✅

### 4. Model Not Downloaded
**Symptom:** Vision agent fails
**Test:** Check LLaVA model exists
**Fix:** `ollama pull llava:7b`

---

## ✅ WHAT'S SOLID (Don't Touch)

- UI layout & styling
- MCP architecture
- Agent registration system
- Architect mode toggle
- File structure
- Documentation

---

## 🎬 RECOMMENDED PRE-BUILD ACTIONS

**Priority 1 - MUST DO (5 min):**
1. Test all 4 agents work
2. Verify Ollama is connected
3. Add "Thinking..." indicator

**Priority 2 - SHOULD DO (5 min):**
4. Add better error handling
5. Test memory saves correctly

**Priority 3 - NICE TO HAVE (skip if rushed):**
6. Add keyboard shortcuts
7. Add welcome message
8. Polish animations

---

## 💡 MY RECOMMENDATION

**DO THIS NOW:**
1. ✅ Test agents (critical)
2. ✅ Add "Thinking..." (UX)
3. ✅ Better errors (stability)

**SKIP FOR NOW:**
- Welcome messages (cosmetic)
- Animations (polish)
- Keyboard shortcuts (future)

**BUILD COMPANION AFTER:**
- All tests pass
- Errors handled gracefully
- User sees feedback during processing

---

## 🤔 QUESTIONS FOR YOU

1. **Test the agents now?** (Will take 2 min - just send test messages)
2. **Add quick fixes?** (10 min total - better stability)
3. **Or go straight to Companion?** (Risk: debugging later)

**My vote: 10 min of fixes NOW = Hours saved debugging Companion later**

What do you want to do?
