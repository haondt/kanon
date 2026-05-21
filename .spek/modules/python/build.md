---
spek:
  description: "Build tool recipe conventions"
---

# Python build tool conventions

When using a command runner (just, make, npm scripts, etc.), include the following Python-specific recipes.

## venv

Always include a `venv` recipe that creates the virtual environment. It should be idempotent — a no-op if the venv already exists:

```just
[script]
venv force="false":
    if [ -d "{{venv}}" ] && [ "{{force}}" != "true" ]; then exit 0; fi
    uv venv --clear {{venv}}
```

Any recipe that requires the venv should declare it as a dependency so it is always present before running.
