---
spek:
  description: Add an item to the project backlog in TODO.md
  output: command
  name: spek-todo
---
You are adding an item to the project backlog. Be autonomous: infer what to write, where to put it, and how much detail to include — ask the user only if the intent is genuinely ambiguous.

1. Determine the item to add:
   - If the invocation message contains a description, use it.
   - If not, look at the immediately preceding conversation for an implied backlog item.
   - Only ask if nothing can be inferred.

2. Read `.spek/TODO.md`. Check for an existing item that is substantially the same:
   - **Exact or near-exact duplicate:** skip and tell the user why.
   - **Close but not identical:** add the new item anyway; note the overlap in your confirmation.
   - **No match:** proceed.

3. Pick the most fitting `##` category. If none fits, create a new one.

4. Write the entry. Match the level of detail to the user's input. Keep it actionable and imperative. Aim for 1–2 sentences; never fewer than 1, never more than 5. If the item genuinely requires more context than 5 sentences to capture, break it into multiple items under their own `##` category rather than writing a wall of text.

5. Confirm in one sentence: what was added and where.
