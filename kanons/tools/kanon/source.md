---
kanon:
  description: "Manage named source directories for kanons"
---

# kanon source

Sources are named directories of kanons. Declare them in `~/.kanon/settings.yaml` (global, shared across all projects) or `.kanon/kanon.yaml` (project-scoped). Once registered, kanons from a source are referenced as `source-name::kanon/path`.

- `kanon source add <source-name> <path> [--global] [--force]` — register a source; local paths are expanded to absolute at add time; use `--global` to write to `~/.kanon/settings.yaml`; errors on duplicate name unless `--force`
- `kanon source remove <source-name> [--global]` — remove a source from the config
- `kanon source status [--global]` — table showing: source name, path, type (local / gh / gl), scope (global / project), and whether it currently resolves

## Path formats

| Format | Example | Type |
|---|---|---|
| Absolute path | `/home/user/specs` | local |
| Home-relative | `~/shared-specs` | local (expanded at add time) |
| GitHub shorthand | `gh::org/repo` or `gh::org/repo@ref` | gh (not yet fetchable) |
| GitLab shorthand | `gl::group/repo` or `gl::group/subgroup/repo@ref` | gl (not yet fetchable) |

Remote sources (`gh::` / `gl::`) are validated at add time but kanon fetching is not yet implemented. They appear in `kanon source status` with type `gh`/`gl` and resolves `n/a`. `kanon check` reports them as info, not errors.

## End-to-end example

```bash
kanon source add mywork ~/shared-kanons          # register a local source
kanon source add upstream gh::org/kanons         # or a remote (fetching not yet supported)
kanon add mywork::python/style            # activate a kanon from that source
kanon sync
```
