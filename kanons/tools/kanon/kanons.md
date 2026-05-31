---
kanon:
  description: "Search the kanon library and modify the locally installed kanons"
---

# kanon kanons

- `kanon list [--json]` — list all available kanons with descriptions and active status; `--json` outputs `[{name, description, active, source}]`; `name` is the value to pass to `set`/`add`
- `kanon set [--sync] <kanon>...` — replace the active kanon list in `kanon.yaml` (full replacement); errors on unknown kanon names
- `kanon add [--sync] <kanon>...` — append kanons to the active list; errors if kanon is unknown; warns if already active
- `kanon remove [--sync] <kanon>...` — remove kanons from the active list; warns if kanon is not currently active
- `kanon search [--source <source-name>] [--json] <term>...` — keyword search across available kanons; all terms must match (case-insensitive); matches against name and description; `--source` filters to one source
- `kanon edit [--sync]` — interactive checkbox picker; saves to `kanon.yaml` on confirm
- `--sync` on `set`/`add`/`remove`/`edit`: runs `kanon sync` after saving

## Kanon name syntax

Kanons from the built-in `kanon` source use bare paths (e.g. `git/commit-base`, `python/style`). Kanons from external sources use the `source-name::bare/path` syntax:

```
mywork::python/style        # 'python/style' kanon from the 'mywork' source
corp::conventions/commits   # 'conventions/commits' kanon from the 'corp' source
```

The `::` separator is the boundary between source name and kanon path. Unlike `kanon ref search`, which searches the reference library, `kanon search` searches the kanon library (rules and skills).
