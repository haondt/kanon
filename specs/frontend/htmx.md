---
spek:
  description: "Guidelines for using htmx for server-driven interactions"
---

# htmx

htmx extends HTML with attributes for AJAX, WebSockets, and server-sent events. Server responses return HTML fragments, not JSON.

## Core attributes

| Attribute | Purpose |
|---|---|
| `hx-get`, `hx-post`, `hx-put`, `hx-patch`, `hx-delete` | Issue a request on trigger |
| `hx-target` | Where to put the response (`#id`, `closest .class`, `this`) |
| `hx-swap` | How to insert (`innerHTML`, `outerHTML`, `beforeend`, `afterend`, etc.) |
| `hx-trigger` | What triggers the request (`click`, `change`, `every 2s`, `revealed`) |

## Common patterns

**Load on reveal (infinite scroll / lazy load)**
```html
<div hx-get="/items?page=2" hx-trigger="revealed" hx-swap="afterend">...</div>
```

**Live search**
```html
<input hx-get="/search" hx-trigger="input changed delay:300ms" hx-target="#results">
```

**Delete with removal**
```html
<tr hx-delete="/item/1" hx-confirm="Delete?" hx-target="closest tr" hx-swap="outerHTML swap:1s">
```

**Out-of-band updates**
Return `hx-swap-oob` elements in the response to update parts of the page outside the target:
```html
<span id="count" hx-swap-oob="true">42</span>
```

## Guidelines

- Return HTML fragments from the server, not JSON — htmx is not a JSON API consumer
- Use `hx-boost` on `<body>` or `<a>`/`<form>` to progressively enhance navigation
