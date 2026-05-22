---
spek:
  description: "htmx auto-save input with inline success/failure indicator"
  keywords:
    - htmx
    - hyperscript
    - input
    - autosave
    - live
    - feedback
    - form
    - settings
    - select
    - checkbox
---

# Live input with htmx feedback

An input that auto-saves via `hx-post` and shows a success or failure indicator inline. No page navigation, no full form submit.

## Pattern

Place the input and two indicator spans inside a common wrapper element. The hyperscript uses DOM traversal to find the indicators relative to the input:

```html
<div class="my-wrapper">
    <select
        name="my_setting"
        hx-trigger="change"
        hx-post="/settings"
        hx-swap="none"
        _="on htmx:beforeRequest
               send hide to the next .success-indicator within the closest .my-wrapper
               send hide to the next .failure-indicator within the closest .my-wrapper
           end
           on htmx:afterRequest
               if event.detail.xhr.status == 200
                   send show to the next .success-indicator within the closest .my-wrapper
               else
                   send show(status: event.detail.xhr.status) to the next .failure-indicator within the closest .my-wrapper
               end
           end">
        <option>...</option>
    </select>

    <span class="success-indicator hidden"
          _="on show remove .hidden end  on hide add .hidden to me">
        ✓
    </span>
    <span class="failure-indicator hidden"
          _="on show(status) remove .hidden set my innerHTML to status end  on hide add .hidden to me">
    </span>
</div>
```

## How it works

- `htmx:beforeRequest` hides both indicators before each request.
- `htmx:afterRequest` shows the success span on 200, or the failure span with the HTTP status code otherwise.
- The indicators receive custom `show` / `hide` events — they manage their own visibility.
- `hx-swap="none"` discards the response body; only the status code matters.
- The wrapper class (`.my-wrapper`) is the only structural requirement — use whatever suits your markup.

## Trigger by input type

| Input type | `hx-trigger` |
|---|---|
| `<select>` | `change` |
| `<input type="number">` / `<input type="text">` | `input delay:0.5s` |
| `<input type="checkbox">` | `change` |
