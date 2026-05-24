---
spek:
  description: "Dependency pinning and lock file rules"
---

# Python dependency management

- **Never manually write version constraints** in `pyproject.toml` — let your package manager resolve and record them
- Keep dev/test dependencies in a separate group from runtime dependencies
