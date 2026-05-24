---
spek:
  description: "Build tool recipe conventions"
---

# Python build tool conventions

- Always include a `venv` recipe that creates the virtual environment; it should be idempotent — a no-op if the venv already exists
- Any recipe that requires the venv should declare it as a dependency so it is always present before running
