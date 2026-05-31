---
kanon:
  description: "Close the session: review todo.yaml and delete session.yaml"
  output: skill
  name: kanon-retro
  preapproved_tools:
    - Bash(git diff *)
    - Bash(git log *)
  skill:
    model_invokable: false
    needs_context: false
---
You are closing out a development session. Your job is to record completed work, update docs, and reset session state.

1. Run `kanon session status --full --json` to understand what was planned and what was done. If the command fails (no session), derive what was done from uncommitted changes via `git diff HEAD`.
2. Summarize what was actually completed. Note any deviations from the plan.
3. Read `README.md` and update it if anything changed this session that it documents.
4. Review and update `.kanon/STRUCTURE.md` if the session changed the project's shape.
5. Review and update `todo.yaml`:
   - Run `kanon todo status --json` to see the current backlog.
   - Remove completed items: `kanon todo remove --section <key> "<text>"`
   - Add new items surfaced during the session: `kanon todo section add <key> "<name>"` + `kanon todo add --section <key> "<text>"`
6. Run `kanon session clear` to delete `session.yaml`.
7. Confirm what was updated and what was closed.
8. Prompt the user to clear their conversation context using whatever mechanism their AI tool provides (e.g. `/clear` in Claude Code).
