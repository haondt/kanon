---
spek:
  output: skill
  name: spek-plan
  description: |-
    When starting a task — design the approach, agree on it before writing code, and record the plan in session.yaml
  skill:
    model_invokable: false
    human_invokable: true
    needs_context: true
  needs_context: true
  preapproved_tools: []
---
Produce a concrete plan, get approval, write it to `session.yaml`, and stop. Do not write code or edit files at any point during this skill.

1. **Establish the goal.** If an argument was passed to this skill, that is the goal. Otherwise run `spek session goal` to read the existing goal; if no session exists, infer from the conversation. Ask only if the goal is still unclear.
2. **Explore** the codebase as needed to understand relevant current state.
3. **Search the reference library.** Run `spek ref search <terms>` with keywords describing the goal. Retrieve and read any matching entries with `spek ref read <name>` before proposing the plan. Only skip this step if the goal is purely organizational or has no implementation component.
4. **Propose a plan.** Numbered steps; for each, state what changes and why. Surface trade-offs and give your recommendation where choices exist.
5. **Wait for explicit approval.** A reply that adds context or asks questions is not approval — wait for a clear "yes", "approved", or equivalent before doing anything else.
6. **Write the plan to `session.yaml`:**
   - If no session exists: `spek session start "<goal>"`
   - Add each step: `spek session plan add-step <key> "<text>"` (use descriptive keys, e.g. `models`, `session-cli`, `tests`)
   - Add any important notes: `spek session plan note "<text>"`
   - The plan must be self-contained: executable without referring back to this conversation. Use markdown formatting for the plan steps and notes to create a detailed and comprehensive plan.
7. **Stop.** Prompt the user to run `/spek-build`. Do not write code, edit files, or take any other action.
