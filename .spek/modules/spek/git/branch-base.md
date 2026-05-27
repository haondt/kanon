---
spek:
  output: rule
  description: Never touch branches without instruction
  skill:
    model_invokable: true
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools: []
---

# Git branch conventions

- Never create, switch, rename, or delete branches without explicit instruction
- Do not suggest branch operations unless asked
