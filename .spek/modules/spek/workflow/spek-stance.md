---
spek:
  description: Switch behavioral stance by loading a named module set
  output: skill
  name: spek-stance
  args: "[stance-name]"
  integrations:
    claude:
      disable-model-invocation: true
---
You are switching behavioral stance. A stance is a named set of modules that shapes how you approach the current session or task.

1. Determine the requested stance:
   - If the user named a stance in their invocation message, use that.
   - Otherwise, list the available stances by scanning `.spek/stances/` for `.yaml` files and `.spek/local/stances/` if it exists. Show each stance name and its `description` field. Ask the user to pick one.

2. Resolve the stance:
   - Read the chosen `.yaml` file to get its `modules:` list.
   - For each module path (e.g. `ai/behaviors/assume-and-proceed`), look for the file at `.spek/modules/<module-path>.md` (e.g. `.spek/modules/ai/behaviors/assume-and-proceed.md`).
   - Read all resolved module files.

3. Adopt every behavior and instruction described in the resolved files for the remainder of this session.

4. Record the active stance: `spek session stance set "<stance-name>"`. If no session exists, skip this step.

5. Briefly confirm which stance is active and summarize its key behaviors in 2–3 bullet points. Do not reproduce the full file content.

If the user asks to clear or reset the stance, run `spek session stance clear` and confirm.
