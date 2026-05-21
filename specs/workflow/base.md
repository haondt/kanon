---
spek:
  description: "4-step session workflow table"
---

# Dev workflow

At the start of each session, read `.spek/STRUCTURE.md` to orient yourself to the project before doing anything else.

Use a 4-step convention each session, driven by the slash commands below:

| Step | Command | Action |
|---|---|---|
| 1. Define | `/spek-define` | Articulate and record the session goal in `.spek/SESSION.md` |
| 2. Plan | `/spek-plan` | Design the approach; get approval before writing code |
| 3. Implement | `/spek-implement` | Execute the agreed plan |
| 4. Review *(optional)* | `/spek-review` | Evaluate the implementation for problems and plan/spec faithfulness |
| 5. Retrospective | `/spek-retro` | Log completed work to `.spek/CHANGELOG.md`; clear `.spek/SESSION.md` |

## Session files

| File | Committed | Purpose |
|---|---|---|
| `.spek/SESSION.md` | No (gitignored) | In-progress goal and plan; handoff state |
| `.spek/CHANGELOG.md` | Yes | Running log of completed work |
| `.spek/TODO.md` | Yes | Project backlog |
| `.spek/STRUCTURE.md` | Yes | Living map of the codebase |

