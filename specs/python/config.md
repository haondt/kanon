# Python configuration and environment

- Read configuration from environment variables; never hardcode secrets or environment-specific values
- Use a single config object (dataclass or Pydantic model) populated at startup — do not scatter `os.getenv` calls throughout the codebase
- Validate and fail fast at startup if required config is missing; do not defer config errors to runtime
- Provide a `.env.example` with all required variables documented (but no real values); add `.env` to `.gitignore`
- Distinguish between environment tiers (`development`, `staging`, `production`) via an explicit `ENV` variable rather than feature flags or hostname detection
