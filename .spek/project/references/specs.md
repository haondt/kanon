---
spek:
  description: "How to write a spec module"
  keywords:
    - spek
    - specs
    - authoring
    - module
---

# specs

Specs are Markdown files that shape AI behavior — either as always-on rules or as explicitly invoked skills.

## Frontmatter

```yaml
spek:
  description: "One phrase — the constraint, not the module name"
  output: skill           # omit for rules (default)
  name: spek-foo          # required if output: skill
  preapproved_tools:      # optional; tools pre-approved for forked skill contexts
    - Bash(git diff *)
  skill:
    model_invokable: false  # set false to prevent AI from invoking this skill autonomously
    human_invokable: false  # set false to prevent human invocation
    args: "[stance-name]"   # optional; argument hint shown in autocomplete
    needs_context: false    # set false to fork context (injects STRUCTURE.md, sets context: fork)
```

- `description` appears in `spek module list` and as the skill description in the AI tool; for skills, this is shown in autocomplete and is the primary signal used to decide whether to invoke the skill — write it to convey *when* to use it, not just *what* it is; must be 1–1024 characters; include keywords that help agents match the skill to relevant tasks
- `output: skill` marks it as an invocable skill rather than a passive rule
- `name` is the skill name (e.g. `spek-foo` → `/spek-foo`); required for skills
- `preapproved_tools` is a list of tool patterns pre-approved for use in forked skill contexts
- `skill.model_invokable` controls whether an AI agent can invoke this skill autonomously (default `true`); set to `false` for human-only skills
- `skill.human_invokable` controls whether a human can invoke this skill (default `true`)
- `skill.args` is a human-readable argument hint shown in autocomplete (e.g. `"[stance-name]"`)
- `skill.needs_context` controls whether the skill is run with full project context (default `true`); set to `false` to fork context — the skill will inject STRUCTURE.md and run with `context: fork`

## Rules

Always-on guidance injected into every context window. Brevity and unambiguity are the primary constraints — every word costs context, and vague rules produce inconsistent behavior.

- Single `#` heading naming the topic
- Bullets only — no prose paragraphs, no sub-sections
- Each bullet: imperative, specific, and unambiguous; leave no room for interpretation
- Omit rationale — if a rule needs justification, it belongs in a reference entry
- One concern per file; split if mixed
- Target under 15 lines

If you want to add rationale or examples, put them in a reference entry and link from the spec.

## Skills

Loaded on demand when the user or AI invokes the skill. Not injected into every context, so length is governed by clarity rather than token cost.

- `description` (1–1024 characters) must cover both *what* the skill does and *when* to invoke it; include specific keywords so agents can identify it as relevant — a label alone is not enough
- Prose and numbered steps are appropriate; match the structure to the complexity of the workflow
- Be explicit: name the exact files to read or write, the exact checks to perform, the exact output to produce
- Anticipate ambiguity and resolve it in the spec rather than leaving it to the AI to infer

## Project-local modules

Drop a `.md` file in `.spek/local/modules/` to add a project-specific spec. Local modules shadow upstream ones on name collision, allowing a project to override any built-in spec entirely.
