---
spek:
  description: Address all findings from the most recent review pass
  output: skill
  name: spek-fix
  preapproved_tools:
    - Write(.spek/SESSION.md)
  integrations:
    claude:
      disable-model-invocation: true
---
You are addressing findings from the most recent review pass. Your job is to implement fixes for every finding.

1. Read `.spek/SESSION.md`. Locate the most recent `### Review Pass N` block under `## Review`. If no `## Review` section exists, say so and stop.

2. If the only finding in the most recent pass is `- **[approval/N/A]** No issues found.`: confirm this to the user and stop — there is nothing to fix.

3. For each finding, in order:
   a. Propose your solution: describe what you plan to change and why it addresses the finding.
   b. Wait for explicit approval from the user before implementing. A reply that asks questions or adds context is not approval — wait for a clear "yes", "approved", "go ahead", or equivalent.
   c. Once approved, implement the fix.

4. After all fixes are implemented, append a `### Fix Pass N` block (same N as the review pass) to the `## Review` section:

   ```markdown
   ### Fix Pass N

   - **[#M type/severity]** description of what was done
   ```

   One entry per finding, in order. `#M` is the finding's 1-based index within the review pass.

5. Prompt the user to run `/spek-review` again to validate the fixes.
