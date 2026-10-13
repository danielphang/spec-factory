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

STATUS: REVISE
CONFIDENCE: high; every cited path, line and "today" result was checked on this checkout, and the one BLOCKING finding is a gloss the rubric names explicitly, with a one-clause fix.
ESCALATIONS: none
