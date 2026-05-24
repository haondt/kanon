---
spek:
  description: "Commands for searching and reading from the spek reference library — on-demand docs, patterns, and examples indexed by keyword"
---

# spek ref

- `spek ref search [-n N] [--match-any] <term>...` — keyword search; all terms must match by default; start with 1-2 terms; `name` in results is the value to pass to `read`
- `spek ref read <name>` — retrieve a single entry by name
- Add `--json` to either command for machine-readable output (`search` → `[{name, description, keywords}]`; `read` → `{name, content}`)
