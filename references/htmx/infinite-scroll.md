---
spek:
  description: "htmx infinite scroll with intersect trigger and page-based pagination"
  keywords:
    - htmx
    - infinite scroll
    - pagination
    - intersect
    - lazy load
    - list
    - jinja2
    - flask
---

# Infinite scroll with htmx

A sentinel div at the bottom of a list triggers an htmx request when it scrolls into view, replacing itself with the next page of items (plus a new sentinel if more pages remain).

## Template partial

```html
<div id="items-container">
    {% for item in items %}
    <div class="item">{{ item }}</div>
    {% endfor %}

    {% if next_page is not none %}
    <div
        hx-get="/items"
        hx-trigger="intersect once"
        hx-select="#items-container > *"
        hx-swap="outerHTML"
        hx-vals='{"page": "{{ next_page }}"}'
        style="height: 1px;">
    </div>
    {% endif %}
</div>
```

This partial is both the initial render and the htmx response — the same template handles both cases.

## Backend

```python
PAGE_SIZE = 20

@app.route('/items')
def get_items():
    page = int(request.args.get('page', 0))
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE

    items = fetch_items(start, end)          # replace with real query
    has_more = end < total_item_count()      # replace with real count

    return render_template('items.html',
                           items=items,
                           next_page=page + 1 if has_more else None)
```

The initial page render passes `next_page=1` (or `None` if all items fit). Subsequent calls increment from whatever page the sentinel carried.

## How it works

- `hx-trigger="intersect once"` fires exactly once when the sentinel enters the viewport — prevents duplicate requests on scroll-back.
- `hx-select="#items-container > *"` extracts only the direct children of the container from the response, discarding the outer wrapper.
- `hx-swap="outerHTML"` replaces the sentinel with those children — which include a new sentinel if `next_page` is set, continuing the chain.
- The 1px height prevents a zero-size element — `IntersectionObserver` (which htmx's `intersect` trigger uses) will not fire on elements with no dimensions.
- `hx-vals` injects `page` as a query parameter without needing a form or hidden input.
