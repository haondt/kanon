---
spek:
  output: rule
  description: General style guidance for python code
  skill:
    model_invokable: true
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools: []
---

# Python style

- Follow PEP 8
- Use `pathlib.Path` over `os.path` or plain strings
- Raise specific exceptions; avoid bare `except:`
- Use `from __future__ import annotations` for deferred type hint evaluation
- Above 200 lines, consider splitting at natural seams (distinct responsibilities, separable layers); extract a sub-package if the architecture encourages it.
- Do not split arbitrarily — a long but cohesive class or algorithm is fine as one file
