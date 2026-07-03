# Structure

CLI tool for managing AI-assisted development conventions across projects.

- Resolves kanons from external sources (`gh::`, `gl::`, local paths) and the built-in library
- Initializes target projects via Q&A (`kanon init`), stamping a resolved set of kanons and stances into `.kanon/`
- Syncs kanon files locally (`kanon sync`) and generates AI tool output (rules, skills); synced copies are gitignored
- Provides a session workflow: `/kanon-sketch` (optional) → `/kanon-plan` → `/kanon-build` → `/kanon-retro`
- Supports on-demand behavioral stances via `/kanon-stance`
- `/kanon-think` enters a non-actionary brainstorming mode for the remainder of the conversation
- `/kanon-detour` makes a quick out-of-scope edit without going through the full workflow
- `/kanon-todo` adds an item to `.kanon/todo.yaml`
- `/kanon-onboard` onboards an existing project: writes STRUCTURE.md, selects kanons via `kanon list --json` + user approval, applies with `kanon set --sync`, adds inline TODOs to `.kanon/todo.yaml`
- `/kanon-why` explains a specific AI decision (quotes the driving kanon or names the gap) and suggests a concrete fix to prevent recurrence
- `/kanon-audit` checks the repository against active kanons, writes findings to `.kanon/audit.md`, and walks triage one-by-one; retro cleans up the audit file

## Tech stack

Python CLI — Click, Pydantic, PyYAML. Dev: uv, just, pytest. Published via GitLab CI from git tags.

## Layout

```
kanons/          # built-in kanon module library — kanon-specific content only
  docs/          # structure.md convention
  systems/       # architectural context modules (systems/base is the behavioral entry point)
  tools/kanon/   # informational reference for kanon CLI tools (ref, kanons, todo, session, source)
  workflow/      # kanon session skill files (kanon-sketch/plan/build/review/fix/retro/stance/onboard/etc.)
profiles/        # YAML files — named kanon+stance bundles; only base/ remains (base, docs, workflow, tools)
.kanon/project/  # project-local content for this repo's dogfooded kanon instance
  references/    # on-demand reference entries searched via kanon ref (e.g. references.md, kanons.md)
src/kanon/
  cli.py         # Click entrypoint; registers all command groups
  commands/      # one file per subcommand: init, profile, local, kanons, source, cache, check, destroy, ref; session/, todo/, and sync/ are packages; _utils.py holds shared helpers (read_text_arg, read_text_arg_json for stdin/JSON input support)
  core/          # pure logic, no CLI dependency
.kanon/          # kanon's own session/project files (dogfooding)
```

## Core modules (`src/kanon/core/`)

- `config.py` — `KanonConfig` Pydantic model; `load()`/`save()` against `.kanon/kanon.yaml`; `sources: dict[str, str]` (raw key→value strings); `local_kanons`/`local_stances` are gone — project-local content is referenced via `project::` in `kanons`/`stances`; scheme constants: `ALIAS_SCHEME="alias"`, `KANON_SCHEME="kanon"`, `GITHUB_SCHEME="gh"`, `GITLAB_SCHEME="gl"`, `LOCAL_SCHEME="local"`; `VALID_SCHEMES`, `KANON_BUILTIN_ADDRESSES={"kanon","project","self"}`; also declares `OutputType`/`Integration` enums (`CLAUDE`, `CODEX`, `WINDSURF`, `DEVIN`, `OPENCODE`) and `KanonEnv` singleton (env-sourced config); `KanonEnv.sources_cache_path` cached property returns `~/.kanon/sources` by default, overridden by `KANON_SOURCES_CACHE_PATH`
- `settings.py` — `SourceSpec(BaseModel)` (`path: str` — unified path string, local or `gh::`/`gl::` remote); `GlobalSettings(BaseModel)` (`sources: dict[str, SourceSpec]`); `load_global_settings()` reads `~/.kanon/settings.yaml`, returns empty model if missing
- `sources/` — package; `hydrate_source_reference(ref)` classifies a `SourceReference` into `LocalSource`, `GitHubSource`, `GitLabSource`, `KanonSource`, `ProjectSource`, or `SelfSource`; `resolve_sources()` merges global + project sources into a keyed `SourcesDict`; `ParsedSource` union type; `AliasRef` placeholder resolved during cycle detection in `resolve_sources()`; `ParsedSource` base has `pull(force=False) -> PullResult` (NOOP default) and `cache_path() -> Path | None` (None default); `PullResult` enum (`CLONED`, `PULLED`, `CACHED`, `NOOP`) in `_base.py`; `GitHubSource` and `GitLabSource` extend `FilesystemSource`, override `cache_path()` and `pull()` using gitpython — cache lives under `KanonEnv.sources_cache_path / scheme / address[@ref]`; `_ensure_cloned()` gates on `(path / '.git').exists()` to handle partial clones
- `yaml_utils.py` — all YAML I/O: `load_yaml(path, model?)`, `save_yaml(data, path)`; also exports `FRONTMATTER_RE` (shared frontmatter regex); exports `_literal_representer`, `_enum_str_representer`, `_make_dumper(*enum_types)` for YAML serialization with block-literal strings and str-enum support
- `render/` — package; reads local kanon copies, strips frontmatter, writes AI tool output files; `_base.py` holds shared rendering helpers (`KanonRenderHelper`, Jinja handling, `DryCleanResult`, `KanonRenderer`); `_kanon.py` is the dispatcher/export layer (`render_kanon`, `render_rule`, `render_settings`, `render_bespoke_rules`, `dry_clean_all`, `clean_all`); per-tool implementations live in `_claude.py`, `_codex.py`, `_windsurf.py`, `_devin.py`, `_opencode.py`; skills require an explicit `kanon.name` — `ValueError` raised at render time if absent; `ClaudeKanonRenderer` writes rules to `.claude/rules/scheme/address/path.md` and skills to `.claude/skills/<name>/SKILL.md`; `CodexKanonRenderer` writes rules into a managed block in root `AGENTS.md` and skills to `.agents/skills/<name>/SKILL.md`; Windsurf and Devin flatten rule paths and convert skills to workflows; `OpenCodeKanonRenderer` mirrors Claude rule paths (`.opencode/rules/scheme/address/path.md`) and skills (`.opencode/skills/<name>/SKILL.md`)
- `kanons.py` — `list_kanons(kanons_dir)` enumerates all kanon files in a given directory
- `profiles.py` — `resolve_profile()` recursive resolution with deduplication; `ProfileSpec` model; built-in profiles under `profiles/base/` only (base, docs, workflow, tools); `Profile.load()` now accepts a `dealias: Callable[[SourcedResource], SourcedResource]` parameter for alias-aware circular-dependency detection
- `references.py` — `search_references(repo_path, terms, project_root?)` keyword search; `read_reference(repo_path, name, project_root?)` retrieves content; project refs in `.kanon/project/references/` shadow upstream on name collision; `ReferenceResult` model
- `session.py` — `SessionState` Pydantic model (goal, plan, build, review, amendments, detours, stance, `_meta`); load/save/lint; `_meta.next_key` tracks next stable key per namespace (`pn`, `bn`, `f`, `p`); `Finding` has required `type: FindingType` and `severity: FindingSeverity` fields; `ReviewPass` has `status: Literal['open','approved']`; YAML serialization helpers moved to `yaml_utils.py`; backing file `.kanon/session.yaml`
- `todo.py` — `TodoState` / `TodoSection` Pydantic models; load/save/lint; backing file `.kanon/todo.yaml`
- `utils.py` — `deep_merge(d1, d2, conflicts?)` — recursive dict merge with three conflict modes (`new`/`old`/`err`); list deduplication safe for unhashable types
- `local.py` — `create_project_ref(name, kind)` scaffolds a new project-local kanon or stance under `.kanon/project/`; `search_project_refs()` removed (superseded by `ProjectSource.search_references()`)

## Data flow

```
kanon init      → writes .kanon/kanon.yaml (kanons, stances, integrations, sources)
kanon sync      → resolves sources: merges ~/.kanon/settings.yaml + config.sources; adds "kanon" → upstream repo/kanons
               → copies kanon files from each source into .kanon/kanons/{scheme}/{address}/{path}.md
               → calls render/ to emit AI tool output (rules, skills, workflows) for each configured integration
               → writes tool-specific settings files (e.g., .claude/settings.json for hooks)
kanon sync --pull → first calls .pull(force=True) on each source referenced by active kanons/stances, then syncs as above
```

## kanon session subcommands

Full `kanon session` command group. Reads/writes `.kanon/session.yaml`. All reads emit file hash; all writes emit before/after hash.

- `start <goal>` — creates session.yaml; fails if exists
- `goal` / `status [--full]` — read goal or full state
- `plan status/add-step/check/uncheck/note/unnote`
- `amend goal/plan step/plan note/plan unnote/add-note/status`
- `build note/unnote/status`
- `detour add/status`
- `stance set/clear/status`
- `review start/add-finding/close-finding/reopen-finding/set-fix-note/approve/status`
- `lint` / `clear` — validate schema / delete session.yaml

## kanon todo subcommands

Full `kanon todo` command group. Reads/writes `.kanon/todo.yaml`. `section add` auto-creates the file on first call.

- `status [--section <key>] [<text>]` / `search <terms>...`
- `add --section <key> <text>` / `remove --section <key> <text>`
- `section status/search/add [--allow-exists] <key> <name>`
- `lint`

## kanon profile subcommands

- `kanon profile list` — list all available profiles across all sources
- `kanon profile search <terms>...` — keyword search across available profiles; all terms must match (case-insensitive); `--source` filters to one source; `--json` outputs `[{name, description}]`
- `kanon profile apply [name] [--replace]` — merge profile kanons/stances into kanon.yaml (additive by default); `--replace` discards existing kanons/stances and uses only the profile

## kanon top-level subcommands

- `kanon edit` — interactive checkbox picker
- `kanon list [--json]` — lists all available kanons across all sources; `--json` outputs `[{name, description, active, source}]` for AI consumption (`source` is the source name)
- `kanon set [--sync] <kanon>...` — non-interactive full replacement of the kanon list; validates names; intended for AI agents
- `kanon add [--sync] <kanon>...` — append kanons to the active list; errors on unknown or already-active
- `kanon remove [--sync] <kanon>...` — remove kanons from the active list; errors if not active
- `kanon search [--source <name>] <terms>...` — keyword search across available kanons; shows active status; `--source` filters to one source

## kanon source subcommands

- `kanon source add [--global] <name> <path>` — register a named source; `--global` writes to `~/.kanon/settings.yaml`, default writes to `.kanon/kanon.yaml`; local paths are expanded to absolute at add time; remote (`gh::`/`gl::`) sources are cloned immediately on add
- `kanon source pull [name]` — force-refresh remote source caches; no name → pulls all resolved sources referenced by active kanons/stances; name → alias or direct ref (e.g. `gh::org/repo`)
- `kanon source remove [--global] <name>` — remove a source from the appropriate config
- `kanon source status [--json]` — table of all sources with name, path, type (local/gh/gl), scope (global/project), and whether the local path resolves

## kanon cache subcommands

- `kanon cache status` — walks `KanonEnv.sources_cache_path`, lists each cached repo with scheme, path, and disk usage
- `kanon cache clear [name]` — no name → `shutil.rmtree` the entire cache dir; name → resolve alias or direct ref, clear only that source's `cache_path()`

## kanon check

- `kanon [--project-root <path>] check` — validates `kanon.yaml`: errors on kanons that don't resolve in any source, errors on local sources whose path doesn't exist; remote sources are validated via their cache (populated on first pull); exits non-zero on errors

## Key concepts

- **kanon reference** — three-part `scheme::address::path` (e.g. `kanon::kanon::git/commit-base`); abbreviated forms are canonical: bare path defaults to `kanon::kanon`, `project::path` = `kanon::project::path`, `alias-name::path` = `alias::alias-name::path`; `gh::`/`gl::`/`local::` always fully qualified
- **source** — identified by `scheme::address`; the `sources` dict in `resolve_sources()` is keyed by `scheme::address`; built-ins: `kanon::kanon` (repo), `kanon::project` (`.kanon/project/`), `kanon::self` (profile context only); user-declared sources become `alias::name` keys
- **`SourcedResource`** — 3-field dataclass `(source: SourceReference, path: str, args: dict[str, str | bool])`; `.args` holds rendering args parsed from the `[key=val,flag]` suffix on a kanon reference; `.as_string` is the shortest unambiguous form including any args suffix; `.as_path_string` is source+path without args (used for file paths and sync identity); `.as_fully_qualified_string` is the full canonical form including args
- **storage paths** — `.kanon/kanons/scheme/address/path.md` and `.kanon/stances/scheme/address/path.yaml`; render output paths: `.claude/rules/scheme/address/path.md`
- **`kanon::project`** — always injected (non-shadowable); points to `.kanon/project/` for project-local kanons/stances/profiles/refs; `project::name` in kanons/stances list means a locally-authored file — replaces the old `local_kanons`/`local_stances` fields
- **`kanon::self`** — stub (no parent context until profile hydration is wired); listing/searching returns empty; hydration raises `ValueError`
- **source key validation** — only `alias::*` and `kanon::kanon` are valid source declaration keys; `kanon::project`, `kanon::self`, and scheme-prefixed keys (`gh::`, `gl::`, `local::`) are rejected by `SourceReference.validate_as_key()` (called via `SourceReference.parse(validate_as_key=True)`)
- **stance** — a YAML file listing kanons; inert until activated via `/kanon-stance`
- **profile** — a YAML file listing kanons and stances; resolved recursively at `kanon init` or `kanon profile apply`
- **active vs inert** — a kanon in `kanon.yaml.kanons` → written to AI rules; a kanon only referenced by a stance → copied to `.kanon/kanons/` only, not emitted until the stance is activated

## Non-obvious

- Output type (`rule` vs `skill`) is declared in kanon file frontmatter; frontmatter is stripped before writing output
- Rule and skill output paths are namespace-prefixed: `.claude/rules/scheme/address/path.md` and `.claude/skills/<name>/SKILL.md`; `kanon.name` override is still respected and produces a flat name as before
- Skills require an explicit `kanon.name` in frontmatter — `render_kanon` raises `ValueError` if absent, preventing path-like qualified names from appearing as the Claude skill name
- `skill` output for Claude is written as `.claude/skills/<name>/SKILL.md` with a YAML frontmatter block (`description`, `argument-hint`, and any `integrations.claude` keys except `hooks`)
- Windsurf converts skills to workflows: `.windsurf/workflows/<name>.md` with `description` frontmatter only (no `argument-hint`/`args`)
- Windsurf rules are flattened (path separators replaced with `--`) and require a `trigger` field in frontmatter (defaults to `always_on`, override via `integrations.windsurf.trigger`)
- Devin integration mirrors Windsurf (output dirs `.devin/rules` and `.devin/workflows`, flattened rule paths, `trigger: always_on` frontmatter) — implemented in `DevinKanonRenderer` in `render/_kanon.py`
- OpenCode integration mirrors Claude rule paths (`.opencode/rules/scheme/address/path.md`) and skills (`.opencode/skills/<name>/SKILL.md`); settings written to `opencode.json` with `$schema` and `instructions` array — implemented in `OpenCodeKanonRenderer` in `render/_kanon.py`
- Hook declarations in `integrations.claude.hooks` frontmatter accumulate across all kanons and are written to `.claude/settings.json` by `render_settings`; the file is fully kanon-managed (overwritten each sync, deleted by `kanon destroy`) — user-managed overrides belong in `.claude/settings.local.json`
- Whether a kanon is always-active or stance-only is determined entirely by its presence in `kanon.yaml.kanons`, not by anything in the file itself
- `_metadata.py` version is `"0.0.0"` in the repo — CI rewrites it from the git tag at build time; do not edit manually
- `kanon.yaml` is for *target projects* — this repo's `.kanon/kanon.yaml` is its own dogfooded config
- `.kanon/kanons/` and `.kanon/stances/` are gitignored — regenerated by `kanon sync`; only `kanon.yaml`, `todo.yaml`, `session.yaml`, `STRUCTURE.md`, and `.kanon/project/` are committed
- `.kanon/TODO.md` and `.kanon/SESSION.md` are no longer created by any code path; session state lives in `session.yaml`, todo backlog in `todo.yaml`
- `commands/session/`, `commands/todo/`, and `commands/sync/` are packages (one file per subgroup) rather than single files; `core/render/` and `core/sources/` are also packages
- Do not edit `.claude/*`, `.windsurf/*` or any other tool-specific files directly. Those files are generated by kanon, if you ever need to edit rules or skills or settings, you should be looking at the upstream kanons, python code or other generators.

## Working in this repo — avoid confusing `kanons/` and `.kanon/`

This repo dogfoods kanon, so it contains **both** the kanon library **and** a `.kanon/` directory for its own sessions.

| Directory | What it is | When to edit |
|---|---|---|
| `kanons/` | Built-in kanon library (workflow, tools, systems, docs kanons only) | Adding or changing built-in kanon content |
| `profiles/` | Named kanon bundles for bootstrapping | Adding or changing profile definitions |
| `.kanon/kanons/` | Synced copies of whichever kanons this project uses (gitignored) | Never edit directly — regenerated by `kanon sync` |
| `.kanon/` (other files) | Session state, todo, structure for this project | Session workflow (session.yaml, todo.yaml) |

**Rule:** if a task involves built-in kanon content (workflow skills, tool references), edit files under `kanons/`. External kanon content (AI conventions, Python style, etc.) lives in an external source repo. If a task involves this project's own session or docs, edit files under `.kanon/`. Never edit `.kanon/kanons/` by hand.

**Sync timing:** `just sync` is run at the user's discretion — they may choose to sync mid-session or wait until after the retro. During a session, `.kanon/kanons/` may intentionally lag `kanons/`; do not flag this as an error.
