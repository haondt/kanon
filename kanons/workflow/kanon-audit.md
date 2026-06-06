---
kanon:
  description: "Audit the codebase for kanon violations; triage findings"
  output: skill
  name: kanon-audit
  skill:
    model_invokable: false
    needs_context: true
---
You are running a kanon audit. Dispatch on the argument provided:

- No argument → **Audit phase**
- Argument is `triage` → **Triage phase**

## Audit phase (no argument)

1. For each active kanon, decide:
   - **Is it checkable?** Some kanons (e.g. behavioral, conversational) cannot be verified against code — skip them.
   - **Where would a violation hide?** Go directly to the most plausible locations for that kanon: specific files, directories, recent commits, config files, etc. Do not scan every file — read only what is relevant to that kanon.
2. Check each targeted area for concrete violations. A finding must be specific — not a generic concern. Kanons vary in scope:
   - **Code-level** (e.g. `python/style`): violations are traceable to specific locations; cite them. **For kanons with multiple sub-rules, verify each sub-rule independently** — do not stop after checking one. Run a separate targeted check (grep, file read, etc.) for every verifiable claim in the kanon.
   - **Architectural** (e.g. `systems/onion-arch`): violations are structural; cite the affected modules or boundaries.
   - **Behavioral or conversational**: not verifiable against code — skip.
3. Write all findings to `.kanon/audit.md` using the format below. Show the list to the user. Prompt to run `/kanon-audit triage`.

If no violations are found: write `audit.md` with `Status: clean` and no findings section. Prompt to run `/kanon-retro` directly.

**`.kanon/audit.md` format:**

```markdown
# kanon-audit

**Date:** YYYY-MM-DD
**Status:** open

## Findings

### F1: <title>
**Kanon:** `python/style`
**Location:** `src/foo.py:42`, `src/bar.py:17`
**Status:** open
**Note:** —

### F2: <title>
**Kanon:** `ai/communication/prefer-brevity`
**Status:** open
**Note:** —
```

`Location` is omitted when the violation is not tied to specific files or lines.

## Triage phase (`triage` argument)

1. Read `.kanon/audit.md`. If it does not exist, tell the user to run `/kanon-audit` first and stop. If `Status: clean`, there is nothing to triage.
2. Walk each `open` finding one by one. For each, offer:
   - **Fix now** — implement the fix, mark `Status: fixed`, record what was done in `Note:`
   - **Defer** — add to `todo.yaml` via `kanon todo add`, mark `Status: deferred`
   - **Dismiss** — mark `Status: dismissed`, record reason in `Note:`
3. After all findings are resolved, update the top-level `**Status:**` to `triaged`. Prompt to run `/kanon-retro`.
