---
spek:
  description: "When to use plain dicts"
---

# Python data modeling — plain dicts

- Use plain dicts for simple, short-lived, or loosely structured data
- Use `TypedDict` when the shape is fixed and type safety matters but a full model class would be overkill
- Do not use dataclasses or advanced modeling. Stick to plain dictionaries exclusively.
