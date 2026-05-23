---
spek:
  description: "todo.yaml schema and CLI reference"
---

# Todo schema

`.spek/todo.yaml` is the project backlog. It is committed and persists across sessions.

## Fields

| Field | Type | Description |
|---|---|---|
| `sections` | dict[key → section] | Backlog sections; each has `name` (string) and `items` (list[string]) |

Sections are auto-deleted when their last item is removed.

## Conventions

- Items are one-line actionable bullets
- Include: planned but unstarted work, identified technical debt, follow-on work that surfaced but was out of scope
- Exclude: vague half-formed ideas, work already tracked in an issue tracker (link instead), completed items
- A stale `todo.yaml` is worse than none — keep it honest

## CLI

Use `spek todo` commands to read and write the backlog. The file is auto-created on the first `spek todo section add` call.

See `spek todo --help` for the full command list.
