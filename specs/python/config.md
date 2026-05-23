---
spek:
  description: "Config class pattern with singleton"
---

# Python configuration

- Centralize all config in a single `Config` class in `config.py`; instantiate a module-level `config = Config()` and import that object everywhere — do not scatter `os.getenv` calls throughout the codebase
- See the `python/config` reference for the full implementation pattern
