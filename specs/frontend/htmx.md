---
spek:
  description: "Guidelines for using htmx for server-driven interactions"
---

# htmx

htmx extends HTML with attributes for AJAX, WebSockets, and server-sent events.

Core attributes: `hx-get`/`hx-post`/`hx-put`/`hx-patch`/`hx-delete` (issue a request on trigger), `hx-target` (where to put the response), `hx-swap` (how to insert — `innerHTML`, `outerHTML`, `beforeend`, etc.), `hx-trigger` (what triggers — `click`, `change`, `every 2s`, `revealed`).

- Return HTML fragments from the server, not JSON — htmx is not a JSON API consumer
- Use `hx-boost` on `<body>` or `<a>`/`<form>` to progressively enhance navigation
- Use `hx-swap-oob` on elements returned in a response to update parts of the page outside the primary target
