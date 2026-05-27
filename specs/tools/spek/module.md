---
spek:
  description: "Search the spek module library and modify the locally installed modules"
---

# spek module

- `spek module list [--json]` — list all available modules with descriptions and active status; `--json` outputs `[{name, description, active, source}]`; `name` is the value to pass to `set`/`add`
- `spek module set [--sync] <module>...` — replace the active module list in `spek.yaml` (full replacement); errors on unknown module names
- `spek module add [--sync] <module>...` — append modules to the active list; errors if module is unknown or already active
- `spek module remove [--sync] <module>...` — remove modules from the active list; errors if module is not currently active
- `spek module search [--source <source-name>] [--json] <term>...` — keyword search across available modules; all terms must match (case-insensitive); matches against name and description; `--source` filters to one source
- `spek module edit [--sync]` — interactive checkbox picker; saves to `spek.yaml` on confirm
- `--sync` on `set`/`add`/`remove`/`edit`: runs `spek sync` after saving

## Module name syntax

Modules from the built-in `spek` source use bare paths (e.g. `git/commit-base`, `python/style`). Modules from external sources use the `source-name::bare/path` syntax:

```
mywork::python/style        # 'python/style' module from the 'mywork' source
corp::conventions/commits   # 'conventions/commits' module from the 'corp' source
```

The `::` separator is the boundary between source name and module path. Unlike `spek ref search`, which searches the reference library, `spek module search` searches the spec module library (rules and skills).
