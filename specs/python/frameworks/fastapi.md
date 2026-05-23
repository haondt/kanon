---
spek:
  description: "FastAPI app layout and conventions"
---

# FastAPI

- Use `APIRouter` to organize routes by domain; do not put all routes in `__init__.py`
- Use `Depends()` for shared logic: auth, database sessions, validated query params
- Use async route handlers where any I/O is involved
- Use `HTTPException` for error responses with appropriate status codes
- Use the lifespan context manager for startup/shutdown logic; do not use the deprecated `@app.on_event`
- Run with `python -m app`
