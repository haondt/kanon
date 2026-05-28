---
spek:
  output: rule
  description: Build tool recipe conventions
  skill:
    model_invokable: true
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools: []
---

# Python build tool conventions

- Always include a `venv` recipe that creates the virtual environment; it should be idempotent — a no-op if the venv already exists
- Any recipe that requires the venv should declare it as a dependency so it is always present before running
