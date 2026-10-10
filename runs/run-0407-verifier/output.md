Commit: 656c179f4a4f4631b8fa61e037c7f871f36cd26d (branch `factory/T-0040.1`, base 37848dbb04f29c63d5d684a3b4c033ed41ede13e)

How it was run. The GIVEN blocks were extracted from their sources and run once each with `TMPDIR=<this run>/scratch/tmp`, and all three exited 0:
- `t0023-parent.sh` from `openspec/specs/human-resolution/spec.md` (first `sh` block);
- `t0024-inflight.sh` from `openspec/specs/live-store-guard/spec.md` (first `sh` block);
- the six `t0040-*` files from input.md lines 279–416. `diff` against spec v4 lines 161–298 shows them identical.

Each WHEN was copied verbatim from input.md into a file. The stop scenario uses the amended text at line 472 (`grep -c '^- run: run-0001-triage'`), which matches v4.md line 354. Each WHEN was then run under `bash` through the running-code wrapper, from the PR worktree and from a base tree. The base tree for scenarios 1–4 and 6 is a `git archive` of 37848db. The base tree for scenario 5 is a `git clone` of 37848db, because `factory init` inside `t0024-inflight.sh` failed in the non-git archive with `no .factory/instance.yaml found`. That was a fault of my setup, not of the spec, so the clone result is the one reported. Logs: `scratch/pr-acceptance.log`, `scratch/base-acceptance.log`, `scratch/gate-suite.log`, `scratch/probe1.log`, `scratch/probe2.log`.

Per criterion:
- NEW | intake parity (4 play sets) | base: `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=2/2 drive=0/0 differ`, `ready-for-triage script=1/1 drive=0/0 differ` | PR: `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same` | PASS
- NEW | each role run records its reply | base: `none` | PR: `triage=ok spec_writer=ok critic=ok` | PASS
- NEW | intake step lines and status file | base: `steps=no untagged=0 last=0 status= ignored=0` | PR: `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1` | PASS
- NEW | stop, KILLED, resume (amended count) | base: `stop: exit=2 running=0 run= ready-for-triage in_flight: [] child=gone last=0` / `resumed: exit=2 ready-for-triage calls=` | PR: `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1` / `resumed: exit=0 closed calls=2` | PASS
- NEW | marker on the driver, never on its roles, and effort | base (git clone): `unmarked=2 marked=2 ready-for-triage calls=0 effort=0 dispatch=0 inside=2` | PR: `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2` | PASS
- NEW (intermediate) | intake half of the argv check (`t0040-calls.py`) | base: one empty line | PR: `critic ok`, `spec_writer ok`, `triage ok` | PASS
- REGRESSION | the Workflow scripts still reach the end of both routes | base: not run | PR: `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate` | PASS
- Intermediate | harness suite exits 0 | base: not run | PR: covered by the gate run below (`511 passed`, exit 0) | PASS

Each NEW criterion fails on base for the reason verification.md states, because `drive` does not exist there, and the base figures match its "today" figures line for line. Each passes on the PR.

Gate suite: PASS
- `git diff --check main...HEAD` (main = 37848db) exited 0 with no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `511 passed in 320.89s (0:05:20)` and exited 0.

Guardrail checks:
- The branch changes only `factory/cli.py`, `factory/drive.py` (new), `factory/store.py`, `factory/instance.template.yaml`, `tests/factory/test_drive.py` (new) and `tests/factory/test_run_scratch.py`.
- The `test_run_scratch.py` changes are exactly the three listed under Tests to change: 4 comment lines and `drive/` counted once; then each of the two expected line lists ending in `"drive/"`.
- No test in `test_drive.py` pins the interim build-phase refusal: grep for `not built`, `"build"` or a build `--phase` found nothing.

Probes:
- Intake routes the acceptance commands do not cover were each run on the script and on the driver. These used a probe copy of the parity fixture (`scratch/parity2.sh`), and the driver ran with no `--phase`, so the stored state chose the phase.
  - triage CLARIFY → `waiting-requester … same` → OK
  - triage NEEDS-HUMAN → `parked … same` → OK
  - triage unknown STATUS (`BOGUS`) → `parked … same` → OK
  - triage REJECT → `closed … same` → OK
  - spec writer NEEDS-HUMAN → `parked script=2/2 drive=2/2 same` → OK
  - spec writer NEEDS-SPLIT, then critic ESCALATE → `parked script=3/3 drive=3/3 same` → OK
  - an EMPTY-OUTPUT triage re-dispatched once, then two EMPTY-OUTPUT critics → `parked script=5/5 drive=5/5 same` → OK
- Resume from the middle of the loop: T-0001 starts at `ready-for-critic` with a spec at round 1, and no `--phase` is given.
  - critic APPROVE → `awaiting-spec-gate script=1/1 drive=1/1 same`, result `"rounds": 1` → OK
  - critic REVISE → `parked script=3/3 drive=3/3 same`, `"reason": "max rounds"` → OK
- A failure message containing `"` and `$HOME` → `differ`. Both sides park with `agent call failed: spec_writer: …` and the same quote replacement. The script's park reason has `$HOME` expanded by its `sh -c`. The driver keeps it verbatim → OK. This is the difference the implementer disclosed under Known gaps. The driver's form is the correct one. It is not covered by any criterion.
- Interim build refusal on a `t0023-parent.sh` store at `ready-for-planner`:
  - with no `--phase`, exit 2; with `--phase build`, exit 2.
  - A checksum of every store file was unchanged, and no `drive/` directory was created.
  - stderr: `T-0001 is ready-for-planner: the build phase of factory drive is not built yet; run the build Workflow script`.
  - → OK
- SIGINT instead of SIGTERM → exit 130, last line `{"ok": false, "ticket": "T-0001", "stopped": "SIGINT"}`, run `KILLED`, status file `ended:` written with `running: []` → OK
- Malformed or empty inputs:
  - a missing ticket (`T-0099`) → exit 1, `{"ok": false, "ticket": "T-0099", "error": "no such ticket: …"}` → OK
  - `--parallel 0` → exit 2 (argparse refusal) → OK
  - `--phase intake` on a `closed` ticket → exit 0, `"note": "nothing to dispatch from this state"` → OK
- A `claude` that exits 0 but prints non-JSON (stderr `first err`, then `auth expired`) → run `KILLED`, `claude: null`, park `agent call failed: triage: auth expired` (the last non-blank stderr line, as Decisions requires) → OK
- No `claude` on `PATH` → park `agent call failed: triage: cannot start claude: [Errno 2] …`, `in_flight: []`, nothing left in flight → OK

No probe shows behaviour fitted only to the tested inputs.

Out-of-scope observations:
- A stopped run gets no `reply.json` and no `claude:` key, a gap the implementer disclosed. The spec's stop sequence names only `--status-override KILLED`, so this meets the spec as written.
- When the driver runs with no `--phase` on a state in neither phase, the status file records `phase: null`. No criterion covers this.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command and both gates were run as written on 656c179. Every NEW command was also run on base, where it failed for the stated reason. Twelve probe cases across intake routes, stops, refusals and failure handling behaved as specified.
ESCALATIONS: none
