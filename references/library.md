---
kanon:
  description: "How to structure a kanon library"
  keywords:
    - kanon
    - library
    - structure
    - layout
    - authoring
---

# kanon library structure

A kanon library is a directory (typically a git repo) with four top-level subdirectories:

```
kanons/         # kanons — rules and skills
references/     # reference entries
profiles/       # named kanon+stance bundles
stances/        # on-demand behavioral overlays
```

All four are optional; omit any that aren't needed.

## kanons/

Each `.md` file is a kanon. The file path relative to `kanons/` (without extension) is its name — e.g. `kanons/python/style.md` → `python/style`.

Group by domain or tool. Flat is fine for small libraries; subdirectories help once you have more than ~10 kanons.

See `kanon ref read kanon::kanons` for kanon authoring conventions.

## references/

Each `.md` file is a reference entry. The file path relative to `references/` (without extension) is its name — e.g. `references/htmx/live-input.md` → `htmx/live-input`.

Group by tool or domain.

See `kanon ref read kanon::references` for reference authoring conventions.

## profiles/

Each `.yaml` file is a named profile. The file path relative to `profiles/` (without extension) is its name — e.g. `profiles/python/cli.yaml` → `python/cli`.

A profile bundles kanons and stances, and can extend other profiles:

```yaml
description: "Python CLI project conventions"
extends:
  - self::base          # another profile in this library
kanons:
  - self::python/style  # a kanon in this library
  - self::python/build
stances:
  - self::verbose       # a stance in this library
```

Use `self::` to reference items within the same library. When consumed by a project, `self::` is resolved to the library's source name.

## stances/

Each `.yaml` file is a named stance. The file path relative to `stances/` (without extension) is its name.

A stance is a temporary overlay that activates a set of kanons on demand:

```yaml
description: "Verbose output mode"
kanons:
  - self::style/verbose
```
