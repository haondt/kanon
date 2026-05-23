---
spek:
  description: "make conventions"
---

# make conventions

- Prefer `make` when there is a real dependency graph (outputs depend on inputs and should only rebuild when stale); for pure task running with no file dependencies, prefer `just`
- Add a target when a command is complex or frequently run and project-specific; do not add targets for generic commands (`git commit`, `docker ps`)
- Declare `.PHONY` directly above each target that does not produce a file of the same name; a missing declaration causes `make` to skip the target silently if a file with that name exists
- Variables: `UPPER_CASE`; prefer `:=` (immediate assignment) over `=` (deferred) unless lazy evaluation is needed; set `SHELL := /bin/bash` at the top for consistent behavior
- Use `$(shell ...)` for computed variable assignments (e.g. `VERSION := $(shell git describe --tags)`)
- Suppress command echo with `@` on lines where the output makes the command redundant
- Use `$(MAKE)` instead of `make` when recursing into sub-makes so flags propagate
- Use `|| true` for commands that may fail harmlessly: `docker rmi $(IMAGE) || true`
- Conventional target names: `build` (compile/build), `clean` (remove artifacts), `test` (run suite), `install` (install deps or deploy)
