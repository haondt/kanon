---
spek:
  description: "Bulma list page with live search toolbar and action buttons"
  keywords:
    - bulma
    - list
    - search
    - toolbar
    - table
    - htmx
    - hyperscript
    - filter
---
```html
<div class="field is-grouped">
    <div class="control is-expanded">
        <form hx-get="/items/search" hx-target="#item-list" hx-swap="outerHTML">
            <p class="control">
                <input
                    _="on input debounced at 200ms send submit to the closest <form />"
                    class="input"
                    name="search"
                    placeholder="Search"
                    type="search" />
            </p>
        </form>
    </div>
    <div class="control buttons">
        <a href="/items/new" hx-boost="true" class="button is-primary">New item</a>
    </div>
</div>

<div id="item-list">
    <!-- list content: table, ul/ol, grid, etc. -->
</div>
```

**Placeholders:** Endpoint URLs (`hx-get`, `href`), the `hx-target` ID (`#item-list`), icon implementation, button label and href.

**Notes:** `field is-grouped` with `control is-expanded` is what makes the search input stretch to fill available width. The form wraps only the search input — action buttons are independent of form submission. The hyperscript debounce (`on input debounced at 200ms send submit to the closest <form />`) drives live search without a separate submit button.

**Extension:** Additional action buttons (Import, Delete Selected, etc.) go in the same `control buttons` div. A filter dropdown fits there too.
