---
kanon:
  description: Iterate conversationally on a change without the session workflow
  output: skill
  name: kanon-iterate
  skill:
    model_invokable: false
---
You are entering iterate mode. The user is building / wants to build something back-and-forth — chat, change, revise, repeat — without a plan or session.

For the remainder of this conversation:

- If a session exists, add a detour note that iterate mode was invoked. Otherwise, don't create or use one; record nothing
- Get explicit approval of the exact change before making it. Approving a plan is not approving execution
  - A plan that changes in any way voids earlier approval, including a change in the same message as the approval ("write it up, but make it yellow"). Restate the plan and ask again
  - Exploratory comments ("what do you think?", "can you make it do both?", "why didn't you add this?") invite discussion, not work
- Before building something from scratch, run `kanon ref search <terms>` and read matches with `kanon ref read <name>`
- Between changes, discuss freely: answer questions, surface trade-offs, take feedback

Iterate mode ends when the user invokes another skill or signals they are done.
