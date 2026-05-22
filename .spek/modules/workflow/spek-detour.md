---
spek:
  description: Make a quick out-of-scope edit without going through the full workflow
  output: skill
  name: spek-detour
  integrations:
    claude:
      disable-model-invocation: true
---
You are making a quick out-of-scope edit that bypasses the normal spek workflow. Do it immediately — no planning, no retro.

1. Determine what to do:
   - If the user stated the task in their invocation message, use that.
   - Otherwise, ask what they want done.

2. Search the reference library. Run `spek ref search <terms>` with keywords relevant to the task. Retrieve and read any matching entries with `spek ref read <name>` before making the change.

3. Make the change.

4. Check if `.spek/SESSION.md` exists. If yes, append a `## Detours` section (or add to it if it already exists) with a single bullet: what changed and why it was a detour rather than a session task. Keep it to one line.

5. If no `.spek/SESSION.md` exists, skip step 4.

6. Confirm what was done in one sentence.
