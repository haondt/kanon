---
spek:
  description: "Skill: design and get plan approval"
  output: command
  name: spek-plan
---
You are in the planning phase. Your job is to produce a concrete implementation plan and get explicit approval before any code is written.

1. Read `.spek/SESSION.md`. If it is missing or has no session goal, tell the user to run `/spek-start` first.
2. Explore the codebase as needed to understand the current state relevant to the goal.
3. Propose a step-by-step implementation plan. For each step, state what changes and why.
4. Surface trade-offs and alternatives where they exist. Be direct about what you recommend and why.
5. Do not write or edit any code yet. Wait for the user to explicitly approve the plan.
6. Once approved, append the full plan to `.spek/SESSION.md`. Include an appropriate amount of detail relative to the complexity of the plan. A summary table alone is not enough; SESSION.md must be executable without referring back to the conversation.
