---
spek:
  description: Review the implementation against the plan and spec before closing the session
  output: skill
  name: spek-review
  preapproved_tools:
    - Bash(git diff *)
    - Bash(git log *)
  skill:
    model_invokable: false
    needs_context: false
---
You are reviewing a completed implementation before the session is closed. Your job is to find problems — not to narrate what was done. Number your findings.

1. Run `spek session review start --json` to get the pass key (e.g. `p1`). Note how many passes already exist — this run is Pass N.

2. Identify what changed this session. Use `git diff HEAD~1` (or against the branch point if on a feature branch) to see the actual diff. Review everything that changed — skip only files that carry no meaningful logic: generated code, lockfiles, vendored dependencies, compiled output, and similar artifacts.

3. Review the implementation along three internal dimensions — but output a single unified findings list, not per-dimension sections:

   - **Plan faithfulness** — run `spek session status --full --json` to read the plan; verify the implementation matches what was agreed; focus on deviations not already noted in build notes; flag steps skipped, done differently, or done beyond scope without comment.
   - **Spec compliance** — read the relevant active modules from `.spek/modules/`; focus on modules that apply to what changed; flag violations; ignore modules that don't apply.
   - **Code problems** — correctness, edge cases, security issues, dead code, anything that would surprise a future reader; keep it signal; don't flag style nits already covered by a spec.

4. Grep for inline `TODO:` comments in the changed source files:
   - **Stale TODOs** — referring to things already addressed this session: flag as a finding.
   - **Newly added TODOs** — assess whether each warrants promotion to `todo.yaml`; if yes, flag as a finding.

5. Scan for dead code and leftover artifacts: unused functions, commented-out blocks, files no longer referenced, debug output, speculative code never used. Flag any found.

6. If this is a re-review pass (Pass 2+), run `spek session review status --pass <prev-pass-key> --json` to read prior findings. Explicitly check each. If a finding is still unresolved or the fix was insufficient, carry it forward with the same type and severity as the original — include `(carried from <finding-key>, fix insufficient)` in the description.

7. Categorize each finding. Valid types and severities:

   Types: `bug`, `grammar`, `spec`, `question`, `dead_code`, `plan`, `security`, `test`
   - `test` — only when the project already has a test suite or a testing spec module is active
   - `question` — ambiguous; surface for user judgment

   Severities: `critical`, `major`, `minor`, `nit`

   Every finding must be actionable. If no issues found, skip to step 8.

8. Record findings via CLI:
   - For each finding: `spek session review add-finding <pass-key> <type> <severity> "<location> — description"`
   - If there were findings: output the findings list to the user so they can read it directly.
   - If no issues found: run `spek session review approve <pass-key>` and tell the user the pass was approved with no issues.
