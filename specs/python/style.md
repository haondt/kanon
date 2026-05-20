# Python style conventions

- Follow PEP 8; enforce with ruff
- Use `from __future__ import annotations` for deferred evaluation of type hints
- Prefer dataclasses over plain dicts for structured data
- Use `pathlib.Path` over `os.path`
- Raise specific exceptions; avoid bare `except:`
- No commented-out code; no `print()` debug statements in committed code
- Type-annotate all public function signatures
