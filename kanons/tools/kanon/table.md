---
kanon:
  description: "kanon table CLI reference"
---

# kanon table CLI

The table is a scratch graph of conversation threads, stored in `.kanon/table.yaml` (gitignored). Items have a letter key (`a`–`z`, then `aa`, `ab`, …; keys are never reused), a title, a summary and a status (`open`, `active`, `resolved`). At most one item is `active`. Edges are undirected.

For multi-line summaries, pass `-` and use a heredoc with stdin.

- `kanon table status [<key>]` — show the table as a graph, or one item with its summary and direct neighbors; a missing file is an empty table
- `kanon table add <title> [--summary <text>] [--link <key>]...` — add an open item; no-op if an item with the same title exists (case-insensitive)
- `kanon table edit <key> [--title <text>] [--summary <text>]` — rewrite an item's text
- `kanon table set-status <key> <open|active|resolved>` — set status; `active` demotes the current active item to `open` and reports it
- `kanon table link <a> <b>` / `kanon table unlink <a> <b>` — add or remove an edge
- `kanon table merge <keep> <absorb>` — fold `absorb` into `keep`: edges unioned, summaries joined, `absorb`'s key retired; the result is active if either was, resolved only if both were, else open
- `kanon table remove <key>` — delete an item and its edges
- `kanon table clear` — delete the table
- `kanon table lint` — validate the table file

All commands accept `--json`; `add` and `edit` also accept `--input-json`. See `kanon table --help` for the full command list.
