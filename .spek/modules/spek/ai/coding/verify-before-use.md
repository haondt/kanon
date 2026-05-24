---
spek:
  description: "Verify APIs exist before calling them"
---

# AI verification before use

- Before using a library method or class, confirm it exists in the installed version — check docs, source, or type stubs; do not rely on training-data recall
- Before using a configuration option, verify it is a valid key in the actual config schema for the version in use
- Before referencing a CLI flag, confirm it exists via `--help` or the source
- If a method, option, or flag cannot be verified, say so rather than proceeding on an assumption
- When uncertain whether something exists, prefer the simpler path that avoids the unverified dependency
