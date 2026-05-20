---
spek:
  output: command
---
You are closing out a development session. Your job is to record completed work and reset session state.

1. Read `.spek/SESSION.md` to understand what was planned and what was done.
2. Summarize what was actually completed. Note any deviations from the plan.
3. Append an entry to `.spek/CHANGELOG.md` under today's date. Write it for a future reader, not as a personal log — what changed and why, not a narration of the session.
4. Review `README.md` and update it if the session changed something user-facing: new commands, changed behaviour, removed features, updated installation steps. Do not update it for internal refactors, test changes, or anything a user of the project would not notice.
5. If `.spek/STRUCTURE.md` exists, review it and update it if the session changed the project's shape: new modules, reorganized directories, renamed concepts. Small within-structure refactors do not need an update.
6. If `.spek/TODO.md` exists, review it and update it: mark anything completed this session as done, add any new items that surfaced, remove anything that is no longer relevant.
7. Scan for dead code and leftover artifacts: unused functions, commented-out blocks, stale TODOs, files that are no longer referenced, debug output, and anything added speculatively that was never used. Remove what is clearly dead. Flag anything uncertain in `.spek/TODO.md` rather than deleting it.
8. Delete the contents of `.spek/SESSION.md` or remove the file entirely.
9. Confirm what was logged and which docs were updated.
