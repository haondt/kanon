---
spek:
  description: "Config class pattern: centralized env-var parsing with a module-level singleton"
  keywords:
    - python
    - config
    - configuration
    - environment variables
    - env vars
    - singleton
---

# Python Config class

Centralize all env-var parsing in a single `Config` class; import the module-level singleton everywhere.

```python
import os

class Config:
    def __init__(self):
        # Required — fail fast if absent
        self.database_url: str = os.environ["DATABASE_URL"]

        # Optional with default
        self.debug: bool = os.getenv("DEBUG", "false").lower() in ("true", "1")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.timeout: float = float(os.getenv("TIMEOUT_SECONDS", "30"))

config = Config()
```

- Read and parse all values in `__init__`; store as typed attributes — the rest of the codebase works with `int`, `bool`, etc., never raw strings
- Use `os.environ[KEY]` (raises `KeyError`) for required values; use `os.getenv(KEY, default)` for optional ones
- For booleans, check against `("true", "1")` — `bool(os.getenv(...))` is always `True` for any non-empty string
- For complex types (timespans, UUIDs, paths) parse in `__init__` using stdlib: `datetime.timedelta(seconds=int(...))`, `pathlib.Path(...)`, `uuid.UUID(...)`

## Variants

**Pydantic Settings** — use `pydantic-settings` (`BaseSettings`) when you want automatic `.env` file loading, type coercion, and validation errors with field-level messages. The singleton pattern still applies: instantiate once at module level.

**Multiple environments** — keep one `Config` class; vary values via env vars, not subclasses. If staging vs production need structurally different config, use a factory function that returns the right instance based on an `ENV` var.
