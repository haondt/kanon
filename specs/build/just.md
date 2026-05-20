# just conventions

`justfile` is a task runner, not a build system. Recipes are thin wrappers — they call tools, they don't contain logic.

## Naming

- Use `kebab-case` for recipe names
- Name recipes after what they do, not what they run (`test`, not `run-pytest`)

## Structure

- Always define a default recipe. A bare `just` with no arguments should either list available recipes or run the most common task:
  ```just
  default:
      just --list
  ```
- Group related recipes together; use a comment line as a section header if the file is long

## Recipes

- Keep recipes thin — one or two commands at most; extract complex logic into a script
- If a recipe is just a single command with fixed arguments, it belongs in the justfile; if it has conditionals or loops, it belongs in a shell script that the recipe calls
- Recipes can call other recipes: `just build && just test` or `just install`

## Variables

- Define variables at the top of the file
- Prefer lowercase for local variables, uppercase is not required by convention
