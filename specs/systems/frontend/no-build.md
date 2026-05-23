---
spek:
  description: "No-build-step frontend stack: htmx + hyperscript + bulma + dcdn"
---

# No-build frontend stack

This stack builds server-rendered web apps with no bundler, transpiler, or npm build step. The server is the source of truth for all state; the frontend is HTML with behavioral attributes.

- Four tools comprise this stack: **htmx** (server interactions), **_hyperscript** (client-side behavior), **Bulma** (styling), **dcdn** (vendor asset management)
- Do not introduce React, Vue, Alpine, or similar alongside this stack — they are incompatible with the no-build constraint and redundant given htmx + _hyperscript
- Vendor assets are local, not CDN-linked; do not reference unpkg, jsdelivr, cdnjs, or similar in templates
- Use htmx for all server interactions; do not use `fetch`, `XMLHttpRequest`, or any JS HTTP client (exception: third-party integrations with no htmx equivalent, e.g. analytics or payment SDKs)
- Use _hyperscript for all client-side behavior; the only acceptable JS is code embedded inside a `js` block within a _hyperscript handler; do not use `addEventListener`, `querySelector`, or other vanilla JS DOM APIs outside of a `js` block
- Use Bulma for all styling; do not introduce a second CSS framework; reach for Bulma modifier classes before writing custom CSS
