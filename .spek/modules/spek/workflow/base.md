---
spek:
  description: "4-step session workflow table"
  integrations:
    claude:
      hooks:
        SessionStart:
          - matcher: "startup"
            command: "bash -c 'test -f .spek/STRUCTURE.md && cat .spek/STRUCTURE.md'"
          - matcher: "clear"
            command: "bash -c 'test -f .spek/STRUCTURE.md && cat .spek/STRUCTURE.md'"
---

# Dev workflow

Use the session workflow below, driven by skills (invoked with `/`). Each step is invoked explicitly by the user — never advance to the next step automatically, even if the current step concluded confidently. The user may review session state between steps via `spek session status`.

| Step | Command | Action |
|---|---|---|
| Sketch *(optional)* | `/spek-sketch` | Clarify a fuzzy goal — skip if the goal is already concrete |
| Plan | `/spek-plan` | Design the approach; get approval before writing code |
| Build | `/spek-build` | Execute the agreed plan |
| Review *(optional)* | `/spek-review` | Evaluate the implementation for problems and plan/spec faithfulness |
| Fix *(optional)* | `/spek-fix` | Address findings from `/spek-review` |
| Retrospective | `/spek-retro` | Close the session; clear `.spek/session.yaml` |

## Session files

| File | Committed | Purpose |
|---|---|---|
| `.spek/session.yaml` | Yes | In-progress goal, plan, review, and build notes |
| `.spek/todo.yaml` | Yes | Project backlog |
| `.spek/STRUCTURE.md` | Yes | Living map of the codebase |

