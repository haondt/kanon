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
  docs/          # readme, structure, session, changelog, todo
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
  commands/      # one file per subcommand: init, sync, profile, local, module, destroy, ref
  core/          # pure logic, no CLI dependency
.spek/           # spek's own session/project files (dogfooding)
```

## Core modules (`src/spek/core/`)

- `config.py` — `SpekConfig` Pydantic model; `load()`/`save()` against `.spek/spek.yaml`
- `yaml_utils.py` — all YAML I/O: `load_yaml(path, model?)`, `save_yaml(data, path)`; also exports `FRONTMATTER_RE` (shared frontmatter regex)
- `render.py` — reads local module copies, strips frontmatter, writes AI tool output files; `ModuleFrontmatter` parses `spek.description/output/name/args/integrations/preapproved_tools`; for `output: skill` + claude, writes `<name>/SKILL.md` with generated YAML frontmatter (`description`, `argument-hint`, plus any keys from `integrations.claude` except `hooks`); `preapproved_tools` from spec frontmatter are merged into `allowed-tools` in the skill frontmatter; when `context: fork`, appends STRUCTURE.md preload commands to `allowed-tools` and injects a `## Project structure` shell-expansion block into the skill body; `collect_hooks(content, ai_tool)` extracts hook declarations from frontmatter; `collect_preapproved_tools(content)` extracts rule-module `preapproved_tools`; `render_settings(hooks_by_event, project_root, ai_tool, preapproved_tools?)` writes `.claude/settings.json` with `permissions.allow` + hooks
- `modules.py` — `list_modules(repo_path)` enumerates all spec files
- `profiles.py` — `resolve_profile()` recursive resolution with deduplication; `ProfileSpec` model
- `references.py` — `search_references(repo_path, terms, project_root?)` keyword search; `read_reference(repo_path, name, project_root?)` retrieves content; local refs in `.spek/local/references/` shadow upstream on name collision; `ReferenceResult` model
- `repo.py` — locates the upstream spek repo (`spek_repo_path`); auto-discovers the local project root (`local_project_path`); reads HEAD SHA

## Data flow

```
spek init   → writes .spek/spek.yaml (modules, stances, integrations)
spek sync   → copies spec files from upstream into .spek/modules/ and .spek/stances/
            → calls render.py to emit .claude/rules/ and .claude/skills/<name>/SKILL.md
            → accumulates hook declarations from all modules; writes .claude/settings.json if any hooks are declared
```

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

## Working in this repo — avoid confusing `specs/` and `.spek/`

This repo dogfoods spek, so it contains **both** the spec library **and** a `.spek/` directory for its own sessions.

| Directory | What it is | When to edit |
|---|---|---|
| `specs/` | The distributable module library — source of truth | Adding or changing spec content for users of spek |
| `.spek/modules/` | Synced copies of whichever modules this project uses | Never edit directly — regenerated by `spek sync` |
| `.spek/` (other files) | Session state, changelog, todo, structure for this project | Session workflow (SESSION.md, CHANGELOG.md, TODO.md) |

**Rule:** if a task involves spec content (guidelines, rules, conventions shipped to users), edit files under `specs/`. If a task involves this project's own session or docs, edit files under `.spek/`. Never edit `.spek/modules/` by hand.

**Sync timing:** `just sync` is run at the user's discretion — they may choose to sync mid-session or wait until after the retro. During a session, `.spek/modules/` may intentionally lag `specs/`; do not flag this as an error.

Before writing or editing a spec, run `spek ref read spek/specs`. Before writing or editing a reference entry, run `spek ref read spek/references`.
