---
spek:
  output: rule
  description: No commented-out code or debug artifacts
  skill:
    model_invokable: true
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools: []
---

# Code hygiene

- No commented-out code in committed files
- No debug artifacts in committed code: `print()`, `console.log()`, `debugger`, breakpoints, etc.
