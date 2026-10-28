---
kanon:
  description: Break the current discussion into a table of items to explore one at a time
  output: skill
  name: kanon-table
  skill:
    model_invokable: false
    args: "[status|sync|clear]"
---
You are managing the table: a graph of items from the current discussion, so threads can be explored one at a time without losing the others. State lives in `.kanon/table.yaml` and is managed with `kanon table` (see its reference). Use the CLI for every change; never edit the file by hand.

Item labels look like `[active]` padded inside the brackets to a fixed width: `[  open  ]`, `[ active ]`, `[resolved]`. Refer to items as `d:{Cookie flags}`.

Pick the behavior from the invocation arguments:

**No arguments — table the discussion**

1. Run `kanon table status --json` to see what is already on the table.
2. Break the current discussion into distinct items: one thread, question or part of a proposal each. Give each a short title and a one- or two-sentence summary.
3. Add only items that are not already on the table: `kanon table add "<title>" --summary "<summary>" [--link <key>]...`. Link items that depend on or affect each other.
4. Run `kanon table status` and show the result. Do not start discussing an item; the user picks which to open.

**`status`** — run `kanon table status` and show the output.

**`clear`** — run `kanon table clear` and confirm.

**`sync`** — reconcile the table with the discussion, with approval:

1. Run `kanon table status --json` and re-read the discussion.
2. Propose changes to existing items and edges only; do not add new items (the user does that with a bare `/kanon-table`). Present them as a numbered list, then stop and change nothing:
   ```
   1. [resolve ]  resolve d:{Cookie flags}
      Settled on httpOnly + SameSite=Lax.

   2. [activate]  set c:{Refresh rotation} active
      Current topic. b:{Token storage} goes back to open.

   3. [ merge  ]  merge a:{Session expiry} into c:{Refresh rotation}
      Both were about token lifetime.

   Apply? (all / numbers / none)
   ```
   Tags are `resolve`, `activate`, `merge`, `link`, `unlink`, `edit` and `remove`, padded inside the brackets to 8 characters. Each change is a tag-and-action line followed by indented explanation: one line for simple changes, more for complex ones.
3. Apply only after the user explicitly approves, and only the approved items, in order. If the user adjusts the list, restate it and ask again. If an approved change depends on a skipped one, say so before proceeding.
4. Run `kanon table status` and show the result.

**Anything else the user asks** (marking items resolved, activating an item, linking, merging, removing items or branches) — do it conversationally with the matching `kanon table` command.

If the table grows past roughly 20 items, suggest moving some to `/kanon-todo`. This is a suggestion, not a limit; do not repeat it once declined.
