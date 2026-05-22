---
spek:
  description: "SESSION.md structure and conventions"
---

# SESSION.md conventions

`.spek/SESSION.md` is a living scratchpad for the current session. It is gitignored — it exists only for the duration of active work and is cleared at retro.

## Structure

```markdown
## Goal
One paragraph or tight bullet list describing what this session is trying to accomplish.

## Plan
Step-by-step implementation plan as agreed during /spek-plan. Steps are marked done as they are completed.

## Stance
Active stance name and its module list (written by /spek-stance).

## Notes
Assumptions made, technical decisions taken, deviations from the plan, anything worth carrying into the retro or CHANGELOG.

## Review
Multi-pass review log. Each `/spek-review` run appends `### Review Pass N` with structured findings; each `/spek-fix` run appends `### Fix Pass N` with fixes. Cycle continues until a review pass returns only an approval finding.

## Amendments
One-line record of each change to the goal or plan made via /spek-amend.

## Detours
One-line record of each out-of-scope edit made via /spek-detour.
```

Only include sections that are relevant — don't create empty headings.

## Guidelines

- Keep it honest: reflect actual progress, not intended progress
- Record decisions and assumptions as they happen, not after the fact
- The Notes section is the raw material for the CHANGELOG entry — write it with that in mind
