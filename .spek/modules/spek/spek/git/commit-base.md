---
spek:
  output: rule
  description: Subject line rules and commit hygiene
  skill:
    model_invokable: true
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools: []
---

# Git commit conventions

- Subject line ≤ 72 characters
- Prefix WIP commits: `WIP `
- Never amend published commits
- Never commit or push unless explicitly asked
- Write commit messages autonomously; do not ask for approval
