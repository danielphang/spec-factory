## Acceptance

Run every scenario from the repository root after `uv sync --frozen`, inside the harness's running-code wrapper (a throwaway HOME). I ran each one on this checkout (`525d73f`). I also ran the five store-setup scenarios on a prototype of the change in my scratch directory, where each printed its THEN exactly. The prototype had no README or changelog edits, so the three harness-docs scenarios were run on this checkout only.

- Every role agent template's frontmatter parses and carries name, description, model and tools → NEW. Today the planner, spec-critic, spec-writer and triage lines print `keys=unparsed`.
- The four fixed templates keep their description's words and every other line → NEW. Today each of the four prints `text=changed rest=same`, because its description does not parse. `others=same` already holds.
- The suite fails on a template with broken frontmatter and names it → NEW. Today it prints `suite=passed clerk=0 stub=0`: the suite passes with both templates broken.
- init reports an edited agent copy and leaves it as it is → NEW. Today it prints `exit=0 stale=absent kept=yes named=0 others=0`: there is no `stale_agents` field and nothing on stderr.
- init still creates a missing agent copy and lists no matching copy → REGRESSION. Today it prints `exit=0 created=factory-triage.md stale=0 same=6 differs=0`.
- README describes init's report of a differing agent copy → NEW. Today it prints `row=0 step=0 missing=1`.
- The changelog records issue 108 in one entry without a numbering gap → NEW. Today it prints `CONTIGUOUS`, then `0`, then `0`.
- README stays within its line budget and both documents pass the whitespace check → REGRESSION. Today it prints `readme=within`, then `check=0`; README is at 1,106 lines.

## Responses

- [BLOCKING] Operator steps leaves "the Driver" and "the runtime upgrade" unglossed → FIXED. The step now opens with both glosses: the runtime checkout is "the separate worktree the factory runs from", moved to the merged revision and accepted with `--accept-harness`, and the Driver is "the session that runs the Nanobot target". I also replaced the step's check. v1 had the operator run `factory init` in Nanobot, which writes to a live target. The new check is a read-only `cmp` loop over the six templates, which prints `same` six times once the copies are refreshed. I ran it on this checkout: it prints `same` six times today, because the templates are not yet fixed. Risk now glosses the upgrade step the same way.
- [SHOULD-FIX] "fresh-HOME wrapper", "instance's own store" and "throwaway store" go unglossed → FIXED. Evidence's first bullet now says "the harness's running-code wrapper (which gives the command a throwaway HOME, so it cannot write the operator's real home directory)". Decisions bullet 5 now says "the target's own store (the directory under the target's `.factory/` that holds the factory's tickets and run records)" and explains `FACTORY_STATE` as the environment variable that points init at another store. verification.md's opening line uses the same gloss.
- [NIT] Part D does not bump README's status-header date → FIXED. D.3 now says to set line 9's "Current state as of" date to the merge date if it differs, and notes this changes no line count.
- Out-of-scope observation (new init tests overlap `test_instance.py`) → FIXED in design part C. The new tests build their target with `git_repo`, `cli` and `js` from `tests/factory/_cli.py`, as the `target` fixture does. They do not import from another test file, because `_cli.py`'s docstring forbids that. They do not edit `test_instance.py`, an existing test this spec does not list under Tests to change.

The base is unchanged since v1: `main` is still `525d73f`, and `git diff --stat 525d73f HEAD` over `agents`, `factory/setup.py`, `README.md`, `docs/changelog.md` and `tests/factory` is empty. So the "today" results in Acceptance, which both the critic and I ran on `525d73f`, still hold.

## Critic rounds

round 1 · spec v1 · run-0518-critic · REVISE

## Critic review, round 1 (spec v1 for issue #108)

What I checked myself, from `~/dev/spec-factory` at `525d73f`:

- Cited paths and lines: `agents/factory-planner.md` line 2 (unquoted `: ` present); `factory/setup.py` 179-184 (copy loop with only the `if not exists` branch), 201-204 (`store.initialised` event, "restart the session" line, `out({...})` with `agents`); `tests/factory/test_instance.py` 57-59, 115-135 (key-based reads of init's JSON, byte comparison with templates); `tests/factory/test_store_branch.py` 269 (named keys); `tests/factory/_cli.py` 16 (`REPO`, imported as `from ._cli import`); `README.md` 463, 575-588, 706, "Maintaining this page" at 1057; `docs/changelog.md` last entry `72. After issue #101 (2026-10-11), …`, 72 numbered entries, contiguous; `docs/design.md` 880; `git log -- agents/` gives `f5d8203`, `9b45041` only; `agents/` holds exactly the six `factory-*.md` files; none of the four descriptions contains `"` or `\`; `pyproject.toml` depends on `pyyaml>=6` and sets `addopts = "-n auto"`; this repo has no `.claude/agents/`; `cmp` of the six templates against `~/dev/nanobot-upstream/.claude/agents/` (read only): all same.
- Acceptance commands run as written, under the fresh-HOME wrapper, on this checkout (none runs the suite): frontmatter scenario printed clerk/stub `keys=ok` and the other four `keys=unparsed`; description scenario printed `text=changed rest=same` four times then `others=same`; init-edited-copy scenario printed `exit=0 stale=absent kept=yes named=0 others=0` (stderr empty, JSON has no `stale_agents`); init-missing-copy scenario printed `exit=0 created=factory-triage.md stale=0 same=6 differs=0`; README scenario printed `row=0 step=0 missing=1`; changelog scenario printed `CONTIGUOUS`, `0`, `0`; budget scenario printed `readme=within`, `check=0`. Every "today" result in verification.md matches.
- Tests pinning old behaviour: searched `tests/factory/` for init JSON equality, stderr-empty assertions and `.claude` writes. All init assertions read named keys; the only `.claude` manipulations are unlinks (test_instance 127, 145; test_live_store_guard 42-46). No test pins the absent `stale_agents` key or an empty stderr on init. "Tests to change: none" holds.
- Decision log: the standing `init` decisions (T-0023, T-0025: refusals, store branch, exclude file) are untouched by this change. Approved changes not yet archived: none.
- Not checked: the suite-fails scenario and the prototype's `590 passed` (both need a suite run); Claude Code's own frontmatter parser (the spec says so itself).

Findings

[BLOCKING] 6 proposal.md, Operator steps, first paragraph
Problem: It uses two terms specific to this system that no human-facing section has glossed, "the Driver" and "the runtime upgrade"; a reader new to the system has to infer who performs the step and what must happen first.
Evidence: "Driver" is glossed only under Out of scope ("the session that runs the Nanobot target"), and the upgrade step is explained only under Risk ("the usual runtime upgrade and `--accept-harness` step"); neither is a section the gate operator reads. Problem, Evidence and Decisions do not gloss either.
Suggested fix: Open the step with the glosses in place, for example "After the merge, and after the factory's runtime checkout has been moved to the merged revision and accepted with `--accept-harness`, the Driver (the session that runs the Nanobot target) refreshes …", and keep the Out of scope sentence as is.

[SHOULD-FIX] 6 proposal.md, Evidence first bullet and Decisions bullet 4
Problem: Two more system-specific terms go unglossed where the operator meets them: "the fresh-HOME wrapper" (Evidence, first bullet) and "the instance's own store" / "a throwaway store (`FACTORY_STATE` naming another store)" (Decisions, bullet 4); "store" and "instance" appear nowhere earlier in the human-facing sections.
Evidence: Problem glosses template, `factory init`, target, `inlineRoles` and `factory drive`, but not store, instance or the wrapper.
Suggested fix: In Evidence say "under the harness's running-code wrapper, which gives the command a throwaway HOME", and in Decisions bullet 4 say "for the target's own store (the directory, under its `.factory/`, that holds the factory's tickets and runs); an init pointed at another store by `FACTORY_STATE` …".

[NIT] 3 design.md, part D
Problem: README's "Maintaining this page" says a change to a command also bumps the date in the status header (line 1069); part D does not mention it, and `init`'s output changes.
Evidence: README line 9 reads "Current state as of 2026-10-13"; if the merge lands on a later day the header is stale and the code reviewer is told to treat that as a finding.
Suggested fix: Add to D.2 "and set the status header's date to the merge date if it differs", inside the four-line net budget (it changes no line count).

No other findings. Grounding, testability, scope and consistency hold: every cited path and line exists; each NEW scenario fails today for the stated reason and would fail a stub (the suite-fails scenario catches a test that asserts nothing; the description scenario catches a rephrased description; the edited-copy scenario catches an overwrite or a missing stderr line); the change fits one PR; protected paths `agents/**` and `factory/**` are declared; the changelog entry format matches the existing `<n>. After issue #<k> (<date>), ` pattern; the README budget (1,110 lines, store-setup current truth) leaves four lines, which part D respects.

Out-of-scope observations
- The new init tests in design part C overlap `test_init_is_idempotent_and_creates_only_what_is_missing` and the deleted-copy test in `tests/factory/test_instance.py` 115-135; the implementer should reuse the `target` fixture and `cli` helper rather than new setup code (harness-suite: shared code lives in helper modules).

Prior findings: none (round 1).

round 2 · spec v2 · run-0520-critic · APPROVE

## Critic review, round 2 (spec v2 for issue #108)

Reviewed per the convergence rule: whether the round-1 findings were resolved, and the text the v1→v2 diff changed (Evidence bullet 1, Decisions bullet 5, Risk paragraph 2, Operator steps, design part C's test paragraph, design D.3, verification.md's opening line and the new Responses section). Unchanged text was not re-reviewed.

What I checked myself, from `~/dev/spec-factory` at `525d73f` (`git rev-parse --short HEAD`; the diff claims the base is unchanged since v1, and the `main` HEAD confirms it):

- Changed text against the repo. Design part C names `git_repo`, `cli` and `js` in `tests/factory/_cli.py`: they are defined at lines 60, 23 and 43, and the file's docstring (lines 1-5) says "A test file imports them from here, never from another test file", as the spec states. The `target` fixture it refers to is `tests/factory/test_instance.py:31-38`: four lines, `git_repo` then `cli(..., "init", "--repo-name", "demo")`. D.3 cites README line 9 ("Current state as of 2026-10-13") and "Maintaining this page": line 1069 says a change to a command "bumps the date in the status header". Both hold. `factory/setup.py:180-184` is still the copy loop with the single `if not exists` branch, and `out({...})` with `agents` is at 203-204.
- Operator steps' new check, run as written, read only: the `cmp` loop over the six templates against `~/dev/nanobot-upstream/.claude/agents/` printed `same` six times, as the Responses section says it does today. It is a read-only command on the protected path, so the v1 problem (running `factory init` in the live Nanobot target) is gone.
- Acceptance commands run as written under the running-code wrapper (neither runs the suite): the frontmatter scenario printed `keys=ok` for clerk and stub and `keys=unparsed` for planner, spec-critic, spec-writer and triage; the README scenario printed `row=0 step=0 missing=1`. Both match verification.md's "today" results.
- Glosses in the human-facing sections, read as the gate operator: Evidence bullet 1 now explains the wrapper; Decisions bullet 5 now explains the store and `FACTORY_STATE`; Risk paragraph 2 now explains the runtime checkout and `--accept-harness`; Operator steps now opens with both the runtime-checkout gloss and the Driver gloss before using either. No new term of art is introduced without a gloss in the changed text.
- Approved changes not yet archived: none, so no scenario has a merge-order dependency.
- Not checked, as in round 1: the suite-fails scenario and the prototype's `590 passed` (both need a suite run); Claude Code's own frontmatter parser (the spec says so itself).

Findings

[NIT] 6 design.md, part C, test paragraph
Problem: "add no new setup code" and "do not import that fixture" read together could make an implementer think a local fixture is forbidden, when the only way to build the target without importing from `test_instance.py` is a local fixture of the same four lines calling `git_repo` and `cli`.
Evidence: `tests/factory/test_instance.py:31-38` is the fixture; `_cli.py` lines 1-5 forbid importing it from another test file; `_cli.py` has no fixture of its own that returns an initialised target.
Suggested fix: Say "build the target with the shared helpers (`git_repo`, `cli`, `js` from `tests/factory/_cli.py`), in a fixture local to the new file, the way `test_instance.py`'s `target` fixture does", and drop "add no new setup code".

Prior findings
- [BLOCKING] 6, Operator steps unglossed "the Driver" and "the runtime upgrade": RESOLVED. The step opens with both glosses; Risk uses the same gloss; the check is now read only.
- [SHOULD-FIX] 6, "fresh-HOME wrapper", "instance's own store", "throwaway store" unglossed: RESOLVED. Evidence bullet 1, Decisions bullet 5 and verification.md's opening line carry the glosses.
- [NIT] 3, part D omits the README status-header date bump: RESOLVED. D.3 names line 9 and the merge date, and notes no line-count change.
- Out-of-scope observation, new init tests overlap `test_instance.py`: addressed in design part C with the shared helpers, without touching the existing test, which keeps "Tests to change: none" true.

Out-of-scope observations
- none new.
