# Structure

CLI tool for managing AI-assisted development conventions across projects.

- Maintains a library of modular spec files (`specs/`) covering git, Python, workflow, docs, etc.
- Initializes target projects via Q&A (`spek init`), stamping a resolved set of modules and stances into `.spek/`
- Syncs spec files into committed local copies (`spek sync`) and generates AI tool output (rules, skills)
- Provides a session workflow: `/spek-sketch` (optional) → `/spek-plan` → `/spek-build` → `/spek-retro`
- Plans can be frozen to files (`/spek-freeze`) and reloaded (`spek session load`); large plans can be decomposed into splits (`/spek-split`)
- Supports on-demand behavioral stances via `/spek-stance`
- `/spek-think` enters a non-actionary brainstorming mode for the remainder of the conversation
- `/spek-detour` makes a quick out-of-scope edit without going through the full workflow
- `/spek-todo` adds an item to `.spek/todo.yaml`
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
  docs/          # readme, structure, session, todo
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
  commands/      # one file per subcommand: init, sync, profile, local, module, destroy, ref; session/, todo/, plan/, and split/ are packages; _utils.py holds shared helpers (read_text_arg, read_text_arg_json for stdin/JSON input support)
  core/          # pure logic, no CLI dependency
.spek/           # spek's own session/project files (dogfooding)
  plans/         # frozen plan files and splits (committed)
```

## Core modules (`src/spek/core/`)

- `config.py` — `SpekConfig` Pydantic model; `load()`/`save()` against `.spek/spek.yaml`; `sources: dict[str, SourceSpec] = {}`; `SPEK_NAMESPACE = "spek"` constant
- `settings.py` — `SourceSpec(BaseModel)` (`path: str`, `url`/`ref` reserved); `GlobalSettings(BaseModel)` (`sources: dict[str, SourceSpec]`); `load_global_settings()` reads `~/.spek/settings.yaml`, returns empty model if missing
- `yaml_utils.py` — all YAML I/O: `load_yaml(path, model?)`, `save_yaml(data, path)`; also exports `FRONTMATTER_RE` (shared frontmatter regex); exports `_literal_representer`, `_enum_str_representer`, `_make_dumper(*enum_types)` for YAML serialization with block-literal strings and str-enum support
- `render.py` — reads local module copies, strips frontmatter, writes AI tool output files; `ModuleFrontmatter` parses `spek.description/output/name/args/integrations/preapproved_tools/template`; `output` and `template` are `Literal`-typed (`Literal["rule","skill"]` and `Literal["jinja"] | None`); when `template: jinja`, body is rendered through `_apply_jinja(body, context)` (Jinja2 `StrictUndefined`, `keep_trailing_newline=True`) with `modules` and `integrations` as sets before rule/skill branching; for `output: skill`, writes `<name>/SKILL.md` with generated YAML frontmatter (`description`, `argument-hint`/`args`, plus any keys from `integrations.<tool>` except `hooks`); Windsurf converts skills to workflows (`.windsurf/workflows/<name>.md` with description frontmatter); skills require an explicit `spek.name` — `ValueError` raised at render time if absent; `preapproved_tools` from spec frontmatter are merged into `allowed-tools` in the skill frontmatter; when `context: fork`, appends STRUCTURE.md preload commands to `allowed-tools` and injects a `## Project structure` shell-expansion block into the skill body; Windsurf rules are flattened (path separators replaced with `--`) and require a `trigger` field in frontmatter (defaults to `always_on`, override via `integrations.windsurf.trigger`); `_TOOL_SPECIFIC_RULES` dict declares extra system-level rules per AI tool (filename, optional frontmatter, body); `render_tool_specific_rules(ai_tool, project_root)` writes the tool-specific rule file (e.g. `.windsurf/rules/spek--windsurf-rules.md`), returns `None` if the tool has no entry; `collect_hooks(content, ai_tool)` extracts hook declarations from frontmatter; `collect_preapproved_tools(content)` extracts rule-module `preapproved_tools`; `render_settings(hooks_by_event, project_root, ai_tool, preapproved_tools?)` writes `.claude/settings.json` with `permissions.allow` + hooks
- `modules.py` — `list_modules(specs_dir)` enumerates all spec files in a given directory; `parse_module_ref(name)` splits on `::`, defaults namespace to `"spek"`; `resolve_sources(repo_path, global_sources, project_sources)` merges global + project (project wins), adds `"spek" → repo_path / "specs"` as fallback when `repo_path` is not None
- `profiles.py` — `resolve_profile()` recursive resolution with deduplication; `ProfileSpec` model
- `references.py` — `search_references(repo_path, terms, project_root?)` keyword search; `read_reference(repo_path, name, project_root?)` retrieves content; local refs in `.spek/local/references/` shadow upstream on name collision; `ReferenceResult` model
- `plan.py` — `PlanFile(BaseModel)` (goal, steps, notes, `_meta`); `SplitIndex(BaseModel)` (goal, `plans: dict[str, SplitEntry]`); `SplitEntry` has `status: Literal["pending","in_progress","done"]`; `parse_plan_ref(name)` splits bare vs `<split>/<name>`; `plan_path`/`index_path` resolve `.spek/plans/` layout; load/save/create helpers for both PlanFile and SplitIndex; `next_note_key(plan)` for pn namespace; backing files `.spek/plans/<name>.yaml` and `.spek/plans/<split>/index.yaml`
- `session.py` — `SessionState` Pydantic model (goal, plan, build, review, amendments, detours, stance, `_meta`); load/save/lint; `_meta.next_key` tracks next stable key per namespace (`pn`, `bn`, `f`, `p`); `Finding` has required `type: FindingType` and `severity: FindingSeverity` fields; `ReviewPass` has `status: Literal['open','approved']`; YAML serialization helpers moved to `yaml_utils.py`; backing file `.spek/session.yaml`
- `todo.py` — `TodoState` / `TodoSection` Pydantic models; load/save/lint; backing file `.spek/todo.yaml`
- `utils.py` — `deep_merge(d1, d2, conflicts?)` — recursive dict merge with three conflict modes (`new`/`old`/`err`); list deduplication safe for unhashable types
- `repo.py` — locates the upstream spek repo (`spek_repo_path`); auto-discovers the local project root (`local_project_path`); reads HEAD SHA

## Data flow

```
spek init   → writes .spek/spek.yaml (modules, stances, integrations, sources)
spek sync   → resolves sources: merges ~/.spek/settings.yaml + config.sources; adds "spek" → upstream repo/specs
            → copies spec files from each namespace into .spek/modules/{ns}/{bare}.md
            → calls render.py to emit AI tool output (rules, skills, workflows) for each configured integration
            → writes tool-specific settings files (e.g., .claude/settings.json for hooks)
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
- `review start/add-finding/close-finding/reopen-finding/set-fix-note/approve/status`
- `lint` / `clear` — validate schema / delete session.yaml
- `freeze <name>` — write plan to `.spek/plans/<name>.yaml` and delete session; fails if no steps, build notes present, or any step done
- `load <path>` — create session from plan file; updates split index to `in_progress` if sub-plan path

## spek plan subcommands

`spek plan` command group. Reads/writes `.spek/plans/<name>.yaml`. Name can be bare or `<split>/<name>`.

- `create <name> <goal>` — create plan file; registers in split index if sub-plan path
- `read <name>` — print goal, steps, notes
- `goal <name> <text>` — overwrite goal
- `add-step <name> <key> <text>` / `edit-step` / `remove-step`
- `note <name> <text>` / `edit-note` / `remove-note` (auto-keyed pn1/pn2/…)

## spek split subcommands

`spek split` command group. Reads/writes `.spek/plans/<name>/index.yaml`.

- `create <name> <goal>` — create split with index.yaml
- `list` — enumerate splits in `.spek/plans/`
- `status <name>` — show goal and each sub-plan's status

## spek todo subcommands

Full `spek todo` command group. Reads/writes `.spek/todo.yaml`. `section add` auto-creates the file on first call.

- `status [--section <key>] [<text>]` / `search <terms>...`
- `add --section <key> <text>` / `remove --section <key> <text>`
- `section status/search/add [--allow-exists] <key> <name>`
- `lint`

## spek module subcommands

- `spek module edit` — interactive checkbox picker (was bare `spek module`; no longer invoked without subcommand)
- `spek module list [--json]` — lists all available modules across all namespaces; `--json` outputs `[{name, description, active, source}]` for AI consumption (`source` is the namespace name)
- `spek module set [--sync] <module>...` — non-interactive full replacement of the module list; validates names; intended for AI agents

## Key concepts

- **module** — a single markdown spec file; plain path (e.g. `git/commit-base`) defaults to the `spek` namespace; external modules use `ns::bare/path` syntax (e.g. `mywork::python/style`)
- **namespace** — a named source directory declared in `~/.spek/settings.yaml` or `spek.yaml.sources`; `"spek"` always resolves to the installed repo's `specs/` unless overridden
- **stance** — a YAML file listing modules; inert until activated via `/spek-stance`
- **profile** — a YAML file listing modules and stances; resolved recursively at `spek init` or `spek profile apply`
- **active vs inert** — a module in `spek.yaml.modules` → written to AI rules; a module only referenced by a stance → copied to `.spek/modules/` only, not emitted until the stance is activated

## Non-obvious

- Output type (`rule` vs `skill`) is declared in spec file frontmatter; frontmatter is stripped before writing output
- Rule and skill output paths are namespace-prefixed: `.claude/rules/{ns}/{bare}.md` and `.claude/skills/{ns}/{bare}/SKILL.md`; `spek.name` override is still respected and produces a flat name as before
- Skills require an explicit `spek.name` in frontmatter — `render_module` raises `ValueError` if absent, preventing path-like qualified names from appearing as the Claude skill name
- `skill` output for Claude is written as `.claude/skills/<name>/SKILL.md` with a YAML frontmatter block (`description`, `argument-hint`, and any `integrations.claude` keys except `hooks`)
- Windsurf converts skills to workflows: `.windsurf/workflows/<name>.md` with `description` frontmatter only (no `argument-hint`/`args`)
- Windsurf rules are flattened (path separators replaced with `--`) and require a `trigger` field in frontmatter (defaults to `always_on`, override via `integrations.windsurf.trigger`)
- Hook declarations in `integrations.claude.hooks` frontmatter accumulate across all modules and are written to `.claude/settings.json` by `render_settings`; the file is fully spek-managed (overwritten each sync, deleted by `spek destroy`) — user-managed overrides belong in `.claude/settings.local.json`
- Whether a module is always-active or stance-only is determined entirely by its presence in `spek.yaml.modules`, not by anything in the file itself
- `_metadata.py` version is `"0.0.0"` in the repo — CI rewrites it from the git tag at build time; do not edit manually
- `spek.yaml` is for *target projects* — this repo's `.spek/spek.yaml` is its own dogfooded config
- `.spek/modules/` and `.spek/stances/` in target projects are committed — AI output can be regenerated without the upstream spek repo
- Session state is now `.spek/session.yaml` (committed); todo backlog is `.spek/todo.yaml` (committed); `.spek/TODO.md` has been deleted; `.spek/SESSION.md` is no longer created by any code path
- `commands/session/` and `commands/todo/` are packages (one module per subgroup) rather than single files
- Do not edit `.claude/*`, `.windsurf/*` or any other tool-specific files directly. Those files are generated by spek, if you ever need to edit rules or skills or settings, you should be looking at the upstream specs, python code or other generators.

## Working in this repo — avoid confusing `specs/` and `.spek/`

This repo dogfoods spek, so it contains **both** the spec library **and** a `.spek/` directory for its own sessions.

| Directory | What it is | When to edit |
|---|---|---|
| `specs/` | The distributable module library — source of truth | Adding or changing spec content for users of spek |
| `.spek/modules/` | Synced copies of whichever modules this project uses | Never edit directly — regenerated by `spek sync` |
| `.spek/` (other files) | Session state, todo, structure for this project | Session workflow (session.yaml, todo.yaml) |

**Rule:** if a task involves spec content (guidelines, rules, conventions shipped to users), edit files under `specs/`. If a task involves this project's own session or docs, edit files under `.spek/`. Never edit `.spek/modules/` by hand.

**Sync timing:** `just sync` is run at the user's discretion — they may choose to sync mid-session or wait until after the retro. During a session, `.spek/modules/` may intentionally lag `specs/`; do not flag this as an error.

Before writing, editing or planning a spec, run `spek ref read spek/specs`. Before writing, editing or planning a reference entry, run `spek ref read spek/references`.
