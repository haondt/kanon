---
kanon:
  description: Turn a vague idea into a concrete, plannable goal
  output: skill
  name: kanon-sketch
  skill:
    model_invokable: false
---
You are helping the user turn a fuzzy or abstract idea into a concrete, plannable goal. This step is optional — if the user already knows what they want to build, they should skip directly to `/kanon-plan`.

1. Ask the user what they have in mind. If they've already described an idea in their invocation message, treat that as the starting point.
2. Ask clarifying questions to sharpen the idea: what problem is being solved, what success looks like, what is in or out of scope. Avoid asking for specific files or implementation details — that belongs in `/kanon-plan`.
3. Write the concrete goal using `kanon session start "<goal>"`. If a session already exists, use `kanon session amend goal "<goal>"` instead.
4. Confirm what was written, then prompt the user to run `/kanon-plan` when ready.
