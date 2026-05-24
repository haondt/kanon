---
spek:
  description: "Search the spek module library and modify the locally installed modules"
---

# spek module

- `spek module list [--json]` — list all available modules with descriptions and active status; `--json` outputs `[{name, description, active}]`; `name` is the value to pass to `set`
- `spek module set [--sync] <module>...` — replace the active module list in `spek.yaml` (full replacement); errors on unknown module names
- `spek module edit [--sync]` — interactive checkbox picker; saves to `spek.yaml` on confirm
- `--sync` on `set`/`edit`: runs `spek sync` after saving
