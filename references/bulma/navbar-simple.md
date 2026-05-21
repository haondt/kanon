---
spek:
  description: "Bulma navbar with htmx boost and hyperscript burger toggle"
  keywords:
    - bulma
    - navbar
    - navigation
    - burger
    - responsive
    - htmx
    - hyperscript
---
```html
<nav class="navbar" id="navbar">
    <div class="navbar-brand">
        <a href="/" hx-boost="true" class="navbar-item">
            <p class="title is-3">spek</p>
        </a>
        <a
           _="on click toggle .is-active on the next .navbar-menu toggle .is-active on me"
           class="navbar-burger">
          <span></span>
          <span></span>
          <span></span>
          <span></span>
        </a>
    </div>
    <div class="navbar-menu">
        <div class="navbar-start">
            <a href="/commands" hx-boost="true" class="navbar-item">Commands</a>
            <a href="/cli" hx-boost="true" class="navbar-item">CLI</a>
        </div>
        <div class="navbar-end">
            <a href="/settings" hx-boost="true" class="navbar-item">Settings</a>
        </div>
    </div>
</nav>
```

**Placeholders:** App name, hrefs, and link labels are illustrative. `id="navbar"` is only needed if targeted externally. htmx and hyperscript are assumed; use project-appropriate equivalents.

**Notes:** The burger hyperscript toggles `.is-active` on itself and `next .navbar-menu` (opening/closing the mobile menu); the four `<span>`s render the icon. `hx-boost` converts links to fetch-based navigation.
