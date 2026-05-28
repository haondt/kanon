---
spek:
  output: rule
  description: 'Commit body: explain why, not what'
  skill:
    model_invokable: true
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools: []
---

# Git commit style (with body)

- Add more detail to commits with a body
- Separate from subject with a blank line
- Keep it to 1–2 sentences: summarize changes
- Do not enumerate individual changes — the diff already provides greater levels of detail
