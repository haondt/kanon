---
spek:
  description: "Close the session: review todo.yaml and delete session.yaml"
  output: skill
  name: spek-retro
  preapproved_tools:
    - Bash(git diff *)
    - Bash(git log *)
  integrations:
    claude:
      disable-model-invocation: true
      context: fork
---
You are closing out a development session. Your job is to record completed work, update docs, and reset session state.

1. Run `spek session status --full --json` to understand what was planned and what was done. If the command fails (no session), derive what was done from uncommitted changes via `git diff HEAD`.
2. Summarize what was actually completed. Note any deviations from the plan.
3. Update `README.md` if needed.
4. Review and update `.spek/STRUCTURE.md` if the session changed the project's shape.
5. Review and update `todo.yaml`:
   - Run `spek todo status --json` to see the current backlog.
   - Remove completed items: `spek todo remove --section <key> "<text>"`
   - Add new items surfaced during the session: `spek todo section add <key> "<name>"` + `spek todo add --section <key> "<text>"`
6. Run `spek session clear` to delete `session.yaml`.
7. Confirm what was updated and what was closed.
8. Prompt the user to clear their conversation context using whatever mechanism their AI tool provides (e.g. `/clear` in Claude Code).
