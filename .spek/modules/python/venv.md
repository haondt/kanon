---
spek:
  description: "Always use ./.venv, never global Python"
---

# Python virtual environment

- Always use a virtual environment; never install packages into the system Python
- The venv lives at `./.venv` unless STRUCTURE.md says otherwise
- Invoke `python`, `pip`, and test runners via `./.venv/bin/` — never globally, unless a build tool (e.g. `just`) wraps the invocation
