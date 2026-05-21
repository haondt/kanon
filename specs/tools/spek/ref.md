---
spek:
  description: "spek ref — search and read the reference library"
---

# spek ref

The spek reference library contains entries for library documentation, usage examples, drop-in code patterns, and architectural notes. Entries live in `references/` in the spek repo; project-local entries in `.spek/local/references/` shadow upstream entries on name collision.

## Commands

```sh
spek ref search [--json] [-n N] [--match-any] <term>...
spek ref read [--json] <name>
```

### search

Searches entries by keyword. All terms must match by default; `--match-any` returns entries that match any term.

- `--json`: output as a JSON array of `{name, description, keywords}` objects
- `-n N`: limit results (default 10; 0 for unlimited)
- `name` in results is the exact value to pass to `read`

### read

Retrieves a single reference entry by name.

- `--json`: output as a JSON object with `{name, content}` fields
