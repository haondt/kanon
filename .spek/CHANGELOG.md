# Changelog

## 2026-05-20 (session 15)

- `specs/workflow/spek-amend.md` — new `/spek-amend` skill: updates SESSION.md in place mid-session (goal, plan, or both); infers intent from invocation args → conversation context → interactive prompt; logs change under `## Amendments`
- `profiles/base/workflow.yaml` and `.spek/spek.yaml` — registered `workflow/spek-amend`
- Detour: `specs/workflow/base.md` — added rule: never advance to the next workflow step automatically; each step requires explicit user invocation

## 2026-05-20 (session 14)

- `src/spek/commands/module.py` — new `spek module` command group: picker (questionary checkbox, pre-checked from `spek.yaml`, type-to-filter) and `spek module list` (all available modules with descriptions and selection markers); `--sync` flag runs sync after saving
- `src/spek/core/modules.py` — new: `list_modules(repo_path)` extracted from `scaffold.py`; shared by `init` and `module`
- `src/spek/core/render.py` — added `description: str | None = None` to `_SpekMeta` (nested under `spek:` in frontmatter, alongside `output` and `name`)
- `specs/**/*.md` — added `spek.description` frontmatter to all 52 spec files (short descriptions, ≤8 words, double-quoted to avoid YAML colon ambiguity)
- Post-plan fix: description initially placed at top-level `ModuleFrontmatter`; moved inside `spek:` block for consistency with `output`/`name`
- Post-plan fix: unquoted descriptions containing `: ` caused YAML parse errors; all values now double-quoted

## 2026-05-20 (session 13)

- `src/spek/commands/scaffold.py` — replaced all three `spek init` text prompts with `questionary` pickers: integrations (checkbox), profile (select with "none" option), modules (checkbox with search filter, pre-checked from resolved profile)
- `pyproject.toml` / `uv.lock` — added `questionary>=2.1.1` as runtime dependency
- All three pickers use `use_jk_keys=False` for consistency; required on the modules picker anyway since `use_search_filter=True` and j/k conflict
- Post-review fix: `use_jk_keys=False` added to integrations and profile pickers to match the modules picker
- Detour: added rule to `specs/ai/style/confirm-before-acting.md` — when a change breaks an established pattern, consider whether to propagate it rather than leave a one-off inconsistency

## 2026-05-20 (session 12)

- `src/spek/commands/destroy.py` — new `spek destroy` command; removes `.spek/` and all configured integration output dirs; prompts for confirmation (default no); `--yes`/`-y` skips prompt
- `src/spek/cli.py` — registered `destroy` command
- `tests/test_destroy_cli.py` — 6 tests covering removal, preservation of hand-written files, no-config exit, confirmation prompt, and abort on "no"
- Note: planned "Nothing to remove" branch was unreachable (`.spek/` always exists when `spek.yaml` does); removed the dead branch and dropped the corresponding test

## 2026-05-20 (session 11)

- `specs/workflow/spek-retro.md` — step 1 now handles missing SESSION.md by falling back to `git diff HEAD` to derive what was done

## 2026-05-20 (session 10)

- Rewrote `README.md` to follow the `docs/readme` spec: combined quick start, overview with lexicon, collapsible spek.yaml and AI commands sections, dependencies section, lean development section
- `justfile` — replaced runtime-only `install` (uv sync) with `uv tool install --editable .`; `install-dev` and `test` unchanged

## 2026-05-20 (session 9)

- Added `specs/workflow/spek-detour.md` — new `/spek-detour` command; makes a quick out-of-scope edit immediately, logs a one-liner to `## Detours` in SESSION.md if a session is active, skips logging otherwise
- `profiles/base/workflow.yaml` — added `workflow/spek-detour`

## 2026-05-20 (session 8)

- Added `specs/workflow/spek-think.md` — new `/spek-think` command; enters a non-actionary brainstorming mode for the remainder of the conversation; exits on any other spek command or natural conversation ender
- `profiles/base/workflow.yaml` — added `workflow/spek-think`
- `specs/workflow/spek-plan.md` — added instruction to write the full plan detail into SESSION.md at approval time, not just a summary table
- Aside: `specs/workflow/spek-review.md` updated to record review findings in SESSION.md (carried over from prior session, committed with session 7)

## 2026-05-20 (session 7)

- `specs/workflow/spek-review.md` — added rule to **Code problems** section: only report findings that require action; silence means clean. Prevents noise from investigated-and-acceptable items appearing in review output.

## 2026-05-20 (session 6)

- `render.py` — added optional `name` field to `_SpekMeta`; when set, used as the output filename stem instead of the path-derived `dir--name` form
- All six workflow command specs (`spek-define`, `spek-plan`, `spek-implement`, `spek-review`, `spek-retro`, `spek-stance`) now set `name: spek-*` in frontmatter — they appear as `/spek-define` etc. in Claude Code instead of `/workflow--spek-define`
- Added `test_sync_command_name_override` to `tests/test_sync_cli.py`
- Minor: `render_module` now uses `meta.spek.output` directly instead of calling `output_type()` (which re-parsed frontmatter); no behavior change
- Moved venv from `.venv/` to `venv/` to match `python/venv` rule; updated `.gitignore`
- Rewrote `justfile` to use `UV_PROJECT_ENVIRONMENT=venv` in `install`/`install-dev`, add idempotent `venv` recipe, route `test`/`test-cov` through `venv/bin/pytest`
- `specs/workflow/spek-review.md` — added step 5: append review findings and verdict to `.spek/SESSION.md` under a `## Review` heading

## 2026-05-20 (session 5)

- Added `/spek-review` workflow skill — optional step between implement and retro; reviews plan faithfulness, spec compliance, and code problems; ends with a three-way verdict; read-only by default
- `git/commit-base` — added rule: never create a commit unless explicitly asked
- `spek-review` scope clarified: review everything changed, skip only files with no meaningful logic (generated code, lockfiles, vendored deps)
- `spek init` now writes `.spek/.gitignore` containing `SESSION.md`, so SESSION.md is gitignored at the project level rather than relying on the root `.gitignore`

## 2026-05-20 (session 4)

Major expansion of the spec module library. All changes are to `specs/`, `stances/`, and `profiles/` — no CLI changes.

**AI specs reorganized**
- Split `specs/ai/` into four subdirectories: `style/`, `communication/`, `analysis/`, `coding/`
- Removed `architect` stance; merged `reviewer` + `skeptic` into `critic`
- Stances list collapsed to three: `autonomous`, `collaborative`, `critic` — moved from `base/ai` profile to `base/base`
- Several modules merged to reduce overlap: `propose-before-implement` + `confirm-before-acting`, `prefer-reuse` + `seek-prior-art`, `prefer-momentum` + `assume-and-proceed`
- Deleted: `systems-thinking`, `propose-before-implement`, `prefer-momentum`, `seek-prior-art`

**Git specs broken up**
- Replaced single `git/commit-style` with: `commit-base` (subject line rules), `commit-long` (body conventions), `commit-short` (no-body short commits), `branch-base` (never touch branches without instruction), `branch-trunk` (all work to main), `branch-feature` (verify on feature branch, short names)

**Python specs expanded**
- Added `python/venv.md` — always use `./venv`, all invocations via `./venv/bin/`
- Added `python/models/` — `dataclasses`, `pydantic`, `dicts`, `sqlmodel`
- Added `python/frameworks/` — `fastapi`, `flask` (each with sample app layout)
- Simplified `python/style.md` (removed prescriptive model/config guidance now covered by dedicated specs)
- Updated `python/config.md` — Config class pattern with module-level singleton
- Updated `python/dependencies/uv.md` — `uv venv venv` for venv creation, `uv sync`

**New general-purpose specs**
- `specs/config/base.md` — env vars, fail fast, `.env.example`, namespaced prefixes
- `specs/code/hygiene.md` — no commented-out code, no debug artifacts
- `specs/persistence/sqlite.md`, `postgres.md`, `redis.md` — per-medium conventions (parameterized queries, WAL mode, TTLs, etc.)

**Docs specs added**
- `specs/docs/session.md` — SESSION.md structure and conventions
- `specs/docs/changelog.md` — CHANGELOG.md format and writing guidelines
- `specs/docs/todo.md` — TODO.md structure, what belongs, inline TODO promotion (moved from `specs/workflow/todos.md`)

**Workflow specs simplified**
- `spek-define`, `spek-plan`, `spek-retro` — stripped inline format guidance for SESSION.md, CHANGELOG.md, TODO.md, STRUCTURE.md now that each has its own spec
- `spek-implement` — SESSION.md is now a living record: mark steps done, log assumptions/decisions/deviations as they happen; ends with a 2-3 sentence session summary and prompt to run `/spek-retro`
- `workflow/base.md` — removed trailing format notes now covered by doc specs

**Profiles updated**
- Added `python/base` — new intermediate profile (style, venv, dependencies, testing); `python/cli` and `python/webservice` now extend it
- `base/git` — updated to use new split git specs (`commit-base`, `commit-long`, `branch-base`)
- `base/base` — stances now included here instead of `base/ai`

## 2026-05-20 (session 3)

**Tests**
- Added `tests/` directory with 27 unit and CLI integration tests across 5 files:
  - `test_yaml_utils.py` — `load_yaml` with model type, `save_yaml` with `BaseModel`, roundtrip
  - `test_config.py` — `SpekConfig` load/save roundtrip; verifies empty lists and `None` are omitted from YAML
  - `test_profiles.py` — `resolve_profile` inheritance ordering, deduplication, circular dependency detection, missing profile error
  - `test_sync_cli.py` — rule output, frontmatter stripping, command routing, missing config error, stance-only modules not rendered
  - `test_local_cli.py` — `local module` and `local stance` create files and register in config; duplicate and missing-config error paths
  - `test_profile_cli.py` — `profile apply` with explicit name and recorded profile; error paths; `profile list` against real profiles
- Fixed `save_yaml` to use `exclude_defaults=True` instead of `exclude_none=True` — empty lists (`stances: []`, `local_modules: []`) were previously written to `spek.yaml` when they should be omitted (caught by test)
- Updated `justfile` to use `uv run pytest` instead of bare `pytest`

## 2026-05-20 (session 2)

**CLI refactoring**
- Renamed `spek scaffold` → `spek init`; renamed internal `lock_path`/`lock` variables to `config_path`/`config`
- Renamed `--upstream` → `--pull` on `spek sync`; removed `--record-sha` (SHA is now always recorded when `--pull` is used)
- Added `src/spek/core/yaml_utils.py` — centralizes all YAML I/O: `parse_yaml(str)`, `load_yaml(path[, model])`, `dump_yaml(data)`, `save_yaml(data, path)`
  - `load_yaml` accepts an optional Pydantic model type and calls `model_validate` automatically
  - `save_yaml`/`dump_yaml` accept either `dict[str, Any]` or a `BaseModel` (calls `model_dump(exclude_none=True)` automatically)
- Migrated all raw `yaml.safe_load` / `yaml.dump` calls across `config.py`, `profiles.py`, `render.py`, `sync.py` to use `yaml_utils`
- Added `ProfileSpec(BaseModel)` in `profiles.py` — replaces raw dict access for profile YAML files
- Added `ModuleFrontmatter` / `_SpekMeta` Pydantic models in `render.py` — replaces chained `.get()` calls for frontmatter parsing; `output_type()` now reads `meta.spek.output`
- `SpekConfig.save()` now passes `self` directly to `save_yaml`; `SpekConfig.load()` uses `load_yaml(path, cls)`

## 2026-05-20

Initial implementation of spek.

**CLI commands**
- `spek init` — interactive Q&A to write `.spek/spek.yaml` (integrations, profile, modules, stances)
- `spek sync` — reconcile `.spek/modules/` and `.spek/stances/` from upstream, generate AI tool output; `--pull` force-refreshes all files and records SHA
- `spek profile list` / `spek profile apply [name]` — list profiles, re-resolve and apply a profile; `--sync` flag runs sync immediately after
- `spek local module <name>` — create a project-local spec module and register it in `spek.yaml`; `--sync` flag
- `spek local stance <name>` — create a project-local stance YAML and register it in `spek.yaml`

**Spec module library** (`specs/`)
- `ai/` — 14 spec files covering always-active AI conventions (brevity, scope, reuse, caution, verification) and stance-activatable behavioral modules (assume-and-proceed, prefer-momentum, propose-before-implement, explain-reasoning, seek-prior-art, find-problems, challenge-premise, surface-risks, systems-thinking)
- `docs/` — readme and structure doc conventions
- `git/` — commit style
- `python/` — style, dependencies (base + uv), testing (base + pytest), async, config stubs
- `workflow/` — base workflow table, todos conventions, and five skills: `/spek-define`, `/spek-plan`, `/spek-implement`, `/spek-retro`, `/spek-stance`

**Stance system** (`stances/`)
- Five built-in stances: `autonomous`, `collaborative`, `reviewer`, `skeptic`, `architect`
- Each is a YAML file listing module paths; modules are synced to `.spek/modules/` and stay inert until `/spek-stance` activates them

**Profile system** (`profiles/`)
- `base/base` — extends ai + git + docs + workflow (the standard starting point)
- `base/ai`, `base/git`, `base/docs`, `base/workflow` — composable base profiles
- `python/cli`, `python/webservice` — extend `base/base` with Python-specific modules
- Profiles support `extends:` (recursive, deduplicated), `modules:`, and `stances:`

**Key design decisions**
- `.spek/modules/` and `.spek/stances/` are committed to target projects — AI output can be regenerated without the upstream spek repo
- No `output: behavior` or routing-by-filename — all spec files are plain markdown; whether a module is always-active or stance-only is determined entirely by `spek.yaml`
- Session state in `.spek/SESSION.md` (gitignored); work log in `.spek/CHANGELOG.md`; backlog in `.spek/TODO.md`; codebase map in `.spek/STRUCTURE.md`
