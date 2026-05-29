# spek

A package manager for AI coding conventions — subscribe to spec modules from any source, sync them into every project.

Most AI coding tools let you drop a rules file into each project. That works until you have a dozen projects and the rules drift apart. spek lets projects declare which spec modules they want via `spek.yaml` — pulling from external sources like GitHub repos or local directories — and `spek sync` copies them locally and generates AI tool integrations for each configured tool.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- [git](https://git-scm.com/)

## Quick start

```bash
git clone <this repo>
cd spek
uv tool install --editable .
```

```bash
# In a new project directory
spek init
spek sync
```

Commit `.spek/spek.yaml` — your project's spec config is now self-contained. Synced module files are gitignored and regenerated on demand.

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

`/spek-onboard` crawls the project to understand the tech stack and structure, writes `.spek/STRUCTURE.md`, proposes an appropriate module selection for your approval, applies it, and adds any inline `TODO:` comments it finds to `.spek/todo.yaml`.

## Concepts

spek manages spec modules — markdown files covering coding conventions, git behavior, AI behavioral rules, and more. Projects declare which modules they want in `.spek/spek.yaml`; `spek sync` fetches them from their sources and generates AI tool integrations. The same source modules produce `.claude/rules/` for Claude Code, `.windsurf/rules/` for Windsurf, and so on — one config, multiple tools.

| Term | Meaning |
|---|---|
| **module** | A single markdown spec file, identified by a reference `scheme::address::path` (e.g. `gh::org/specs::git/commit-base`); bare paths default to the built-in spek source |
| **source** | A named directory of spec modules — local path, `gh::org/repo`, or `gl::group/repo`; declared in `spek.yaml` or `~/.spek/settings.yaml` |
| **profile** | A named bundle of modules and stances — useful for consistent bootstrapping across projects of the same type |
| **stance** | A named set of modules activatable on demand via `/spek-stance`; use when you need the AI to behave differently for a specific task without permanently changing your config |
| **integration** | The AI tool output files that spek generates from your specs (`claude`, `windsurf`, etc.) |

## Skills

The workflow skills enforce a structured session lifecycle. Each step is a checkpoint where you can review and adjust before the AI proceeds — goal before planning, plan before coding, implementation before closing.

**Workflow**

| Command | Description |
|---|---|
| `/spek-sketch` | (Optional) Clarify a fuzzy goal — skip if the goal is already concrete |
| `/spek-plan` | Design the approach; get approval before writing code |
| `/spek-build` | Execute the agreed plan |
| `/spek-reconcile` | (Optional) Sync session state after work done outside `/spek-build` — marks plan steps done based on git diff |
| `/spek-review` | (Optional) Review the implementation for problems before closing the session |
| `/spek-fix` | (Optional) Evaluate and fix findings surfaced by `/spek-review` |
| `/spek-retro` | Repo housekeeping (update `README.md`, todos, `STRUCTURE.md`); clear `session.yaml` |

**Extras**

| Command | Description |
|---|---|
| `/spek-stance` | Activate a behavioral stance for the session |
| `/spek-think` | Enter brainstorm mode — AI discusses ideas without taking action |
| `/spek-detour` | Make a quick out-of-scope edit without going through the full workflow |
| `/spek-amend` | Amend the current session goal or plan in place |
| `/spek-todo` | Add an item to the project backlog |
| `/spek-onboard` | Onboard an existing project: write STRUCTURE.md, select modules, extract TODOs |

## Object references

Every module, stance, and profile is identified by a three-part reference:

```
scheme::address::path
```

| Part | Meaning |
|---|---|
| `scheme` | How the source is located (`spek`, `alias`, `gh`, `gl`, `local`) |
| `address` | The source identifier within the scheme (repo path, alias name, etc.) |
| `path` | Path to the file within the source, relative to `specs/` |

**Abbreviated forms** — most references can be shortened:

| Written | Expands to | Meaning |
|---|---|---|
| `git/commit-base` | `spek::spek::git/commit-base` | Built-in spek source |
| `mywork::python/style` | `alias::mywork::python/style` | Registered source by alias |
| `gh::org/repo::python/style` | *(already full)* | GitHub source, no alias needed |
| `project::my-module` | `spek::project::my-module` | Project-local file under `.spek/project/` |
| `self::python/style` | `spek::self::python/style` | Profile-internal: same source as the profile file |

**Special addresses** under the `spek` scheme:

| Reference | Points to |
|---|---|
| `spek::spek` | The built-in spek module library (`specs/` in this repo) |
| `spek::project` | The consuming project's own local content (`.spek/project/`) |
| `spek::self` | The profile's own source — only valid inside profile YAML files; rewritten to the profile's actual source at load time |

`self::` is how profiles in an external library reference their own sibling modules without hardcoding a source name:

```yaml
# profiles/python/cli.yaml in gh::myorg/myspecs
extends:
  - self::profiles/base        # → gh::myorg/myspecs::profiles/base
modules:
  - self::python/style         # → gh::myorg/myspecs::python/style
  - self::python/testing/pytest
```

## Spec libraries

A spec library is any directory with this layout:

```
specs/        # modules (.md files, may be nested)
references/   # on-demand reference entries
profiles/     # named module+stance bundles
stances/      # named module sets for on-demand activation
```

The built-in spek library follows the same layout. You can create your own and share it across projects.

### Authoring a library

Create the directory structure above and add `.md` files under `specs/`. Each file is a module. The filename (relative to `specs/`, without extension) is the module path, e.g. `specs/python/style.md` → path `python/style`.

Modules can include YAML frontmatter with spek metadata:

```markdown
---
spek:
  output: rule              # rule (default) or skill
  name: my-skill            # output name; required for skills, optional for rules
  description: "..."        # shown in skill picker and module list
  template: jinja           # omit unless you need Jinja2 templating
  needs_context: true       # false: inject ## Project structure block into body
  preapproved_tools:        # tool patterns added to Claude skill's allowed-tools
    - Bash(git status)
  skill:                    # skill-only settings
    args: "<query>"         # argument hint shown in Claude's skill picker
    model_invokable: true   # false: sets disable-model-invocation in Claude
    needs_context: true     # false: sets context: fork + allowed-tools in Claude
---

# Python style

...
```

When `template: jinja` is set, the body is rendered as a Jinja2 template before output. Available context variables: `modules` (set of active module refs), `integrations` (set of configured integration names).

Profiles and stances reference modules using `self::` to stay portable:

```yaml
# profiles/base.yaml
description: "Base conventions for all projects"
modules:
  - self::git/commit-base
  - self::python/style
```

### Importing a library

Register the library as a named source, then activate modules from it:

```bash
# Local directory
spek source add mywork ~/shared-specs

# GitHub repo (cloned to ~/.spek/sources/ automatically)
spek source add mywork gh::org/specs

# Specific tag or branch
spek source add mywork gh::org/specs@v1.0.0

# Activate modules
spek module add mywork::python/style mywork::git/commit-base

# Or apply a profile from the library
spek profile apply mywork::python/cli

# Sync
spek sync
```

Sources can also be declared globally in `~/.spek/settings.yaml` so they're available in every project without re-registering:

```bash
spek source add --global mywork gh::org/specs
```

## Usage

<details>
<summary>Command reference</summary>

```bash
spek init                       # set up a project
spek sync                       # fetch missing modules from sources and regenerate integrations
spek sync --pull                # force-refresh all remote sources, then regenerate
spek profile list               # list available profiles
spek profile apply [name]       # re-resolve and apply a profile
spek module edit                # re-select modules interactively
spek module list                # list all available modules with descriptions
spek module set <module>...     # non-interactively set modules (full replacement)
spek module add <module>...     # append modules to the active list
spek module remove <module>...  # remove modules from the active list
spek module search <term>...    # keyword search across available modules
spek source add <name> <path>   # register a named source (local path or gh::/gl:: shorthand)
spek source pull [name]         # clone/refresh a remote source cache (all sources if no name)
spek source remove <name>       # remove a source
spek source status              # show all sources and their resolution status
spek cache status               # show disk usage of the local source cache
spek cache clear [name]         # clear the entire cache, or just one source's cache
spek check                      # validate that all modules and sources resolve
spek local module <name>        # create a project-local spec module
spek local stance <name>        # create a project-local stance
spek local ref <name>           # create a project-local reference entry
spek destroy                    # remove all spek-managed files from a project
spek ref search [--json] [-n N] [--match-all] <term>...  # search the reference library (upstream + .spek/project/references/)
spek ref read [--json] <name>                            # read a reference entry
```

See `spek --help` or `spek <command> --help` for full options.

</details>

<details>
<summary>spek.yaml format</summary>

```yaml
meta:
  spek_version: "1.0.0"
  spek_sha: "abc1234"      # SHA at last sync — informational only
  integrations:
    - claude
  profile: "base"          # omitted if no profile was used
modules:                   # always-active rules/skills
  - workflow/base          # bare path → built-in spek source
  - mywork::git/commit-base   # module from an external source (alias::path shorthand)
  - gh::org/specs::python/style  # fully-qualified remote module
  - project::my-conventions  # project-local module under .spek/project/
stances:                   # omitted if empty
  - mywork::autonomous
  - gh::org/specs::collaborative
sources:                   # omitted if empty; project-scoped sources
  mywork: /home/user/shared-specs    # local path (expanded to absolute at add time)
  upstream: gh::org/specs            # remote (cloned to ~/.spek/sources/ cache on first use)
```

</details>

<details>
<summary>Environment variables</summary>

| Variable | Default | Description |
|---|---|---|
| `SPEK_SETTINGS_PATH` | `~/.spek/settings.yaml` | Override the global settings file path |
| `SPEK_REPO_PATH` | auto-detected from package location | Override the spek repo root (mainly for development) |
| `SPEK_SOURCES_CACHE_PATH` | `~/.spek/sources` | Override the remote source cache directory |

</details>

## Configuration

### AI tool allowlists

To allow the AI to run spek commands without confirmation, add the following patterns to your tool's allowlist.

**Windsurf:**

- `spek ref *`
- `spek session *`
- `spek todo *`
- `spek module list`

This enables the AI to auto-execute these spek commands during workflow skills without requiring approval for each invocation.

## Development

```bash
# One-time setup
just install-dev   # create .venv and install dev dependencies

# Common tasks
just test          # run the test suite
just test-cov      # run tests with coverage report
just sync          # spek sync --pull (refresh this repo's own spec modules)
```

The project dogfoods spek — `.spek/` contains its own session files and module config. `just sync` re-syncs the rules and skills used during development.
