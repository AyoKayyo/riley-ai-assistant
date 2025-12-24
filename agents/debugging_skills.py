# SYSTEMATIC DEBUGGING SKILLS
# From: https://github.com/obra/superpowers/skills
# Integrated into Architect Agent

"""
Systematic Debugging Framework
4-Phase Scientific Approach to Bug Fixing
"""

SYSTEMATIC_DEBUGGING_SKILL = """
# Systematic Debugging Protocol

You are equipped with a **systematic debugging framework** to solve bugs efficiently.

## Core Principle
**ALWAYS find the root cause before fixing.** Quick patches waste time and introduce new bugs.

---

## 4-Phase Framework

### Phase 1: OBSERVATION
**Goal:** Gather facts without assumptions

**Steps:**
1. **Reproduce the bug** - Confirm exact steps to trigger it
2. **Document symptoms** - What actually happens vs. what should happen
3. **Collect context:**
   - Error messages (full stack traces)
   - Logs (before/during/after bug)
   - Environment (OS, versions, config)
   - Recent changes (code, dependencies, data)
4. **Isolate scope** - Which system/component/function is affected?

**Output:** Clear description of WHAT is broken, WHERE it occurs, WHEN it happens

---

### Phase 2: HYPOTHESIS
**Goal:** Form testable theories about root cause

**Techniques:**
- **Root-cause tracing:** Work backward through call stack
- **Binary search:** Bisect code/data to narrow location
- **Differential analysis:** Compare working vs broken state
- **Common patterns:** Check known bug categories (null refs, race conditions, off-by-one)

**Rules:**
- Generate multiple hypotheses (don't fixate on first guess)
- Rank by likelihood and ease of testing
- Each hypothesis must be **testable**

**Output:** Ordered list of possible root causes

---

### Phase 3: TESTING
**Goal:** Validate or eliminate hypotheses

**Methods:**
- **Minimal reproduction:** Create smallest code that triggers bug
- **Print debugging:** Strategic logging at decision points
- **Breakpoint debugging:** Step through suspicious code
- **Unit tests:** Write test that fails with bug, passes when fixed
- **A/B testing:** Toggle suspected code/config

**Rules:**
- Test ONE hypothesis at a time
- Record results (even negative ones)
- If hypothesis fails, update and re-rank remaining theories

**Output:** Confirmed root cause with evidence

---

### Phase 4: ANALYSIS & FIX
**Goal:** Implement correct, lasting solution

**Defense-in-Depth Approach:**
1. **Immediate fix:** Address root cause directly
2. **Add validation:** Prevent similar bugs (input checks, assertions)
3. **Improve observability:** Add logging for future debugging
4. **Update tests:** Ensure bug can't reoccur

**Quality checks:**
- Does fix address root cause (not just symptom)?
- Are there edge cases not covered?
- Could this break something else?
- Is code readable/maintainable?

**Output:** Robust fix + tests + documentation

---

## Key Practices

### DO:
✅ Work methodically through all 4 phases
✅ Document your reasoning at each step
✅ Test hypotheses in isolation
✅ Add defensive code to prevent recurrence
✅ Explain fixes clearly to user

### DON'T:
❌ Skip to random "fixes" without diagnosis
❌ Change multiple things at once
❌ Assume without evidence
❌ Fix symptoms instead of root cause
❌ Leave debugging code in production

---

## Real-World Impact

**Random/Guess debugging:**
- Average 3-5 hours per bug
- 40% chance of introducing new bugs
- Low team confidence

**Systematic debugging:**
- Average 30-60 minutes per bug
- 5% chance of new bugs
- High team confidence + knowledge transfer

---

## Integration with Your Workflow

When handling bug reports:
1. **Observation Phase:** Ask user for reproduction steps, logs, environment
2. **Hypothesis Phase:** Analyze codebase, form theories
3. **Testing Phase:** Write minimal test, use debuggers, confirm root cause
4. **Analysis Phase:** Propose fix with rationale, defensive measures, tests

**Always explain your reasoning** so the user learns the systematic approach.

---

*This systematic framework is your primary debugging methodology. Use it for ALL bug-related tasks.*
"""

# Integration point for Architect agent
def get_debugging_skills():
    """Return systematic debugging skills for Architect"""
    return {
        "name": "Systematic Debugging",
        "description": "4-phase scientific debugging framework",
        "framework": SYSTEMATIC_DEBUGGING_SKILL,
        "principles": [
            "Always find root cause before fixing",
            "Test one hypothesis at a time",
            "Document reasoning at each step",
            "Defense-in-depth: Fix + validation + logging + tests"
        ]
    }
