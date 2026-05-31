---
kanon:
  description: Make a quick out-of-scope edit without going through the full workflow
  output: skill
  name: kanon-detour
  skill:
    model_invokable: false
---
You are making a quick out-of-scope edit that bypasses the normal kanon workflow. Do it immediately — no planning, no retro.

1. Determine what to do:
   - If the user stated the task in their invocation message, use that.
   - Otherwise, ask what they want done.

2. Search the reference library. Run `kanon ref search <terms>` with keywords relevant to the task. Retrieve and read any matching entries with `kanon ref read <name>` before making the change.

3. Make the change.

4. Check if a session exists by running `kanon session goal`. If the command succeeds, record the detour: `kanon session detour add "<what changed and why it was a detour>"`. Keep it to one line.

5. If no session exists, skip step 4.

6. Confirm what was done in one sentence.
