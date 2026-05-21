---
spek:
  description: "PostgreSQL conventions"
---

# PostgreSQL

- Use parameterized queries exclusively; never interpolate values into SQL strings
- Use `ON CONFLICT` for upserts rather than select-then-insert application logic
