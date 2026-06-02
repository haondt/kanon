---
kanon:
  description: Explain an AI decision and suggest a kanon fix to prevent recurrence
  output: skill
  name: kanon-why
  skill:
    argument_hint: '[description of the decision in question]'
---
The user is questioning a specific decision you made. Explain it and suggest how to prevent a similar gap in future sessions.

1. Determine what decision is in question:
   - If the user described it in the invocation message, use that. The user may omit the leading word "why" in their invocation message, so it can be read as "/kanon-why did you do X?" -> "kanon, why did you do X?".
   - Otherwise, ask them to describe the decision they want explained.

2. Explain what drove the decision — without reverting or apologizing for it:
   - Was it following an active kanon? Quote the relevant rule and its source file.
   - Was it a default behavior in the absence of a rule? Name the default and why it applies.
   - Was it a gap — something no kanon addressed? Say so clearly.

3. Suggest a concrete fix to prevent recurrence. Pick the most appropriate form:
   - **New kanon module** — if no rule exists for this class of decision; name the file path and draft the rule in one or two sentences.
   - **Edit to an existing kanon** — if a current rule is ambiguous or incomplete; name the file and describe the change.
   - **Nothing needed** — if the behavior was correct and the kanon already covers it; briefly say why.

Keep the explanation to a short paragraph and the suggestion to two or three sentences. Do not implement the fix unless the user asks.
