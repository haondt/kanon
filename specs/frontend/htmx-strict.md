---
spek:
  description: "Enforce htmx as the only mechanism for server interactions"
---

# htmx — enforcement

- Use htmx for all server interactions; do not use `fetch`, `XMLHttpRequest`, or any JS HTTP client
- Server endpoints must return HTML fragments, not JSON — do not build JSON API endpoints for frontend consumption
- Do not introduce a frontend framework (React, Vue, Alpine, etc.) alongside htmx
- JavaScript that performs its own network requests is only acceptable for third-party integrations (e.g. analytics, payment SDKs) with no htmx equivalent
