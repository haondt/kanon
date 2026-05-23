---
spek:
  description: "Use after implementing work yourself (manual coding, raw prompts, or detours) to mark session.yaml plan steps done before /spek-review"
  output: skill
  name: spek-reconcile
  preapproved_tools:
    - Bash(git diff *)
    - Bash(git status)
    - Bash(spek session *)
  integrations:
    claude:
      disable-model-invocation: true
---
You are reconciling session state after work was done outside of `/spek-build` — by the human directly, through raw prompts, or via detours.

1. Run `spek session status --full --json` to read the current plan. If no session exists, warn the user and stop — there is nothing to reconcile.

2. Inspect what changed:
   - Run `git diff HEAD` to see modified tracked files.
   - Run `git status` to catch untracked or staged files not yet committed.

3. Compare the diff against each plan step. For each step that is evidently complete based on the changes observed, mark it done: `spek session plan check <key>`. Never overwrite or erase the original step text.

4. For steps that are partially addressed or ambiguous, leave them unmarked and record the ambiguity as a build note: `spek session build note "<text>"`.

5. Append a brief build note describing what was observed: who did the work if you can tell, a short summary of what the diff shows, and any steps that could not be confidently marked done.

6. Prompt the user to run `/spek-review`.
