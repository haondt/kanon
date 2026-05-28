---
spek:
  output: rule
  description: spek session CLI reference
  skill:
    model_invokable: true
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools: []
---

# spek session CLI

For multi-line content, use a heredoc with stdin (pass `-` as the argument) to avoid shell escaping issues:

```bash
spek session plan add-step frontmatter - << 'EOF'
# Multi-line content here
EOF
```

## Session lifecycle

- `spek session start <goal>` — create a new session
- `spek session goal` — read the current session goal
- `spek session status [--full]` — show session summary
- `spek session lint` — validate the session file
- `spek session clear` — delete the session file

## Plan

- `spek session plan status [--key]` — show plan status (all steps or specific step)
- `spek session plan add-step <key> <text> [--input-json]` — add a plan step with markdown description
- `spek session plan check <key>` — mark a plan step as done
- `spek session plan uncheck <key>` — mark a plan step as not done
- `spek session plan note <text> [--input-json]` — append a plan-time note

## Amend

- `spek session amend goal <text> [--input-json]` — overwrite the session goal
- `spek session amend plan step <key> <text> [--input-json]` — overwrite a plan step's text
- `spek session amend plan note <key> <text> [--input-json]` — edit an existing plan note
- `spek session amend plan unnote <key>` — remove a plan note by key
- `spek session amend add-note <text> [--input-json]` — append an amendment note
- `spek session amend status` — show amendments

## Build

- `spek session build note <text> [--input-json]` — append a build-time note
- `spek session build unnote <key>` — remove a build note by key
- `spek session build status` — show build notes

## Detour

- `spek session detour add <text> [--input-json]` — record a detour
- `spek session detour status` — show detours

## Review

- `spek session review start` — start a new review pass
- `spek session review add-finding <pass_key> <type> <severity> <text> [--input-json]` — add a finding (types: bug, grammar, spec, question, dead_code, plan, security, test; severities: critical, major, minor, nit)
- `spek session review approve <pass_key>` — approve a review pass (all findings must be closed)
- `spek session review close-finding <pass_key> <key>` — close a finding
- `spek session review reopen-finding <pass_key> <key>` — reopen a finding
- `spek session review set-fix-note <pass_key> <key> <text> [--input-json]` — set the fix note for a finding
- `spek session review status [--pass <key>] [--finding <key>]` — show review status

## Stance

- `spek session stance set <name>` — set the active stance
- `spek session stance clear` — clear the active stance
- `spek session stance status` — show the active stance

## Example

```bash
spek session plan add-step models - << 'EOF'
# User Model

Create **Pydantic** models for the user schema with proper field validation
- Required fields: `id`, `email`, `created_at`
- Optional fields: `updated_at`, `is_active`
EOF
```

All commands accept `--json` for machine-readable output. See `spek session --help` for the full command list.
