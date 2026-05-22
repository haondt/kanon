# Spec TODO

Planned modules — not started yet.

## Containerization

- `specs/docker/dockerfile.md` — Dockerfile best practices (layer ordering, cache efficiency, non-root user, minimal base images)
- `specs/docker/compose.md` — docker-compose / compose file conventions
- `specs/docker/podman.md` — podman-specific conventions and differences from Docker
- Profile: `containers/docker`, `containers/podman`

## Persistence

- `specs/persistence/base.md` — tool-agnostic persistence conventions (migrations, connection lifecycle, no raw queries in business logic)
- Profile: `persistence/sql`, `persistence/redis`

## Configuration

- `specs/config/python.md` — Python-specific: Pydantic settings, single instantiation point (note: `specs/python/config.md` covers the Config class pattern — decide whether to fold or keep separate)
- `specs/config/dotnet.md` — `appsettings.json` / `appsettings.{Environment}.json` structure, secrets management, `IOptions<T>` pattern

## AI stances — follow-on work

Stances implemented (`stances/`, `/spek-stance` skill, `spek local stance`). Possible follow-on:

- Have `/spek-plan` and `/spek-build` check the active stance in `.spek/SESSION.md` and adjust their behavior accordingly (e.g. collaborative stance → `/spek-plan` surfaces more trade-offs)
- Additional stances: `performance.yaml`, `security.yaml`, `mentor.yaml` (explain everything, teach as you go)

## File naming conventions and project structure

- `specs/conventions/naming.md` — file and directory naming conventions: `kebab-case` for files, `snake_case` for Python modules, when to use `.yaml` vs `.yml` (prefer `.yaml`), `src/` layout vs flat layout
- `specs/conventions/python-structure.md` — Python package vs module (when to use `__init__.py`, when a single file suffices), `src/` layout, entry points
- `specs/conventions/project-structure.md` — what belongs at repo root vs subdirectory, when to use a monorepo, dotfile conventions (`.claude/`, `.spek/`, etc.)

## Refactoring

- `specs/refactoring/base.md` — when to refactor vs. when to leave it, refactor as a separate commit, test coverage before refactoring
- `specs/refactoring/python.md` — Python-specific: extraction patterns, naming, avoiding over-abstraction

## External spec sources

Currently spek only syncs modules from its own repo, which limits it to a single opinionated library. The goal is to allow modules, stances, and profiles in `spek.yaml` to reference external sources directly — so personal/work configs can be kept separate and so other people can use spek with their own spec libraries.

- Replace the flat module path string (e.g. `git/commit-base`) with a richer format that can optionally carry a source (e.g. a repo URL + ref) alongside the path
- `spek sync --pull` fetches each module from its declared source; modules with no source continue to resolve against the built-in repo as today
- Consider how `spek init` / `spek profile apply` should work when profiles live in an external source


## Workflow

- Update `specs/workflow/spek-build.md` to mark plan steps complete non-destructively — e.g. append a completion marker rather than overwriting the checkbox, so the original plan text is preserved as a record of what was agreed.
- Redesign the `spek-review` / `spek-fix` cycle so SESSION.md accumulates an audit trail rather than being edited in place. `spek-fix` should close finding threads and annotate its work but leave the verdict untouched; a subsequent `spek-review` run should validate the fixes, search for new issues, and append its own verdict entry. The `## Review` section should read as a chronological history of passes, not a mutable status board.
- Update `specs/workflow/spek-retro.md` to prompt the user to clear the conversation context after the retro is complete, using whatever tool is available (e.g. `/clear` in Claude Code).

## Tools modules

- Convert `specs/tools/` modules (e.g. `tools/spek/ref.md`, `tools/spek/module.md`) from `output: rule` to `output: command` so they are emitted as AI-invoked skills rather than always-on rules. These modules describe CLI tool usage, not behavioral conventions — the AI should pull them on demand rather than having them injected as passive context into every session.

## Cleanup

- `specs/workflow/cleanup.md` — standalone spec for identifying and removing dead code: unused functions, stale TODOs, commented-out blocks, unreferenced files, speculative code that was never used. Complements the retro step but can be invoked independently.
