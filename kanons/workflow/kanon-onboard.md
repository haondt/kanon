---
kanon:
  description: "Onboard an existing project: write STRUCTURE.md and select kanons"
  output: skill
  name: kanon-onboard
  skill:
    model_invokable: false
---

You are onboarding an existing ("brownfield") project into kanon. Your job is to understand the project, write its STRUCTURE.md, select and apply appropriate kanons, and surface inline TODOs.

1. **Check prerequisites.** Verify `.kanon/kanon.yaml` exists. If it does not, stop and tell the user to run `kanon init` followed by `kanon sync` first.

2. **Crawl the project.** Read the directory tree and key config files: `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, `justfile`, `Makefile`, `docker-compose.yml`, `Dockerfile`, CI config (`.github/workflows/`, `.gitlab-ci.yml`), and the existing README. Build a picture of the tech stack, project structure, and key patterns.

3. **Write `.kanon/STRUCTURE.md`.** If the file already exists and has content beyond a placeholder, ask the user whether to overwrite before proceeding. Write a complete structure document following the `docs/structure` conventions: project summary (one sentence + 3–5 bullets), annotated directory layout, key packages and how they relate, tech stack, architectural patterns, domain concepts, and non-obvious conventions.

4. **Select kanons.** Use `kanon list` to enumerate available kanons. Based on the tech stack and project shape from step 2, select the kanons that apply. Prefer specificity — if the project uses Docker, include the relevant docker kanon; if it does not, leave it out.

5. **Present the proposed selection** to the user and wait for explicit approval. Call out any borderline inclusions and explain why you included or excluded them.

6. **Apply the selection.** Once approved, run `kanon set --sync <kanon>...` with the full approved list.

7. **Extract inline TODOs.** Grep source files for `TODO:` comments, excluding generated directories (`.venv`, `venv`, node_modules, `.git`, build output, dist). For each unique TODO found, run `kanon todo add --section <key> "<text>"` to add it under an appropriate category. Skip any already covered by an existing backlog item.

8. **Report.** Summarize what was written to STRUCTURE.md, which kanons were added or removed, and how many TODOs were extracted.
