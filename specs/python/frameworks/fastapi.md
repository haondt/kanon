# FastAPI

- Use `APIRouter` to organize routes by domain; do not put all routes in `__init__.py`
- Use `Depends()` for shared logic: auth, database sessions, validated query params
- Use async route handlers where any I/O is involved
- Use `HTTPException` for error responses with appropriate status codes
- Use the lifespan context manager for startup/shutdown logic; do not use the deprecated `@app.on_event`
- Run with `python -m app`

Sample structure:
```
app/
  static/         # static files
    css/
    images/
    js/
  templates/      # html templates
  __init__.py     # FastAPI() instance, lifespan, router includes, create_app()
  __main__.py     # uvicorn entrypoint
  config.py       # Config class
  dependencies.py # shared Depends() functions
  routers/
    users.py      # APIRouter
    items.py
  schemas/        # Pydantic request/response models
  services/       # business logic, no FastAPI imports
  models/         # ORM models
```

This is just an example. Don't create empty directories/files just to follow the structure.

`__main__.py` should look something like this:
```python
from .config import config
import uvicorn

if __name__ == "__main__":
    kwargs = {
        'factory': True,
        'host': '0.0.0.0',
        'port': config.server_port,
        'log_config': None
    }
    if config.is_development:
        kwargs['reload'] = True
        kwargs['reload_excludes'] = 'data'
    uvicorn.run("app:create_app", **kwargs)
```
