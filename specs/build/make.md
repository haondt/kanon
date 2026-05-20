# make conventions

Prefer `make` when there is a real dependency graph (outputs depend on inputs and should only rebuild when stale). For pure task running with no file dependencies, prefer `just`.

## Phony targets

Declare every target that does not produce a file of the same name:

```makefile
.PHONY: build test clean install
```

A missing `.PHONY` declaration causes `make` to skip the target if a file with that name exists.

## Default target

Put the most common task first, or set it explicitly:

```makefile
.DEFAULT_GOAL := build
```

## Variables

- Use `UPPER_CASE` for variables
- Prefer `:=` (immediate assignment) over `=` (deferred) unless deferred evaluation is needed
- Define variables at the top; allow overrides from the command line: `make BUILD_DIR=out`

## Recipes

- Suppress noisy command echo with `@` on lines that don't need it
- Keep recipe bodies thin — shell out to scripts for anything with logic
- Use `$(MAKE)` instead of `make` when recursing into sub-makes so flags propagate correctly
