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

- Add `~/.spek/settings.json` — a global user-level config file that declares a list of module sources (initially local directories; eventually remote sources like GitHub repos). Other global settings can live here too. `spek sync` and `spek module list` should respect declared sources alongside the built-in repo.
- Replace the flat module path string (e.g. `git/commit-base`) with a richer format that can optionally carry a source (e.g. a repo URL + ref) alongside the path
- `spek sync --pull` fetches each module from its declared source; modules with no source continue to resolve against the built-in repo as today
- Consider how `spek init` / `spek profile apply` should work when profiles live in an external source

## Frontend patterns

- Add `specs/systems/basic-crud.md` (conventions for a basic crud app) and `references/basic-crud-frontend`, `references/basic-crud-backend`, `references/basic-crud-htmx`, etc (full pattern: URL structure, create/edit page shape, form layout, button placement, `hx-confirm` for delete, response fragment conventions, etc). Use `spek.template: jinja` in the spec with `{% if "frontend/htmx" in modules %}` blocks so htmx-specific content is only rendered when that module is active. (`spek.template: jinja` is now implemented.)

## spek-audit

New standalone skill that evaluates a project against its active spek modules and guides remediation.

- Initial AI pass (module-by-module) writes findings to `.spek/audit.yaml` with severity and status
- Triage phase walks through findings one at a time; resolutions: fix in-place, manual user fix, move to TODO, deactivate module, defer for upstream spec change, ignore/note in STRUCTURE.md
- O(n) fix evaluation — lazily marks findings already resolved by a prior fix rather than re-scanning
- Final retro phase: CHANGELOG entry + delete audit file
- Follows the linting model: AI writes `audit.yaml` directly, `spek session validate` (or equivalent) enforces schema

## Plan splitting (`/spek-split`)

Add a `/spek-split` skill and supporting conventions for decomposing a large SESSION.md plan into multiple committed sub-plans, each executable as a standalone session.

- **`/spek-split` skill** (runs between `/spek-plan` and `/spek-build`): reads SESSION.md, proposes a set of sub-plans and a group directory name (AI-suggested, user-approved), writes `.spek/plans/<group>/index.yaml` and one `.md` plan file per sub-plan, then prompts the user to either defer all (deletes SESSION.md) or start one now (moves that plan file to SESSION.md).
- **Directory structure:** `.spek/plans/<group>/index.yaml` (goal, overview, ordered plan list with `status: pending/done`) + `.spek/plans/<group>/<name>.md` (Goal + Plan + `## Group` section containing `<group>/<name>`). Plan files are committed; the structure mirrors the existing `.spek/` conventions.
- **`## Group` convention in SESSION.md:** a single line `<group>/<plan>` added to plan files and preserved in SESSION.md after loading; skills that need broader context can follow it to `index.yaml` without it being mandatory.
- **Retro extension:** if SESSION.md contains a `## Group` section, retro locates the matching entry in `index.yaml` and sets `status: done` before clearing SESSION.md. No in-progress state — plans go directly from `pending` to `done`.
- **Loading a plan:** user manually moves a plan file to SESSION.md (`mv .spek/plans/<group>/<name>.md .spek/SESSION.md`); no new skill needed for this step.

## Cleanup

- `specs/workflow/cleanup.md` — standalone spec for identifying and removing dead code: unused functions, stale TODOs, commented-out blocks, unreferenced files, speculative code that was never used. Complements the retro step but can be invoked independently.

