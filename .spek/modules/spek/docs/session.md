---
spek:
  description: "session.yaml schema and CLI reference"
---

# Session schema

`.spek/session.yaml` is the backing file for the current session. It is deleted at retro.

## Fields

| Field | Type | Description |
|---|---|---|
| `goal` | string | What the session is trying to accomplish |
| `plan.steps` | dict[key → step] | Step objects with `text` (string) and `done` (bool) |
| `plan.notes` | dict[key → string] | Stable-keyed plan-time notes (keys: `pn1`, `pn2`, …) |
| `stance` | string \| null | Active stance name |
| `build.notes` | dict[key → string] | Stable-keyed build-time notes (keys: `bn1`, `bn2`, …) |
| `review` | dict[pass-key → pass] | Review passes; each pass has `status` and `findings` dict |
| `review[p].status` | `Literal['open','approved']` | Pass-level approval marker; `'open'` until all findings are closed |
| `review[p].findings` | dict[key → finding] | Finding objects with `type`, `severity`, `text`, `status`, and optional `fix_note` |
| `amendments` | list[string] | One-line records of goal or plan changes |
| `detours` | list[string] | One-line records of out-of-scope edits |
| `_meta.next_key` | dict[ns → int] | Tracks next available key per namespace; never decremented |

Finding `status` values: `open` | `closed` | `reopened`

`FindingType` values: `bug` | `grammar` | `spec` | `question` | `dead_code` | `plan` | `security` | `test`

`FindingSeverity` values: `critical` | `major` | `minor` | `nit`

Key namespaces: `pn` (plan notes), `bn` (build notes), `f` (findings, global across passes), `p` (review passes)

## CLI

All `spek session` and `spek todo` commands accept `--json`. Read commands include a `hash` field. Write commands include `before` and `after` hashes.

See `spek session --help` and `spek todo --help` for the full command list.
