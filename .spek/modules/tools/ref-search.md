---
spek:
  description: "Use spek ref search/read before implementing from scratch"
---

# Reference library

A library of reference entries is available in the spek repo. Entries can be anything — library documentation, usage examples, drop-in code, architectural notes, or patterns. Before implementing anything from scratch, search the library first.

## Commands

```sh
# Search by keyword — use this first
spek ref search --json <term> <term2> <term3>...

# Retrieve a specific entry by name
spek ref read --json <name>
```

Always use the `--json` flag — the output is easier to parse than the default format.

## Workflow

1. When asked to implement something (a UI component, a library integration, a pattern, etc.), run `spek ref search --json <terms>` first
2. If a matching entry is returned, use `spek ref read --json <name>` to retrieve it — the `name` field from search results is the exact value to pass to `read`
3. Use the entry as your implementation base or guide; adapt as needed for the specific context
4. Only implement from scratch if no relevant entry exists
