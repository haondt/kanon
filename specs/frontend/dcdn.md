---
spek:
  description: "Guidelines for managing local vendor assets with dcdn"
---

# dcdn

dcdn pulls individual files from npm packages into a local directory, replacing CDN `<script>` and `<link>` tags with self-hosted assets.

- Initialize a project with `dcdn init [output-dir]`, which creates `dcdn.json`
- `dcdn add <package>[@version][/path]` — add a file and update `dcdn.json`; prefer latest version unless pinning is required
- `dcdn install` — copy all files listed in `dcdn.json` to the output directory; run after cloning or pulling
- `dcdn remove <package>[@version][/path]` — remove a file; `dcdn update [package]` — update to latest
- Commit the generated files `dcdn.json`, `package.json`, and `bun.lock`; do not commit `node_modules/` or the output directory
