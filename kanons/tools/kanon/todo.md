---
kanon:
  description: "kanon todo CLI reference"
---

# kanon todo CLI

For multi-line content, use a heredoc with stdin (pass `-` as the argument) to avoid shell escaping issues:

```bash
kanon todo add --section backlog - << 'EOF'
# Multi-line content here
EOF
```

## Items

- `kanon todo status [--section <key>] [text]` — show backlog items, optionally filtered by section or substring
- `kanon todo search <terms>... [--section <key>]` — search backlog items (all terms must match, case-insensitive)
- `kanon todo add --section <key> <text> [--input-json]` — add an item to a section
- `kanon todo remove --section <key> <text> [--input-json]` — remove an item from a section (exact match), removes section if empty

## Sections

- `kanon todo section status` — list all sections with item counts
- `kanon todo section search <text>` — search section names (case-insensitive substring)
- `kanon todo section add <key> <name> [--allow-exists]` — add a new section (file auto-created on first call)

## Validation

- `kanon todo lint` — validate the todo file

## Example

```bash
kanon todo add --section backlog - << 'EOF'
Add user authentication to the API
EOF
```

All commands accept `--json` for machine-readable output. See `kanon todo --help` for the full command list.
