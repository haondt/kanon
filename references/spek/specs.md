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

- `description` appears in `spek module list` and as the skill description in the AI tool; for commands, this is shown in autocomplete and is the primary signal used to decide whether to invoke the command — write it to convey *when* to use it, not just *what* it is
- `output: command` marks it as a slash command rather than a passive rule
- `name` is the slash command name (e.g. `spek-foo` → `/spek-foo`); required for commands
- `args` is a human-readable argument hint shown in autocomplete (e.g. `"[stance-name]"`)
- `integrations` passes additional keys verbatim into the rendered output for a specific tool; for Claude, these become SKILL.md frontmatter fields (`disable-model-invocation`, `context`, etc.)

## Rules

Always-on guidance injected into every context window. Brevity and unambiguity are the primary constraints — every word costs context, and vague rules produce inconsistent behavior.

- Single `#` heading naming the topic
- Bullets only — no prose paragraphs, no sub-sections
- Each bullet: imperative, specific, and unambiguous; leave no room for interpretation
- Omit rationale — if a rule needs justification, it belongs in a reference entry
- One concern per file; split if mixed
- Target under 15 lines

If you want to add rationale or examples, put them in a reference entry and link from the spec.

## Commands

Loaded on demand when the user or AI invokes the slash command. Not injected into every context, so length is governed by clarity rather than token cost.

- `description` must be informative enough for a user or AI to decide when to invoke it — include trigger conditions, not just a label
- Prose and numbered steps are appropriate; match the structure to the complexity of the workflow
- Be explicit: name the exact files to read or write, the exact checks to perform, the exact output to produce
- Anticipate ambiguity and resolve it in the spec rather than leaving it to the AI to infer

## Project-local modules

Drop a `.md` file in `.spek/local/modules/` to add a project-specific spec. Local modules shadow upstream ones on name collision, allowing a project to override any built-in spec entirely.
