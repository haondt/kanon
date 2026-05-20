# Spec TODO

Planned modules — not started yet.

## Containerization

- `specs/docker/dockerfile.md` — Dockerfile best practices (layer ordering, cache efficiency, non-root user, minimal base images)
- `specs/docker/compose.md` — docker-compose / compose file conventions
- `specs/docker/podman.md` — podman-specific conventions and differences from Docker
- Profile: `containers/docker`, `containers/podman`

## Persistence

- `specs/persistence/redis.md` — key naming, TTLs, connection handling, when not to use Redis
- `specs/persistence/sqlite.md` — schema conventions, migration approach, when SQLite is appropriate
- `specs/persistence/postgres.md` — schema conventions, indexing, migrations, connection pooling
- `specs/persistence/base.md` — tool-agnostic persistence conventions (migrations, connection lifecycle, no raw queries in business logic)
- Profile: `persistence/sql`, `persistence/redis`

## Configuration

- `specs/config/base.md` — tool-agnostic configuration conventions (env vars, fail-fast validation, no hardcoded secrets, `.env.example`)
- `specs/config/python.md` — Python-specific: config module pattern (`config.py` or `settings.py`), Pydantic settings, single instantiation point
- `specs/config/dotnet.md` — `appsettings.json` / `appsettings.{Environment}.json` structure, secrets management, `IOptions<T>` pattern
- Note: `specs/python/config.md` already exists as a stub — fold it in or replace it

## TODOs and technical debt tracking

- ~~`specs/workflow/todos.md`~~ — done

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

## Cleanup

- `specs/workflow/cleanup.md` — standalone spec for identifying and removing dead code: unused functions, stale TODOs, commented-out blocks, unreferenced files, speculative code that was never used. Complements the retro step but can be invoked independently.
