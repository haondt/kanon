---
spek:
  description: "Skill: review implementation before retro"
  output: command
  name: spek-review
---
You are reviewing a completed implementation before the session is closed. Your job is to find problems — not to narrate what was done.

1. Read `.spek/SESSION.md`

2. Identify what changed this session. Use `git diff HEAD~1` (or against the branch point if on a feature branch) to see the actual diff. Review everything that changed — skip only files that carry no meaningful logic: generated code, lockfiles, vendored dependencies, compiled output, and similar artifacts.

3. Review along three dimensions. Report findings under each:

   **Plan faithfulness**
   Verify the implementation matches what was agreed. Deviations already noted in SESSION.md are known — focus on anything that wasn't captured. Flag steps that were skipped, done differently, or done beyond scope without comment.

   **Spec compliance**
   Read the relevant active modules from `.spek/modules/` — focus on the ones that apply to what changed (e.g. if Python files changed, check python/ modules; if commits were made, check git/ modules). Flag violations. Ignore modules that don't apply to this session's scope.

   **Code problems**
   Review for correctness, edge cases, security issues, dead code, and anything that would surprise a future reader. Keep it signal — don't flag style nits already covered by a spec. Only include a finding if it requires action or a decision. If you investigated something and found no problem, do not mention it — silence means clean.

4. Grep for inline `TODO:` comments in the changed source files:
   - **Stale TODOs** — comments referring to things already addressed this session: flag in findings.
   - **Newly added TODOs** — assess whether each warrants promotion to `.spek/TODO.md`; if yes, flag in findings.

5. Scan for dead code and leftover artifacts: unused functions, commented-out blocks, files that are no longer referenced, debug output, and anything added speculatively that was never used. Flag in findings.

6. Write up the findings concisely. Include an open checkbox for each finding to mark it as an open thread. Use a verdict at the end:
   - **Clear to proceed** — no significant issues; run `/spek-retro`
   - **Issues to address** — list what should be fixed before retro; re-run `/spek-review` after fixes if needed
   - **Your call** — minor issues that don't warrant a fix cycle; note them for the CHANGELOG

7. Append the review findings and verdict to `.spek/SESSION.md` under a `## Review` heading.

8. Do not make changes yourself. This is a review pass only. If the user asks you to fix something, do so — then re-review the affected area.
