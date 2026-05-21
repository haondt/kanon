# Spec TODO

Planned modules — not started yet.

## Containerization

- `specs/docker/dockerfile.md` — Dockerfile best practices (layer ordering, cache efficiency, non-root user, minimal base images)
- `specs/docker/compose.md` — docker-compose / compose file conventions
- `specs/docker/podman.md` — podman-specific conventions and differences from Docker
- Profile: `containers/docker`, `containers/podman`

## Persistence

- ~~`specs/persistence/redis.md`~~ — done
- ~~`specs/persistence/sqlite.md`~~ — done
- ~~`specs/persistence/postgres.md`~~ — done
- `specs/persistence/base.md` — tool-agnostic persistence conventions (migrations, connection lifecycle, no raw queries in business logic)
- Profile: `persistence/sql`, `persistence/redis`

## Configuration

- ~~`specs/config/base.md`~~ — done
- `specs/config/python.md` — Python-specific: Pydantic settings, single instantiation point (note: `specs/python/config.md` covers the Config class pattern — decide whether to fold or keep separate)
- `specs/config/dotnet.md` — `appsettings.json` / `appsettings.{Environment}.json` structure, secrets management, `IOptions<T>` pattern

## TODOs and technical debt tracking

- ~~`specs/docs/todo.md`~~ — done (moved from `specs/workflow/todos.md`)

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

## CLI

- ~~`spek destroy`~~ — done

## Workflow skills

- `specs/workflow/spek-amend.md` — skill for modifying the current session's goal or plan mid-session: update `.spek/SESSION.md` in place, note what changed and why, without starting a full new define/plan cycle
- `specs/workflow/spek-todo.md` — skill for adding items to `.spek/TODO.md`; takes a description from the user, finds and surfaces any related inline `TODO:` comments from code, and writes a consolidated backlog entry under the appropriate category
- ~~`specs/workflow/spek-detour.md`~~ — done

## Build tooling

- ~~`specs/build/just.md`~~ — done
- ~~`specs/build/make.md`~~ — done

## Cleanup

- `specs/workflow/cleanup.md` — standalone spec for identifying and removing dead code: unused functions, stale TODOs, commented-out blocks, unreferenced files, speculative code that was never used. Complements the retro step but can be invoked independently.
