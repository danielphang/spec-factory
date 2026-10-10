Sub-ticket: T-0040.1 (T-0040.A, the driver core and the intake phase). Parent spec: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v4.md` (v4, pinned)
Branch: `factory/T-0040.1`, head `656c179f4a4f4631b8fa61e037c7f871f36cd26d`, base `37848dbb04f29c63d5d684a3b4c033ed41ede13e`

Part A of `factory drive` is ready for review. `factory drive` is a new harness command that takes a ticket through the intake half of the pipeline. Intake runs triage, then the spec writer and the spec critic, and stops at the spec gate. The driver is an ordinary Python process, so it needs no clerk agent to relay its store calls. Every part A acceptance criterion and both gates pass on the head above. The build phase is part B's work.

## Since the last run: the operator's ruling

The last implementer run (run-0405) built this head and stopped with BLOCKED. One criterion counted the run id twice in the status file, which is the driver's live view of itself in the store. The run id appears once in the `running` list and once on the `last:` line, as design.md A.7 requires. The operator ruled on 2026-10-09 that the criterion was wrong, not the build. The amended criterion counts only the `running` list's entry (`grep -c '^- run: run-0001-triage'`). Design A.7 stays as built.

This run made no code change and no commit. It re-ran the amended scenario, which now prints the expected line. It also re-ran every other acceptance command and both gates on the same head, and all of them still pass.

## What changed

Part A covers items 1 to 10 of design.md. All of it is in commit 656c179.

1. **Command** (`factory/cli.py`): a new `drive` subparser takes `TICKET`, `--phase {intake,build}`, `--parallel N` and `--prompt-mode {append,replace}`. `--parallel N` must be at least 1, defaults to 2 and is unused until part B. `--prompt-mode` defaults to `append`. `drive_cmd` dispatches through `main()`, so the instance refusal, the fence and the harness lock apply at start. The fence is the check that refuses an unmarked store write while a run is in flight. The harness lock is the check that the running harness revision is the one this instance accepted. After those checks, `factory.drive.drive` sets `FACTORY_DISPATCH=1` in `os.environ`. That variable is the dispatcher marker, which the fence lets through.
2. **Store calls** (`factory/drive.py` `call`): each call runs `cli.main(argv)` with stdout and stderr captured. It returns the last stdout line that is a JSON object, plus `exit` and `stderr`. It normalises the result the same way the scripts' `clerk()` does. Calls are synchronous, so they run one at a time on the main thread.
3. **Role runner** (`run_role` and `run_once`): these follow the scripts' `runRole` and `runOnce`. The steps are `run start`, then `run compose`, then one `claude` process.
   - The process runs from the run directory, with stdin `/dev/null`. Its environment is the driver's, minus `FACTORY_DISPATCH`.
   - `role_argv` builds the argv in the design's order, with real absolute paths. Each `Edit` rule's path therefore starts with `//`. The implementer gets the `Edit` tool, its worktree rule and `--add-dir`. `--effort` comes from `effort[role]` in `instance.yaml`.
   - Stdout is written to `<run>/reply.json` as printed.
   - A failed call is a non-zero exit, or stdout that is not a JSON object. It goes to `run finish --status-override KILLED --reply`, then a checker's cleanup, then a park with `agent call failed: <role>: <message>`.
   - Otherwise the order is `run finish --reply`, then a checker's cleanup, then the script's branches. Those branches are the `harness-bug` park on a refused finish, a tripwire `parked`, `run last-message` on EMPTY-OUTPUT, and one re-dispatch. A second EMPTY-OUTPUT parks.
   - The build-only branches are ported as the scripts have them, but no part A test reaches them. They are the `BLOCKED ` run-start refusal parked verbatim, and the checker cleanup.
4. **`run finish --reply FILE`** (`factory/cli.py` `_claude_record`): when FILE is a JSON object, it records `claude: {session_id, total_cost_usd, num_turns, usage}` in `meta.yaml`. Otherwise it records `claude: null`. Without `--reply`, nothing changes.
5. **Intake routing** (`Driver.intake`): a branch-for-branch port of `intake.js` from its `// --- start` marker. It covers triage ACCEPT, REJECT, NEEDS-HUMAN, CLARIFY and unknown, then the writer/critic loop with `max_rounds.spec` and `models` from `factory config`. The transitions, `--round` operations, `spec add` calls and park reasons match the script, including `--by workflow`. Park reasons get the script's `"` to `'` replacement.
6. **Phase**: without `--phase`, the stored state selects the phase. Intake states run. A state in neither phase ends with `nothing to dispatch from this state`. **Interim behaviour**: `--phase build`, or a stored state that selects build, is refused before anything is written. The command exits 2 and prints `<T> is <state>: the build phase of factory drive is not built yet; run the build Workflow script`. As the sub-ticket asks, no suite test pins this refusal.
7. **Progress**: the driver prints one flushed line per step, of the form `<ticket id> "<title>": <step>`. The steps are start, finish, transition, park, the critic's approval note and `end: …`. The title is read again after triage ACCEPT. The status file `drive/<ticket>.yaml` is written with `store.write_yaml` at start, at each step and at the end. Its keys are `ticket`, `title`, `phase`, `pid`, `started`, `updated`, `running`, `last` and `ended`. The last stdout line is the script's result object with `"ok": true` added. `STORE_GITIGNORE` (`factory/store.py`) gains one comment line, then `drive/`.
8. **Stop** (`Driver.stop`): SIGINT and SIGTERM handlers cancel the routing. Each role process then gets SIGTERM, and SIGKILL if it is still running 10 seconds later. Each of the driver's in-flight runs is finished with `--status-override KILLED`, and a checker's run gets its cleanup. Nothing is parked. `ended` is written, the last line is `{"ok": false, "ticket": …, "stopped": "SIGTERM"}`, and the exit code is 128 plus the signal number. An unexpected exception runs the same sequence and exits 1.
9. **`factory/instance.template.yaml`**: a commented `# effort: {critic: high}` example, with one comment line on what it does.
10. **Suite**: the new `tests/factory/test_drive.py`, and the three listed changes to `test_run_scratch.py`.

## Acceptance results

I ran the GIVEN blocks once, with `TMPDIR` set to this run's scratch directory. They were extracted verbatim from the store's current-truth specs: `openspec/specs/human-resolution/spec.md` lines 13–65 (`t0023-parent.sh`) and `openspec/specs/live-store-guard/spec.md` lines 13–67 (`t0024-inflight.sh`). The six `t0040-*` files came from spec v4 lines 161–298. Each WHEN command was then extracted verbatim from this run's input. Each ran from the worktree on 656c179, through the running-code wrapper, under `bash`, with the same `TMPDIR`. The full log is `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0406-implementer/scratch/acceptance.log`.

| Scenario | Before (base 37848db, from run-0405) | After (656c179, this run) | Result |
|---|---|---|---|
| NEW: intake fixtures follow the same routes as the script | `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=2/2 drive=0/0 differ`, `ready-for-triage script=1/1 drive=0/0 differ` | `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same` | met |
| NEW: each role run records its reply | `none` | `triage=ok spec_writer=ok critic=ok` | met |
| NEW: step lines and status file | `steps=no untagged=0 last=0 status= ignored=0` | `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1` | met |
| NEW: stop, KILLED, resume (amended count) | `stop: exit=2 running=0 run= ready-for-triage in_flight: [] child=gone last=0` / `resumed: exit=2 ready-for-triage calls=` | `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1` / `resumed: exit=0 closed calls=2` | met |
| NEW: marker on the driver, never on its roles, and effort | `unmarked=2 marked=2 ready-for-triage calls=0 effort=0 dispatch=0 inside=2` | `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2` | met |
| NEW (intermediate): intake half of the argv check | one empty line | `critic ok`, `spec_writer ok`, `triage ok` | met |
| REGRESSION: the Workflow scripts still reach their ends | not run (regression check) | `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate` | met |

What the results show:
- **Same route as the script.** `same` means the driver's store records match the intake script's, apart from ids and times. Each `n/n` pair says both sides started one `claude` process per run.
- **Stop.** `running=1` means the stopped run was listed as running while its role process ran. `exit=143` is 128 plus SIGTERM. `run=KILLED` means the run was recorded as killed, and `in_flight: []` means none of its runs were left in flight. `child=gone` means the role process was ended. The resume line shows that a second `factory drive` with no `--phase` picked intake from `ready-for-triage` and finished the route.
- **Marker.** `unmarked=2` and `inside=2` mean the fence refused the driver unmarked, and also refused it marked from inside a run directory. `dispatch=1` means the role process ran without the marker. `effort=1` means the configured `--effort low` reached triage.

The "before" figures were recorded by run-0405 on the base. They match verification.md's "today" figures.

Gates, each run exactly as written from the worktree on 656c179 (`main` is 37848db):
- `git diff --check main...HEAD` exited 0 with no output: the branch has no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `511 passed in 250.36s (0:04:10)` and exited 0. This run also serves as the intermediate check that the suite passes.

Run-0405 checked the interim build refusal by hand, without a test, on a `t0023-parent.sh` store whose T-0001 is `ready-for-planner`. `bin/factory drive T-0001` exited 2, and so did `--phase build`. A checksum of every store file was unchanged. The code is the same here, and I did not repeat that check.

## Tests added and changed

Added: `tests/factory/test_drive.py`, with 15 tests. They are black-box tests through `bin/factory`, with a Python stand-in `claude` first on `PATH`. They cover:
- each intake route of the parity table: approval after one revision, max rounds, two EMPTY-OUTPUTs with the last message kept, and a failed process recorded KILLED with no retry;
- triage REJECT, CLARIFY, NEEDS-HUMAN and unknown;
- stdout that is not JSON, reported by its last stderr line;
- the exact argv, with no marker even when the driver starts marked;
- `--prompt-mode replace`;
- the implementer's `Edit` tool, worktree rule and `--add-dir`. These are tested through `role_argv` in a subprocess, because the suite's own `factory` package name is `tests/factory`;
- a configured effort for one role only;
- the `claude:` record and `reply.json`, and `claude: null` for a reply that is not a JSON object;
- step lines and the status file, a state with nothing to dispatch, and a stop and resume. The stop test asserts that the `running` list is exactly `[run-0001-triage]` while the role runs, which is what the amended scenario now checks too.

Run-0405 saw these tests fail before the change: with `factory/` stashed back to base, 17 failed and 10 passed.

Changed: only the three tests listed under Tests to change, all in `tests/factory/test_run_scratch.py`. Each change follows the Decision that git ignores the status file.
- `test_a_new_store_gitignore_is_the_full_commented_block_once` now expects 4 comment lines, and counts `drive/` once.
- `test_an_existing_store_gitignore_gains_only_the_missing_lines` now expects the list to end `"runs/*/scratch/", "drive/"`.
- `test_an_existing_store_gitignore_without_a_final_newline_keeps_its_last_line` now expects the list to end `"drive/"`.

## Known gaps and uncertainties

- `factory:` markers added: one, at `factory/drive.py:390`, on the interim build-phase refusal that part B replaces.
- No part A test reaches the build-only paths in `run_once`. Those are the `BLOCKED ` run-start refusal and the checker cleanup after a finish or a failure.
- Store calls capture only `sys.stdout` and `sys.stderr`. A CLI command that starts a subprocess without capturing its output would write straight to the driver's stdout and break the line format. I saw none in intake. Part B should watch for this in the build commands, which run git.
- Park reasons and `--text` go to the CLI as single arguments (`--reason=…`, `--text=…`). The scripts pass them through `sh -c` inside double quotes, so the shell expands a `$` or a backtick in a reason there. The driver keeps them verbatim.
- When `config` or `ticket show` fails, the driver prints `{"ok": false, "ticket", "error"}` and exits 1, before it writes a status file. The spec does not say what such a failure returns, so this is my choice.
- A stop does not write `reply.json` or pass `--reply` for a killed process, so that run has no `claude:` key. The spec's stop sequence names only `--status-override KILLED`.
- A second signal during the stop sequence is ignored. The 10-second SIGKILL bound still applies.
- `ruff` is not installed in the worktree's `.venv`, so I did not run it. It is not a gate command here.

## Out-of-scope observations

- The briefing says a change to a command updates the README in the same ticket. The plan assigns that to part C, so this branch leaves the README unchanged.
- The scenario fixture files were written under this run's scratch directory (`TMPDIR=<scratch>/tmp`), not the shared `$TMPDIR`. Other runs' copies of the same fixture names cannot collide with them.
- Protected paths this branch touches, all declared by the sub-ticket: `factory/drive.py`, `factory/cli.py`, `factory/store.py` and `factory/instance.template.yaml`.

## Responses to findings

None. No reviewer or verifier has reviewed this head yet. This run answers the operator's ruling on run-0405's BLOCKED report, as described above.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every part A acceptance command printed its expected output, and both gates passed, all run in this session on 656c179.
ESCALATIONS: none
