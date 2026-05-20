# just conventions

`justfile` is a task runner. Recipes range from one-liners to multi-step shell scripts — use whichever fits.

## When to add a recipe

Add a recipe when a command is:
- **Complex** — multi-step, multi-flag, or requires environment variables set in a specific way. If a new dev would have to look it up, it belongs here.
- **Frequently run and project-specific** — even if simple, if it's something you run constantly and it's specific to this project, put it in the justfile.

Don't add recipes for generic commands that apply to any project. The justfile is for project operations, not general tooling.

## Variables

- Define at the top of the file, lowercase
- Use `/` for path joining: `python := venv / "bin/python"`
- Interpolate with `{{varname}}`

## Naming

- `kebab-case` for recipe names
- Name after what is accomplished, not the tool invoked (`test`, not `run-pytest`)

## Recipes

- List dependencies after the colon: `dev: venv` — `just` runs `venv` first
- For multi-line shell logic, use `[script]` to run the body in a single shell instead of line-by-line:
  ```just
  [script]
  venv force="false":
      if [ -d "{{venv}}" ] && [ "{{force}}" != "true" ]; then exit 0; fi
      uv venv --clear {{venv}}
  ```
- Set environment variables inline: `ENV=dev {{python}} -m app`
- Recipe arguments take defaults: `venv force="false":`

## Arguments

Use `[arg()]` for typed, flagged arguments:

```just
[arg("force", short="f", long="force", value="true")]
venv force="false":
```

```just
[arg('target', pattern='client|silo')]
build target:
```

## Common recipes

These names are conventional — use them where they apply:

| Recipe | What it does |
|---|---|
| `dev` | Start the development server or process |
| `build` | Compile or build the project |
| `test` | Run the test suite |
| `install` | Install dependencies |
| `clean` | Remove generated artifacts (venv, build output, etc.) |
| `reinstall` | `clean` + `install` |

For idempotent recipes, always include a --force flag.
