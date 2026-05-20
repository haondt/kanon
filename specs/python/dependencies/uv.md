# Python dependency management — uv

Extends `python/dependencies/base` with uv-specific conventions.

- Add a new dependency: `uv add <package>` — uv resolves the latest compatible version and writes the constraint to `pyproject.toml`
- Add a dev dependency: `uv add --optional dev <package>` — goes into `[project.optional-dependencies] dev`
- Upgrade a specific package: `uv add <package>` (re-resolves to latest)
- Upgrade all: `uv sync --upgrade`
- Lock file: `uv.lock` — commit it
