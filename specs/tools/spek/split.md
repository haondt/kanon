---
spek:
  description: "spek split CLI reference — manage plan splits (collections of related sub-plans)"
---

# spek split CLI

Splits are named collections of sub-plans. A split lives at `.spek/plans/<name>/` with an `index.yaml` tracking each sub-plan's status.

## Commands

- `spek split create <name> <goal>` — create a new split; fails if it already exists
- `spek split list` — list all splits with their goals
- `spek split status <name>` — show the split goal and each sub-plan's name + status (`pending`, `in_progress`, `done`)

All commands accept `--project-root` and `--json`.

## Sub-plan status lifecycle

Sub-plan entries in `index.yaml` track progress:
- `pending` — created but not yet loaded into a session
- `in_progress` — set automatically when `spek session load <split>/<name>` is run
- `done` — set manually or by tooling when the sub-plan's work is complete
