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

- Have `/spek-plan` and `/spek-implement` check the active stance in `.spek/SESSION.md` and adjust their behavior accordingly (e.g. collaborative stance → `/spek-plan` surfaces more trade-offs)
- Additional stances: `performance.yaml`, `security.yaml`, `mentor.yaml` (explain everything, teach as you go)

## File naming conventions and project structure

- `specs/conventions/naming.md` — file and directory naming conventions: `kebab-case` for files, `snake_case` for Python modules, when to use `.yaml` vs `.yml` (prefer `.yaml`), `src/` layout vs flat layout
- `specs/conventions/python-structure.md` — Python package vs module (when to use `__init__.py`, when a single file suffices), `src/` layout, entry points
- `specs/conventions/project-structure.md` — what belongs at repo root vs subdirectory, when to use a monorepo, dotfile conventions (`.claude/`, `.spek/`, etc.)

## Refactoring

- `specs/refactoring/base.md` — when to refactor vs. when to leave it, refactor as a separate commit, test coverage before refactoring
- `specs/refactoring/python.md` — Python-specific: extraction patterns, naming, avoiding over-abstraction

## Workflow commands

- Rename `/spek-implement` to `/spek-build` — shorter, fits the existing verb register (sketch/plan/build/review/retro)

## Workflow skills

- `specs/workflow/spek-todo.md` — skill for adding items to `.spek/TODO.md`; takes a description from the user, finds and surfaces any related inline `TODO:` comments from code, and writes a consolidated backlog entry under the appropriate category

## External spec sources

Currently spek only syncs modules from its own repo, which limits it to a single opinionated library. The goal is to allow modules, stances, and profiles in `spek.yaml` to reference external sources directly — so personal/work configs can be kept separate and so other people can use spek with their own spec libraries.

- Replace the flat module path string (e.g. `git/commit-base`) with a richer format that can optionally carry a source (e.g. a repo URL + ref) alongside the path
- `spek sync --pull` fetches each module from its declared source; modules with no source continue to resolve against the built-in repo as today
- Consider how `spek init` / `spek profile apply` should work when profiles live in an external source

## Brownfield / onboarding

Support for adopting spek in an existing project via a `spek-onboard` skill:

- Workflow: run `spek init` with the base profile, then `/spek-onboard`
- `/spek-onboard` crawls the project to understand tech stack, workflows, and structure, then:
  - Fills in `.spek/STRUCTURE.md`
  - Calls `spek module list` (new subcommand, see below) to enumerate available modules
  - Selects appropriate modules and reconfigures `spec.yaml` via `spek module` (or a new subcommand)
  - Extracts any inline `TODO:` comments into `.spek/TODO.md`
- `spek module` refactor: move current behavior to a subcommand (e.g. `spek module edit`); add `spek module list` to list all available modules; add `--json` flag for AI consumption; add `spek module list` to the tools spec so AI agents can call it
- Update README to document the brownfield onboarding flow

## Cleanup

- `specs/workflow/cleanup.md` — standalone spec for identifying and removing dead code: unused functions, stale TODOs, commented-out blocks, unreferenced files, speculative code that was never used. Complements the retro step but can be invoked independently.
