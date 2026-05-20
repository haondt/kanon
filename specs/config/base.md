# Configuration conventions

- Read configuration from environment variables; never hardcode secrets or environment-specific values
- Validate and fail fast at startup if required config is missing or invalid
- Provide sample values for configuration somewhere. If the project has a built-in sample configuration mechanism (e.g. `appsettings.Production.json`), external or embedded documentation, etc, use that, otherwise document them in the README.
- Distinguish environment tiers via an explicit variable (e.g. `APP_ENVIRONMENT=dev`) rather than hostname detection or feature flags
- Prefix all environment variables with a short project-specific namespace (e.g. `DRIP_`, `MYAPP_`) to avoid collisions
