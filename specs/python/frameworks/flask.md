---
spek:
  description: "Flask app layout and conventions"
---

# Flask

- Use an application factory (`create_app()`) rather than a module-level `app` instance
- Use `Blueprint` to organize routes by domain; register them in the factory
- Use `abort()` for HTTP error responses; use `jsonify()` for JSON responses
- Use `current_app` and `g` for request-scoped context; do not store mutable state on the app object
- Run with `python -m app`

Sample structure:
```
app/
  static/         # static files
    css/
    images/
    js/
  templates/      # html templates
  __init__.py     # create_app() factory — registers blueprints, extensions, error handlers
  __main__.py     # calls app.run
  config.py       # Config class
  routes/
    users.py      # Blueprint
    items.py
  services/       # business logic, no Flask imports
  models/
```

This is just an example. Don't create empty directories/files just to follow the structure.

- The `app.run` call should at minimum include:
  - `debug=config.is_development`
  - `port=config.server_port`
