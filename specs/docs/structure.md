# Project structure doc

Maintain a `.spek/STRUCTURE.md` at the project root as a living map of the codebase for developers.

## Purpose

`.spek/STRUCTURE.md` is not a tutorial (that's `README.md`) and not a design proposal (that's a PR or ADR). It is a current, accurate snapshot of how the project is organized and why — a map for someone already in the codebase who wants to understand what exists and where to find it.

## What to include

- Directory layout with a short description of each significant directory
- Key modules, packages, or services and their responsibilities
- Important concepts or domain terms used throughout the codebase
- Non-obvious conventions: naming patterns, where configuration lives, how layers interact
- Data or request flows if the project has meaningful runtime structure (e.g. request → middleware → handler → service → repo)

## What to omit

- Installation instructions — that's `README.md`
- Future plans or proposed changes — those belong in `TODO.md` or a design doc
- Exhaustive file lists — describe structure at the level of directories and key modules, not every file

## Format

Use a mix of prose and annotated directory trees. Keep it scannable:

```
src/
  commands/     # CLI subcommands, one file per command
  core/         # business logic with no CLI dependency
    config.py   # SpekConfig dataclass and load/save
    render.py   # frontmatter parsing and output routing
```

## Maintenance

Update `.spek/STRUCTURE.md` whenever the session meaningfully changes the project's shape: new modules added, directories reorganized, key concepts renamed or introduced. Small refactors within existing structure do not need an update.

Review it at retro — if it no longer matches the code, fix it.
