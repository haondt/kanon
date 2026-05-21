---
spek:
  description: "Simple Bulma navbar with burger menu"
  keywords:
    - bulma
    - navbar
    - navigation
    - burger
    - responsive
---
<nav class="navbar" role="navigation" aria-label="main navigation">
  <div class="navbar-brand">
    <a class="navbar-item" href="/">
      <strong>App Name</strong>
    </a>
    <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false"
       data-target="navbarMain"
       _="on click toggle .is-active on me then toggle .is-active on #navbarMain">
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
      <span aria-hidden="true"></span>
    </a>
  </div>
  <div id="navbarMain" class="navbar-menu">
    <div class="navbar-start">
      <a class="navbar-item" href="/">Home</a>
    </div>
    <div class="navbar-end">
      <div class="navbar-item">
        <div class="buttons">
          <a class="button is-primary" href="/signup">Sign up</a>
          <a class="button is-light" href="/login">Log in</a>
        </div>
      </div>
    </div>
  </div>
</nav>
