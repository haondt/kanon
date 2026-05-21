---
spek:
  description: "Python dataclasses usage"
---

# Python data modeling — dataclasses

- Use `@dataclass` for structured data; prefer it over plain dicts or tuples for anything with more than 2-3 fields
- Type-annotate all fields
- Use `field(default_factory=...)` for mutable defaults; never use a mutable default directly
- Use `@dataclass(frozen=True)` for value objects that should not be mutated after creation
