---
spek:
  description: "How to write a reference entry for the spek reference library"
---

# Reference entry style

A reference is a starting point — something an AI or developer can lift and adapt. It can be a code snippet, a fill-in-the-blank template, library documentation, a methodology, a process definition, architectural guidelines, or anything else worth having on hand during implementation.

## What belongs

- The core content: minimal and portable, not tied to one project's choices
- Brief explanation of non-obvious parts
- Variants when the implementer faces a meaningful choice

## What doesn't

- Project-specific details (endpoint URLs, field names, business logic) — use placeholders, stubs or example values
- Anything that would need to be rewritten for a different project

## Structure

1. **One-line description** — what it does or is, in a sentence
2. **Core content** — the primary reference material (code, template, definition, process steps, etc.)
3. **Explanation** — only what the code or content doesn't make obvious
4. **Variants** — when there's a meaningful choice the implementer must make

Not every section is required. A simple code snippet may need no explanation; a methodology entry may have no variants.

## Length

Keep entries under ~200 lines. If an entry is growing beyond that, either split it into focused sub-entries or link to external documentation.

## Frontmatter

```yaml
spek:
  description: "Short description — what it does, not what it is"
  keywords:
    - tool name
    - pattern name
    - what you would search for
```

Keywords are what an implementer would type when searching — include the tools involved and the problem being solved.

## File location

```
references/<topic>/<entry-name>.md
```

The file path (without extension) is the name passed to `spek ref read`. Group by tool or domain (`htmx/live-input`, `bulma/list-page`).
