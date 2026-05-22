---
spek:
  description: "How to write a spec module"
  keywords:
    - spek
    - spec
    - authoring
    - module
---

# specs

Specs are Markdown files that shape AI behavior — either as always-on rules or as explicitly invoked slash commands.

## Frontmatter

```yaml
spek:
  description: "One phrase — the constraint, not the module name"
  output: command         # omit for rules (default)
  name: spek-foo          # required if output: command
  args: "[stance-name]"   # optional; generic argument hint
  integrations:           # optional; integration-specific kwargs passed into rendered output
    claude:
      disable-model-invocation: true
      context: fork
```

- `description` appears in `spek module list` and as the skill description in the AI tool
- `output: command` marks it as a slash command rather than a passive rule
- `name` is the slash command name (e.g. `spek-foo` → `/spek-foo`); required for commands
- `args` is a human-readable argument hint shown in autocomplete (e.g. `"[stance-name]"`)
- `integrations` passes additional keys verbatim into the rendered output for a specific tool; for Claude, these become SKILL.md frontmatter fields (`disable-model-invocation`, `context`, etc.)

## Rules

Always-on guidance. Loaded into every context window, so brevity matters.

- Single `#` heading naming the topic
- Bullets only — no prose paragraphs, no sub-sections
- Each bullet: imperative and specific; omit rationale
- One concern per file; split if mixed
- Target under 15 lines

If you want to add rationale or examples, put them in a reference entry and link from the spec.

## Commands

Invoked explicitly by the user. Can be longer and more structured — prose and numbered steps are appropriate. The constraint is clarity, not length.

## Project-local modules

Drop a `.md` file in `.spek/local/modules/` to add a project-specific spec. Local modules shadow upstream ones on name collision, allowing a project to override any built-in spec entirely.
