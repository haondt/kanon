---
spek:
  description: "Freeze the current plan into a named plan file for later execution"
  output: skill
  name: spek-freeze
  integrations:
    claude:
      disable-model-invocation: true
---
Capture the current plan as a named, reusable plan file. Do not write code or edit implementation files.

1. **Determine the source.** Check what is available:
   - Run `spek session status --full --json` to check for an active session.
   - A session is eligible for freezing if it has plan steps, no build notes, and no checked steps.
   - If both a session and rich conversation context exist, confirm with the user which to use.

2. **Choose a name.** If an argument was passed to this skill, use it as the plan name. Otherwise, propose a short kebab-case name derived from the goal and wait for confirmation. For a sub-plan of a split, use `<split>/<name>` addressing.

3. **Session path** (session has eligible plan steps):
   - Run `spek session freeze <name>` — this writes the plan file and deletes the session.

4. **Conversation path** (no eligible session — formalizing from conversation context):
   - Create the plan file: `spek plan create <name> "<goal>"`
   - Populate steps: `spek plan add-step <name> <key> "<text>"` for each step
   - Add any relevant notes: `spek plan note <name> "<text>"`

5. **Confirm.** Report the plan name and path. If there was an active session and it has been cleared, mention that.
