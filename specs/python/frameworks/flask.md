---
spek:
  description: "Flask app layout and conventions"
---

# Flask

- Use an application factory (`create_app()`) rather than a module-level `app` instance
- Use `Blueprint` to organize routes by domain; register them in the factory
- Use `abort()` for HTTP error responses; use `jsonify()` for JSON responses
- Use `current_app` and `g` for request-scoped context; do not store mutable state on the app object
- Run with `python -m app`; the `app.run` call should at minimum pass `debug=config.is_development` and `port=config.server_port`
