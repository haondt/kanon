---
kanon:
  description: "Commands for searching and reading from the kanon reference library — on-demand docs, patterns, and examples indexed by keyword"
---

# kanon ref

- `kanon ref search [-n N] [--match-all] <term>...` — keyword search; any term matching returns a result by default; use `--match-all` to require all terms; start with 1-2 terms; `name` in results is the value to pass to `read`
- `kanon ref read <name>` — retrieve a single entry by name
- Add `--json` to either command for machine-readable output (`search` → `[{name, description, keywords}]`; `read` → `{name, content}`)
