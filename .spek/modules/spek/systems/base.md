---
spek:
  output: rule
  description: Use the spek reference library before implementing from scratch
  skill:
    model_invokable: true
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools:
  - Bash(spek ref *)
  - Bash(spek session *)
  - Bash(spek todo *)
  - Bash(spek module list)
---

# spek reference library

Before implementing anything from scratch — a UI component, a library integration, an architectural pattern — search the reference library first.

1. Run `spek ref search <terms>` with keywords relevant to the task; then run `spek ref read <name>` on any matching entry to retrieve its full content
2. Use the entry as your implementation base; adapt as needed for the specific context and toolchain
3. Only implement from scratch if no relevant entry exists
