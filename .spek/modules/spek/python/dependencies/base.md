---
spek:
  output: rule
  description: Dependency pinning and lock file rules
  skill:
    model_invokable: true
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools: []
---

# Python dependency management

- **Never manually write version constraints** in `pyproject.toml` — let your package manager resolve and record them
- Keep dev/test dependencies in a separate group from runtime dependencies
