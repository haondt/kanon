---
spek:
  description: "Manage named source directories for spec modules"
---

# spek source

Sources are named directories of spec modules. Declare them in `~/.spek/settings.yaml` (global, shared across all projects) or `.spek/spek.yaml` (project-scoped). Once registered, modules from a source are referenced as `source-name::module/path`.

- `spek source add <source-name> <path> [--global] [--force]` — register a source; local paths are expanded to absolute at add time; use `--global` to write to `~/.spek/settings.yaml`; errors on duplicate name unless `--force`
- `spek source remove <source-name> [--global]` — remove a source from the config
- `spek source status [--global]` — table showing: source name, path, type (local / gh / gl), scope (global / project), and whether it currently resolves

## Path formats

| Format | Example | Type |
|---|---|---|
| Absolute path | `/home/user/specs` | local |
| Home-relative | `~/shared-specs` | local (expanded at add time) |
| GitHub shorthand | `gh::org/repo` or `gh::org/repo@ref` | gh (not yet fetchable) |
| GitLab shorthand | `gl::group/repo` or `gl::group/subgroup/repo@ref` | gl (not yet fetchable) |

Remote sources (`gh::` / `gl::`) are validated at add time but module fetching is not yet implemented. They appear in `spek source status` with type `gh`/`gl` and resolves `n/a`. `spek check` reports them as info, not errors.

## End-to-end example

```bash
spek source add mywork ~/shared-specs           # register a local source
spek source add upstream gh::org/specs          # or a remote (fetching not yet supported)
spek module add mywork::python/style            # activate a module from that source
spek sync
```
