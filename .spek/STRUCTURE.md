# Structure

CLI tool for managing AI-assisted development conventions across projects.

- Resolves spec modules from external sources (`gh::`, `gl::`, local paths) and the built-in library
- Initializes target projects via Q&A (`spek init`), stamping a resolved set of modules and stances into `.spek/`
- Syncs spec files locally (`spek sync`) and generates AI tool output (rules, skills); synced copies are gitignored
- Provides a session workflow: `/spek-sketch` (optional) → `/spek-plan` → `/spek-build` → `/spek-retro`
- Supports on-demand behavioral stances via `/spek-stance`
- `/spek-think` enters a non-actionary brainstorming mode for the remainder of the conversation
- `/spek-detour` makes a quick out-of-scope edit without going through the full workflow
- `/spek-todo` adds an item to `.spek/todo.yaml`
- `/spek-onboard` onboards an existing project: writes STRUCTURE.md, selects modules via `spek module list --json` + user approval, applies with `spek module set --sync`, adds inline TODOs to `.spek/todo.yaml`

## Tech stack

Python CLI — Click, Pydantic, PyYAML. Dev: uv, just, pytest. Published via GitLab CI from git tags.

## Layout

```
specs/           # built-in spec module library — spek-specific content only
  docs/          # structure.md convention
  systems/       # architectural context modules (systems/base is the behavioral entry point)
  tools/spek/    # informational reference for spek CLI tools (ref, module, todo, session, source)
  workflow/      # spek session skill files (spek-sketch/plan/build/review/fix/retro/stance/onboard/etc.)
profiles/        # YAML files — named module+stance bundles; only base/ remains (base, docs, workflow, tools)
.spek/project/   # project-local content for this repo's dogfooded spek instance
  references/    # on-demand reference entries searched via spek ref (e.g. references.md, specs.md)
src/spek/
  cli.py         # Click entrypoint; registers all command groups
  commands/      # one file per subcommand: init, profile, local, module, source, cache, check, destroy, ref; session/, todo/, and sync/ are packages; _utils.py holds shared helpers (read_text_arg, read_text_arg_json for stdin/JSON input support)
  core/          # pure logic, no CLI dependency
.spek/           # spek's own session/project files (dogfooding)
```

## Core modules (`src/spek/core/`)

- `config.py` — `SpekConfig` Pydantic model; `load()`/`save()` against `.spek/spek.yaml`; `sources: dict[str, str]` (raw key→value strings); `local_modules`/`local_stances` are gone — project-local content is referenced via `project::` in `modules`/`stances`; scheme constants: `ALIAS_SCHEME="alias"`, `SPEK_SCHEME="spek"`, `GITHUB_SCHEME="gh"`, `GITLAB_SCHEME="gl"`, `LOCAL_SCHEME="local"`; `VALID_SCHEMES`, `SPEK_BUILTIN_ADDRESSES={"spek","project","self"}`; also declares `OutputType`/`Integration` enums, `AI_TOOL_OUTPUT_DIRS`, `AI_TOOL_SETTINGS_FILES`, `AI_TOOL_SPECIFIC_RULES`, and `SpekEnv` singleton (env-sourced config); `SpekEnv.sources_cache_path` cached property returns `~/.spek/sources` by default, overridden by `SPEK_SOURCES_CACHE_PATH`
- `settings.py` — `SourceSpec(BaseModel)` (`path: str` — unified path string, local or `gh::`/`gl::` remote); `GlobalSettings(BaseModel)` (`sources: dict[str, SourceSpec]`); `load_global_settings()` reads `~/.spek/settings.yaml`, returns empty model if missing
- `sources/` — package; `hydrate_source_reference(ref)` classifies a `SourceReference` into `LocalSource`, `GitHubSource`, `GitLabSource`, `SpekSource`, `ProjectSource`, or `SelfSource`; `resolve_sources()` merges global + project sources into a keyed `SourcesDict`; `ParsedSource` union type; `AliasRef` placeholder resolved during cycle detection in `resolve_sources()`; `ParsedSource` base has `pull(force=False) -> PullResult` (NOOP default) and `cache_path() -> Path | None` (None default); `PullResult` enum (`CLONED`, `PULLED`, `CACHED`, `NOOP`) in `_base.py`; `GitHubSource` and `GitLabSource` extend `FilesystemSource`, override `cache_path()` and `pull()` using gitpython — cache lives under `SpekEnv.sources_cache_path / scheme / address[@ref]`; `_ensure_cloned()` gates on `(path / '.git').exists()` to handle partial clones
- `yaml_utils.py` — all YAML I/O: `load_yaml(path, model?)`, `save_yaml(data, path)`; also exports `FRONTMATTER_RE` (shared frontmatter regex); exports `_literal_representer`, `_enum_str_representer`, `_make_dumper(*enum_types)` for YAML serialization with block-literal strings and str-enum support
- `render/` — package; reads local module copies, strips frontmatter, writes AI tool output files; `ModuleFrontmatter` parses `spek.description/output/name/args/integrations/preapproved_tools/template`; `output` and `template` are `Literal`-typed (`Literal["rule","skill"]` and `Literal["jinja"] | None`); when `template: jinja`, body is rendered through `_apply_jinja(body, context)` (Jinja2 `StrictUndefined`, `keep_trailing_newline=True`) with `modules` and `integrations` as sets before rule/skill branching; for `output: skill`, writes `<name>/SKILL.md` with generated YAML frontmatter (`description`, `argument-hint`/`args`, plus any keys from `integrations.<tool>` except `hooks`); Windsurf converts skills to workflows (`.windsurf/workflows/<name>.md` with description frontmatter); skills require an explicit `spek.name` — `ValueError` raised at render time if absent; `preapproved_tools` from spec frontmatter are merged into `allowed-tools` in the skill frontmatter; when `context: fork`, appends STRUCTURE.md preload commands to `allowed-tools` and injects a `## Project structure` shell-expansion block into the skill body; Windsurf rules are flattened (path separators replaced with `--`) and require a `trigger` field in frontmatter (defaults to `always_on`, override via `integrations.windsurf.trigger`); tool-specific rules declared in `config.AI_TOOL_SPECIFIC_RULES`; `render_tool_specific_rules(ai_tool, project_root)` writes the tool-specific rule file; `collect_hooks(content, ai_tool)` extracts hook declarations from frontmatter; `collect_preapproved_tools(content)` extracts rule-module `preapproved_tools`; `render_settings(hooks_by_event, project_root, ai_tool, preapproved_tools?)` writes `.claude/settings.json` with `permissions.allow` + hooks
- `modules.py` — `list_modules(specs_dir)` enumerates all spec files in a given directory
- `profiles.py` — `resolve_profile()` recursive resolution with deduplication; `ProfileSpec` model; built-in profiles under `profiles/base/` only (base, docs, workflow, tools)
- `references.py` — `search_references(repo_path, terms, project_root?)` keyword search; `read_reference(repo_path, name, project_root?)` retrieves content; project refs in `.spek/project/references/` shadow upstream on name collision; `ReferenceResult` model
- `session.py` — `SessionState` Pydantic model (goal, plan, build, review, amendments, detours, stance, `_meta`); load/save/lint; `_meta.next_key` tracks next stable key per namespace (`pn`, `bn`, `f`, `p`); `Finding` has required `type: FindingType` and `severity: FindingSeverity` fields; `ReviewPass` has `status: Literal['open','approved']`; YAML serialization helpers moved to `yaml_utils.py`; backing file `.spek/session.yaml`
- `todo.py` — `TodoState` / `TodoSection` Pydantic models; load/save/lint; backing file `.spek/todo.yaml`
- `utils.py` — `deep_merge(d1, d2, conflicts?)` — recursive dict merge with three conflict modes (`new`/`old`/`err`); list deduplication safe for unhashable types
- `local.py` — `create_project_ref(name, kind)` scaffolds a new project-local module or stance under `.spek/project/`; `search_project_refs()` removed (superseded by `ProjectSource.search_references()`)

## Data flow

```
spek init      → writes .spek/spek.yaml (modules, stances, integrations, sources)
spek sync      → resolves sources: merges ~/.spek/settings.yaml + config.sources; adds "spek" → upstream repo/specs
               → copies spec files from each source into .spek/modules/{scheme}/{address}/{path}.md
               → calls render/ to emit AI tool output (rules, skills, workflows) for each configured integration
               → writes tool-specific settings files (e.g., .claude/settings.json for hooks)
spek sync --pull → first calls .pull(force=True) on each source referenced by active modules/stances, then syncs as above
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

## spek todo subcommands

Full `spek todo` command group. Reads/writes `.spek/todo.yaml`. `section add` auto-creates the file on first call.

- `status [--section <key>] [<text>]` / `search <terms>...`
- `add --section <key> <text>` / `remove --section <key> <text>`
- `section status/search/add [--allow-exists] <key> <name>`
- `lint`

## spek module subcommands

- `spek module edit` — interactive checkbox picker (was bare `spek module`; no longer invoked without subcommand)
- `spek module list [--json]` — lists all available modules across all sources; `--json` outputs `[{name, description, active, source}]` for AI consumption (`source` is the source name)
- `spek module set [--sync] <module>...` — non-interactive full replacement of the module list; validates names; intended for AI agents
- `spek module add [--sync] <module>...` — append modules to the active list; errors on unknown or already-active
- `spek module remove [--sync] <module>...` — remove modules from the active list; errors if not active
- `spek module search [--source <name>] <terms>...` — keyword search across available modules; shows active status; `--source` filters to one source

## spek source subcommands

- `spek source add [--global] <name> <path>` — register a named source; `--global` writes to `~/.spek/settings.yaml`, default writes to `.spek/spek.yaml`; local paths are expanded to absolute at add time; remote (`gh::`/`gl::`) sources are cloned immediately on add
- `spek source pull [name]` — force-refresh remote source caches; no name → pulls all resolved sources referenced by active modules/stances; name → alias or direct ref (e.g. `gh::org/repo`)
- `spek source remove [--global] <name>` — remove a source from the appropriate config
- `spek source status [--json]` — table of all sources with name, path, type (local/gh/gl), scope (global/project), and whether the local path resolves

## spek cache subcommands

- `spek cache status` — walks `SpekEnv.sources_cache_path`, lists each cached repo with scheme, path, and disk usage
- `spek cache clear [name]` — no name → `shutil.rmtree` the entire cache dir; name → resolve alias or direct ref, clear only that source's `cache_path()`

## spek check

- `spek [--project-root <path>] check` — validates `spek.yaml`: errors on modules that don't resolve in any source, errors on local sources whose path doesn't exist; remote sources are validated via their cache (populated on first pull); exits non-zero on errors

## Key concepts

- **module reference** — three-part `scheme::address::path` (e.g. `spek::spek::git/commit-base`); abbreviated forms are canonical: bare path defaults to `spek::spek`, `project::path` = `spek::project::path`, `alias-name::path` = `alias::alias-name::path`; `gh::`/`gl::`/`local::` always fully qualified
- **source** — identified by `scheme::address`; the `sources` dict in `resolve_sources()` is keyed by `scheme::address`; built-ins: `spek::spek` (repo), `spek::project` (`.spek/project/`), `spek::self` (profile context only); user-declared sources become `alias::name` keys
- **`SourcedResource`** — 2-field dataclass `(source: SourceReference, path: str)`; `.source` is the `SourceReference` for sources-dict lookups; `.as_string` is the shortest unambiguous form
- **storage paths** — `.spek/modules/scheme/address/path.md` and `.spek/stances/scheme/address/path.yaml`; render output paths: `.claude/rules/scheme/address/path.md`
- **`spek::project`** — always injected (non-shadowable); points to `.spek/project/` for project-local modules/stances/profiles/refs; `project::name` in modules/stances list means a locally-authored file — replaces the old `local_modules`/`local_stances` fields
- **`spek::self`** — stub (no parent context until profile hydration is wired); listing/searching returns empty; hydration raises `ValueError`
- **source key validation** — only `alias::*` and `spek::spek` are valid source declaration keys; `spek::project`, `spek::self`, and scheme-prefixed keys (`gh::`, `gl::`, `local::`) are rejected by `SourceReference.validate_as_key()` (called via `SourceReference.parse(validate_as_key=True)`)
- **stance** — a YAML file listing modules; inert until activated via `/spek-stance`
- **profile** — a YAML file listing modules and stances; resolved recursively at `spek init` or `spek profile apply`
- **active vs inert** — a module in `spek.yaml.modules` → written to AI rules; a module only referenced by a stance → copied to `.spek/modules/` only, not emitted until the stance is activated

## Non-obvious

- Output type (`rule` vs `skill`) is declared in spec file frontmatter; frontmatter is stripped before writing output
- Rule and skill output paths are namespace-prefixed: `.claude/rules/scheme/address/path.md` and `.claude/skills/<name>/SKILL.md`; `spek.name` override is still respected and produces a flat name as before
- Skills require an explicit `spek.name` in frontmatter — `render_module` raises `ValueError` if absent, preventing path-like qualified names from appearing as the Claude skill name
- `skill` output for Claude is written as `.claude/skills/<name>/SKILL.md` with a YAML frontmatter block (`description`, `argument-hint`, and any `integrations.claude` keys except `hooks`)
- Windsurf converts skills to workflows: `.windsurf/workflows/<name>.md` with `description` frontmatter only (no `argument-hint`/`args`)
- Windsurf rules are flattened (path separators replaced with `--`) and require a `trigger` field in frontmatter (defaults to `always_on`, override via `integrations.windsurf.trigger`)
- Hook declarations in `integrations.claude.hooks` frontmatter accumulate across all modules and are written to `.claude/settings.json` by `render_settings`; the file is fully spek-managed (overwritten each sync, deleted by `spek destroy`) — user-managed overrides belong in `.claude/settings.local.json`
- Whether a module is always-active or stance-only is determined entirely by its presence in `spek.yaml.modules`, not by anything in the file itself
- `_metadata.py` version is `"0.0.0"` in the repo — CI rewrites it from the git tag at build time; do not edit manually
- `spek.yaml` is for *target projects* — this repo's `.spek/spek.yaml` is its own dogfooded config
- `.spek/modules/` and `.spek/stances/` are gitignored — regenerated by `spek sync`; only `spek.yaml`, `todo.yaml`, `session.yaml`, `STRUCTURE.md`, and `.spek/project/` are committed
- `.spek/TODO.md` and `.spek/SESSION.md` are no longer created by any code path; session state lives in `session.yaml`, todo backlog in `todo.yaml`
- `commands/session/`, `commands/todo/`, and `commands/sync/` are packages (one module per subgroup) rather than single files; `core/render/` and `core/sources/` are also packages
- Do not edit `.claude/*`, `.windsurf/*` or any other tool-specific files directly. Those files are generated by spek, if you ever need to edit rules or skills or settings, you should be looking at the upstream specs, python code or other generators.

## Working in this repo — avoid confusing `specs/` and `.spek/`

This repo dogfoods spek, so it contains **both** the spec library **and** a `.spek/` directory for its own sessions.

| Directory | What it is | When to edit |
|---|---|---|
| `specs/` | Built-in module library (workflow, tools, systems, docs specs only) | Adding or changing built-in spek spec content |
| `profiles/` | Named module bundles for bootstrapping | Adding or changing profile definitions |
| `.spek/modules/` | Synced copies of whichever modules this project uses (gitignored) | Never edit directly — regenerated by `spek sync` |
| `.spek/` (other files) | Session state, todo, structure for this project | Session workflow (session.yaml, todo.yaml) |

**Rule:** if a task involves built-in spec content (workflow skills, tool references), edit files under `specs/`. External spec content (AI conventions, Python style, etc.) lives in an external source repo. If a task involves this project's own session or docs, edit files under `.spek/`. Never edit `.spek/modules/` by hand.

**Sync timing:** `just sync` is run at the user's discretion — they may choose to sync mid-session or wait until after the retro. During a session, `.spek/modules/` may intentionally lag `specs/`; do not flag this as an error.

Before writing, editing or planning a spec, run `spek ref read spek/specs`. Before writing, editing or planning a reference entry, run `spek ref read spek/references`.
