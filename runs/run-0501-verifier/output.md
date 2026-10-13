Commit: b3b978dce1d5544c7f346695292b8ef37f64eaae

Checked out: the run's worktree `wt` at b3b978d (branch `factory/T-0050.1`; `main` resolves to the base 2fbc170). Base runs used a fresh clone of the dev repo at 2fbc170453cc3c549c487a6dd2c326b2b636e626 under this run's scratch directory, after `uv sync --frozen` in both. Every command ran through the fresh-HOME wrapper with `TMPDIR` under scratch, except the suite scenario, which pins its own `/tmp` directory as written. The GIVEN blocks (t0023-parent.sh from human-resolution, t0032-checks.sh from build-dispatch, t0050-wf.mjs from this spec, t0040 fixtures from build-dispatch) were taken verbatim from the current-truth specs and run once per checkout.

Per criterion:

- NEW | A run start given a model the instance does not name is refused and writes nothing, and one without --model records the instance's model
  base: `refused: exit=0  runs=1 started=1` / `default: exit=2 returned= recorded=opus logged=opus` (the "today" text verification.md states)
  PR: `refused: exit=2 model opus refused for triage: the instance names sonnet runs=0 started=0` / `default: exit=0 returned=sonnet recorded=sonnet logged=sonnet`
  PASS

- REGRESSION | A run start given the instance's own model is accepted and records it
  base: not run (passed on the PR)
  PR: `exit=0 returned=sonnet recorded=sonnet`
  PASS

- NEW | An intake run told the wrong triage model parks before triage starts, and one told the right model runs triage on it
  base: `agent triage T-0001 model=opus` / `swap=none closed runs=triage=opus` / `agent triage T-0001 model=fable` / `swap=triage=fable closed runs=triage=fable` (triage launched and recorded on fable, as verification.md states)
  PR: `agent triage T-0001 model=opus` / `swap=none closed runs=triage=opus` / `park T-0001: harness-bug: run start triage: model fable refused for triage: the instance names opus` / `swap=triage=fable parked runs=`
  PASS

- NEW | A build told the wrong verifier model parks the sub-ticket before any verifier starts, and the reviewer still runs on its own model
  base: `agent reviewer T-0001.1 model=fable` / `agent verifier T-0001 model=fable` / `agent verifier T-0001.1 model=fable` / `park T-0001: archive: no spec store (factory init not run)` / `merged runs=reviewer=fable verifier=fable verifier=fable` (both verifiers on fable, as verification.md states)
  PR: `agent reviewer T-0001.1 model=fable` / `park T-0001.1: harness-bug: run start verifier: model fable refused for verifier: the instance names opus` / `parked runs=reviewer=fable`
  PASS

- REGRESSION | The harness suite passes with only the two fixtures that passed a wrong model changed
  command: `(P=$(mktemp -d /tmp/t0050-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only --diff-filter=DMR main...HEAD -- tests)`
  base: not run (passed on the PR)
  PR: `583 passed in 267.27s (0:04:27)` then `tests/factory/test_coding_standard.py`, `tests/factory/test_turn_economy.py`
  PASS

- NEW | The build spec and the README describe the model check
  base: `old=1 guard=0 readme=0`
  PR: `old=0 guard=1 readme=1`
  PASS

Also re-run, as verification.md asks (current truth, build-dispatch), on the PR:
- "The driver takes the build fixtures through the same routes as the build script": `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same`. Exactly the THEN.
- "Each role runs as one claude process with its prompt, model and tool limits": `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`. Exactly the THEN.
- "The Workflow scripts still take both fixtures to the end of their routes": `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate`. Exactly the THEN.

New test file on base: copying `tests/factory/test_run_start_model.py` onto the base clone and running it gave `4 failed, 3 passed in 2.89s` (the refusal tests fail there; the no-model and matching-model tests pass, as the implementer reported). The copy was removed afterwards; the base clone is clean.

Gate suite: PASS
- `git diff --check main...HEAD`: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `583 passed in 274.91s (0:04:34)`, exit 0.

Probes (all on the PR, instance with `triage: sonnet`, fresh store with T-0001 at ready-for-triage):
- `--model ""` (empty string) → exit 2, `model  refused for triage: the instance names sonnet`, no run directory → OK (an empty relayed value is refused, not treated as "absent")
- `--model Sonnet` (case differs) → exit 2, refused → OK (exact match, no normalisation that could let a retyped value through)
- critic with wrong model on a ticket in the wrong state → model refusal, exit 2; same critic with its own model `fable` → `T-0001 is ready-for-triage, not ready-for-critic`, exit 2 → OK (model check precedes the state guard, as design A.1 orders it; the state guard is intact)
- unknown role with `--model` → `unknown role bogus; ...`, exit 2 → OK (role check still first)
- wrong model on a ticket that does not exist (T-0099) → model refusal, exit 2; T-0001's `in_flight` untouched → OK (refusal before the ticket is loaded, nothing written)
- instance file with no `models.verifier` entry, `--model opus` → `factory: KeyError: 'verifier'`, generic failure. The same instance without `--model` fails identically on the base → OK as a non-regression; it is the known gap the PR description names (an instance missing a role's model used to pass when `--model` was given, now fails either way). Both instance files and the template name every role.
- store after all probes: `runs=0 started=0` → OK (no refused start wrote anything)
- `factory/drive.py:186` passes `self.models[role]` and `drive.py:201` launches on `start.get("model") or self.models[role]` → consistent with the Risk claim that the driver is unaffected; confirmed by the parity scenarios above.
- `factory/cli.py` is 884 lines (limit 900); `run start --help` shows `--model MODEL    must match the instance's model for the role`.

Changed files: README.md, dev/build-harness.spec.md, factory/cli.py (declared protected path), tests/factory/test_coding_standard.py, tests/factory/test_turn_economy.py, tests/factory/test_run_start_model.py (new). No change to docs/design.md or docs/prompts/, as the spec requires. README status date is already 2026-10-12.

STATUS: VERIFIED
CONFIDENCE: high. Every NEW scenario printed verification.md's "today" text on the base and exactly its THEN on the PR; both REGRESSION scenarios, both gates and the three parity scenarios pass; probes at the boundaries (empty, case, ordering of guards, missing ticket) show the refusal is general, not tied to the tested inputs.
ESCALATIONS: none
