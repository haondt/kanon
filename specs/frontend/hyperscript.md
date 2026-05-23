---
spek:
  description: "Guidelines for using _hyperscript for client-side scripting"
---

# _hyperscript

_hyperscript is an event-driven scripting language designed for HTML. It lives in `_` attributes and responds to DOM events. Handlers follow `on <event> <commands>`; target elements with `me` (self), `#id`, `.class`, or `<tag/>`; chain commands with `then`.

- Prefer `_` attribute over `script` blocks for inline behavior
- Prefer `add`/`remove`/`toggle` for class manipulation over direct `.classList` calls
- Use `wait` for simple delays; avoid `setTimeout` in _hyperscript blocks
- Move reused or large hyperscript blocks into a `behavior` in a `._hs` file (served as a static asset, loaded with `<script type="text/hyperscript">`, installed with the `install` attribute) rather than duplicating inline
