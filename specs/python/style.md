---
spek:
  description: "PEP 8, pathlib, type hints"
---

# Python style

- Follow PEP 8
- Use `pathlib.Path` over `os.path` or plain strings
- Raise specific exceptions; avoid bare `except:`
- Use `from __future__ import annotations` for deferred type hint evaluation
