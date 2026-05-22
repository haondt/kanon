---
spek:
  description: Review the implementation against the plan and spec before closing the session
  output: skill
  name: spek-review
  integrations:
    claude:
      disable-model-invocation: true
      context: fork
---
You are reviewing a completed implementation before the session is closed. Your job is to find problems — not to narrate what was done.

1. Read `.spek/SESSION.md`. Note how many `### Review Pass N` blocks already exist under `## Review` — this run appends **Pass N+1** (or Pass 1 if none exist).

2. Identify what changed this session. Use `git diff HEAD~1` (or against the branch point if on a feature branch) to see the actual diff. Review everything that changed — skip only files that carry no meaningful logic: generated code, lockfiles, vendored dependencies, compiled output, and similar artifacts.

3. Review the implementation along three internal dimensions — but output a single unified findings list, not per-dimension sections:

   - **Plan faithfulness** — verify the implementation matches what was agreed; focus on deviations not already noted in SESSION.md; flag steps skipped, done differently, or done beyond scope without comment.
   - **Spec compliance** — read the relevant active modules from `.spek/modules/`; focus on modules that apply to what changed; flag violations; ignore modules that don't apply.
   - **Code problems** — correctness, edge cases, security issues, dead code, anything that would surprise a future reader; keep it signal; don't flag style nits already covered by a spec.

4. Grep for inline `TODO:` comments in the changed source files:
   - **Stale TODOs** — referring to things already addressed this session: flag as a finding.
   - **Newly added TODOs** — assess whether each warrants promotion to `.spek/TODO.md`; if yes, flag as a finding.

5. Scan for dead code and leftover artifacts: unused functions, commented-out blocks, files no longer referenced, debug output, speculative code never used. Flag any found.

6. If this is a re-review pass (Pass 2+), explicitly check each finding from the most recent prior pass. If a finding is still unresolved or the fix was insufficient, carry it forward: `- **[type/severity]** (carried from Pass N #M, fix insufficient) — description`.

7. Produce the findings list. Each finding is one line:

   ```
   - **[type/severity]** `location` — description
   ```

   Types: `bug`, `grammar`, `spec`, `question`, `dead-code`, `plan`, `security`, `test`, `approval`
   - `test` — only when the project already has a test suite or a testing spec module is active
   - `question` — ambiguous; surface for user judgment
   - `approval` — used only for the no-issues case

   Severities: `critical`, `major`, `minor`, `nit`, `N/A` (approval only)

   Rules:
   - Every finding must be actionable.
   - If no issues found: emit exactly one line: `- **[approval/N/A]** No issues found.`
   - Do not include a verdict, checkbox, or summary section — the findings list is the complete output.

8. Append the findings to `.spek/SESSION.md` under a `## Review` heading (create it if absent) as a new sub-section:

   ```markdown
   ### Review Pass N

   - **[type/severity]** `location` — description
   ```
