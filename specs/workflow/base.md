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

Use the session workflow below, driven by slash commands. Each step is invoked explicitly by the user — never advance to the next step automatically, even if the current step concluded confidently. The user may want to review or edit `.spek/SESSION.md` between steps.

| Step | Command | Action |
|---|---|---|
| Sketch *(optional)* | `/spek-sketch` | Clarify a fuzzy goal — skip if the goal is already concrete |
| Plan | `/spek-plan` | Design the approach; get approval before writing code |
| Build | `/spek-build` | Execute the agreed plan |
| Review *(optional)* | `/spek-review` | Evaluate the implementation for problems and plan/spec faithfulness |
| Fix *(optional)* | `/spek-fix` | Address findings from `/spek-review` |
| Retrospective | `/spek-retro` | Log completed work to `.spek/CHANGELOG.md`; clear `.spek/SESSION.md` |

## Session files

| File | Committed | Purpose |
|---|---|---|
| `.spek/SESSION.md` | No (gitignored) | In-progress goal and plan; handoff state |
| `.spek/CHANGELOG.md` | Yes | Running log of completed work |
| `.spek/TODO.md` | Yes | Project backlog |
| `.spek/STRUCTURE.md` | Yes | Living map of the codebase |

