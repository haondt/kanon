---
spek:
  description: Execute the implementation plan recorded in SESSION.md
  output: command
  name: spek-build
  integrations:
    claude:
      disable-model-invocation: true
      context: fork
---
You are in the implementation phase. Your job is to execute the agreed plan faithfully.

1. Read `.spek/SESSION.md`. If no `## Plan` section exists, tell the user to run `/spek-plan` first.
2. Execute the plan step by step. Keep `.spek/SESSION.md` updated as you go — it should be a living record of the session:
   - Mark steps complete as they are finished
   - Record any assumptions made and why
   - Note significant technical decisions and the reasoning behind them
   - Log any deviations from the original plan, even minor ones
   - This should be a purely additive process. Do not make any destructive or reductive changes to the plan's content.
3. If you discover that a step cannot be done as planned, or that the plan needs to change, stop and flag it to the user before proceeding. Do not silently deviate.
4. When implementation is complete, write a 2-3 sentence session summary: how closely the implementation followed the plan, any notable deviations or surprises, and whether anything was left unresolved. Then prompt the user to run `/spek-review` (optional) or `/spek-retro`.
