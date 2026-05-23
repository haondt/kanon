---
spek:
  description: "SESSION.md structure and conventions"
---

# SESSION.md conventions

- `.spek/SESSION.md` is a living scratchpad for the current session; it is gitignored and cleared at retro
- Include only sections that are relevant — do not create empty headings
- `## Goal` — one paragraph or tight bullet list describing what the session is trying to accomplish
- `## Plan` — step-by-step plan as agreed during `/spek-plan`; mark steps done additively by appending ` — done`
- `## Stance` — active stance name and its module list (written by `/spek-stance`)
- `## Notes` — assumptions made, technical decisions taken, deviations from the plan; the raw material for the CHANGELOG entry
- `## Review` — multi-pass review log; each `/spek-review` run appends `### Review Pass N`, each `/spek-fix` run appends `### Fix Pass N`
- `## Amendments` — one-line record of each change to the goal or plan made via `/spek-amend`
- `## Detours` — one-line record of each out-of-scope edit made via `/spek-detour`
- Keep it honest: reflect actual progress, not intended progress; record decisions as they happen, not after the fact
