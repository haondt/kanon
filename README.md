# spek

A package manager for AI coding conventions — define them once in a central library, subscribe from every project.

Most AI coding tools let you drop a rules file into each project. That works until you have a dozen projects and the rules drift apart. spek manages a central library of spec modules; projects subscribe to a subset via `spek.yaml`, and `spek sync` pulls them into committed local copies and generates AI tool integrations for each configured tool.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)

## Quick start

```bash
uv tool install haondt-spek
```

```bash
# In a new project directory
spek init
spek sync
```

Commit `.spek/spek.yaml`, `.spek/modules/`, and `.spek/stances/` — your project's spec config is now self-contained.

## AI tool configuration

### Windsurf

To allow the AI to run spek commands without confirmation, add the following to Windsurf's allowlist:

- `spek ref *`
- `spek session *`
- `spek todo *`
- `spek module list`

This enables the AI to auto-execute these spek commands during workflow skills without requiring approval for each invocation.

## Overview

spek maintains a library of spec modules — markdown files covering coding conventions, git behavior, AI behavioral rules, and more. Projects declare which modules they want in `.spek/spek.yaml`; `spek sync` copies them into committed local files and generates AI tool integrations. The same source modules produce `.claude/rules/` for Claude Code, `.windsurf/rules/` for Windsurf, and so on — one config, multiple tools.

### Lexicon

| Term | Meaning |
|---|---|
| **module** | A single markdown spec file; path relative to `specs/` (e.g. `git/commit-base`) |
| **profile** | A named bundle of modules and stances — useful for consistent bootstrapping across projects of the same type (e.g. `python/cli`) |
| **stance** | A named set of modules activatable on demand via `/spek-stance`; use when you need the AI to behave differently for a specific task without permanently changing your config |
| **integration** | The AI tool output files that spek generates from your modules (`claude`, `windsurf`, etc.) |

## Skills

The workflow skills enforce a structured session lifecycle. Each step is a checkpoint where you can review and adjust before the AI proceeds — goal before planning, plan before coding, implementation before closing.

**Workflow**

| Command | Description |
|---|---|
| `/spek-sketch` | (Optional) Clarify a fuzzy goal — skip if the goal is already concrete |
| `/spek-plan` | Design the approach; get approval before writing code |
| `/spek-build` | Execute the agreed plan |
| `/spek-review` | (Optional) review the implementation for problems before closing the session |
| `/spek-fix` | (Optional) evaluate and fix findings surfaced by `/spek-review` |
| `/spek-retro` | Repo housekeeping (update `README.md`, todos, `STRUCTURE.md`); clear `SESSION.md` |

**Extras**

| Command | Description |
|---|---|
| `/spek-stance` | Activate a behavioral stance for the session |
| `/spek-think` | Enter brainstorm mode — AI discusses ideas without taking action |
| `/spek-detour` | Make a quick out-of-scope edit without going through the full workflow |
| `/spek-amend` | Amend the current session goal or plan in place |
| `/spek-todo` | Add an item to the project backlog |
| `/spek-onboard` | Onboard an existing project: write STRUCTURE.md, select modules, extract TODOs |

## Usage

```bash
spek init                       # set up a project
spek sync                       # reconcile local copies and regenerate integrations
spek sync --pull                # force-refresh all modules from upstream
spek profile list               # list available profiles
spek profile apply [name]       # re-resolve and apply a profile
spek module edit                # re-select modules interactively
spek module list                # list all available modules with descriptions
spek module set <module>...     # non-interactively set modules (full replacement)
spek local module <name>        # create a project-local spec module
spek local stance <name>        # create a project-local stance
spek destroy                    # remove all spek-managed files from a project
spek ref search [--json] [-n N] [--match-all] <term>...  # search the reference library (upstream + .spek/local/references/)
spek ref read [--json] <name>                            # read a reference entry
```

See `spek --help` or `spek <command> --help` for full options.

<details>
<summary>spek.yaml format</summary>

```yaml
meta:
  spek_version: "1.0.0"
  spek_sha: "abc1234"      # SHA at last sync — informational only
  integrations:
    - claude
  profile: "python/cli"    # omitted if no profile was used
modules:                   # always-active rules/skills
  - git/commit-base
  - python/style
  - workflow/spek-sketch
stances:                   # omitted if empty
  - autonomous
  - collaborative
local_modules:             # omitted if empty; short names like regular modules
  - my-conventions
local_stances:             # omitted if empty
  - .spek/local/stances/my-stance.yaml
```

</details>

## Onboarding an existing project

To adopt spek in a project that already has code:

```bash
spek init      # select integrations, profile, and modules
spek sync      # copy spec files and generate AI tool output
```

Then in your AI coding tool:

```
/spek-onboard
```

`/spek-onboard` crawls the project to understand the tech stack and structure, writes `.spek/STRUCTURE.md`, proposes an appropriate module selection for your approval, applies it, and extracts any inline `TODO:` comments into `.spek/TODO.md`.

## Development

```bash
just test
```
