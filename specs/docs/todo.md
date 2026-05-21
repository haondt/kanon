---
spek:
  description: "TODO.md structure and maintenance"
---

# TODO conventions

Maintain a `.spek/TODO.md` at the project root as the project-level backlog.

## Structure

Organize by category, not as a flat list. Each category is an `##` heading. Items are bullet points — one line, actionable.

```markdown
## Authentication

- Replace session tokens with JWTs
- Add refresh token rotation

## Performance

- Profile the sync endpoint under load
- Add a cache for resolved profiles
```

## What belongs in .spek/TODO.md

- Known work that is planned but not yet started
- Technical debt you've identified and want to address later
- Follow-on work that surfaced during a session but was out of scope

## What does not belong

- Vague notes or half-formed ideas — either make it actionable or don't write it down
- Work that is already tracked in an issue tracker — link to the issue instead, don't duplicate
- Completed items — remove them entirely

## Inline TODOs

Use `TODO:` comments in code for local, code-level notes that don't warrant a backlog item. Keep them short. If an inline TODO is significant enough to track across sessions, promote it to `.spek/TODO.md`.

Do not let inline TODOs accumulate indefinitely — review and either resolve or promote them.

## Maintenance

Review `.spek/TODO.md` during every retro: delete completed items, add new items that surfaced, remove anything that is no longer relevant. Keep it honest — a stale .spek/TODO.md is worse than none.
