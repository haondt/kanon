---
kanon:
  description: Switch behavioral stance by loading a named kanon set
  output: skill
  name: kanon-stance
  skill:
    model_invokable: false
    args: "[stance-name]"
---
You are switching behavioral stance. A stance is a named set of kanons that shapes how you approach the current session or task.

1. Determine the requested stance:
   - If the user named a stance in their invocation message, use that.
   - Otherwise, list the available stances by scanning `.kanon/stances/` for `.yaml` files and `.kanon/local/stances/` if it exists. Show each stance name and its `description` field. Ask the user to pick one.

2. Resolve the stance:
   - Read the chosen `.yaml` file to get its `kanons:` list.
   - For each kanon path (e.g. `ai/behaviors/assume-and-proceed`), look for the file at `.kanon/kanons/<kanon-path>.md` (e.g. `.kanon/kanons/ai/behaviors/assume-and-proceed.md`).
   - Read all resolved kanon files.

3. Adopt every behavior and instruction described in the resolved files for the remainder of this session.

4. Record the active stance: `kanon session stance set "<stance-name>"`. If no session exists, skip this step.

5. Briefly confirm which stance is active and summarize its key behaviors in 2–3 bullet points. Do not reproduce the full file content.

If the user asks to clear or reset the stance, run `kanon session stance clear` and confirm.
