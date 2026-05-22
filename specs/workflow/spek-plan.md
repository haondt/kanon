---
spek:
  description: "When starting a task — design the approach, agree on it before writing code, and record the plan in SESSION.md"
  output: skill
  name: spek-plan
  integrations:
    claude:
      disable-model-invocation: true
---
Produce a concrete plan, get approval, write it to `.spek/SESSION.md`, and stop. Do not write code or edit files at any point during this skill.

1. **Establish the goal.** If an argument was passed to this skill, that is the goal. Otherwise read `.spek/SESSION.md`; if it has no goal, infer from the conversation. Ask only if the goal is still unclear.
2. **Explore** the codebase as needed to understand relevant current state.
3. **Propose a plan.** Numbered steps; for each, state what changes and why. Surface trade-offs and give your recommendation where choices exist.
4. **Wait for explicit approval.** A reply that adds context or asks questions is not approval — wait for a clear "yes", "approved", or equivalent before doing anything else.
5. **Write the plan to `.spek/SESSION.md`** under a `## Plan` heading. It must be self-contained: executable without referring back to this conversation.
6. **Stop.** Prompt the user to run `/spek-build`. Do not write code, edit files, or take any other action.
