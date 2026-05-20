# Python dependency management

- **Never manually write version constraints** in `pyproject.toml` — let your package manager resolve and record them
- Use a lock file for reproducible installs; commit it alongside `pyproject.toml`
- Keep dev/test dependencies in a separate group from runtime dependencies
- Do not pin exact versions (`==`) in `pyproject.toml`; the lock file handles reproducibility
- To upgrade a dependency, re-add it through your package manager rather than editing the version by hand
