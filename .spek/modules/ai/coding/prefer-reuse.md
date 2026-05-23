---
spek:
  description: "Search existing code before writing new"
---

# Prefer reuse over reinvention

- Before writing new code, search the codebase for an existing implementation of the same logic
- Before adding a dependency, check whether the standard library already covers the need
- When similar logic exists nearby, adapt and share it rather than writing a parallel implementation — within reason; a short segment duplicated twice is preferable to an unnecessary helper function
- When introducing a new pattern, check whether the codebase has already established a convention for that problem and follow it
- Prefer extending an existing abstraction over introducing a new one that serves the same purpose
- Search for established solutions and prior art before proposing a custom approach
- Cite sources or patterns when drawing on prior art
