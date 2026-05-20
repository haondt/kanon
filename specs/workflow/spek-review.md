---
spek:
  output: command
---
You are reviewing a completed implementation before the session is closed. Your job is to find problems — not to narrate what was done.

1. Read `.spek/SESSION.md` to understand:
   - The session goal
   - The agreed plan
   - The active stance, if any
   - Any deviations, assumptions, or decisions already noted during implementation

2. Identify what changed this session. Use `git diff HEAD~1` (or against the branch point if on a feature branch) to see the actual diff. If the diff is large, focus on the areas most relevant to the plan.

3. Review along three dimensions. Report findings under each:

   **Plan faithfulness**
   Verify the implementation matches what was agreed. Deviations already noted in SESSION.md are known — focus on anything that wasn't captured. Flag steps that were skipped, done differently, or done beyond scope without comment.

   **Spec compliance**
   Read the relevant active modules from `.spek/modules/` — focus on the ones that apply to what changed (e.g. if Python files changed, check python/ modules; if commits were made, check git/ modules). Flag violations. Ignore modules that don't apply to this session's scope.

   **Code problems**
   Review for correctness, edge cases, security issues, dead code, and anything that would surprise a future reader. Keep it signal — don't flag style nits already covered by a spec.

4. Write up the findings concisely. Use a verdict at the end:
   - **Clear to proceed** — no significant issues; run `/spek-retro`
   - **Issues to address** — list what should be fixed before retro; re-run `/spek-review` after fixes if needed
   - **Your call** — minor issues that don't warrant a fix cycle; note them for the CHANGELOG

5. Do not make changes yourself. This is a review pass only. If the user asks you to fix something, do so — then re-review the affected area.
