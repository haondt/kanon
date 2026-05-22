---
spek:
  description: "Skill: design and get plan approval"
  output: command
  name: spek-plan
---
You are in the planning phase. Your job is to produce a concrete implementation plan and get explicit approval before any code is written.

1. Read `.spek/SESSION.md` if it exists. If it is missing or has no session goal, infer the goal from the surrounding conversation. Only ask the user directly if the goal is still unclear after reading the context.
2. Explore the codebase as needed to understand the current state relevant to the goal.
3. Propose a step-by-step implementation plan. For each step, state what changes and why.
4. Surface trade-offs and alternatives where they exist. Be direct about what you recommend and why.
5. Obtain explicit approval from the user before continuing.
6. Once approved, append the full plan to `.spek/SESSION.md`. Include an appropriate amount of detail relative to the complexity of the plan. A summary table alone is not enough; SESSION.md must be executable without referring back to the conversation.
7. Encourage the user to continue with `/spek-build`. Do not invoke it yourself — stop here and wait.
