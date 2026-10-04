## Spot checks (base `3a3f58c`, clean clone, fresh HOME, TMPDIR under this run's scratch)

Paths and symbols: `factory/instance.py:55` `find()`, `:105` `is_own_store`, `:141` `guard`; `factory/cli.py:845` `init_cmd`, `:885` agent copy, `:1193` `main()` with `root = store.state_root(cfg)` then `instance.guard(...)` at `:1201-1202`, `:638-639` `_by()`, `:1063` `--by` required, `:231` `in_flight.append`; `factory/workflows/intake.js:26` and `build.js:21` build `ENV`; `tests/factory/test_instance.py:25` `cli(cwd, *argv, **extra)` takes env overrides, `:132` `test_init_refused_outside_a_git_work_tree`, `:271-274` the test to change; `README.md:367` "never entered it", `README.md:102-103` the parent-close sentence; `docs/design.md:54` "**Tripwire on live files.**"; changelog last entry is 51; `grep -rn FACTORY_DISPATCH factory bin docs dev .factory/instance.yaml` finds nothing; `run_gates` has only its definition. All as cited.

Acceptance commands run on base, each matching the Acceptance section's "today" line:
- Unmarked writes: `init=0 new=0 transition=0 decision=0 store=changed agents=written`
- Harness acceptance: `accept=0 store=changed`
- Marked commands (REGRESSION): `decision=0 finish=0 cleared=1`
- Clerk marker count: `intake: sent unmarked=6`, `build: sent unmarked=2`
- README: `bullet=1 stale=1`; changelog: `CONTIGUOUS`, `2`

The negative control (marker removed from `intake.js` parks the intake) is the writer's result; I did not rebuild the prototype. The spec's fix shape follows from the code I read, so I accept it.

## Findings

[BLOCKING] 6 Decisions, first bullet
Problem: The first paragraph of Decisions uses two system-specific terms no earlier human-facing section glossed: "Instance B" (the Problem calls it only "this repository"; the gloss "this repository (instance B)" first appears under Risk, after Decisions) and `decisions.md` (Evidence names it only as a file `init` created).
Evidence: Read Problem, Evidence and Decisions in order as the gate operator; "instance B" is not in Problem or Evidence; `decisions.md` appears in Evidence bullet 1 with no statement of what it is.
Suggested fix: Write "Instance B, the factory instance of this repository, keeps the spec store ..." and "already in `decisions.md`, the store's standing decision log that later roles read".

[NIT] 2 Tests to change
Problem: The existing `cli()` helper's `STRIP` tuple (`tests/factory/test_instance.py:21`) does not drop `FACTORY_DISPATCH`, so under a shell that exported the marker the changed test passes with or without its one-line edit, while the new test file protects itself.
Evidence: `STRIP = ("FACTORY_INSTANCE", "FACTORY_REPO", "FACTORY_STATE", "FACTORY_INTEGRATION_BRANCH", "FACTORY_CWD")`.
Suggested fix: Since that file is already under Tests to change, add `FACTORY_DISPATCH` to `STRIP` in the same edit, or say in Tests to change why it is left alone.

[NIT] 5 design.md A.4 / Risk
Problem: Placing the fence before `instance.guard` changes which refusal a dirty checkout prints when a run is in flight on an own store (fence text, not "has uncommitted changes"), which the `guard` docstring's "refused first" ordering and the harness-suite current truth describe without that case.
Evidence: `factory/instance.py:141-151` docstring; current-truth scenario "The uncommitted-edit refusal still holds" uses a target with no run in flight, so it keeps passing.
Suggested fix: One sentence in the design-doc paragraph (C) saying the fence is checked before the harness lock, so a fenced command never reaches the lock or its acceptance.

## Out-of-scope observations
- The end-to-end scenario (`t0024-e2e.mjs`) runs clerk commands with the environment unchanged, so an exported marker in the runner's shell would let it pass even if part B were missing; the first scenario would then fail instead, so the set as a whole still catches it.

STATUS: REVISE
CONFIDENCE: high, every cited path and five acceptance commands checked on a clean clone of base; the only block is a first-use gloss the rubric names as blocking.
ESCALATIONS: none
