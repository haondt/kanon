---
kanon:
  description: "Use the kanon reference library before implementing from scratch"
  preapproved_tools:
    - Bash(kanon ref *)
    - Bash(kanon session *)
    - Bash(kanon todo *)
    - Bash(kanon list)
---

# kanon reference library

Before implementing anything from scratch — a UI component, a library integration, an architectural pattern — search the reference library first.

1. Run `kanon ref search <terms>` with keywords relevant to the task; then run `kanon ref read <name>` on any matching entry to retrieve its full content
2. Use the entry as your implementation base; adapt as needed for the specific context and toolchain
3. Only implement from scratch if no relevant entry exists
