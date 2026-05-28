---
spek:
  output: rule
  description: uv-specific dependency management
  skill:
    model_invokable: true
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools: []
---

# Python dependency management — uv

- Create the venv with `uv venv` — this produces `./.venv` (uv default)
- Add a new dependency: `uv add <package>` — uv resolves the latest compatible version and writes the constraint to `pyproject.toml`
- Add a dev dependency: `uv add --optional dev <package>` — goes into `[project.optional-dependencies] dev`
- Upgrade a specific package: `uv add <package>` (re-resolves to latest)
- Upgrade all: `uv sync --upgrade`
- Install dependencies into the venv: `uv sync`
