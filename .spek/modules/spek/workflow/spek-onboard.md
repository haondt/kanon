---
spek:
  output: skill
  name: spek-onboard
  description: 'Onboard an existing project: write STRUCTURE.md and select modules'
  skill:
    model_invokable: false
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools: []
---

You are onboarding an existing ("brownfield") project into spek. Your job is to understand the project, write its STRUCTURE.md, select and apply appropriate modules, and surface inline TODOs.

1. **Check prerequisites.** Verify `.spek/spek.yaml` exists. If it does not, stop and tell the user to run `spek init` followed by `spek sync` first.

2. **Crawl the project.** Read the directory tree and key config files: `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, `justfile`, `Makefile`, `docker-compose.yml`, `Dockerfile`, CI config (`.github/workflows/`, `.gitlab-ci.yml`), and the existing README. Build a picture of the tech stack, project structure, and key patterns.

3. **Write `.spek/STRUCTURE.md`.** If the file already exists and has content beyond a placeholder, ask the user whether to overwrite before proceeding. Write a complete structure document following the `docs/structure` conventions: project summary (one sentence + 3–5 bullets), annotated directory layout, key modules or packages and how they relate, tech stack, architectural patterns, domain concepts, and non-obvious conventions.

4. **Select modules.** Use `spek module list` to enumerate available modules. Based on the tech stack and project shape from step 2, select the modules that apply. Prefer specificity — if the project uses Docker, include the relevant docker module; if it does not, leave it out.

5. **Present the proposed selection** to the user and wait for explicit approval. Call out any borderline inclusions and explain why you included or excluded them.

6. **Apply the selection.** Once approved, run `spek module set --sync <module>...` with the full approved list.

7. **Extract inline TODOs.** Grep source files for `TODO:` comments, excluding generated directories (`.venv`, `venv`, node_modules, `.git`, build output, dist). For each unique TODO found, run `spek todo add --section <key> "<text>"` to add it under an appropriate category. Skip any already covered by an existing backlog item.

8. **Report.** Summarize what was written to STRUCTURE.md, which modules were added or removed, and how many TODOs were extracted.
