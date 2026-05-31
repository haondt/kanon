---
spek:
  description: "spek plan CLI reference — manage standalone plan files"
---

# spek plan CLI

Plan files live at `.spek/plans/<name>.yaml`. Sub-plans of a split live at `.spek/plans/<split>/<name>.yaml`.

For multi-line content, use a heredoc with stdin (pass `-` as the argument):

```bash
spek plan add-step myplan s1 - << 'EOF'
# Step content here
EOF
```

## Name addressing

- Bare name: `spek plan <cmd> myplan` — operates on `.spek/plans/myplan.yaml`
- Split sub-plan: `spek plan <cmd> mysplit/myplan` — operates on `.spek/plans/mysplit/myplan.yaml`; the split must exist before creating a sub-plan

## Commands

- `spek plan create <name> <goal>` — create a new plan file; if `<split>/<name>`, the split must already exist; registers the entry in the split's `index.yaml` as `pending`
- `spek plan read <name>` — print goal, steps, and notes
- `spek plan goal <name> <text>` — overwrite the plan goal
- `spek plan add-step <name> <key> <text> [--input-json]` — add a step with an explicit key
- `spek plan edit-step <name> <key> <text> [--input-json]` — overwrite a step's text
- `spek plan remove-step <name> <key>` — delete a step
- `spek plan note <name> <text> [--input-json]` — append a note, auto-keyed `pn1`, `pn2`, …
- `spek plan edit-note <name> <key> <text> [--input-json]` — overwrite a note
- `spek plan remove-note <name> <key>` — delete a note

All commands accept `--project-root` and `--json` for machine-readable output. Write commands emit `{"before": <hash>, "after": <hash>}`.
