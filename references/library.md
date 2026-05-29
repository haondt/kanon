---
spek:
  description: "How to structure a spek spec library"
  keywords:
    - spek
    - library
    - structure
    - layout
    - authoring
---

# spek library structure

A spek library is a directory (typically a git repo) with four top-level subdirectories:

```
specs/          # spec modules — rules and skills
references/     # reference entries
profiles/       # named module+stance bundles
stances/        # on-demand behavioral overlays
```

All four are optional; omit any that aren't needed.

## specs/

Each `.md` file is a module. The file path relative to `specs/` (without extension) is its name — e.g. `specs/python/style.md` → `python/style`.

Group by domain or tool. Flat is fine for small libraries; subdirectories help once you have more than ~10 modules.

See `spek ref read spek::modules` for module authoring conventions.

## references/

Each `.md` file is a reference entry. The file path relative to `references/` (without extension) is its name — e.g. `references/htmx/live-input.md` → `htmx/live-input`.

Group by tool or domain.

See `spek ref read spek::references` for reference authoring conventions.

## profiles/

Each `.yaml` file is a named profile. The file path relative to `profiles/` (without extension) is its name — e.g. `profiles/python/cli.yaml` → `python/cli`.

A profile bundles modules and stances, and can extend other profiles:

```yaml
description: "Python CLI project conventions"
extends:
  - self::base          # another profile in this library
modules:
  - self::python/style  # a spec module in this library
  - self::python/build
stances:
  - self::verbose       # a stance in this library
```

Use `self::` to reference items within the same library. When consumed by a project, `self::` is resolved to the library's source name.

## stances/

Each `.yaml` file is a named stance. The file path relative to `stances/` (without extension) is its name.

A stance is a temporary overlay that activates a set of modules on demand:

```yaml
description: "Verbose output mode"
modules:
  - self::style/verbose
```
