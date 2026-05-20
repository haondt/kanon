# Changelog

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
