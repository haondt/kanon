---
kanon:
  description: "Use the kanon reference library before implementing from scratch"
  preapproved_tools:
    - Bash(kanon ref *)
    - Bash(kanon session *)
    - Bash(kanon todo *)
    - Bash(kanon list)
---

# kanons

Kanons are named conventions (e.g. `python/style`, `git/commit-base`) that were compiled into the rules already loaded into your context. You know their content — you do not need to re-read any rule files. If you need the canonical kanon path to cite or reference a specific rule, run `cat .kanon/kanon.yaml` to get the active list.

# references

kanons are behavioral rules that govern how you work; references are on-demand implementation guides you search when building something.

# kanon reference library

Before implementing anything from scratch — a UI component, a library integration, an architectural pattern — search the reference library first.

1. Run `kanon ref search <terms>` with keywords relevant to the task; then run `kanon ref read <name>` on any matching entry to retrieve its full content
2. Use the entry as your implementation base; adapt as needed for the specific context and toolchain
3. Only implement from scratch if no relevant entry exists
