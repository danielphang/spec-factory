Type: chore

Title: Get one harness-suite run well under the 10-minute tool-call cap, and name a background wait in the EMPTY-OUTPUT park reason (spec-factory #106)

Summary:
One run of the harness's own test suite (`tests/factory`) now takes 7 to 10 minutes. A single agent tool call is capped at 10 minutes. When a role (one AI agent in the pipeline: implementer, verifier, reviewer) has to run the suite, it starts the run in the background and ends its turn waiting for it. That run then leaves no output and parks the ticket as EMPTY-OUTPUT, as T-0047.2 did on 2026-10-12. The requester asks for three things:
- (A) one suite run well under the cap, with a target under 3 minutes, by whichever of the two candidates measures faster. The candidates are parallel runs with `pytest-xdist` or calling the CLI in-process in `tests/factory/_cli.py`. Either way, the load-sensitive timing test must keep passing.
- (B) the gate commands and the verifier's suite REGRESSION check use the faster form. Gate commands are the repository's check commands that every sub-ticket must pass before merge.
- (C) when an EMPTY-OUTPUT run's last message says it is waiting on a command, the park reason says "ended its turn waiting on a background command". A human then knows a plain redispatch will repeat the failure.
The requester rules out any prompt change: that needs the golden baseline first (#96 row 4a).

Evidence:
- The request: T-0047.2 (#100) parked 2026-10-12 20:29Z with `EMPTY-OUTPUT from verifier`. Both verifier runs, run-0486 and run-0487, ended on "Waiting for the suite runs to finish before writing the output." The implementer, run-0484, wrote: "One full suite run takes about 9 to 10 minutes on this machine, close to the 10-minute limit a single tool call allows. I had to run it in the background."
- The request's measured suite times: 443.67 s on a quiet clone at `700ce73`. Verifier runs took 479 s to 605 s; the 605 s run had a second suite running beside it.
- The request's profile: the 40 slowest tests take 151 s of 443 s, and the slowest takes 19 s. The other tests average about 0.55 s each, mostly spent spawning the CLI as a subprocess.
- Later comment: `test_drive_build.py::test_build_step_lines_and_the_status_file_name_the_subticket_in_flight` failed 3 times in 8 full-suite runs on the T-0047.2 head and 0 times in 2 on base. Its 2-second sleeps decide whether a checker gets killed. The requester asks that Part A make this test independent of load.
- Checked on this checkout (`main` at `88c65e1`):
  - `uv run --frozen pytest -q -p no:cacheprovider --collect-only tests/factory` (through the HOME wrapper) prints "583 tests collected". The request says 576; T-0050 has merged since. The gap does not change the problem.
  - `tests/factory/_cli.py` imports `subprocess`. Its helpers `cli`, `run` and `run_env` (lines 23-39) each call `subprocess.run` on the CLI. This matches the request's account of where the per-test time goes.
  - The timing test is at `tests/factory/test_drive_build.py:123`. Its stand-in plays give the reviewer and verifier `"sleep": 2`. The 19 s test is at `tests/factory/test_shepherd.py:480`.
  - `factory/prompts/preamble.md:45-48` already says "Run every command in the foreground and wait for it to finish."
  - The EMPTY-OUTPUT park reason is written in three places: `factory/drive.py:182`, `factory/workflows/intake.js:83` and `factory/workflows/build.js:74`. Each writes `EMPTY-OUTPUT from <role>`.
  - `.factory/config` does not exist. The gate commands are `gate_commands` in `.factory/instance.yaml:22-24`, and the suite command there is `uv run --frozen pytest -q -p no:cacheprovider tests/factory`.
  - `pytest-xdist` does not appear in this repo's `pyproject.toml`.
  - The ordering condition is met: T-0047 is `closed`, and its four sub-tickets are `merged`.
- Duplicate search: no open or recently closed ticket covers this. T-0016 and T-0028 cut the number of suite runs per sub-ticket. T-0032 added the "wait for your own commands" rule. None of them makes one run faster or changes the EMPTY-OUTPUT park reason. T-0051 is this request's own ticket.
- The request names no Nanobot-side commit. Nanobot's `pyproject.toml` lists `xdist`, but that is the target's own suite, not this harness. No as-built fix to verify.

Capabilities: harness-suite, build-dispatch, gate-commands, harness-docs

Assumptions:
- (Inference) "Measure both and pick by speed" leaves the choice to the spec writer or implementer, with the timings recorded. Combining both is allowed if it measures fastest. I read this as delegated, not as an open product decision.
- (Inference) "Well under the cap" is judged against the 443.67 s quiet baseline on the same machine. The target is under 180 s quiet. The spec should also state a bound under load, because the failure happened under load.
- (Inference) Part A keeps every test and assertion (harness-suite: "The refactor keeps every test and assertion but the one duplicate"). The suite still writes nothing into the checkout ("A suite run writes nothing into the checkout"). An in-process CLI call must keep the exit code, stdout and stderr a subprocess call gives. At least some tests should still exercise the real `bin/factory` entry point.
- (Inference) Making the timing test independent of load means replacing the fixed sleep race with a condition the test waits on. It must not loosen the assertion or add a retry, skip or xfail.
- (Inference) Part C detects "waiting on a command" from the run's kept last message, as `factory/cli.py:299-303` already keeps it. Part C applies in all three places that write the park reason, and the driver and Workflow scripts keep giving the same reason.
- (Inference) Part B can be a no-op for the gate command if the in-process route wins, because the command line itself would not change.
- (Note for the spec writer) Several files this request may change are protected paths: `.factory/instance.yaml` (infra), and `pyproject.toml`, `uv.lock` and `factory/**` (harness). The spec's Risk section must declare each one it changes, or the merge gate will refuse the merge.
- Priority suggestion (a human call): high. Every ticket that runs the suite can park this way under load.

Reason: The intent is clear and the evidence is concrete. The choice between the two speed-ups is delegated to measurement. No product decision is needed.

STATUS: ACCEPT
CONFIDENCE: high. Every path, line and test name the request cites was checked on this checkout. The one discrepancy (`.factory/config` does not exist; the gate commands live in `.factory/instance.yaml`) does not change the intent.
ESCALATIONS: none
