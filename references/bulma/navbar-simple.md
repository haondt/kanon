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
            <p class="title is-3">App Name</p>
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
            <a href="/section-one" hx-boost="true" class="navbar-item">Section One</a>
            <a href="/section-two" hx-boost="true" class="navbar-item">Section Two</a>
        </div>
        <div class="navbar-end">
            <a href="/settings" hx-boost="true" class="navbar-item">Settings</a>
        </div>
    </div>
</nav>
```

**Placeholders:** App name, hrefs, and link labels. `id="navbar"` is only needed if targeted externally.

**Notes:** The burger hyperscript toggles `.is-active` on itself and `next .navbar-menu` (opening/closing the mobile menu); the four `<span>`s render the icon. `hx-boost` converts links to fetch-based navigation.
