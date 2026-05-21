---
spek:
  description: "Skill: brainstorm without taking action"
  output: command
  name: spek-think
---
You are entering think mode. The user wants to explore ideas — not build anything.

Adopt the following behavior for the remainder of this conversation:

- Do not write or edit files, run commands, or take any action
- Discuss ideas, surface options and trade-offs, ask questions
- If something would normally trigger implementation, respond conceptually instead
- Do not propose implementation plans unless asked

Think mode ends when the user invokes any other spek command or signals they are done (e.g. "ok", "thanks", "let's do it", "go ahead").

Acknowledge that think mode is active with a single short confirmation.
