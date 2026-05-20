# STRUCTURE.md conventions

Maintain a `.spek/STRUCTURE.md` as a living mini-map of the codebase — oriented primarily toward AI assistants, secondarily toward developers.

## Purpose

A quick-reference snapshot that answers: where do things live, how does the project fit together, and what does an AI need to know to navigate it confidently without reading every file.

## What to include

- **Directory layout** — annotated tree showing significant directories and their role
- **Key modules or packages** — what each does and how they relate
- **Tech stack** — languages, frameworks, major libraries, and any non-obvious tooling choices
- **Architectural patterns** — how layers or components interact; request flows, data flows, or processing pipelines if relevant
- **Domain concepts** — important terms used throughout the codebase and what they mean
- **Non-obvious conventions** — naming patterns, where config lives, how layers interact, anything that would surprise a reader

## Format

Use whatever format conveys structure most clearly — annotated directory trees, grouped listings, or prose. A literal file tree is not required; describe at whatever level of granularity is useful.

Only call out things that are non-obvious. A directory named `tests/` needs no annotation; a naming convention like `Foo.Bar.*` projects all belonging to the ingestion pipeline does.

```
src/
  commands/     # CLI subcommands, one file per command
  core/         # business logic with no CLI dependency
```

Keep entries to phrases, not sentences.

## Maintenance

Update whenever the session meaningfully changes the project's shape: new modules, reorganized directories, renamed concepts, or new architectural patterns. Small refactors within existing structure do not need an update.
