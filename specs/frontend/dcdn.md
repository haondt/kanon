---
spek:
  description: "Guidelines for managing local vendor assets with dcdn"
---

# dcdn

dcdn pulls individual files from npm packages into a local directory, replacing CDN `<script>` and `<link>` tags with self-hosted assets. It is a wrapper around Bun — `dcdn add` installs packages via Bun and also creates/updates `package.json`, `bun.lock`, and `node_modules/`. `dcdn.json` records only the extra information about which files to extract to the output directory.

## Configuration

`dcdn.json` at the project root:

```json
{
    "output": "static/vendor",
    "npm": {
        "bulma": ["css/bulma.min.css"],
        "@fontawesome/fontawesome-free": ["css/all.min.css"]
    }
}
```

Default output directory is `static/vendor`.

## Commands

| Command | Description |
|---|---|
| `dcdn init [output-dir]` | Create `dcdn.json` |
| `dcdn add <package>[@version][/path]` | Add a file and update `dcdn.json` |
| `dcdn install` | Copy all files listed in `dcdn.json` to the output directory |
| `dcdn remove <package>[@version][/path]` | Remove a file (removes package entry if last file) |
| `dcdn update [package]` | Update all packages or a specific one to latest |

## Adding packages

```sh
# Latest version, specific file
dcdn add bulma/css/bulma.min.css

# Pinned version
dcdn add bulma@1.0.3/css/bulma.min.css

# Scoped package
dcdn add @fortawesome/fontawesome-free@6.4.2/css/all.min.css
```

## Guidelines

Unless otherwise stated, always just add the latest version of a file.
