---
spek:
  description: "Implement only what was requested"
---

# AI scope discipline

- Implement only what was requested; do not add adjacent improvements, extra options, or "while I'm here" cleanups unless asked
- Do not refactor surrounding code while fixing a bug or adding a feature
- Do not introduce abstractions for hypothetical future requirements — wait until the pattern is clearly established across multiple real cases
- A one-shot script or throwaway tool does not need error handling, logging, or configuration flags
- If the correct solution is simpler than what was asked for, say so — but implement what was asked unless given permission to simplify
- If implementing what was asked requires touching more than was discussed, flag it before proceeding rather than silently expanding or silently stopping
