---
spek:
  description: Turn a vague idea into a concrete, plannable goal
  output: skill
  name: spek-sketch
  preapproved_tools:
    - Bash(spek session *)
  integrations:
    claude:
      disable-model-invocation: true
---
You are helping the user turn a fuzzy or abstract idea into a concrete, plannable goal. This step is optional — if the user already knows what they want to build, they should skip directly to `/spek-plan`.

1. Ask the user what they have in mind. If they've already described an idea in their invocation message, treat that as the starting point.
2. Ask clarifying questions to sharpen the idea: what problem is being solved, what success looks like, what is in or out of scope. Avoid asking for specific files or implementation details — that belongs in `/spek-plan`.
3. Write the concrete goal using `spek session start "<goal>"`. If a session already exists, use `spek session amend goal "<goal>"` instead.
4. Confirm what was written, then prompt the user to run `/spek-plan` when ready.
