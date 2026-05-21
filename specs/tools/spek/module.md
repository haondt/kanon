---
spek:
  description: "spek module — enumerate and configure project modules"
---

# spek module

## Commands

```sh
spek module list [--json] [--project-root DIR]
spek module set [--sync] [--project-root DIR] <module>...
spek module edit [--sync] [--project-root DIR]
```

### list

Lists all modules available in the spek library with descriptions and active status.

- `--json`: output as a JSON array of `{name, description, active}` objects; `active` is true when the module is currently in `spek.yaml`
- `name` in results is the exact value to pass to `set`

### set

Non-interactively replaces the module list in `spek.yaml` with the given modules (full replacement). Errors if any name is not a known module.

- `--sync`: run `spek sync` after saving

### edit

Opens an interactive checkbox picker to select modules; saves to `spek.yaml` on confirm.

- `--sync`: run `spek sync` after saving
