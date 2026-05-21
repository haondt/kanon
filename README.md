# spek

CLI for managing AI-assisted development conventions across projects.

## Dependencies

- [uv](https://docs.astral.sh/uv/)
- [just](https://just.systems/)

## Quick start

```bash
git clone https://github.com/haondt/spek
cd spek
just install
```

```bash
# In a new project directory
spek init
spek sync
```

Commit `.spek/spek.yaml`, `.spek/modules/`, and `.spek/stances/` — your project's spec config is now self-contained.

Your AI agent now has the dev workflow commands available:

```
/spek-define   start a session — articulate and record the goal
/spek-plan     design the approach and get approval before coding
/spek-implement execute the agreed plan
/spek-retro    log completed work and close the session
```

## Overview

spek maintains a central library of markdown spec files covering coding conventions, tool usage, and model behavior. Projects define a `.spek/spek.yaml` file, which details which spec files to include. `spec sync` copies those files into the project and generates AI tool integrations (rules and slash commands).

### Lexicon

| Term | Meaning |
|---|---|
| **module** | A single markdown spec file; path relative to `specs/` (e.g. `git/commit-base`) |
| **profile** | A named bundle of modules and stances. `spek.yaml` can be (re)generated using a profile |
| **stance** | A named set of modules that can be temporarily activated with `/spek-stance` |
| **integration** | The collection of files that spek generates to import specs into AI tools (`claude`, `windsurf`, etc.) |

## Usage

```bash
spek init                       # set up a project
spek sync                       # reconcile local copies and regenerate integrations
spek sync --pull                # force-refresh all modules from upstream
spek profile list               # list available profiles
spek profile apply [name]       # re-resolve and apply a profile
spek local module <name>        # create a project-local spec module
spek local stance <name>        # create a project-local stance
spek destroy                    # remove all spek-managed files from a project
```

See `spek --help` or `spek <command> --help` for full options.

<details>
<summary>AI slash commands</summary>

**Workflow**

| Command | Description |
|---|---|
| `/spek-define` | Start a session — articulate and record the goal in `SESSION.md` |
| `/spek-plan` | Design the approach; get approval before writing code |
| `/spek-implement` | Execute the agreed plan |
| `/spek-review` | (Optional) review the implementation for problems before closing the session |
| `/spek-retro` | Log completed work to `CHANGELOG.md`; clear `SESSION.md` |

**Extras**

| Command | Description |
|---|---|
| `/spek-stance` | Activate a behavioral stance for the session |
| `/spek-think` | Enter brainstorm mode — AI discusses ideas without taking action |
| `/spek-detour` | Make a quick out-of-scope edit without going through the full workflow |

</details>

<details>
<summary>spek.yaml format</summary>

```yaml
meta:
  spek_version: "1.0.0"
  spek_sha: "abc1234"      # SHA at last sync — informational only
  integrations:
    - claude
  profile: "python/cli"    # omitted if no profile was used
modules:                   # always-active rules/commands
  - git/commit-base
  - python/style
  - workflow/spek-define
stances:                   # omitted if empty
  - autonomous
  - collaborative
local_modules:             # omitted if empty; paths relative to project root
  - .spek/local/modules/my-conventions.md
local_stances:             # omitted if empty
  - .spek/local/stances/my-stance.yaml
```

</details>

## Development

```bash
just test
```
