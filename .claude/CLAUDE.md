# spek

A personal CLI tool for managing AI-assisted development conventions across projects.

## What it does

- Maintains a central git repo of modular spec files (`specs/`) and stance definitions (`stances/`)
- Initializes new projects via Q&A (picks integrations, profile, modules, stances)
- Keeps a committed local copy of all needed spec files in `.spek/modules/` and stance configs in `.spek/stances/`; generates AI tool output (rules, commands) from that copy
- Provides a 4-step dev workflow via slash commands: `/spek-define` → `/spek-plan` → `/spek-implement` → `/spek-retro`
- Supports on-demand behavioral stances via `/spek-stance`
- Manages session state in `.spek/SESSION.md` (gitignored) and work history in `.spek/CHANGELOG.md` (committed)

## Repo layout

```
specs/           # Spec module library, organized by concern
  ai/            # AI behavioral conventions, split into subdirs:
    style/       #   assume-and-proceed, confirm-before-acting, stay-in-scope
    communication/ # prefer-brevity, explain-reasoning
    analysis/    #   find-problems, surface-risks, challenge-premise
    coding/      #   prefer-reuse, verify-before-use
  code/          # language-agnostic coding conventions (hygiene)
  config/        # configuration conventions (base; dotnet/python planned)
  docs/          # readme, structure, session, changelog, todo conventions
  git/           # commit-base/long/short, branch-base/trunk/feature
  persistence/   # sqlite, postgres, redis
  python/
    dependencies/
    frameworks/  # fastapi, flask
    models/      # dataclasses, pydantic, dicts, sqlmodel
    testing/
  workflow/      # spek-define/plan/implement/retro/stance skill specs
stances/         # Stance definitions (YAML files listing module paths)
profiles/        # Named bundles of modules + stances (init presets)
  base/
  python/
src/spek/
  _metadata.py   # __version__ = "0.0.0" — overwritten by CI from git tag
  cli.py         # Click entrypoint
  commands/      # init, sync, profile, local subcommands
  core/          # config.py, repo.py, render.py, profiles.py, yaml_utils.py
.spek/
  spek.yaml      # project config: modules, stances, local paths
  CHANGELOG.md   # committed — log of completed work
  TODO.md        # committed — project backlog
  SESSION.md     # gitignored — current session notes
  modules/       # populated by spek sync — committed local copy of spec files
  stances/       # populated by spek sync — committed local copy of stance configs
  local/
    modules/     # project-local spec modules
    stances/     # project-local stances
.claude/
  CLAUDE.md      # this file
justfile         # dev task runner (use just, not uv directly)
pyproject.toml
```

## Dev setup

```bash
just install     # uv pip install -e .
spek --help
```

Use `just` for routine dev tasks:

```
just install      # install in editable mode
just install-dev  # install with dev extras (pytest etc.)
just test         # run test suite
just test-cov     # run tests with coverage report
```

## Adding dependencies

Use `uv add` — never manually write version constraints:

```bash
uv add <package>                    # adds to [dependencies]
uv add --optional dev <package>     # adds to [project.optional-dependencies] dev
```

uv resolves the latest compatible version and writes it to `pyproject.toml`. Commit `uv.lock` for reproducible installs.

## Dev workflow

spek dogfoods its own 4-step convention:

| Step | Command | Action |
|---|---|---|
| 1. Define | `/spek-define` | Articulate and record the session goal in `.spek/SESSION.md` |
| 2. Plan | `/spek-plan` | Design the approach; get approval before writing code |
| 3. Implement | `/spek-implement` | Execute the agreed plan |
| 4. Review *(optional)* | `/spek-review` | Evaluate the implementation for problems and plan/spec faithfulness |
| 5. Retrospective | `/spek-retro` | Log completed work to `.spek/CHANGELOG.md`; clear `.spek/SESSION.md` |

## Session files

| File | Committed | Purpose |
|---|---|---|
| `.spek/SESSION.md` | No (gitignored) | In-progress goal, plan, and active stance |
| `.spek/CHANGELOG.md` | Yes | Log of completed work, updated each session |
| `.spek/TODO.md` | Yes | Project backlog |
| `.spek/STRUCTURE.md` | Yes | Living map of the codebase |

## Spec module output types

Spec files declare their output type in YAML frontmatter:

```markdown
---
spek:
  output: command   # → .claude/commands/ for claude
---
```

Only two output types exist: `rule` (default, no frontmatter needed) and `command`. There is no `behavior` or `stance` output type — those concepts no longer exist at the file level.

Whether a module becomes an always-active rule or stays inert is determined entirely by `spek.yaml`:
- Listed in `modules:` → written to `.claude/rules/` (or `.claude/commands/`)
- Referenced only by a stance's `modules:` list → copied to `.spek/modules/` only, activated on demand via `/spek-stance`

Frontmatter is stripped before writing output files.

## spek.yaml format (written into target projects, not this repo)

```yaml
meta:
  spek_version: "0.1.0"   # spek CLI version that wrote this file
  spek_sha: "abc1234"      # SHA of spek HEAD at last sync (informational only)
  integrations:            # one or more: claude, windsurf
    - claude
  profile: "python/cli"    # omitted if no profile was used
modules:                   # always-active rules/commands
  - git/commit-base
  - python/style
  - python/dependencies/uv
  - workflow/spek-define
stances:                   # omitted if empty; names from stances/ dir
  - autonomous
  - collaborative
local_modules:             # omitted if empty; paths relative to project root
  - .spek/local/modules/my-conventions.md
local_stances:             # omitted if empty; paths relative to project root
  - .spek/local/stances/my-stance.yaml
```

## Target project layout (after spek sync)

```
myproject/
  .spek/
    spek.yaml              # config: modules, stances, local paths
    SESSION.md             # gitignored — current session notes
    CHANGELOG.md           # committed — log of completed work
    TODO.md                # committed — project backlog
    STRUCTURE.md           # committed — living map of the codebase
    modules/               # committed — all synced spec files (direct + stance deps)
    stances/               # committed — synced stance YAML configs
    local/
      modules/             # project-local spec modules (committed)
      stances/             # project-local stances (committed)
  .claude/
    CLAUDE.md              # project conventions (hand-written)
    rules/                 # generated rule files (gitignored)
    commands/              # generated skill files (gitignored)
```

## Supported AI tool outputs

| Tool | Rules path | Commands path |
|---|---|---|
| `claude` | `.claude/rules/<module>.md` | `.claude/commands/<module>.md` |
| `windsurf` | `.windsurf/rules/<module>.md` | `.windsurf/rules/<module>.md` |

## Versioning

Semver via git tags. The version lives in `src/spek/_metadata.py` as `__version__ = "0.0.0"`.
The CI/CD pipeline (GitLab) rewrites this file from the git tag before building/publishing.
Do not manually edit `_metadata.py` or set the version in `pyproject.toml`.

## Key design constraints

- No vendor lock-in — spec source files are tool-agnostic markdown; output is generated per AI tool
- Local copy as source of truth — `.spek/modules/` and `.spek/stances/` are committed, so AI output can be regenerated without the upstream spek repo
- Everything backed by git — both this repo and target projects
