# 🛡️ SAFETY PROTOCOL - Riley Development

**CRITICAL RULES - NEVER BREAK THE BUILD**

---

## 🔒 Rule 1: Git Tag Before Every Risky Change

**Before ANY file edit that could break the app:**
```bash
git tag -a "v1.x-feature-name-stable" -m "STABLE: Description"
git push --tags
```

**To rollback:**
```bash
git checkout <tag-name>
# or for single file:
git checkout <commit-hash> -- path/to/file.py
```

---

## 🔒 Rule 2: Syntax Check MANDATORY

**After EVERY code edit:**
```bash
python -m py_compile <file>.py
```

**If fails → immediately rollback:**
```bash
git checkout <file>.py
```

---

## 🔒 Rule 3: Protected Files (NO EDITS)

These files are WORKING and PROTECTED:
- ✅ `agents/companion.py` - Riley's brain
- ✅ `agents/gemini_architect.py` - Architect routing
- ✅ `agents/conversation_db.py` - Database (unless migration needed)

**Only edit if explicitly requested by user.**

---

## 🔒 Rule 4: Isolated Feature Branches

**For risky features (UI overhauls, integrations):**
```bash
git checkout -b feature/ui-polish
# Make changes
# Test
git checkout main
git merge feature/ui-polish
```

---

## 🔒 Rule 5: Test Before Deploy

**Before restarting Riley:**
1. Syntax check all modified files
2. Check for import errors
3. Verify no circular dependencies
4. Test in isolated environment if possible

---

## 📋 Current Stable Tags

- `v1.1.0` - Architect Mode working
- `v1.2-gemini-sidebar-stable` - Phase 2 Gemini sidebar complete

---

## 🚨 Emergency Rollback

**If Riley is broken:**
```bash
# Rollback everything to last stable tag:
git checkout v1.2-gemini-sidebar-stable

# Or rollback single file:
git checkout HEAD -- path/to/file.py

# Restart:
pkill -9 -f command_center_ui.py
python command_center_ui.py &
```

---

**BOTTOM LINE: Never commit broken code. Always test. Always tag stable versions.**
