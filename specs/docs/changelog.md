# CHANGELOG.md conventions

`.spek/CHANGELOG.md` is a running log of completed work, appended to at the end of each session.

## Format

Entries are grouped under a date heading, newest first. Each entry describes what changed and why — written for a future reader, not as a session narration:

```markdown
## 2026-05-20

Short description of what was done and the motivation behind it. Follow-on notes if relevant.
```

## Guidelines

- Write for someone reading this six months from now, not for the person who did the work
- Record the *why* alongside the *what* — the diff shows the what
- One entry per session is typical; split into sub-entries if the session covered genuinely unrelated areas
- Do not duplicate the CHANGELOG with a retro narration — it should read like a concise commit message, not a journal
