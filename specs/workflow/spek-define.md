---
spek:
  output: command
---
You are starting a new development session. Your job is to surface a clear, concrete session goal and record it.

1. Ask the user what they want to accomplish this session. If they've already stated a goal in their invocation message, treat that as the starting point rather than asking again.
2. Ask clarifying questions until the goal is specific enough to plan against — what changes, in which files or systems, with what observable outcome.
3. Write `.spek/SESSION.md` (overwrite if it exists) with the session goal. Keep it concise: one short paragraph or a tight bullet list. Do not include a plan yet — that's for `/spek-plan`.
4. Confirm what was written.
