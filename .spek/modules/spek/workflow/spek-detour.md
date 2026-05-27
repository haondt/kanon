---
spek:
  output: skill
  name: spek-detour
  description: Make a quick out-of-scope edit without going through the full workflow
  skill:
    model_invokable: false
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools: []
---
You are making a quick out-of-scope edit that bypasses the normal spek workflow. Do it immediately — no planning, no retro.

1. Determine what to do:
   - If the user stated the task in their invocation message, use that.
   - Otherwise, ask what they want done.

2. Search the reference library. Run `spek ref search <terms>` with keywords relevant to the task. Retrieve and read any matching entries with `spek ref read <name>` before making the change.

3. Make the change.

4. Check if a session exists by running `spek session goal`. If the command succeeds, record the detour: `spek session detour add "<what changed and why it was a detour>"`. Keep it to one line.

5. If no session exists, skip step 4.

6. Confirm what was done in one sentence.
