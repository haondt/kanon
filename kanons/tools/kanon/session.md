---
kanon:
  description: "kanon session CLI reference"
---

# kanon session CLI

For multi-line content, use a heredoc with stdin (pass `-` as the argument) to avoid shell escaping issues:

```bash
kanon session plan add-step frontmatter - << 'EOF'
# Multi-line content here
EOF
```

## Session lifecycle

- `kanon session start <goal>` — create a new session
- `kanon session goal` — read the current session goal
- `kanon session status [--full]` — show session summary
- `kanon session lint` — validate the session file
- `kanon session clear` — delete the session file

## Plan

- `kanon session plan status [--key]` — show plan status (all steps or specific step)
- `kanon session plan add-step <key> <text> [--input-json]` — add a plan step with markdown description
- `kanon session plan check <key>` — mark a plan step as done
- `kanon session plan uncheck <key>` — mark a plan step as not done
- `kanon session plan note <text> [--input-json]` — append a plan-time note

## Amend

- `kanon session amend goal <text> [--input-json]` — overwrite the session goal
- `kanon session amend plan step <key> <text> [--input-json]` — overwrite a plan step's text
- `kanon session amend plan note <key> <text> [--input-json]` — edit an existing plan note
- `kanon session amend plan unnote <key>` — remove a plan note by key
- `kanon session amend add-note <text> [--input-json]` — append an amendment note
- `kanon session amend status` — show amendments

## Build

- `kanon session build note <text> [--input-json]` — append a build-time note
- `kanon session build unnote <key>` — remove a build note by key
- `kanon session build status` — show build notes

## Detour

- `kanon session detour add <text> [--input-json]` — record a detour
- `kanon session detour status` — show detours

## Review

- `kanon session review start` — start a new review pass
- `kanon session review add-finding <pass_key> <type> <severity> <text> [--input-json]` — add a finding (types: bug, grammar, kanon, question, dead_code, plan, security, test; severities: critical, major, minor, nit)
- `kanon session review approve <pass_key>` — approve a review pass (all findings must be closed)
- `kanon session review close-finding <pass_key> <key>` — close a finding
- `kanon session review reopen-finding <pass_key> <key>` — reopen a finding
- `kanon session review set-fix-note <pass_key> <key> <text> [--input-json]` — set the fix note for a finding
- `kanon session review status [--pass <key>] [--finding <key>]` — show review status

## Stance

- `kanon session stance set <name>` — set the active stance
- `kanon session stance clear` — clear the active stance
- `kanon session stance status` — show the active stance

## Example

```bash
kanon session plan add-step models - << 'EOF'
# User Model

Create **Pydantic** models for the user schema with proper field validation
- Required fields: `id`, `email`, `created_at`
- Optional fields: `updated_at`, `is_active`
EOF
```

All commands accept `--json` for machine-readable output. See `kanon session --help` for the full command list.
