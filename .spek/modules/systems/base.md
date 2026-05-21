---
spek:
  description: "Use the spek reference library before implementing from scratch"
---

# spek reference library

Before implementing anything from scratch — a UI component, a library integration, an architectural pattern — search the reference library first.

1. Run `spek ref search --json <term> <term2>...` with keywords describing what you want to implement
2. If a matching entry is returned, retrieve it: `spek ref read --json <name>` — the `name` field from search results is the exact value to pass
3. Use the entry as your implementation base; adapt as needed for the specific context and toolchain
4. Only implement from scratch if no relevant entry exists
