---
spek:
  description: "SQLModel ORM conventions"
---

# SQLModel

- Use separate classes for table models and API schemas when they diverge — do not reuse a table model directly as a response body
- Use `Field(foreign_key=...)` for relationships; define `Relationship()` explicitly rather than relying on implicit joins
- Use `select()` for queries — prefer SQLModel's typed query builder over raw SQL strings
- Use `Session` from `sqlmodel` (not SQLAlchemy directly) to stay within the typed API
- Manage sessions via dependency injection; never share a session across requests
