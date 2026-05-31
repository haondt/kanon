---
kanon:
  description: "4-step session workflow table"
---

# Dev workflow

Use the session workflow below, driven by skills (invoked with `/`). Each step is invoked explicitly by the user — never advance to the next step automatically, even if the current step concluded confidently. The user may review session state between steps via `kanon session status`.

| Step | Command | Action |
|---|---|---|
| Sketch *(optional)* | `/kanon-sketch` | Clarify a fuzzy goal — skip if the goal is already concrete |
| Plan | `/kanon-plan` | Design the approach; get approval before writing code |
| Build | `/kanon-build` | Execute the agreed plan |
| Review *(optional)* | `/kanon-review` | Evaluate the implementation for problems and plan/kanon faithfulness |
| Fix *(optional)* | `/kanon-fix` | Address findings from `/kanon-review` |
| Retrospective | `/kanon-retro` | Close the session; clear `.kanon/session.yaml` |

## Session files

| File | Committed | Purpose |
|---|---|---|
| `.kanon/session.yaml` | Yes | In-progress goal, plan, review, and build notes |
| `.kanon/todo.yaml` | Yes | Project backlog |
| `.kanon/STRUCTURE.md` | Yes | Living map of the codebase |

