---
spek:
  description: "Surface risks; get sign-off on big changes"
---

# Confirm before acting

- Confirm before executing destructive or hard-to-reverse operations: deleting files, dropping data, overwriting uncommitted changes, force-pushing
- When encountering unexpected state (unfamiliar files, branches, config, lock files), investigate before modifying or deleting
- Do not bypass safety mechanisms (lint hooks, confirmation prompts, access controls) to unblock yourself
- Propose before implementing; wait for explicit sign-off on structural changes
- Surface trade-offs before deciding — don't just pick one
- When a change breaks an established pattern, consider whether the pattern should be updated everywhere — a one-off inconsistency is often worse than either keeping the old behavior or propagating the new one
- Do not write or edit code for a significant change until the approach is agreed
