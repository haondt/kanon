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

## Behaviors (external scripts)

When hyperscript logic is reused across multiple elements or grows large enough to be unwieldy inline, move it to a standalone `._hs` file using the `behavior` feature:

```hyperscript
-- assets/behaviors/collapsible._hs
behavior Collapsible
  on click toggle .open on me
  toggle @aria-expanded on me
end
```

Serve the file as a static asset and load it with a `<script>` tag:

```html
<script src="/assets/behaviors/collapsible._hs" type="text/hyperscript"></script>
```

Install the behavior on elements with the `install` attribute:

```html
<div class="collapsible" install="Collapsible">...</div>
```

See [hyperscript.org/features/behavior](https://hyperscript.org/features/behavior/) for full documentation.

## Guidelines

- Prefer `_` attribute over `script` blocks for inline behavior
- Prefer `add`/`remove`/`toggle` for class manipulation over direct `.classList` calls
- Use `wait` for simple delays; avoid `setTimeout` in _hyperscript blocks
- Move reused or large hyperscript blocks into a `behavior` in a `._hs` file rather than duplicating inline
