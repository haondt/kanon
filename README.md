# kanon

A tool for managing granular AI rules and syncing them across projects.

Projects declare which kanons they use in `.kanon/kanon.yaml`, pulling from shared libraries on GitHub, GitLab, or local directories, and `kanon sync` generates AI tool config for each configured integration.

## Prerequisites

- [uv](https://docs.astral.sh/uv/)
- [git](https://git-scm.com/)

## Quick start

```bash
git clone <this repo>
cd kanon
uv tool install --editable .
```

```bash
# In a new project directory
kanon init
kanon sync
```

Commit `.kanon/kanon.yaml` — your project's kanon config is now self-contained. Synced kanon files are gitignored and regenerated on demand.

## Onboarding an existing project

To adopt kanon in a project that already has code:

```bash
kanon init      # select integrations, profile, and kanons
kanon sync      # copy kanon files and generate AI tool output
```

Then in your AI coding tool:

```
/kanon-onboard
```

`/kanon-onboard` crawls the project to understand the tech stack and structure, writes `.kanon/STRUCTURE.md`, proposes an appropriate kanon selection for your approval, applies it, and adds any inline `TODO:` comments it finds to `.kanon/todo.yaml`.

## Concepts

kanon manages kanons — markdown files covering coding conventions, git behavior, AI behavioral rules, and more. Projects declare which kanons they want in `.kanon/kanon.yaml`; `kanon sync` fetches them from their sources and generates AI tool integrations. The same source kanons produce `.claude/rules/` for Claude Code, a managed `AGENTS.md` block plus `.agents/skills/` for Codex, `.windsurf/rules/` for Windsurf, and so on — one config, multiple tools.

| Term | Meaning |
|---|---|
| **kanon** | A single markdown file representing an AI rule or skill. Identified by a reference `scheme::address::path` (e.g. `gh::org/kanons::git/commit-base`); bare paths default to the built-in kanon source |
| **source** | A named directory of kanons — local path, `gh::org/repo`, or `gl::group/repo`; declared in `kanon.yaml` or `~/.kanon/settings.yaml` |
| **stance** | A named set of kanons activatable on demand via `/kanon-stance`; use when you need the AI to behave differently for a specific task without permanently changing your config |
| **profile** | A named bundle of kanons and stances — useful for consistent bootstrapping across projects of the same type |
| **integration** | The AI tool output files that kanon generates from your kanons (`claude`, `codex`, `windsurf`, `devin`, `opencode`, etc.) |

## Skills

The workflow skills enforce a structured session lifecycle. Each step is a checkpoint where you can review and adjust before the AI proceeds — goal before planning, plan before coding, implementation before closing.

**Workflow**

| Command | Description |
|---|---|
| `/kanon-sketch` | (Optional) Clarify a fuzzy goal — skip if the goal is already concrete |
| `/kanon-plan` | Design the approach; get approval before writing code |
| `/kanon-build` | Execute the agreed plan |
| `/kanon-reconcile` | (Optional) Sync session state after work done outside `/kanon-build` — marks plan steps done based on git diff |
| `/kanon-review` | (Optional) Review the implementation for problems before closing the session |
| `/kanon-fix` | (Optional) Evaluate and fix findings surfaced by `/kanon-review` |
| `/kanon-retro` | Repo housekeeping (update `README.md`, todos, `STRUCTURE.md`); clear `session.yaml` |

**Extras**

| Command | Description |
|---|---|
| `/kanon-stance` | Activate a behavioral stance for the session |
| `/kanon-think` | Enter brainstorm mode — AI discusses ideas without taking action |
| `/kanon-detour` | Make a quick out-of-scope edit without going through the full workflow |
| `/kanon-amend` | Amend the current session goal or plan in place |
| `/kanon-todo` | Add an item to the project backlog |
| `/kanon-onboard` | Onboard an existing project: write STRUCTURE.md, select kanons, extract TODOs |
| `/kanon-why` | Explain a specific AI decision and suggest a kanon fix to prevent recurrence |

## Object references

Every kanon, stance, and profile is identified by a three-part reference:

```
scheme::address::path
```

| Part | Meaning |
|---|---|
| `scheme` | How the source is located (`kanon`, `alias`, `gh`, `gl`, `local`) |
| `address` | The source identifier within the scheme (repo path, alias name, etc.) |
| `path` | Path to the file within the source, relative to `kanons/` |

**Abbreviated forms** — most references can be shortened:

| Written | Expands to | Meaning |
|---|---|---|
| `git/commit-base` | `kanon::kanon::git/commit-base` | Built-in kanon source |
| `mywork::python/style` | `alias::mywork::python/style` | Registered source by alias |
| `gh::org/repo::python/style` | *(already full)* | GitHub source, no alias needed |
| `project::my-kanon` | `kanon::project::my-kanon` | Project-local file under `.kanon/project/` |
| `self::python/style` | `kanon::self::python/style` | Profile-internal: same source as the profile file |

**Special addresses** under the `kanon` scheme:

| Reference | Points to |
|---|---|
| `kanon::kanon` | The built-in kanon library (`kanons/` in this repo) |
| `kanon::project` | The consuming project's own local content (`.kanon/project/`) |
| `kanon::self` | The profile's own source — only valid inside profile YAML files; rewritten to the profile's actual source at load time |

`self::` is how profiles in an external library reference their own sibling kanons without hardcoding a source name:

```yaml
# profiles/python/cli.yaml in gh::myorg/mykanons
extends:
  - self::profiles/base        # → gh::myorg/mykanons::profiles/base
kanons:
  - self::python/style         # → gh::myorg/mykanons::python/style
  - self::python/testing/pytest
```

## Kanon libraries

A kanon library is any directory with this layout:

```
kanons/       # kanons (.md files, may be nested)
references/   # on-demand reference entries
profiles/     # named kanon+stance bundles
stances/      # named kanon sets for on-demand activation
```

The built-in kanon library follows the same layout. You can create your own and share it across projects.

### Authoring a library

Create the directory structure above and add `.md` files under `kanons/`. Each file is a kanon. The filename (relative to `kanons/`, without extension) is the kanon path, e.g. `kanons/python/style.md` → path `python/style`.

Kanons can include YAML frontmatter with kanon metadata:

```markdown
---
kanon:
  output: rule              # rule (default) or skill
  name: my-skill            # output name; required for skills, optional for rules
  description: "..."        # shown in skill picker and kanon list
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

When `template: jinja` is set, the body is rendered as a Jinja2 template before output. Available context variables: `kanons` (set of active kanon refs), `integrations` (set of configured integration names), `args` (dict of rendering args parsed from the kanon reference suffix, e.g. `foo/bar[flag,key=val]`; missing keys are falsy), `source` (shortest unambiguous source identifier for the kanon, e.g. `kanon::kanon`, `myalias`, or `gh::org/repo`).

Profiles and stances reference kanons using `self::` to stay portable:

```yaml
# profiles/base.yaml
description: "Base conventions for all projects"
kanons:
  - self::git/commit-base
  - self::python/style
```

### Importing a library

Register the library as a named source, then activate kanons from it:

```bash
# Local directory
kanon source add mywork ~/shared-kanons

# GitHub repo (cloned to ~/.kanon/sources/ automatically)
kanon source add mywork gh::org/kanons

# Specific tag or branch
kanon source add mywork gh::org/kanons@v1.0.0

# Activate kanons
kanon add mywork::python/style mywork::git/commit-base

# Or apply a profile from the library
kanon profile apply mywork::python/cli

# Sync
kanon sync
```

Sources can also be declared globally in `~/.kanon/settings.yaml` so they're available in every project without re-registering:

```bash
kanon source add --global mywork gh::org/kanons
```

## Usage

<details>
<summary>Command reference</summary>

```bash
kanon init                        # set up a project
kanon sync                        # fetch missing kanons from sources and regenerate integrations
kanon sync --pull                 # force-refresh all remote sources, then regenerate
kanon profile list                # list available profiles
kanon profile search <term>...    # keyword search across available profiles
kanon profile apply [name]        # merge profile kanons/stances into kanon.yaml (additive by default; --replace for full replacement)
kanon edit                        # re-select kanons interactively
kanon list                        # list all available kanons with descriptions
kanon set <kanon>...              # non-interactively set kanons (full replacement)
kanon add <kanon>...              # append kanons to the active list
kanon remove <kanon>...           # remove kanons from the active list
kanon search <term>...            # keyword search across available kanons
kanon source add <name> <path>    # register a named source (local path or gh::/gl:: shorthand)
kanon source pull [name]          # clone/refresh a remote source cache (all sources if no name)
kanon source remove <name>        # remove a source
kanon source status               # show all sources and their resolution status
kanon cache status                # show disk usage of the local source cache
kanon cache clear [name]          # clear the entire cache, or just one source's cache
kanon check                       # validate that all kanons and sources resolve
kanon local kanon <name>          # create a project-local kanon
kanon local stance <name>         # create a project-local stance
kanon local ref <name>            # create a project-local reference entry
kanon destroy                     # remove all kanon-managed files from a project
kanon ref search [--json] [-n N] [--match-all] <term>...  # search the reference library (upstream + .kanon/project/references/)
kanon ref read [--json] <name>                            # read a reference entry
```

See `kanon --help` or `kanon <command> --help` for full options.

</details>

<details>
<summary>kanon.yaml format</summary>

```yaml
meta:
  kanon_version: "1.0.0"
  kanon_sha: "abc1234"     # SHA at last sync — informational only
  integrations:
    - claude
    - codex
    - opencode
  profile: "base"          # omitted if no profile was used
kanons:                    # always-active rules/skills
  - workflow/base          # bare path → built-in kanon source
  - mywork::git/commit-base   # kanon from an external source (alias::path shorthand)
  - gh::org/kanons::python/style  # fully-qualified remote kanon
  - project::my-conventions  # project-local kanon under .kanon/project/
stances:                   # omitted if empty
  - mywork::autonomous
  - gh::org/kanons::collaborative
sources:                   # omitted if empty; project-scoped sources
  mywork: /home/user/shared-kanons    # local path (expanded to absolute at add time)
  upstream: gh::org/kanons            # remote (cloned to ~/.kanon/sources/ cache on first use)
```

</details>

<details>
<summary>Environment variables</summary>

| Variable | Default | Description |
|---|---|---|
| `KANON_SETTINGS_PATH` | `~/.kanon/settings.yaml` | Override the global settings file path |
| `KANON_REPO_PATH` | auto-detected from package location | Override the kanon repo root (mainly for development) |
| `KANON_SOURCES_CACHE_PATH` | `~/.kanon/sources` | Override the remote source cache directory |

</details>

## Configuration

### AI tool allowlists

To allow the AI to run kanon commands without confirmation, add the following patterns to your tool's allowlist.

**Windsurf:**

- `kanon ref *`
- `kanon session *`
- `kanon todo *`
- `kanon list`

**OpenCode:**

- `kanon ref *`
- `kanon session *`
- `kanon todo *`
- `kanon list`

This enables the AI to auto-execute these kanon commands during workflow skills without requiring approval for each invocation.

## Development

```bash
# One-time setup
just install-dev   # create .venv and install dev dependencies

# Common tasks
just test          # run the test suite
just test-cov      # run tests with coverage report
just sync          # kanon sync --pull (refresh this repo's own kanons)
```

The project dogfoods kanon — `.kanon/` contains its own session files and kanon config. `just sync` re-syncs the rules and skills used during development.
