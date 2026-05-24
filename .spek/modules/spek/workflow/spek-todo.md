---
spek:
  description: Add an item to the project backlog in todo.yaml
  output: skill
  name: spek-todo
---
You are adding an item to the project backlog. Be autonomous: infer what to write, where to put it, and how much detail to include — ask the user only if the intent is genuinely ambiguous.

1. Determine the item to add:
   - If the invocation message contains a description, use it.
   - If not, look at the immediately preceding conversation for an implied backlog item.
   - Only ask if nothing can be inferred.

2. Run `spek todo status --json` to read the current backlog. Check for an existing item that is substantially the same:
   - **Exact or near-exact duplicate:** skip and tell the user why.
   - **Close but not identical:** add the new item anyway; note the overlap in your confirmation.
   - **No match:** proceed.

3. Pick the most fitting section key. If none fits, create a new one: `spek todo section add <key> "<name>"`.

4. Add the item: `spek todo add --section <key> "<text>"`. Match the level of detail to the user's input. Keep it actionable and imperative. Aim for 1–2 sentences; never fewer than 1, never more than 5. If the item genuinely requires more context than 5 sentences to capture, break it into multiple items rather than writing a wall of text.

5. Confirm in one sentence: what was added and where.
