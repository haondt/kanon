---
kanon:
  description: Amend the current session goal or plan without restarting
  output: skill
  name: kanon-amend
  skill:
    model_invokable: false
---
You are amending an in-progress session. Your job is to update `session.yaml` to reflect a change in direction — without starting a new define/plan cycle.

1. Run `kanon session goal` to check if a session exists. If it fails, tell the user there is no active session to amend and stop.

2. Determine what to amend:
   - If the invocation message contains a description, use it.
   - If not, look at the immediately preceding conversation. If the user's last message(s) clearly describe a desired change (e.g. "actually let's do X instead"), state your interpretation in one sentence and proceed.
   - If the intent is still unclear, ask: "What would you like to amend?"

3. Run `kanon session status --full --json` to read the current goal and plan.

4. Apply the amendment:
   - Goal changed: `kanon session amend goal "<new goal>"`
   - Plan step changed: `kanon session amend plan step <key> "<new text>"` (preserves `done` flag)
   - Plan note changed: `kanon session amend plan note <key> "<new text>"`
   - Note removed: `kanon session amend plan unnote <key>`
   - Both goal and plan: apply both.

5. Record the amendment: `kanon session amend add-note "<what changed and why>"`

6. Confirm what was amended in one sentence.
