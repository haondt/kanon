---
spek:
  description: "Config class pattern with singleton"
---

# Python configuration

- Centralize all config in a single `Config` class in a dedicated `config.py` module; do not scatter `os.getenv` calls throughout the codebase
- Read and parse all values in `__init__`; store them as plain attributes with sensible defaults. If the app cannot sensibly function with a default value, don't put one. Use `os.environ[...]` and fail fast.
- Instantiate a single module-level `config = Config()` and import that object everywhere
- Parse env vars into their target types at load time (e.g. `int(os.getenv(...))`, `float(...)`) so the rest of the codebase works with typed values, not strings
- For booleans, treat `'true'`, `'1'`, and non-zero numeric strings as truthy; avoid relying on Python's `bool(os.getenv(...))` which is always `True` for any non-empty string
- For complex types (timespans, UUIDs, paths), parse them in `__init__` using a helper or stdlib function; store the parsed result, not the raw string

```python
# config.py
import os

class Config:
    def __init__(self):
        self.debug = os.getenv('APP_DEBUG', 'false').lower() in ('true', '1')
        self.port = int(os.getenv('APP_PORT', 8080))
        self.db_path = os.path.abspath(os.getenv('APP_DB_PATH', '/data/app.db'))

config = Config()
```
