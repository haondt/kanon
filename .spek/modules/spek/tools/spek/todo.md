---
spek:
  description: "spek todo CLI reference"
---

# spek todo CLI

For multi-line content, use a heredoc with stdin (pass `-` as the argument) to avoid shell escaping issues:

```bash
spek todo add --section backlog - << 'EOF'
# Multi-line content here
EOF
```

## Items

- `spek todo status [--section <key>] [text]` — show backlog items, optionally filtered by section or substring
- `spek todo search <terms>... [--section <key>]` — search backlog items (all terms must match, case-insensitive)
- `spek todo add --section <key> <text> [--input-json]` — add an item to a section
- `spek todo remove --section <key> <text> [--input-json]` — remove an item from a section (exact match), removes section if empty

## Sections

- `spek todo section status` — list all sections with item counts
- `spek todo section search <text>` — search section names (case-insensitive substring)
- `spek todo section add <key> <name> [--allow-exists]` — add a new section (file auto-created on first call)

## Validation

- `spek todo lint` — validate the todo file

## Example

```bash
spek todo add --section backlog - << 'EOF'
Add user authentication to the API
EOF
```

All commands accept `--json` for machine-readable output. See `spek todo --help` for the full command list.
