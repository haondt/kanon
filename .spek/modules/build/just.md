---
spek:
  description: "just task runner conventions"
---

# just conventions

- If a justfile is present, ensure its existence is noted in STRUCTURE.md
- When a justfile is present, prefer `just <recipe>` over the raw underlying command — recipes may set required environment variables or manage dependencies the raw command skips
- Add a recipe when a command is complex (multi-step, multi-flag, or requires specific env setup) or frequently run and project-specific
- Recipe names: `kebab-case`, named after what is accomplished, not the tool invoked (`test`, not `run-pytest`)
- Recipe arguments take defaults: `venv force="false":`; use `[arg()]` for typed, flagged CLI arguments
- Conventional recipe names: `dev` (start dev server), `build` (compile/build), `test` (run suite), `install` (install deps), `clean` (remove artifacts), `reinstall` (`clean` + `install`)
- For idempotent recipes, use a `force` argument defaulting to `"false"` (`venv force="false":`); expose it as a CLI flag with `[arg("force", short="f", long="force", value="true")]` if direct invocation is needed
