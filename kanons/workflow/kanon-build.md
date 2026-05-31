---
kanon:
  description: Execute the implementation plan recorded in session.yaml
  output: skill
  name: kanon-build
  skill:
    model_invokable: false
    needs_context: false
---
You are in the implementation phase. Your job is to execute the agreed plan faithfully.

1. Run `kanon session status --full --json` to read the plan. If no session exists (command fails), tell the user to run `/kanon-plan` first.
2. Execute the plan step by step. Keep `session.yaml` updated as you go — it should be a living record of the session:
   - Mark steps complete as they are finished: `kanon session plan check <key>`
   - Record assumptions and technical decisions: `kanon session build note "<text>"`
   - Log any deviations from the original plan, even minor ones, as build notes
   - This should be a purely additive process. Do not remove or alter existing steps or notes.
3. If you discover that a step cannot be done as planned, or that the plan needs to change, stop and flag it to the user before proceeding. Do not silently deviate.
4. When implementation is complete, write a 2-3 sentence session summary: how closely the implementation followed the plan, any notable deviations or surprises, and whether anything was left unresolved. Then prompt the user to run `/kanon-review` (optional) or `/kanon-retro`.
