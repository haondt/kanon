---
spek:
  description: "Close the session: append to CHANGELOG.md and delete SESSION.md"
  output: command
  name: spek-retro
  integrations:
    claude:
      disable-model-invocation: true
      context: fork
---
You are closing out a development session. Your job is to record completed work and reset session state.

1. Read `.spek/SESSION.md` to understand what was planned and what was done. If SESSION.md does not exist (e.g. the session consisted entirely of `/spek-detour` calls), derive what was done from uncommitted changes via `git diff HEAD`.
2. Summarize what was actually completed. Note any deviations from the plan.
3. Append an entry to `.spek/CHANGELOG.md`.
4. Update `README.md` if needed.
5. Review and update `.spek/STRUCTURE.md` if the session changed the project's shape.
6. Review and update `.spek/TODO.md`.
7. Delete `.spek/SESSION.md`.
8. Confirm what was logged and which docs were updated.
