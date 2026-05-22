---
spek:
  description: "Use the spek reference library before implementing from scratch"
  preapproved_tools:
    - Bash(spek ref *)
    - Bash(git status)
    - Edit(.spek/SESSION.md)
    - Write(.spek/SESSION.md)
    - Edit(.spek/STRUCTURE.md)
    - Write(.spek/STRUCTURE.md)
---

# spek reference library

Before implementing anything from scratch — a UI component, a library integration, an architectural pattern — search the reference library first.

1. Run `spek ref search <terms>` with keywords relevant to the task; then run `spek ref read <name>` on any matching entry to retrieve its full content
2. Use the entry as your implementation base; adapt as needed for the specific context and toolchain
3. Only implement from scratch if no relevant entry exists
