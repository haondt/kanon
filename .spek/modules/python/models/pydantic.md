# Python data modeling — Pydantic

- Use `BaseModel` for structured data, especially at system boundaries (API payloads, config, deserialized files)
- Use `model_validate()` for deserialization; do not construct models by passing raw dicts to `__init__`
- Use `model_dump(exclude_none=True)` when serializing to avoid noisy output
- Type-annotate all fields; use `field = None` only when `Optional[T]` is the explicit intent
