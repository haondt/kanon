---
name: spek-fix
description: Address findings from a completed review, one by one
disable-model-invocation: true

---
You are addressing findings from a completed review. Your job is to evaluate each finding, plan fixes with the user, and implement them.

1. Read the `## Review` section of `.spek/SESSION.md`. If no review findings exist, say so and stop.
2. Work through each open finding one at a time:
   a. Ask the user whether it warrants a fix in this session.
   b. If yes, propose how you will fix it. For trivial fixes, briefly state your approach. For non-trivial ones, discuss options with the user and agree on an approach. Record the agreed solution in SESSION.md.
   c. If no, note the reasoning in SESSION.md.
3. Get final confirmation from the user, then implement all agreed fixes.
4. After implementation, update the `## Review` section of SESSION.md by appending a reply under each finding: what was done or why it was dismissed. Close each finding by checking it and update the verdict.
