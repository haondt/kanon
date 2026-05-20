# make conventions

Prefer `make` when there is a real dependency graph (outputs depend on inputs and should only rebuild when stale). For pure task running with no file dependencies, prefer `just`.

## When to add a target

Add a target when a command is:
- **Complex** — multi-step, multi-flag, or requires specific environment setup. If a new dev would have to look it up, it belongs here.
- **Frequently run and project-specific** — even if simple, if it's something you run constantly and it's specific to this project, put it in the Makefile.

Don't add targets for generic commands that apply to any project: `git commit`, `docker ps`. The Makefile is for project operations, not general tooling.

## Phony targets

Declare `.PHONY` directly above each target that does not produce a file of the same name:

```makefile
.PHONY: build
build:
    docker build -t $(IMAGE) .
```

A missing `.PHONY` declaration causes `make` to skip the target silently if a file with that name exists.

## Variables

- `UPPER_CASE` for all variables
- Prefer `:=` (immediate assignment) over `=` (deferred) unless lazy evaluation is needed
- Use `$(shell ...)` for shell evaluation in assignments: `SCRIPT_DIR := $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))`
- Set `SHELL := /bin/bash` at the top for consistent shell behavior

## Recipes

- Multiline commands: use `\` continuation and indent consistently
- Suppress command echo with `@` on lines where the output makes the command redundant
- Use `|| true` for commands that may fail harmlessly: `docker rmi $(IMAGE) || true`
- Use `$(MAKE)` instead of `make` when recursing into sub-makes so flags propagate

## Common targets

These names are conventional — use them where they apply:

| Target | What it does |
|---|---|
| `build` | Compile or build the project (binary, image, etc.) |
| `clean` | Remove generated artifacts |
| `test` | Run the test suite |
| `install` | Install dependencies or deploy |
