---
spek:
  description: "Guidelines for using _hyperscript for client-side scripting"
---

# _hyperscript

_hyperscript is an event-driven scripting language designed for HTML. It lives in `_` attributes and responds to DOM events.

## Syntax basics

```html
<button _="on click toggle .active on #menu">Toggle</button>
<input _="on input put my.value into #preview.innerHTML">
```

- Event handlers: `on <event> <commands>`
- Target elements: `me` (self), `#id`, `.class`, `<tag/>`
- Chaining: use `then` between commands

## Common patterns

**Toggle visibility**
```html
<button _="on click toggle .hidden on #modal">Open</button>
```

**Fetch and update**
```html
<button _="on click fetch /api/data then put it into #result.innerHTML">Load</button>
```

**Form validation**
```html
<input _="on blur if my.value is empty add .error to me else remove .error from me end">
```

**With htmx**
Keep _hyperscript for local DOM manipulation; let htmx handle server requests.

## Guidelines

- Prefer `_` attribute over `script` blocks for inline behavior
- Prefer `add`/`remove`/`toggle` for class manipulation over direct `.classList` calls
- Use `wait` for simple delays; avoid `setTimeout` in _hyperscript blocks
