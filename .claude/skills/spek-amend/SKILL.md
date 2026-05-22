---
name: spek-amend
description: Amend the current session goal or plan without restarting
disable-model-invocation: true

---
You are amending an in-progress session. Your job is to update SESSION.md to reflect a change in direction — without starting a new define/plan cycle.

1. If `.spek/SESSION.md` does not exist, tell the user there is no active session to amend and stop.

2. Determine what to amend:
   - If the invocation message contains a description, use it.
   - If not, look at the immediately preceding conversation. If the user's last message(s) clearly describe a desired change (e.g. "actually let's do X instead"), state your interpretation in one sentence and proceed.
   - If the intent is still unclear, ask: "What would you like to amend?"

3. Read `.spek/SESSION.md` to understand the current goal and plan.

4. Edit SESSION.md in place:
   - Goal changed: update the goal section directly.
   - Plan changed: update the affected plan steps in place; preserve ✓ markers on already-completed steps.
   - Both: update both.
   Do not append a new plan — edit existing content so SESSION.md always reflects the current intended state.

5. Append an `## Amendments` section (or add to it if it already exists) with a single bullet: what changed and why. One line.

6. Confirm what was amended in one sentence.
