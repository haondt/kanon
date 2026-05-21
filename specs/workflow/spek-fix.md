---
spek:
  description: "Skill: evaluate and fix review findings"
  output: command
  name: spek-fix
---
You are addressing findings from a completed review. Your job is to evaluate each finding, fix genuine problems, and close out the thread on each one.

1. Read the `## Review` section of `.spek/SESSION.md`. If no review findings exist, say so and stop.
2. For each finding:
   a. Evaluate whether it is a genuine problem that warrants a fix in this session.
   b. If yes, implement the fix.
   c. If no (e.g. it is a known trade-off, out of scope, or on reflection not a real problem), note why.
3. After all findings are addressed, update the `## Review` section of SESSION.md by appending a reply under each finding: what was done, or why it was dismissed.
