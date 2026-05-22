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

2. Make the change.

3. If `.spek/SESSION.md` exists, append a `## Detours` section (or add to it if it already exists) with a single bullet: what changed and why it was a detour rather than a session task. Keep it to one line.

4. If no `.spek/SESSION.md` exists, skip step 3.

5. Confirm what was done in one sentence.
