---
spek:
  output: command
---
You are closing out a development session. Your job is to record completed work and reset session state.

1. Read `.spek/SESSION.md` to understand what was planned and what was done.
2. Summarize what was actually completed. Note any deviations from the plan.
3. Append an entry to `.spek/CHANGELOG.md`.
4. Update `README.md` if needed.
5. Review and update `.spek/STRUCTURE.md` if the session changed the project's shape.
6. Review and update `.spek/TODO.md`.
7. Scan for dead code and leftover artifacts: unused functions, commented-out blocks, stale TODOs, files that are no longer referenced, debug output, and anything added speculatively that was never used. Remove what is clearly dead. Flag anything uncertain in `.spek/TODO.md` rather than deleting it.
8. Delete the contents of `.spek/SESSION.md` or remove the file entirely.
9. Confirm what was logged and which docs were updated.
