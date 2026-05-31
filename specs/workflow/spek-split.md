---
spek:
  description: "Decompose a large plan into a named split of focused sub-plans"
  output: skill
  name: spek-split
  integrations:
    claude:
      disable-model-invocation: true
---
Break a plan down into a named split of smaller, independently executable sub-plans. Do not write code or edit implementation files.

1. **Read the current plan.** Run `spek session status --full --json`. If no session exists, derive the plan from the conversation. If neither is available, ask the user to describe the work.

2. **Propose a decomposition.** Suggest a split name (kebab-case) and a set of sub-plan names with their goals. Each sub-plan should be independently executable. Wait for explicit approval before proceeding.

3. **Create the split.** Once approved:
   - `spek split create <split-name> "<split-goal>"`

4. **Create each sub-plan:**
   - `spek plan create <split-name>/<plan-name> "<goal>"`
   - `spek plan add-step <split-name>/<plan-name> <key> "<text>"` for each step
   - `spek plan note <split-name>/<plan-name> "<text>"` for any relevant notes

5. **Handle the active session** (if one existed):
   - Ask the user: start a fresh session pointing to this split, or discard the session entirely?
   - If fresh session: `spek session clear`, then `spek session start "<updated goal>"`, then `spek session plan add-step next "Work through split '<split-name>' — load next sub-plan with spek session load <split-name>/<plan-name>"`
   - If discarding: `spek session clear`

6. **Confirm.** List the split name and all sub-plan names created.
