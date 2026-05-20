# spek

CLI for managing AI-assisted development conventions across projects.

spek maintains a central git repo of modular spec files and stamps them into target projects. Each project keeps a committed local copy of its spec files in `.spek/` — independent of the upstream repo once synced.

## Installation

```bash
git clone <this repo>
just install
```

## Quick start

```bash
# In a new project directory
spek init    # Q&A: pick integrations, profile, modules, and stances
spek sync    # pull specs into .spek/modules/, generate AI tool output
```

`spek.yaml` is written to your project as the resolved module and stance list. Commit it along with `.spek/modules/` and `.spek/stances/`.

## Commands

### `spek init`

Interactive Q&A that writes `spek.yaml`. Prompts for integrations, then a profile (which sets modules and stances) or individual module selection.

### `spek sync`

Reads modules and stances from `.spek/modules/` and `.spek/stances/` (committed local copies) and writes AI tool output. Missing files are automatically pulled from the upstream spek repo. Extras are pruned.

```bash
spek sync        # reconcile local copies and generate output
spek sync --pull # force-refresh all files from upstream and record SHA
```

Only modules listed in `spek.yaml.modules` are written as always-active rules/commands. Modules referenced only by stances are stored in `.spek/modules/` and stay inert until activated via `/spek-stance`.

| Integration | Rules | Commands |
|---|---|---|
| `claude` | `.claude/rules/` | `.claude/commands/` |
| `windsurf` | `.windsurf/rules/` | `.windsurf/rules/` |

### `spek profile list`

List all available profiles.

### `spek profile apply [name]`

Re-resolve a profile and update `modules:` and `stances:` in `spek.yaml`. Uses the profile recorded in `spek.yaml` if no name is given. `local_modules` and `local_stances` are preserved. Pass `--sync` to also run `spek sync` immediately.

### `spek local module <name>`

Create a new project-local spec module at `.spek/local/modules/<name>.md` and register it in `spek.yaml`. Pass `--sync` to also run `spek sync` immediately.

### `spek local stance <name>`

Create a new project-local stance at `.spek/local/stances/<name>.yaml` and register it in `spek.yaml`. Run `spek sync` afterwards so its module dependencies are pulled into `.spek/modules/`.

## spek.yaml

Written by `spek init`. Records the integrations, profile, modules, and stances:

```yaml
meta:
  spek_version: "1.0.0"
  spek_sha: "abc1234"      # SHA at last sync — informational only
  integrations:
    - claude
  profile: "python/cli"    # omitted if no profile was used
modules:                   # always-active rules/commands
  - git/commit-style
  - python/style
  - python/dependencies/uv
  - workflow/base
  - workflow/spek-define
stances:                   # omitted if empty
  - autonomous
  - collaborative
local_modules:             # omitted if empty; paths relative to project root
  - .spek/local/modules/my-conventions.md
local_stances:             # omitted if empty; paths relative to project root
  - .spek/local/stances/my-stance.yaml
```

## Project layout after sync

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

## Profiles

| Profile | Description |
|---|---|
| `base/base` | Core conventions for all projects (ai + git + docs + workflow) |
| `base/ai` | AI assistant behavioral conventions and stances |
| `base/git` | Git conventions |
| `base/docs` | Documentation conventions |
| `base/workflow` | Dev workflow skills |
| `python/cli` | Python CLI tool |
| `python/webservice` | Python web service or API |

Profiles support `extends:` and can specify both `modules:` and `stances:`:

```yaml
description: "My custom profile"
extends:
  - python/cli
modules:
  - some/extra-module
stances:
  - security
```

## Dev setup

```bash
git clone <this repo>
just install-dev
just test
```
