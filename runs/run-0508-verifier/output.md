Commit: 5e00a1f5261b2576ae6243b46ac8895f71042ff9

Setup. The PR head is the worktree `wt` at `5e00a1f`, with an empty `git status`. The base is a `git clone` of `~/dev/spec-factory` in `scratch/base`, checked out at `88c65e147495debccaef62986a15df1ee54b59f4`. `main` is still that SHA, so `main...HEAD` compares against the stated base. I ran `uv sync --frozen` in each checkout through the running-code wrapper. The PR's `.venv` then had pytest-xdist 3.8.0, and the base's had no `xdist` module. I took the GIVEN blocks verbatim from the spec files:
- from the pinned spec `specs/T-0051/v3.md`: `t0051-time.py`, `t0051-standin.py`, `t0032-checks.sh` and `t0032-build.mjs`;
- from the current-truth specs: `human-resolution` lines 13-65 (the `t0023-*` files) and `build-dispatch` lines 53-100 and 277-414 (the `t0022-*` and `t0040-*` files).

I wrote them once into `scratch/tmp`. A script copied each WHEN command out of v3.md byte for byte (16 commands). I ran each one from the checkout under test, through the wrapper, with `TMPDIR=scratch/tmp`. The timing script gives each suite copy its own TMPDIR under `/tmp`, as the spec says. The gate suite ran with the system TMPDIR, which is outside any repository.

Per criterion (NEW/REGRESSION | command | base | PR | result):
- NEW | One suite run passes in under three minutes | `stopped | over 180 s` | `584 passed in 135.55s (0:02:15) | under 180 s` | PASS
- NEW | Two suite runs at once each pass in under five minutes | not run (base, as in the spec: one base run alone was stopped at 180 s above) | `584 passed in 239.01s (0:03:59) | under 300 s`, then `584 passed in 239.29s (0:03:59) | under 300 s` | PASS
- NEW | Four stand-ins of one role started together all reply, 200 times over | `STANDIN: 200 rounds, 21 with a copy that did not reply, counter 750`, then `BUILD_STANDIN: 200 rounds, 18 with a copy that did not reply, counter 760` | `STANDIN: 200 rounds, 0 with a copy that did not reply, counter 800`, then `BUILD_STANDIN: 200 rounds, 0 with a copy that did not reply, counter 800` | PASS
- NEW | No test is removed and only the two listed assertions change | `pair: 0`, `removed: 0`, `added: 0`, `missing: 0` | `pair: 1`, `removed: 0`, `added: 1` (`tests/factory/test_empty_output.py::test_last_message_that_is_not_about_waiting_prints_waiting_false`), `missing: 2`, then exactly the two expected lines: `missing test_drive.py::test_two_empty_outputs_park_with_both_runs_and_keep_the_last_message: assert parked['reason'] == 'EMPTY-OUTPUT from triage'` and `missing test_empty_output.py::test_last_message_is_kept_for_an_empty_output_run: assert res == {'ok': True, 'run_id': s.rid, 'last_message': f'runs/{s.rid}/last-`. Two tar locale warnings went to stderr, which the scenario says to ignore. | PASS
- NEW | The gate's suite command, as the instance lists it, passes in under three minutes | not run (base, as in the spec: the same command form was stopped at 180 s in the first row) | `gate: uv run --frozen pytest -q -p no:cacheprovider tests/factory`, then `584 passed in 138.18s (0:02:18) | under 180 s` | PASS
- NEW | A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows | `park T-0001.1: EMPTY-OUTPUT from reviewer`; the other three lines matched | `park T-0001.1: EMPTY-OUTPUT from reviewer: ended its turn waiting on a background command`, `reviewer: EMPTY-OUTPUT EMPTY-OUTPUT `, `verifier: VERIFIED `, `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` | PASS
- REGRESSION | One empty reviewer run followed by a real one routes on the real one | not run | `park T-0001.1: SPEC-DEFECT from verifier`, `reviewer: EMPTY-OUTPUT APPROVE ` | PASS
- REGRESSION | An implementer that returns nothing twice parks as EMPTY-OUTPUT | not run | `park T-0001.2: EMPTY-OUTPUT from implementer`, `implementer: EMPTY-OUTPUT EMPTY-OUTPUT ` | PASS
- REGRESSION | An intake role's second empty output in a row parks as EMPTY-OUTPUT | not run | `start: triage`, `start: triage`, `park: EMPTY-OUTPUT from triage` | PASS
- NEW | An intake role that ends waiting twice parks with the waiting reason, in the driver and the script | `parked script=2/2 drive=2/2 same`, `script EMPTY-OUTPUT from triage`, `drive EMPTY-OUTPUT from triage` | `parked script=2/2 drive=2/2 same`, `script EMPTY-OUTPUT from triage: ended its turn waiting on a background command`, `drive EMPTY-OUTPUT from triage: ended its turn waiting on a background command` | PASS
- NEW | A build checker that ends waiting twice parks with the waiting reason, in the driver and the script | `planned script=4/4 drive=4/4 same`, `script EMPTY-OUTPUT from reviewer`, `drive EMPTY-OUTPUT from reviewer` | `planned script=4/4 drive=4/4 same`, `script EMPTY-OUTPUT from reviewer: ended its turn waiting on a background command`, `drive EMPTY-OUTPUT from reviewer: ended its turn waiting on a background command` | PASS
- REGRESSION | A role whose last message is not about waiting parks with the plain reason | not run | `parked script=2/2 drive=2/2 same`, `script EMPTY-OUTPUT from triage`, `drive EMPTY-OUTPUT from triage` | PASS
- NEW | The design doc and build spec name the waiting park reason, and no prompt copy changes | `design=0 spec=0 cli=0 prompts=0` | `design=1 spec=1 cli=1 prompts=0` | PASS
- NEW | The README names pytest-xdist and the waiting reason | `bullet=1 waiting=0 unfired=1 xdist=0` | `bullet=1 waiting=1 unfired=0 xdist=1` | PASS
- NEW | The changelog records issue 106 as its last entry, without a numbering gap | `CONTIGUOUS`, `0`, `0` | `CONTIGUOUS`, `1`, `5` | PASS
- REGRESSION | The parallel-suite change adds no whitespace errors | not run | `exit=0` | PASS

Every NEW criterion failed on base for the reason verification.md gives, and passed on the PR.

Gate suite: PASS
  `git diff --check main...HEAD`, run from the worktree exactly as written: no output, exit 0.
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`, run exactly as written: `584 passed in 99.44s (0:01:39)`, exit 0.

Other checks. `wc -l factory/cli.py` gives 891, under the 900-line limit. `git diff --stat 88c65e1...HEAD` lists 13 files. The only protected paths among them are `pyproject.toml`, `uv.lock`, `factory/cli.py`, `factory/drive.py`, `factory/workflows/intake.js` and `factory/workflows/build.js`, which are exactly the paths the spec's Risk line declares. Nothing under `docs/prompts/`, no role prompt and nothing under `.factory/` changed.

Probes:
- Only one of the two empty runs says it is waiting, in either order. Inputs: triage plays `[waiting, plain]` and `[plain, "The tests are STILL RUNNING in another shell."]`, through `t0040-parity.sh` with PHASE=intake. Result: both print `parked script=2/2 drive=2/2 same`, and the script and the driver both give `EMPTY-OUTPUT from triage: ended its turn waiting on a background command`. This is the spec's "either run" rule, applied the same way by the script and the driver. → OK
- The first run is blank, and the second says `awaiting approval; it waited too long`. Result: `parked script=2/2 drive=2/2 same`, with the plain reason `EMPTY-OUTPUT from triage` in both. The blank run makes no `run last-message` call, and `awaiting` and `waited` are not the whole words `wait` or `waiting`. → OK
- The `WAITING` regex in `factory/cli.py`, given these messages: `Wait.`, `waiting`, `Still In Progress`, `running in the background` and `I wait-listed it` match. `awaiting review`, `it waited`, `still\nrunning` and an empty string do not. This is the spec's rule: case-insensitive, the whole word `wait` or `waiting`, or one of the three phrases. Nothing is special-cased to the test messages. → OK (the `wait-listed` match is the known limit of a word match. Per the spec's Decisions it changes only the park wording, never the route.)

Notes for the reader. The timing runs ran while other sessions were loading this 10-core machine: its load average read between 7 and 21 during them. One run took 135-138 s against the 180 s bound, and two at once took 239 s each against 300 s. The implementer measured 93-106 s and 163-166 s. Every bound held, but the margins are smaller than the PR reports. The spec's Risk section already says the timing scenarios depend on the machine.

STATUS: VERIFIED
CONFIDENCE: high, every acceptance command ran byte for byte from the spec on both the base and the head, both gates passed on the head, and the probes found nothing special-cased.
ESCALATIONS: none
