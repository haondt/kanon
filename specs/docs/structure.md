---
spek:
  description: "STRUCTURE.md maintenance guidelines"
---

# STRUCTURE.md conventions

- Maintain `.spek/STRUCTURE.md` as a living mini-map of the codebase — oriented primarily toward AI assistants, secondarily toward developers
- It should answer: where do things live, how does the project fit together, and what does an AI need to know to navigate without reading every file
- Include: project summary (one sentence + 3–5 bullets), annotated directory layout, key modules and their relationships, tech stack, architectural patterns, domain concepts, and non-obvious conventions
- Use whatever format conveys structure most clearly — annotated directory trees, grouped listings, or prose
- Only call out things that are non-obvious; keep entries to phrases, not sentences
- Update whenever the session meaningfully changes the project's shape: new modules, reorganized directories, renamed concepts, or new architectural patterns
- Small refactors within existing structure do not need an update
