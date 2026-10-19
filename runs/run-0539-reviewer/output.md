Commit: e12ca713eb3b8594445773d44e87790fd480faa1 (branch `factory/T-0054.1`, base `308d038`, one commit)

## Test integrity

No existing test file changed: `git diff --stat 308d038 e12ca71` lists three new files under `tests/factory/` and nothing else there. No assertion weakened, no skip or xfail, no error swallowed. The new tests assert specific values: the launch copy's diff is exactly `-const LAUNCH = null` plus one `+const LAUNCH = {...}` line whose JSON equals what `paths` and `config` print (`test_launch_script.py:63-70`); the refused `--to checks` cases compare a byte-for-byte store snapshot before and after (`test_resolve_to_checks.py:121-124`); the node-driven build checks every agent call's model against the instance's models and the recorded run models (`test_workflow_launch_copy.py:168-176`).

## Correctness, against the spec's intent

I read the diff against spec v3's Proposed change A to F and confirmed each helper the new code calls exists with the behaviour the code assumes.

- **A, `launch-script`** (`factory/launch.py`, `factory/cli.py:823-826,844-845`). Refuses with exit 2 unless `const LAUNCH = null` occurs exactly once; `mkdtemp(prefix="factory-launch-")`; one line replaced; `json.dumps(..., ensure_ascii=False)`; mode 0444; prints the five designed keys. `instance` is `str(instance.require())`, which is the same `str(inst)` that `paths_cmd` prints (`factory/setup.py:355`). `("launch-script", None)` in `READ_ONLY` matches how `main()` keys the set, `(a.cmd, getattr(a, "sub", None))` at `factory/cli.py:859`, so the fence is skipped and `instance.guard` still runs: Decision 4. Cleanup (`launch.py:45-56`) applies the three conditions of Decision 15 and swallows `OSError`/`ValueError` per directory, so it cannot change exit or output.
- **B, the scripts honour a copy.** `INSTANCE` comes from `LAUNCH` before `ENV` is built (`build.js:21`, `intake.js:28`), so every clerk command carries the recorded instance. The instance mismatch check runs before the first clerk call (`build.js:232-234`, `intake.js:153-155`), so a mismatched copy runs no store command. `cfg = { ok: true, ...LAUNCH }` carries `models`, `max_rounds`, `state_dir`; the lines after it are unchanged.
- **C, `clerk()`.** Whole trimmed text first, then the unchanged last-line scan (`build.js:51-57`, `intake.js:60-66`). A single-line reply parses identically to before, so no caller sees a change except on a multi-line JSON value.
- **D, `resolve --to checks`** (`factory/human.py:255-264`). The four conditions are checked before any write. `store.implemented_since_ready` (`store.py:103-120`) matches a move into ready-for-implementer by the `to` field or `ticket.created`'s `status`, as the design asks, and the `human.resolved` event that `move` writes carries `to` (`human.py:205`), so a `--ruling` back to the implementer resets the "entered" mark as it should. `run.finished` carries `run` and `status` (`cli.py:353`); a `run.killed` run leaves `status` None and is refused. `set_head` is `ticket head`'s body moved intact, with its one lazy `gitops` import; `_apply_round` moved with its exact text. The route's round step is `pr:init`, and `move` saves the ticket after the in-memory round change, so the round persists.
- **E, tests.** Node-driven tests use a real `sh -c` clerk with miscopy knobs, as Decision 12 allows. Each file points `TMPDIR` into its `tmp_path` with an autouse fixture, and `launch()` fails any copy outside it: coding rule 6's guard for the new outside path.
- **F, documents.** README is 1,109 lines (`wc -l README.md`), within the 1,110 budget; the "Starting a run" hunk replaces 19 lines with 19 (`-696,19 +697,19`), the fence sentence is rewrapped with no added line (`-829,9 +830,9`), and the run-start paragraph grows by one. `design.md` lines 44, 64 and 109 and changelog entry 75 say what the spec asked.

## Findings

- [NIT] tests/factory/test_workflow_launch_copy.py:103-124 and tests/factory/test_resolve_to_checks.py:30-56: the two new files each define their own `planned()`/`implement()` scaffolding that sets up T-0001.1 and simulates one implementer run → a later change to how an implementer run is simulated has to be made in two places. Both are new, so this is not a `reuse:` finding against an existing helper, and the existing `_fixtures` classes bind a stand-in `claude` these tests do not want. Fine to leave.

Coding standard pass: Lean already. `config_values` is spec-mandated and has two callers; `set_head` and `_apply_round` are moves, not additions.

Scope: no changes outside parts A to F. The "resolve needs one of …" usage line now says `--to spec-gate|checks`; the PR description declares it, and it follows from D.

Silent behaviour changes: `ticket head` prints `t["head"]` instead of a local `head`, which is the same value (`store.py:214`). The clerk's parse changes only for a stdout whose whole text is one JSON value, which previously produced "no JSON on stdout". Nothing else a caller would notice.

Security and data safety: the copy is written with `mkdtemp` under the temporary directory and read-only; cleanup removes only directories matching three conditions, never the checkout or store. JSON embedded in JS via `json.dumps` escapes quotes and backslashes.

PR description: What changed and Known gaps read well and gloss the clerk, launch copy and the park on first use. The Known gaps honestly report the untested "line not exactly once" refusal, the Workflow-tool gap, the scenario-3 shell issue and the `STATE` gap.

Prior findings: none (round 1).

## Out-of-scope observations

- The `STATE`/`FACTORY_STATE` divergence the implementer notes (a copy launched without `args.state` builds `ENV` before `STATE` is known) is pre-existing behaviour of the clerk path too, and the design did not ask to change it. Worth its own small ticket if copies are ever launched against a throwaway store.

STATUS: APPROVE
CONFIDENCE: high: every part of the design is present with the behaviour it asks for, each helper the new code calls was confirmed to exist with the assumed fields, the new tests assert specific values and no existing test changed; I did not run the suite or the Workflow tool, which the verifier and Operator step 1 cover.
ESCALATIONS: protected path `factory/**` touched (`launch.py`, `cli.py`, `gates.py`, `human.py`, `store.py`, `workflows/build.js`, `workflows/intake.js`); the parent spec's Risk section declares it, listed for the record only.
