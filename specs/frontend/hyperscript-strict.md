---
spek:
  description: "Enforce _hyperscript as the only client-side scripting language"
---

# _hyperscript — enforcement

- Use _hyperscript for all client-side behavior; do not write standalone JavaScript
- The only acceptable JS is code embedded inside a `js` block within a _hyperscript handler
- Do not add `<script>` tags or `.js` files for client-side logic
- Do not use `addEventListener`, `querySelector`, or other vanilla JS DOM APIs outside of a _hyperscript `js` block
