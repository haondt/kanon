---
spek:
  description: Address all findings from the most recent review pass
  output: skill
  name: spek-fix
  integrations:
    claude:
      disable-model-invocation: true
---
You are addressing findings from the most recent review pass. Your job is to implement fixes for every finding.

1. Run `spek session review status --json` to get all review passes. Identify the most recent pass key (e.g. `p2`). Run `spek session review status --pass <key> --json` to get its findings. If no review passes exist, say so and stop.

2. Check the pass `status` field from the JSON. If `status == "approved"`: confirm this to the user and stop — there is nothing to fix.

3. For each finding, in order:
   a. Propose your solution: describe what you plan to change and why it addresses the finding.
   b. Wait for explicit approval from the user before implementing. A reply that asks questions or adds context is not approval — wait for a clear "yes", "approved", "go ahead", or equivalent.
   c. Once approved, implement the fix.
   d. Record the fix: `spek session review set-fix-note <pass-key> <finding-key> "<what was done>"`
   e. Close the finding: `spek session review close-finding <pass-key> <finding-key>`

4. After all fixes are implemented, summarize what was done: one line per finding, referencing its key (e.g. `f1`).

5. Prompt the user to run `/spek-review` again to validate the fixes.
