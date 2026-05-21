---
spek:
  description: "Prefer template loops and reusable fragments over hardcoded repetition"
---

# Template conventions

- Where markup repeats over a list of items (nav links, table rows, cards), drive it from a data structure and loop rather than writing each element out individually
- Extract repeated markup blocks (navbars, footers, form fields) into partials, includes, or components rather than copy-pasting them
