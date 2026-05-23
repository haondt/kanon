# Changelog

## 2026-05-22 (session: spec audit — condense all specs/ to bullets-only)

Audited and condensed 15 spec files across `specs/` to comply with the bullets-only, no-code-block, no-sub-section rule for rule-type specs. The goal was to eliminate teaching aids and structural prose that belonged in reference entries rather than active AI rules.

Changes by group:

- **Minor fixes (3 files):** `ai/coding/prefer-reuse.md` — removed nested sub-bullet; `python/dependencies/uv.md` — removed prose opener; `git/commit-long.md` — fixed mid-sentence trailing period.
- **Code blocks and sub-sections removed (4 files):** `python/build.md`, `python/config.md`, `python/frameworks/fastapi.md`, `python/frameworks/flask.md` — collapsed code examples and headings into behavioral bullets.
- **Multi-section docs specs collapsed (5 files):** `docs/changelog.md`, `docs/readme.md`, `docs/session.md`, `docs/structure.md`, `docs/todo.md` — dropped `## Format`/`## Guidelines`/`## Structure` headings and code blocks; distilled into ~6–8 bullets each.
- **Major rewrites (3 files):** `build/just.md` (~55 lines → ~10 bullets), `build/make.md` (~45 lines → ~8 bullets), `systems/frontend/no-build.md` (~55 lines → ~12 bullets).
- **Frontend informative specs trimmed (3 files):** `frontend/dcdn.md`, `frontend/htmx.md`, `frontend/hyperscript.md` — removed command tables and code pattern examples; kept core guidance as bullets or brief prose.

The review/fix cycle produced two additional changes: a test was added to `tests/test_render.py` verifying that `preapproved_tools` and `integrations.claude.allowed-tools` are merged rather than one clobbering the other; and `specs/build/just.md`'s idempotent-recipe bullet was corrected to describe the actual just idiom (`force="false":` argument with optional `[arg()]`) rather than implying a standard `--force` CLI flag.

Detours: `specs/python/config.md` implementation detail moved to a new `references/python/config.md`; `specs/python/venv.md` wording tightened; `specs/systems/frontend/no-build.md` trimmed from 9 to 6 bullets by removing coverage already in component specs; `spek sync` run mid-session.

## 2026-05-22 (session: spek-reconcile skill + render/utils fixes)

Added `specs/workflow/spek-reconcile.md` — a new skill for catching up SESSION.md after the human does implementation work directly (manual coding, raw prompts, or detours). The skill reads `SESSION.md` and `git diff HEAD`, infers which plan steps are complete, marks them done, adds a brief observation note, and prompts the user to run `/spek-review`. Registered in `.spek/spek.yaml`; synced to `.claude/skills/spek-reconcile/SKILL.md`.

As a side effect of the review/fix cycle, several bugs and style issues in `src/spek/core/` were addressed. A new `src/spek/core/utils.py` was extracted with a `deep_merge` helper (three conflict modes: `new`/`old`/`err`; recursive dict merge; list deduplication safe for unhashable types). `render.py` was fixed so that `allowed-tools` from `integrations.claude` is merged into the existing `preapproved_tools`-populated list rather than silently overwriting it; three PEP 8 blank-line violations were also corrected. `tests/test_utils.py` was added with 9 direct unit tests for `deep_merge` covering all conflict modes, type-mismatch behavior, list deduplication, and nested dict recursion. `tests/test_render.py` gained an assertion for `includeGitInstructions` in the permissions-only settings path. Test suite: 89 tests passing.

## 2026-05-22 (session: render.py skill enhancements and workflow spec refinements)

Extended `render.py` and workflow specs to give fork-context skills richer tool access and context.

`render.py` gains `collect_preapproved_tools(content)` to extract `preapproved_tools` from rule module frontmatter. `render_module` now merges `preapproved_tools` into `allowed-tools` in Claude skill frontmatter; when `context: fork`, it also appends STRUCTURE.md preload commands to `allowed-tools` and injects a `## Project structure` shell-expansion block at the end of the skill body (so fork subagents receive codebase context automatically). `render_settings` gained an optional `preapproved_tools` parameter that writes a `permissions.allow` block into `.claude/settings.json`. `sync.py` accumulates `preapproved_tools` across all rendered modules and passes them to `render_settings`.

`spek-build`, `spek-review`, `spek-retro`, `spek-fix`, and `spek-detour` workflow specs were updated with explicit `allowed-tools` in frontmatter and `context: fork` where applicable. `spek-review` was revised so the approval finding is omitted when other findings are present. `spek-fix` was revised to propose and get explicit user approval for each fix before implementing. `spek-todo` and `spek-onboard` gained minor refinements.

`specs/tools/spek/ref.md` and `specs/tools/spek/module.md` were condensed from sub-section prose to flat bullet lists (both now under 8 lines). `references/spek/specs.md` was updated to document the 1–1024 character `description` limit and keyword/trigger guidance for skill descriptions.

The session's original goal (converting `tools/spek/ref.md` and `module.md` to `output: skill`) was attempted and then reversed — the `output: rule` form is the current behavior; the conversion remains a backlog item.

## 2026-05-22 (session: review/fix redesign)

Redesigned the `spek-review` / `spek-fix` cycle from a mutable-verdict model to a structured, pass-based audit trail.

`specs/workflow/spek-review.md` completely rewritten: each invocation appends a `### Review Pass N` block to `## Review` in SESSION.md rather than overwriting it. Output is a flat, typed findings list (`- **[type/severity]** location — description`) with no verdict, no checkboxes, and no per-dimension sections. Types: `bug`, `grammar`, `spec`, `question`, `dead-code`, `plan`, `security`, `test`, `approval`. Re-review passes explicitly carry forward unresolved findings.

`specs/workflow/spek-fix.md` completely rewritten: reads the most recent `### Review Pass N`, appends `### Fix Pass N`, fixes every finding unconditionally. No-op if the only finding is the approval sentinel. Ends by prompting the user to re-run `/spek-review`.

`specs/docs/session.md` `## Review` description updated to describe the multi-pass append model.

`specs/workflow/spek-build.md` step-completion instruction made explicitly additive: suffix ` — done` or add a `Completed.` sub-bullet; never overwrite or erase original step text.

`specs/workflow/spek-retro.md` gained a step 9: prompt the user to clear conversation context (e.g. `/clear` in Claude Code).

`specs/workflow/spek-plan.md` and `specs/workflow/spek-detour.md` each gained an explicit reference-library search step (`spek ref search`) before proposing a plan or making a change.

All completed Workflow items removed from `.spek/TODO.md`. Detour: added sync-timing note to `.spek/STRUCTURE.md` clarifying that `.spek/modules/` may intentionally lag `specs/` during a session.

## 2026-05-22 (session: terminology cleanup)

Replaced remaining "slash command" / "command" references with "skill" across documentation and specs, following the `output: command` → `output: skill` rename completed in the previous session. Changed files: `references/spek/specs.md` (4 wording changes), `.spek/STRUCTURE.md` (workflow directory annotation), `specs/workflow/base.md` ("driven by slash commands" → "driven by skills"), and `README.md` (section heading + one sentence).

Review-triggered fixes: `specs/workflow/spek-plan.md` step 1 changed "this command" → "this skill"; `specs/workflow/spek-think.md` "any other spek command" → "any other spek skill". Both propagated via `just sync`.

## 2026-05-22 (session: output-type rename)

Renamed the `output: command` output type to `output: skill` throughout the codebase. "skills" is the unified term in modern AI tool platforms (e.g. agentskills.io), and all 12 workflow spec files already used skill-style output; the old `command` key was an artifact of an earlier naming pass.

Changed: `AI_TOOL_OUTPUT_DIRS["claude"]["command"]` key in `render.py` (2 dict sites + 1 branch condition); all 12 `specs/workflow/*.md` frontmatter blocks; 4 fixture strings and 1 test name in `tests/test_sync_cli.py`; the description and section heading in `references/spek/specs.md`; one TODO.md backlog item and two lines in `.spek/STRUCTURE.md`. `spek sync` was re-run to regenerate `.spek/modules/workflow/`.

Detours: updated `specs/workflow/spek-plan.md` to forbid post-approval changes, rewrote the body for directness (bold step verbs, explicit approval definition, hard stop in step 6); fixed a pre-existing test gap in `test_render_settings_writes_json` to include `includeGitInstructions: false` in expected output.

## 2026-05-22 (detours)

`README.md` quick start updated to `uv tool install haondt-spek` and the `just` prerequisite removed — the tool is now distributed via PyPI so cloning the repo is no longer the install path.

`specs/git/commit-long.md` reworded: the two bullets now read "Add more detail to commits with a body" and "Separate from subject with a blank line" (previously the second bullet was "Body explains *why*, not *what*", which was moved to the `commit-long` body convention). `.spek/modules/git/commit-long.md` regenerated to match.

`references/spek/specs.md` expanded the descriptions and commands sections: `description` guidance now explicitly says to write trigger conditions rather than labels; the rules section tightens the "unambiguous" and "omit rationale" guidance; the commands section notes that commands are loaded on demand (not injected) and calls out the need to be explicit about files, checks, and output.

`specs/workflow/spek-retro.md` description clarified: "clear SESSION.md" → "delete SESSION.md"; step 7 simplified to "Delete `.spek/SESSION.md`".

`.spek/TODO.md` gained a new "Tools modules" category: convert `specs/tools/` modules from `output: rule` to `output: skill` so CLI reference docs are pulled on demand rather than injected into every context.

## 2026-05-21 (session: hooks/settings generation)

`spek sync` now generates `.claude/settings.json` when any active module declares `hooks` in its frontmatter. This allows spec modules to inject Claude Code hook entries automatically — the first use case being auto-loading `.spek/STRUCTURE.md` into context at session start, so AI assistants no longer have to be instructed to read it manually.

`render.py` gained `collect_hooks(content, ai_tool)` (parses `integrations.{ai_tool}.hooks` from frontmatter) and `render_settings(hooks_by_event, project_root, ai_tool)` (writes `.claude/settings.json` from accumulated hook entries; raises `ValueError` on missing/empty `command`). `AI_TOOL_SETTINGS_FILES` constant maps integrations to their settings file path. `render_module` now excludes the `hooks` key when building SKILL.md frontmatter so hook declarations don't bleed into Claude's skill metadata.

`sync.py` accumulates hooks across all rendered modules into a combined `hooks_by_event` dict and calls `render_settings` after the render loop. Stale settings files are deleted at the start of Phase 5 (before output dirs are wiped).

`destroy.py` now also removes settings files listed in `AI_TOOL_SETTINGS_FILES` for each active integration, using `unlink()` rather than `rmtree()`.

`specs/workflow/base.md` was updated to declare two `SessionStart` hook entries: one for `startup` (new session) and one for `clear` (after `/clear`). Each runs `bash -c 'test -f .spek/STRUCTURE.md && cat .spek/STRUCTURE.md'` so it silently no-ops on projects without STRUCTURE.md. The manual instruction to read STRUCTURE.md at session start was removed from the rule body since the hook now handles it automatically.

9 unit tests added to `tests/test_render.py` covering `collect_hooks` and `render_settings`; 4 integration tests added to `test_sync_cli.py`; 1 test added to `test_destroy_cli.py`. Suite: 81 tests, all passing.

## 2026-05-21 (skills migration)

Migrated Claude command output from `.claude/commands/` (flat `.md` files) to `.claude/skills/<name>/SKILL.md` with generated YAML frontmatter. This matches the Claude Code skill format and allows per-command metadata (`description`, `argument-hint`, `disable-model-invocation`, `context`) to be declared in spec frontmatter and rendered automatically.

`_SpekMeta` in `render.py` gained two fields: `args` (maps to `argument-hint` in Claude output) and `integrations` (a dict of tool-specific kwargs passed verbatim into the generated frontmatter). The `AI_TOOL_OUTPUT_DIRS["claude"]["command"]` path changed from `.claude/commands` to `.claude/skills`; sync now unconditionally clears all dirs in `AI_TOOL_OUTPUT_DIRS[integration].values()` before rendering. Dead function `output_type()` was removed. Frontmatter separator was fixed to emit `\n---\n` (with blank line before closing delimiter) so the separator is never elided by body content that doesn't start with a newline.

All 12 workflow spec files were updated with user-facing descriptions, `args` entries for specs that take arguments (e.g. spek-stance), and `integrations.claude` blocks carrying `disable-model-invocation` and `context` as appropriate. `tests/test_sync_cli.py` and `tests/test_destroy_cli.py` were updated to cover skill output and frontmatter; 67/67 tests pass. `.claude/skills/` was regenerated via `just sync`; the now-stale `.claude/commands/` directory was removed.

Detours: converted the project-local `writing-specs` and `writing-references` modules to reference entries under `references/spek/specs.md` and `references/spek/references.md` (more portable, searchable via `spek ref`); updated `references/spek/specs.md` to document the `args` and `integrations` frontmatter fields added this session; added `.spek/local/modules/spec-authoring.md` capturing a guardrail-vs-convention authoring principle.

## 2026-05-21

Added `references/htmx/infinite-scroll.md` — reference entry for the htmx infinite scroll pattern: a sentinel div with `hx-trigger="intersect once"` that replaces itself with the next page via `hx-select` + `hx-swap="outerHTML"`, chaining indefinitely until no next page remains. Includes a Jinja2 template partial and a Flask pagination endpoint sketch.

Fixed `specs/workflow/spek-plan.md` step 7 to explicitly prohibit auto-invoking `/spek-build` after plan approval — the prior wording ("encourage the user to continue") was ambiguous enough to allow it.

Fixed `references/bulma/navbar-simple.md` to replace hardcoded app-specific values (`spek`, `/commands`, `/cli`) with generic placeholders.

## 2026-05-21 (detours)

`specs/frontend/hyperscript.md`: added a Behaviors section documenting when to extract hyperscript to a standalone `._hs` file using the `behavior` feature, and how to serve and install it.

Added `references/htmx/live-input.md` — reference entry for the htmx auto-save input pattern: an input that posts via htmx and shows inline success/failure feedback driven by hyperscript custom `show`/`hide` events, with no page navigation.

Added `.spek/local/modules/references-style.md` — a local spec for this repo covering how to write reference entries: what belongs (portable mechanism, generic names), what to strip (project-specific details), structure (description → core content → explanation → variants), length cap (~200 lines), frontmatter, and file naming.

`local_modules` in `spek.yaml` now uses short names identical in format to regular modules (e.g. `my-rules` instead of `.spek/local/modules/my-rules.md`). `sync.py` resolves via `_find` against `LOCAL_MODULES_DIR`; `local.py` registers the short name and uses an f-string instead of `with_suffix` to avoid misbehavior on names containing dots. Added `test_local_module_creates_file_in_subdirectory` to cover the subdirectory case.

## 2026-05-21 (detour)

Added `tests/test_module_cli.py` — 10 tests covering the new `spek module` subcommands: `list --json` (valid JSON, entry shape, active/inactive flag accuracy, default text output), `set` (saves modules, full replacement, rejects unknown names, no-config error, preserves stances and meta), and bare `module` group displaying all subcommands.

## 2026-05-21 (session 33, post-review)

Informal review of the session 33 onboarding implementation. Found two out-of-scope edits to workflow specs: `spek-build.md` had a grammatically broken bullet (fixed: "To not" → "Do not", "plans" → "plan's"); `spek-plan.md` had step 5 reworded and a new step 7 added ("Encourage the user to continue with `/spek-build`") — both accepted as intentional. Minor finding noted but not actioned: the Docker example in `spek-onboard.md` step 4 refers to a module category that doesn't exist yet.

## 2026-05-21 (session 33)

Implemented the brownfield onboarding flow.

`spek module` was refactored: bare `spek module` now shows group help instead of launching the picker; the picker moved to `spek module edit`; `spek module list` gained a `--json` flag that outputs `[{name, description, active}]` for AI consumption; a new `spek module set [--sync] <module>...` subcommand does a non-interactive full replacement of the module list with name validation.

`specs/tools/ref-search.md` was deleted and replaced by two files with a clearer separation: `specs/tools/spek/ref.md` and `specs/tools/spek/module.md` are purely informational (command syntax and output shape only); the behavioral guidance ("search before implementing from scratch") moved to `specs/systems/base.md`. This keeps tool specs machine-readable references and concentrates behavioral rules in the systems layer where they belong.

Added `specs/workflow/spek-onboard.md` — the `/spek-onboard` skill. It crawls the project to understand the tech stack, writes `.spek/STRUCTURE.md`, enumerates modules with `spek module list --json`, proposes a selection for user approval, applies it with `spek module set --sync`, and greps source files for inline `TODO:` comments to populate `.spek/TODO.md`.

Profiles updated: `base/tools.yaml` now includes `tools/spek/ref` and `tools/spek/module`; `base/base.yaml` includes `systems/base`; `base/workflow.yaml` includes `workflow/spek-onboard`. README updated with `spek module edit`/`set` in the usage table, `/spek-onboard` in the slash commands table, and a new "Onboarding an existing project" section.

## 2026-05-21 (session 32)

Fixed workflow alignment gaps surfaced by a cross-spec analysis. Added `/spek-fix` as an optional step in the `workflow/base` table (it was registered and documented in the README but absent from the canonical always-active rule). Updated `docs/session` to document the `## Review`, `## Amendments`, and `## Detours` sections that skills write to SESSION.md but that were missing from the spec. Fixed `spek-build`'s closing prompt to mention `/spek-review` as an optional step before retro.

## 2026-05-21 (session 31)

Added `/spek-todo` — a utility skill that writes an actionable backlog entry to `.spek/TODO.md`. It infers the item from the invocation message or conversation context, checks for duplicates (exact → skip; near-match → add with note), picks or creates a category, and writes 1–2 sentences of detail (capped at 5). Registered in `profiles/base/workflow.yaml`, `.spek/spek.yaml`, README, and STRUCTURE.md.

Also restructured the review/retro workflow: inline `TODO:` scanning and dead-code artifact scanning moved from `/spek-retro` step 7 into `/spek-review` as explicit steps (grep for stale and newly added TODOs; scan for dead code). Retro step 7 now only covers removal of clearly dead artifacts. `/spek-review` findings now include checkboxes to track open threads.

Detour: rewrote `/spek-fix` for clarity and to make the flow collaborative — it now consults the user on each finding, agrees on an approach before writing code, and batch-implements at the end. Fixed structural bugs in the user's draft (duplicate step number, missing sub-item label, typo).

Post-retro: clarified `/spek-review` step 5 (dead code scan) to explicitly say "flag in findings" rather than leaving the disposition implicit.

## 2026-05-21 (session 30)

Renamed `/spek-implement` to `/spek-build` throughout. The new name fits the established verb register (sketch → plan → build → review → retro) and is shorter. Changed: `specs/workflow/spek-implement.md` → `spek-build.md` (frontmatter updated), `specs/workflow/base.md`, `profiles/base/workflow.yaml`, `.spek/spek.yaml`, `README.md`, `.spek/STRUCTURE.md`, and the AI stances follow-on item in `.spek/TODO.md`. Ran `spek sync --pull` to regenerate `.spek/modules/workflow/` and `.claude/commands/` with the new name.

## 2026-05-21 (session 29)

Added `/spek-fix` — a new workflow skill that follows `/spek-review`. For each finding in the `## Review` section of SESSION.md, it evaluates whether the finding is a genuine problem, implements a fix or records a dismissal with reasoning, and appends a reply under the finding to close the thread. No next-step prompts; the user decides whether to re-review or proceed to retro. Registered in `profiles/base/workflow.yaml` and `.spek/spek.yaml`; added to README and STRUCTURE.md. Also added a TODO item to rename `/spek-implement` to `/spek-build`.

## 2026-05-21 (session 28)

Updated `specs/docs/todo.md`: completed items should be deleted from `TODO.md` entirely rather than struck through, with the CHANGELOG as the paper trail. Removed all accumulated struck-through items from `.spek/TODO.md` to apply the new convention immediately.

## 2026-05-21 (session 27)

Renamed `/spek-start` to `/spek-sketch` and made it optional. The skill is now framed as a fuzzy-goal clarification step for when an idea isn't concrete enough to plan against — when the goal is already clear, users skip directly to `/spek-plan`. `/spek-plan` was updated to infer the goal from conversation context when SESSION.md is missing, only asking the user directly if the goal remains unclear. Updated `specs/workflow/base.md` (workflow table, dropped "4-step" language), `profiles/base/workflow.yaml`, `.spek/spek.yaml`, README, STRUCTURE.md, and tests; `just sync` regenerated all derived files.

## 2026-05-21 (session 26)

Post-session cleanup: deleted `list_references` from `core/references.py` (became unreachable after session 25 refactored `search_references` to use `_score_dir` directly). Added 7 tests to `tests/test_ref_cli.py` covering local reference search, merge with upstream, local-shadows-upstream for both `search` and `read`, upstream fallback when name not in local, and graceful degradation when no local project is found.

## 2026-05-21 (session 25)

Added local reference support to `spek ref search` and `spek ref read`. References in `.spek/local/references/` of the target project are now searched alongside upstream refs, with local taking precedence on name collision. Project root is auto-discovered by walking up from CWD looking for `.spek/spek.yaml` — no flag required. New `local_project_path()` in `core/repo.py`; `search_references`, `read_reference`, and `list_references` in `core/references.py` all accept an optional `project_root` parameter.

## 2026-05-21 (session 24)

Added `references/bulma/list-page.md` — reference entry for the Bulma list page pattern: a `field is-grouped` toolbar with an expanding live-search input (htmx form + hyperscript debounce) and action buttons on the right, above a list content area (table, grid, etc.). Distilled from two real Razor/htmx app examples.

## 2026-05-21 (session 23)

Rewrote `references/bulma/navbar-simple.md` with a real-world Bulma navbar template using htmx (`hx-boost`) and hyperscript (burger toggle via `next .navbar-menu`). The entry now includes prose notes distinguishing demo placeholders (app name, hrefs, link labels, `id="navbar"`) from essential parts (burger hyperscript, four `<span>`s, `hx-boost`), and an Extension note on `hx-target`/`hx-select` for partial swaps. Also added `specs/code/templates.md` with a generalized convention for preferring template loops and reusable fragments over hardcoded repetition in any template engine.

## 2026-05-21 (session 22)

Enhanced `spek ref search` to accept multiple positional terms. Default mode requires all terms to match (AND); `--match-any` switches to OR. Results are ranked by match count (descending) and capped at 10 by default; `-n N` overrides the limit and `-n 0` removes it. Matching is substring-based so a single-word term matches multi-word keywords. The `search_references` core function was updated to take `terms: list[str]` and `match_all: bool`; truncation was kept in the command layer. Updated `specs/tools/ref-search.md` to reflect the new multi-term syntax.

## 2026-05-21 (session 21)

Added `spek ref` command group with `search` and `read` subcommands backed by a new `references/` top-level directory. Reference entries are markdown files with `spek.description`/`spek.keywords` frontmatter — docs, examples, patterns, or any reusable material. `spek ref search --json <query>` does case-insensitive keyword substring matching; `spek ref read --json <name>` returns stripped content. Added a `specs/tools/ref-search.md` module that instructs the AI to search the reference library before implementing anything from scratch, and wired it into `profiles/base/tools.yaml` (a new profile extending `base/base`). Sample entry: `references/frontend/bulma/navbar-simple.md`. The concept started as "templates" but was renamed to "ref/references" — the entries are general-purpose reference material, not fill-in-the-blank scaffolding. `FRONTMATTER_RE` was consolidated into `yaml_utils.py` (previously duplicated across `render.py` and `references.py`); JSON serialization uses Pydantic's `exclude_none` so absent fields are omitted rather than emitted as `null`.

## 2026-05-21 (session 19)

Added `specs/frontend/` with six new modules: `hyperscript`, `hyperscript-strict`, `htmx`, `htmx-strict`, `bulma`, `bulma-strict`. The informative modules (`hyperscript`, `htmx`, `bulma`) cover syntax, common patterns, and guidelines. The `-strict` variants are thin behavioral overlays — policy rules only, no reference content — so projects that want enforcement include both, and projects that only want reference include just the informative one. All six were added to `profiles/python/webservice.yaml`. Also added a clarifying section to `STRUCTURE.md` explaining the `specs/` vs `.spek/modules/` distinction, since this repo dogfoods spek and the two directories can be easily confused.

## 2026-05-21 (session 20)

Added `specs/frontend/dcdn.md` — reference module for the dcdn vendor asset tool (Bun-backed, pulls individual files from npm packages). Introduced `specs/systems/` as a new top-level directory for architectural context modules: prose docs that explain how a set of tools works together as a system, as opposed to per-tool rules. First entry: `specs/systems/frontend/no-build.md`, covering the no-build-step web stack (htmx + _hyperscript + Bulma + dcdn) — its constraints, division of responsibilities, and consolidated enforcement rules. The per-tool `-strict` variants (`bulma-strict`, `htmx-strict`, `hyperscript-strict`, `dcdn-strict`) were removed; their enforcement content now lives in the system spec. `profiles/python/webservice.yaml` updated accordingly: strict modules replaced with `frontend/dcdn` and `systems/frontend/no-build`. Added a backlog item for external spec sources (multi-repo module references).

## 2026-05-21 (session 18)

Renamed `/spek-define` to `/spek-start` across the entire codebase. The old name was a weak fit — "define" is abstract and doesn't signal that this command starts a session. Updated: spec file (`specs/workflow/spek-start.md`), workflow table in `specs/workflow/base.md`, fallback message in `specs/workflow/spek-plan.md`, `profiles/base/workflow.yaml`, `.spek/spek.yaml`, README, STRUCTURE.md, and tests. `spek sync --pull` regenerated all module copies and AI output; old `spek-define.md` files were pruned automatically. Also added a `just sync` recipe to the justfile (`{{venv}}/bin/spek sync --pull`).

## 2026-05-20 (session 17)

Rewrote `README.md` to position spek for a first-time reader coming from Cursor/Windsurf rules. The one-liner now leads with the distribution model ("package manager for AI coding conventions"). A new positioning paragraph before Quick start names the per-project rules problem and states spek's approach. The Overview section was rewritten to make the library → subscription → sync → multi-tool output flow explicit. The workflow slash commands were moved out of a collapsible into a top-level section with framing that explains the structured-session-lifecycle goal. Lexicon entries for `stance` and `profile` were expanded with motivation, not just definitions.

## 2026-05-20 (session 16)

- `specs/build/just.md` — added "Using the justfile" section: when a justfile is present, prefer `just <recipe>` over the raw underlying command for any task a recipe covers

## 2026-05-20 (session 15)

- `specs/workflow/spek-amend.md` — new `/spek-amend` skill: updates SESSION.md in place mid-session (goal, plan, or both); infers intent from invocation args → conversation context → interactive prompt; logs change under `## Amendments`
- `profiles/base/workflow.yaml` and `.spek/spek.yaml` — registered `workflow/spek-amend`
- Detour: `specs/workflow/base.md` — added rule: never advance to the next workflow step automatically; each step requires explicit user invocation

## 2026-05-20 (session 14)

- `src/spek/commands/module.py` — new `spek module` command group: picker (questionary checkbox, pre-checked from `spek.yaml`, type-to-filter) and `spek module list` (all available modules with descriptions and selection markers); `--sync` flag runs sync after saving
- `src/spek/core/modules.py` — new: `list_modules(repo_path)` extracted from `scaffold.py`; shared by `init` and `module`
- `src/spek/core/render.py` — added `description: str | None = None` to `_SpekMeta` (nested under `spek:` in frontmatter, alongside `output` and `name`)
- `specs/**/*.md` — added `spek.description` frontmatter to all 52 spec files (short descriptions, ≤8 words, double-quoted to avoid YAML colon ambiguity)
- Post-plan fix: description initially placed at top-level `ModuleFrontmatter`; moved inside `spek:` block for consistency with `output`/`name`
- Post-plan fix: unquoted descriptions containing `: ` caused YAML parse errors; all values now double-quoted

## 2026-05-20 (session 13)

- `src/spek/commands/scaffold.py` — replaced all three `spek init` text prompts with `questionary` pickers: integrations (checkbox), profile (select with "none" option), modules (checkbox with search filter, pre-checked from resolved profile)
- `pyproject.toml` / `uv.lock` — added `questionary>=2.1.1` as runtime dependency
- All three pickers use `use_jk_keys=False` for consistency; required on the modules picker anyway since `use_search_filter=True` and j/k conflict
- Post-review fix: `use_jk_keys=False` added to integrations and profile pickers to match the modules picker
- Detour: added rule to `specs/ai/style/confirm-before-acting.md` — when a change breaks an established pattern, consider whether to propagate it rather than leave a one-off inconsistency

## 2026-05-20 (session 12)

- `src/spek/commands/destroy.py` — new `spek destroy` command; removes `.spek/` and all configured integration output dirs; prompts for confirmation (default no); `--yes`/`-y` skips prompt
- `src/spek/cli.py` — registered `destroy` command
- `tests/test_destroy_cli.py` — 6 tests covering removal, preservation of hand-written files, no-config exit, confirmation prompt, and abort on "no"
- Note: planned "Nothing to remove" branch was unreachable (`.spek/` always exists when `spek.yaml` does); removed the dead branch and dropped the corresponding test

## 2026-05-20 (session 11)

- `specs/workflow/spek-retro.md` — step 1 now handles missing SESSION.md by falling back to `git diff HEAD` to derive what was done

## 2026-05-20 (session 10)

- Rewrote `README.md` to follow the `docs/readme` spec: combined quick start, overview with lexicon, collapsible spek.yaml and AI commands sections, dependencies section, lean development section
- `justfile` — replaced runtime-only `install` (uv sync) with `uv tool install --editable .`; `install-dev` and `test` unchanged

## 2026-05-20 (session 9)

- Added `specs/workflow/spek-detour.md` — new `/spek-detour` command; makes a quick out-of-scope edit immediately, logs a one-liner to `## Detours` in SESSION.md if a session is active, skips logging otherwise
- `profiles/base/workflow.yaml` — added `workflow/spek-detour`

## 2026-05-20 (session 8)

- Added `specs/workflow/spek-think.md` — new `/spek-think` command; enters a non-actionary brainstorming mode for the remainder of the conversation; exits on any other spek command or natural conversation ender
- `profiles/base/workflow.yaml` — added `workflow/spek-think`
- `specs/workflow/spek-plan.md` — added instruction to write the full plan detail into SESSION.md at approval time, not just a summary table
- Aside: `specs/workflow/spek-review.md` updated to record review findings in SESSION.md (carried over from prior session, committed with session 7)

## 2026-05-20 (session 7)

- `specs/workflow/spek-review.md` — added rule to **Code problems** section: only report findings that require action; silence means clean. Prevents noise from investigated-and-acceptable items appearing in review output.

## 2026-05-20 (session 6)

- `render.py` — added optional `name` field to `_SpekMeta`; when set, used as the output filename stem instead of the path-derived `dir--name` form
- All six workflow command specs (`spek-define`, `spek-plan`, `spek-implement`, `spek-review`, `spek-retro`, `spek-stance`) now set `name: spek-*` in frontmatter — they appear as `/spek-define` etc. in Claude Code instead of `/workflow--spek-define`
- Added `test_sync_command_name_override` to `tests/test_sync_cli.py`
- Minor: `render_module` now uses `meta.spek.output` directly instead of calling `output_type()` (which re-parsed frontmatter); no behavior change
- Moved venv from `.venv/` to `venv/` to match `python/venv` rule; updated `.gitignore`
- Rewrote `justfile` to use `UV_PROJECT_ENVIRONMENT=venv` in `install`/`install-dev`, add idempotent `venv` recipe, route `test`/`test-cov` through `venv/bin/pytest`
- `specs/workflow/spek-review.md` — added step 5: append review findings and verdict to `.spek/SESSION.md` under a `## Review` heading

## 2026-05-20 (session 5)

- Added `/spek-review` workflow skill — optional step between implement and retro; reviews plan faithfulness, spec compliance, and code problems; ends with a three-way verdict; read-only by default
- `git/commit-base` — added rule: never create a commit unless explicitly asked
- `spek-review` scope clarified: review everything changed, skip only files with no meaningful logic (generated code, lockfiles, vendored deps)
- `spek init` now writes `.spek/.gitignore` containing `SESSION.md`, so SESSION.md is gitignored at the project level rather than relying on the root `.gitignore`

## 2026-05-20 (session 4)

Major expansion of the spec module library. All changes are to `specs/`, `stances/`, and `profiles/` — no CLI changes.

**AI specs reorganized**
- Split `specs/ai/` into four subdirectories: `style/`, `communication/`, `analysis/`, `coding/`
- Removed `architect` stance; merged `reviewer` + `skeptic` into `critic`
- Stances list collapsed to three: `autonomous`, `collaborative`, `critic` — moved from `base/ai` profile to `base/base`
- Several modules merged to reduce overlap: `propose-before-implement` + `confirm-before-acting`, `prefer-reuse` + `seek-prior-art`, `prefer-momentum` + `assume-and-proceed`
- Deleted: `systems-thinking`, `propose-before-implement`, `prefer-momentum`, `seek-prior-art`

**Git specs broken up**
- Replaced single `git/commit-style` with: `commit-base` (subject line rules), `commit-long` (body conventions), `commit-short` (no-body short commits), `branch-base` (never touch branches without instruction), `branch-trunk` (all work to main), `branch-feature` (verify on feature branch, short names)

**Python specs expanded**
- Added `python/venv.md` — always use `./venv`, all invocations via `./venv/bin/`
- Added `python/models/` — `dataclasses`, `pydantic`, `dicts`, `sqlmodel`
- Added `python/frameworks/` — `fastapi`, `flask` (each with sample app layout)
- Simplified `python/style.md` (removed prescriptive model/config guidance now covered by dedicated specs)
- Updated `python/config.md` — Config class pattern with module-level singleton
- Updated `python/dependencies/uv.md` — `uv venv venv` for venv creation, `uv sync`

**New general-purpose specs**
- `specs/config/base.md` — env vars, fail fast, `.env.example`, namespaced prefixes
- `specs/code/hygiene.md` — no commented-out code, no debug artifacts
- `specs/persistence/sqlite.md`, `postgres.md`, `redis.md` — per-medium conventions (parameterized queries, WAL mode, TTLs, etc.)

**Docs specs added**
- `specs/docs/session.md` — SESSION.md structure and conventions
- `specs/docs/changelog.md` — CHANGELOG.md format and writing guidelines
- `specs/docs/todo.md` — TODO.md structure, what belongs, inline TODO promotion (moved from `specs/workflow/todos.md`)

**Workflow specs simplified**
- `spek-define`, `spek-plan`, `spek-retro` — stripped inline format guidance for SESSION.md, CHANGELOG.md, TODO.md, STRUCTURE.md now that each has its own spec
- `spek-implement` — SESSION.md is now a living record: mark steps done, log assumptions/decisions/deviations as they happen; ends with a 2-3 sentence session summary and prompt to run `/spek-retro`
- `workflow/base.md` — removed trailing format notes now covered by doc specs

**Profiles updated**
- Added `python/base` — new intermediate profile (style, venv, dependencies, testing); `python/cli` and `python/webservice` now extend it
- `base/git` — updated to use new split git specs (`commit-base`, `commit-long`, `branch-base`)
- `base/base` — stances now included here instead of `base/ai`

## 2026-05-20 (session 3)

**Tests**
- Added `tests/` directory with 27 unit and CLI integration tests across 5 files:
  - `test_yaml_utils.py` — `load_yaml` with model type, `save_yaml` with `BaseModel`, roundtrip
  - `test_config.py` — `SpekConfig` load/save roundtrip; verifies empty lists and `None` are omitted from YAML
  - `test_profiles.py` — `resolve_profile` inheritance ordering, deduplication, circular dependency detection, missing profile error
  - `test_sync_cli.py` — rule output, frontmatter stripping, command routing, missing config error, stance-only modules not rendered
  - `test_local_cli.py` — `local module` and `local stance` create files and register in config; duplicate and missing-config error paths
  - `test_profile_cli.py` — `profile apply` with explicit name and recorded profile; error paths; `profile list` against real profiles
- Fixed `save_yaml` to use `exclude_defaults=True` instead of `exclude_none=True` — empty lists (`stances: []`, `local_modules: []`) were previously written to `spek.yaml` when they should be omitted (caught by test)
- Updated `justfile` to use `uv run pytest` instead of bare `pytest`

## 2026-05-20 (session 2)

**CLI refactoring**
- Renamed `spek scaffold` → `spek init`; renamed internal `lock_path`/`lock` variables to `config_path`/`config`
- Renamed `--upstream` → `--pull` on `spek sync`; removed `--record-sha` (SHA is now always recorded when `--pull` is used)
- Added `src/spek/core/yaml_utils.py` — centralizes all YAML I/O: `parse_yaml(str)`, `load_yaml(path[, model])`, `dump_yaml(data)`, `save_yaml(data, path)`
  - `load_yaml` accepts an optional Pydantic model type and calls `model_validate` automatically
  - `save_yaml`/`dump_yaml` accept either `dict[str, Any]` or a `BaseModel` (calls `model_dump(exclude_none=True)` automatically)
- Migrated all raw `yaml.safe_load` / `yaml.dump` calls across `config.py`, `profiles.py`, `render.py`, `sync.py` to use `yaml_utils`
- Added `ProfileSpec(BaseModel)` in `profiles.py` — replaces raw dict access for profile YAML files
- Added `ModuleFrontmatter` / `_SpekMeta` Pydantic models in `render.py` — replaces chained `.get()` calls for frontmatter parsing; `output_type()` now reads `meta.spek.output`
- `SpekConfig.save()` now passes `self` directly to `save_yaml`; `SpekConfig.load()` uses `load_yaml(path, cls)`

## 2026-05-20

Initial implementation of spek.

**CLI commands**
- `spek init` — interactive Q&A to write `.spek/spek.yaml` (integrations, profile, modules, stances)
- `spek sync` — reconcile `.spek/modules/` and `.spek/stances/` from upstream, generate AI tool output; `--pull` force-refreshes all files and records SHA
- `spek profile list` / `spek profile apply [name]` — list profiles, re-resolve and apply a profile; `--sync` flag runs sync immediately after
- `spek local module <name>` — create a project-local spec module and register it in `spek.yaml`; `--sync` flag
- `spek local stance <name>` — create a project-local stance YAML and register it in `spek.yaml`

**Spec module library** (`specs/`)
- `ai/` — 14 spec files covering always-active AI conventions (brevity, scope, reuse, caution, verification) and stance-activatable behavioral modules (assume-and-proceed, prefer-momentum, propose-before-implement, explain-reasoning, seek-prior-art, find-problems, challenge-premise, surface-risks, systems-thinking)
- `docs/` — readme and structure doc conventions
- `git/` — commit style
- `python/` — style, dependencies (base + uv), testing (base + pytest), async, config stubs
- `workflow/` — base workflow table, todos conventions, and five skills: `/spek-define`, `/spek-plan`, `/spek-implement`, `/spek-retro`, `/spek-stance`

**Stance system** (`stances/`)
- Five built-in stances: `autonomous`, `collaborative`, `reviewer`, `skeptic`, `architect`
- Each is a YAML file listing module paths; modules are synced to `.spek/modules/` and stay inert until `/spek-stance` activates them

**Profile system** (`profiles/`)
- `base/base` — extends ai + git + docs + workflow (the standard starting point)
- `base/ai`, `base/git`, `base/docs`, `base/workflow` — composable base profiles
- `python/cli`, `python/webservice` — extend `base/base` with Python-specific modules
- Profiles support `extends:` (recursive, deduplicated), `modules:`, and `stances:`

**Key design decisions**
- `.spek/modules/` and `.spek/stances/` are committed to target projects — AI output can be regenerated without the upstream spek repo
- No `output: behavior` or routing-by-filename — all spec files are plain markdown; whether a module is always-active or stance-only is determined entirely by `spek.yaml`
- Session state in `.spek/SESSION.md` (gitignored); work log in `.spek/CHANGELOG.md`; backlog in `.spek/TODO.md`; codebase map in `.spek/STRUCTURE.md`
