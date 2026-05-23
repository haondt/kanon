# Structure

CLI tool for managing AI-assisted development conventions across projects.

- Maintains a library of modular spec files (`specs/`) covering git, Python, workflow, docs, etc.
- Initializes target projects via Q&A (`spek init`), stamping a resolved set of modules and stances into `.spek/`
- Syncs spec files into committed local copies (`spek sync`) and generates AI tool output (rules, skills)
- Provides a session workflow: `/spek-sketch` (optional) → `/spek-plan` → `/spek-build` → `/spek-retro`
- Supports on-demand behavioral stances via `/spek-stance`
- `/spek-think` enters a non-actionary brainstorming mode for the remainder of the conversation
- `/spek-detour` makes a quick out-of-scope edit without going through the full workflow
- `/spek-todo` adds an item to `.spek/TODO.md`, with duplicate detection
- `/spek-onboard` onboards an existing project: writes STRUCTURE.md, selects modules via `spek module list --json` + user approval, applies with `spek module set --sync`, extracts inline TODOs

## Tech stack

Python CLI — Click, Pydantic, PyYAML. Dev: uv, just, pytest. Published via GitLab CI from git tags.

## Layout

```
specs/           # the spec module library — content, not code
  ai/            # AI behavioral conventions (style/, communication/, analysis/, coding/)
  build/         # just, make
  code/          # hygiene (language-agnostic)
  config/        # configuration conventions
  docs/          # readme, structure, session, todo (changelog.md deleted)
  frontend/      # hyperscript, htmx, bulma, dcdn (reference/informative modules)
  git/           # commit and branch conventions
  persistence/   # sqlite, postgres, redis
  python/        # style, venv, config, build, models/, frameworks/, dependencies/, testing/
  systems/       # architectural context modules — how pieces fit together; systems/base is the behavioral entry point (search ref library first)
  tools/spek/    # informational reference for spek CLI tools (ref.md, module.md) — what commands exist and what they output, no behavioral rules
  workflow/      # spek-sketch/plan/implement/review/fix/retro/stance/onboard skills
references/      # on-demand reference entries (library docs, code patterns, examples); searched via spek ref
stances/         # YAML files — each lists module paths; activated via /spek-stance
profiles/        # YAML files — named module+stance bundles; base/ and python/
src/spek/
  cli.py         # Click entrypoint; registers all command groups
  commands/      # one file per subcommand: init, sync, profile, local, module, destroy, ref; session/ and todo/ are packages
  core/          # pure logic, no CLI dependency
.spek/           # spek's own session/project files (dogfooding)
```

## Core modules (`src/spek/core/`)

- `config.py` — `SpekConfig` Pydantic model; `load()`/`save()` against `.spek/spek.yaml`
- `yaml_utils.py` — all YAML I/O: `load_yaml(path, model?)`, `save_yaml(data, path)`; also exports `FRONTMATTER_RE` (shared frontmatter regex)
- `render.py` — reads local module copies, strips frontmatter, writes AI tool output files; `ModuleFrontmatter` parses `spek.description/output/name/args/integrations/preapproved_tools/template`; `output` and `template` are `Literal`-typed (`Literal["rule","skill"]` and `Literal["jinja"] | None`); when `template: jinja`, body is rendered through `_apply_jinja(body, context)` (Jinja2 `StrictUndefined`, `keep_trailing_newline=True`) with `modules` and `integrations` as sets before rule/skill branching; for `output: skill` + claude, writes `<name>/SKILL.md` with generated YAML frontmatter (`description`, `argument-hint`, plus any keys from `integrations.claude` except `hooks`); `preapproved_tools` from spec frontmatter are merged into `allowed-tools` in the skill frontmatter; when `context: fork`, appends STRUCTURE.md preload commands to `allowed-tools` and injects a `## Project structure` shell-expansion block into the skill body; `collect_hooks(content, ai_tool)` extracts hook declarations from frontmatter; `collect_preapproved_tools(content)` extracts rule-module `preapproved_tools`; `render_settings(hooks_by_event, project_root, ai_tool, preapproved_tools?)` writes `.claude/settings.json` with `permissions.allow` + hooks
- `modules.py` — `list_modules(repo_path)` enumerates all spec files
- `profiles.py` — `resolve_profile()` recursive resolution with deduplication; `ProfileSpec` model
- `references.py` — `search_references(repo_path, terms, project_root?)` keyword search; `read_reference(repo_path, name, project_root?)` retrieves content; local refs in `.spek/local/references/` shadow upstream on name collision; `ReferenceResult` model
- `session.py` — `SessionState` Pydantic model (goal, plan, build, review, amendments, detours, stance, `_meta`); load/save/lint; private `_Dumper` subclass for YAML block-literal strings; `_meta.next_key` tracks next stable key per namespace (`pn`, `bn`, `f`, `p`); backing file `.spek/session.yaml`
- `todo.py` — `TodoState` / `TodoSection` Pydantic models; load/save/lint; backing file `.spek/todo.yaml`
- `utils.py` — `deep_merge(d1, d2, conflicts?)` — recursive dict merge with three conflict modes (`new`/`old`/`err`); list deduplication safe for unhashable types
- `repo.py` — locates the upstream spek repo (`spek_repo_path`); auto-discovers the local project root (`local_project_path`); reads HEAD SHA

## Data flow

```
spek init   → writes .spek/spek.yaml (modules, stances, integrations)
spek sync   → copies spec files from upstream into .spek/modules/ and .spek/stances/
            → calls render.py to emit .claude/rules/ and .claude/skills/<name>/SKILL.md
            → accumulates hook declarations from all modules; writes .claude/settings.json if any hooks are declared
```

## spek session subcommands

Full `spek session` command group. Reads/writes `.spek/session.yaml`. All reads emit file hash; all writes emit before/after hash.

- `start <goal>` — creates session.yaml; fails if exists
- `goal` / `status [--full]` — read goal or full state
- `plan status/add-step/check/uncheck/note/unnote`
- `amend goal/plan step/plan note/plan unnote/add-note/status`
- `build note/unnote/status`
- `detour add/status`
- `stance set/clear/status`
- `review start/add-finding/close-finding/reopen-finding/set-fix-note/status`
- `lint` / `clear` — validate schema / delete session.yaml

## spek todo subcommands

Full `spek todo` command group. Reads/writes `.spek/todo.yaml`. `section add` auto-creates the file on first call.

- `status [--section <key>] [<text>]` / `search <terms>...`
- `add --section <key> <text>` / `remove --section <key> <text>`
- `section status/search/add [--allow-exists] <key> <name>`
- `lint`

## spek module subcommands

- `spek module edit` — interactive checkbox picker (was bare `spek module`; no longer invoked without subcommand)
- `spek module list [--json]` — lists all available modules; `--json` outputs `[{name, description, active}]` for AI consumption
- `spek module set [--sync] <module>...` — non-interactive full replacement of the module list; validates names; intended for AI agents

## Key concepts

- **module** — a single markdown spec file; path relative to `specs/` (e.g. `git/commit-base`)
- **stance** — a YAML file listing modules; inert until activated via `/spek-stance`
- **profile** — a YAML file listing modules and stances; resolved recursively at `spek init` or `spek profile apply`
- **active vs inert** — a module in `spek.yaml.modules` → written to AI rules; a module only referenced by a stance → copied to `.spek/modules/` only, not emitted until the stance is activated

## Non-obvious

- Output type (`rule` vs `skill`) is declared in spec file frontmatter; frontmatter is stripped before writing output
- `skill` output for Claude is written as `.claude/skills/<name>/SKILL.md` with a YAML frontmatter block (`description`, `argument-hint`, and any `integrations.claude` keys passed verbatim except `hooks`); Windsurf `skill` output remains a flat `.md` in `.windsurf/rules/`
- Hook declarations in `integrations.claude.hooks` frontmatter accumulate across all modules and are written to `.claude/settings.json` by `render_settings`; the file is fully spek-managed (overwritten each sync, deleted by `spek destroy`) — user-managed overrides belong in `.claude/settings.local.json`
- Whether a module is always-active or stance-only is determined entirely by its presence in `spek.yaml.modules`, not by anything in the file itself
- `_metadata.py` version is `"0.0.0"` in the repo — CI rewrites it from the git tag at build time; do not edit manually
- `spek.yaml` is for *target projects* — this repo's `.spek/spek.yaml` is its own dogfooded config
- `.spek/modules/` and `.spek/stances/` in target projects are committed — AI output can be regenerated without the upstream spek repo
- Session state is now `.spek/session.yaml` (gitignored); todo backlog is `.spek/todo.yaml` (committed); the old `.spek/SESSION.md` and `.spek/TODO.md` are inert artifacts left in place
- CHANGELOG machinery has been removed — `specs/docs/changelog.md` is deleted; no `spek changelog` CLI exists; running project changelogs remain in `.spek/CHANGELOG.md` but are managed manually
- `commands/session/` and `commands/todo/` are packages (one module per subgroup) rather than single files

## Working in this repo — avoid confusing `specs/` and `.spek/`

This repo dogfoods spek, so it contains **both** the spec library **and** a `.spek/` directory for its own sessions.

| Directory | What it is | When to edit |
|---|---|---|
| `specs/` | The distributable module library — source of truth | Adding or changing spec content for users of spek |
| `.spek/modules/` | Synced copies of whichever modules this project uses | Never edit directly — regenerated by `spek sync` |
| `.spek/` (other files) | Session state, changelog, todo, structure for this project | Session workflow (session.yaml, todo.yaml, CHANGELOG.md) |

**Rule:** if a task involves spec content (guidelines, rules, conventions shipped to users), edit files under `specs/`. If a task involves this project's own session or docs, edit files under `.spek/`. Never edit `.spek/modules/` by hand.

**Sync timing:** `just sync` is run at the user's discretion — they may choose to sync mid-session or wait until after the retro. During a session, `.spek/modules/` may intentionally lag `specs/`; do not flag this as an error.

Before writing or editing a spec, run `spek ref read spek/specs`. Before writing or editing a reference entry, run `spek ref read spek/references`.
