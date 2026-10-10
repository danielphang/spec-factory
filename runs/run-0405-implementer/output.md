Sub-ticket: T-0040.1 (T-0040.A, the driver core and the intake phase). Parent spec: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v3.md`
Branch: `factory/T-0040.1`, head `656c179f4a4f4631b8fa61e037c7f871f36cd26d`, base `37848dbb04f29c63d5d684a3b4c033ed41ede13e`

## Blocked: one acceptance criterion contradicts the design

Part A is built, and every other check passes. One NEW criterion cannot pass while the code follows the approved design. The criterion is "A stopped driver ends its role process, records the run as killed and resumes from the stored state", and it expects `running=1`. Its command counts the lines of `drive/T-0001.yaml` that contain `run-0001-triage`. The status file is the driver's live view of itself in the store.

The design writes that run id on two lines of the file while the role runs:
- the `running` list holds `{run, role, ticket, pid}` (design.md A.7; proposal.md Decisions);
- `last` holds the last step line, which is `T-0001 "Fixture": start triage run-0001-triage`, because a started run's step is `start <role> <run id>` (design.md A.7).

So the command prints `running=2`. This is the status file 1 second after the role starts, taken from a manual run:

```
running:
- run: run-0001-triage
  role: triage
  ticket: T-0001
  pid: 66990
last: 'T-0001 "Fixture": start triage run-0001-triage'
ended: null
```

The rest of that scenario's line matches: `exit=143`, `run=KILLED`, `ready-for-triage`, `in_flight: []`, `child=gone` and `last=1`. The resume line matches exactly.

Making the count 1 would mean dropping the run id from the start step line, or not writing `last` at that step. Either one departs from design.md A.7. That is a design change, so I did not make it. A ruling is needed on one of these:
1. Amend the scenario so that it counts the `running` list only. For example, `grep -c '^- run: run-0001-triage'` keeps the expected `running=1`. This is my recommendation: what the check is for (the run appears as running) is met.
2. Change design.md A.7, so that the start step or `last` does not name the run id.

The suite already pins option 1's meaning. `test_a_stopped_driver_kills_its_role_records_the_run_and_resumes` asserts that the `running` list is exactly `[run-0001-triage]` while the role runs.

## What changed

Part A, items 1 to 10 of design.md:

1. **Command** (`factory/cli.py`): a new `drive` subparser takes `TICKET`, `--phase {intake,build}`, `--parallel N` and `--prompt-mode {append,replace}`. `--parallel N` must be at least 1, defaults to 2 and is unused until part B. `--prompt-mode` defaults to `append`. `drive_cmd` dispatches through `main()`, so the instance refusal, the fence and the harness lock apply at start. The fence is the check that refuses an unmarked write while a run is in flight. The harness lock is the check that the running harness revision is the one the instance accepted. After those checks, `factory.drive.drive` sets `FACTORY_DISPATCH=1` in `os.environ`. That variable is the dispatcher marker, which the fence lets through.
2. **Store calls** (`factory/drive.py` `call`, line 46): each call runs `cli.main(argv)` with stdout and stderr captured. It returns the last stdout line that is a JSON object, plus `exit` and `stderr`. It normalises them as the scripts' `clerk()` does. Calls are synchronous, so they run one at a time on the main thread.
3. **Role runner** (`run_role` and `run_once`, lines 160 and 173): these follow the scripts' `runRole` and `runOnce`. The steps are `run start`, then `run compose`, then one `claude` process.
   - The process runs from the run directory, with stdin `/dev/null` and the driver's environment minus `FACTORY_DISPATCH`.
   - `role_argv` (line 83) builds the argv in the design's order, with real absolute paths. Each `Edit` rule's path therefore starts with `//`. The implementer gets `Edit`, its worktree rule and `--add-dir`. `--effort` comes from `effort[role]` in `instance.yaml`.
   - Stdout is written as printed to `<run>/reply.json`.
   - A failed call is a non-zero exit or stdout that is not a JSON object. It goes to `run finish --status-override KILLED --reply`, then a checker's cleanup, then a park with `agent call failed: <role>: <message>`.
   - Otherwise the order is `run finish --reply`, a checker's cleanup, then the script's branches. Those are the `harness-bug` park on a refused finish, a tripwire `parked`, `run last-message` on EMPTY-OUTPUT, and one re-dispatch, after which a second EMPTY-OUTPUT parks.
   - The build-only branches are ported as the scripts have them, but no part A test reaches them. They are a `BLOCKED ` run-start refusal parked verbatim, and the checker cleanup.
4. **`run finish --reply FILE`** (`factory/cli.py` `_claude_record`, line 497): when FILE is a JSON object, it records `claude: {session_id, total_cost_usd, num_turns, usage}` in `meta.yaml`. Otherwise it records `claude: null`. Without `--reply`, nothing changes. `run_finish` is called only through the CLI: by the two Workflow scripts' clerk commands, by the tests, and now by the driver.
5. **Intake routing** (`Driver.intake`, line 239): a branch-for-branch port of `intake.js` from `// --- start`. It covers triage ACCEPT, REJECT, NEEDS-HUMAN, CLARIFY and unknown, then the writer/critic loop with `max_rounds.spec` and `models` from `factory config`. The transitions, `--round` operations, `spec add` calls and park reasons are the same, including `--by workflow`. Park reasons get the script's `"` → `'` replacement.
6. **Phase**: without `--phase`, the stored state selects the phase. Intake states run. A state in neither phase ends with `nothing to dispatch from this state`. **Interim**: `--phase build`, or a stored state that selects build, raises `Refused` before anything is written. The command exits 2 and prints `<T> is <state>: the build phase of factory drive is not built yet; run the build Workflow script`. As the sub-ticket asks, no suite test pins this.
7. **Progress**: the driver prints one flushed line per step, of the form `<ticket id> "<title>": <step>`. The steps are start, finish, transition, park, the critic's approval note and `end: …`. The title is read again after triage ACCEPT. The status file `drive/<ticket>.yaml` is written with `store.write_yaml` at start, at each step and at the end. It has the keys `ticket`, `title`, `phase`, `pid`, `started`, `updated`, `running`, `last` and `ended`. The last stdout line is the script's result object with `"ok": true` added. `STORE_GITIGNORE` (`factory/store.py`) gains a comment line, then `drive/`. Its only caller is `ensure_gitignore`, which `run start` calls.
8. **Stop** (`Driver.stop`, line 338): SIGINT and SIGTERM handlers cancel the routing. Each role process then gets SIGTERM, and SIGKILL after 10 seconds. Each of the driver's runs in flight is finished `--status-override KILLED`, a checker's run gets its cleanup, and nothing is parked. `ended` is written, the last line is `{"ok": false, "ticket": …, "stopped": "SIGTERM"}`, and the exit code is 128 plus the signal number. An unexpected exception runs the same sequence and exits 1.
9. **`factory/instance.template.yaml`**: a commented `# effort: {critic: high}` example, with a comment on what it does.
10. **Suite**: the new `tests/factory/test_drive.py`, and the three listed `test_run_scratch.py` changes.

## Acceptance results

The GIVEN blocks were extracted verbatim from `openspec/specs/human-resolution/spec.md` (`t0023-parent.sh`), `openspec/specs/live-store-guard/spec.md` (`t0024-inflight.sh`) and spec v3 (the six `t0040-*` files). They were run once with `TMPDIR` set to this run's scratch directory. Every command below ran as written, from the worktree, through the running-code wrapper, with the same `TMPDIR`.

| Scenario | Before (base 37848db) | After (656c179) | Expected |
|---|---|---|---|
| NEW: intake fixtures, same routes as the script | `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=5/5 drive=0/0 differ`, `ready-for-triage script=2/2 drive=0/0 differ`, `ready-for-triage script=1/1 drive=0/0 differ` | `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same` | met |
| NEW: each role run records its reply | `none` | `triage=ok spec_writer=ok critic=ok` | met |
| NEW: step lines and status file | `steps=no untagged=0 last=0 status= ignored=0` | `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1` | met |
| NEW: stop, KILLED, resume | `stop: exit=2 running=0 run= ready-for-triage in_flight: [] child=gone last=0` / `resumed: exit=2 ready-for-triage calls=` | `stop: exit=143 running=2 run=KILLED ready-for-triage in_flight: [] child=gone last=1` / `resumed: exit=0 closed calls=2` | **not met**: `running=2` (see Blocked) |
| NEW: marker, never the roles', and effort | `unmarked=2 marked=2 ready-for-triage calls=0 effort=0 dispatch=0 inside=2` | `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2` | met |
| NEW (intermediate): intake half of the argv check | one empty line | `critic ok`, `spec_writer ok`, `triage ok` | met |
| REGRESSION: the Workflow scripts still reach their ends | not run (it is a regression check) | `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate` | met |

The "before" column matches verification.md's "today" figures.

Gates, each exactly as written, from the worktree, on 656c179:
- `git diff --check main...HEAD` exited 0 with no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `511 passed in 246.45s (0:04:06)` and exited 0. This run is also the intermediate check that the suite passes.

I checked the interim build refusal by hand, without a test, on a `t0023-parent.sh` store whose T-0001 is `ready-for-planner`. `bin/factory drive T-0001` exited 2, and so did `--phase build`. A checksum of every store file was unchanged.

## Tests added and changed

Added: `tests/factory/test_drive.py`, 15 tests, black-box through `bin/factory`. A Python stand-in `claude` sits first on `PATH`. The tests cover:
- each intake route of the parity table: approve after one revision, max rounds, two EMPTY-OUTPUTs with the last message kept, and a failed process recorded KILLED with no retry;
- triage REJECT, CLARIFY, NEEDS-HUMAN and unknown;
- stdout that is not JSON, named by its last stderr line;
- the exact argv, with no marker even when the driver starts marked;
- `--prompt-mode replace`;
- the implementer's `Edit` tool, worktree rule and `--add-dir`, through `role_argv` in a subprocess, because the suite's `factory` package name is `tests/factory`;
- a configured effort for one role only;
- the `claude:` record and `reply.json`, and `claude: null` for a reply that is not a JSON object;
- step lines and the status file, a state with nothing to dispatch, and a stop and resume.

The tests failed before the change: with `factory/` stashed back to base, the drive tests and the three changed scratch tests failed (17 failed, 10 passed).

Changed: only the three listed under Tests to change, in `tests/factory/test_run_scratch.py`:
- `test_a_new_store_gitignore_is_the_full_commented_block_once` now expects 4 comment lines and counts `drive/` once;
- `test_an_existing_store_gitignore_gains_only_the_missing_lines` now expects the list to end `"runs/*/scratch/", "drive/"`;
- `test_an_existing_store_gitignore_without_a_final_newline_keeps_its_last_line` now expects the list to end `"drive/"`.

Each change follows the Decision that git ignores the status file.

## Known gaps and uncertainties

- The `running=1` conflict described under Blocked.
- `factory:` markers added: one, at `factory/drive.py:390`, on the interim build-phase refusal that part B replaces.
- No part A test reaches the build-only paths in `run_once`. Those are the `BLOCKED ` run-start refusal and the checker cleanup on finish or failure.
- Store calls capture `sys.stdout` and `sys.stderr` only. A subprocess that a CLI command starts without capturing its output would write straight to the driver's stdout and break the line format. I saw none in intake, and part B should watch for it in the git-heavy build commands.
- Park reasons and `--text` go to the CLI as single arguments (`--reason=…`, `--text=…`). The scripts pass them through `sh -c` inside double quotes, so a reason that contains `$` or a backtick is expanded there and kept verbatim here.
- When `config` or `ticket show` fails, the driver prints `{"ok": false, "ticket", "error"}` and exits 1, before it writes a status file. The spec does not say what such a failure should return, so I chose this.
- A stop does not write `reply.json` or pass `--reply` for a killed process, so that run's `claude:` key is absent. The spec's stop sequence names only `--status-override KILLED`.
- A second signal during the stop sequence is ignored. The 10-second SIGKILL bound still applies.
- `ruff` is not installed in the worktree's `.venv`, so it was not run. It is not a gate command here.

## Out-of-scope observations

- The parent spec's README rule ("A change to a command … updates it in the same ticket") is assigned to part C by the plan, so this branch leaves the README unchanged.
- I wrote the scenario fixture files under this run's scratch directory (`TMPDIR=<scratch>/tmp`), not the shared `$TMPDIR`. Another run's copies of the same fixture names cannot collide with them.

STATUS: BLOCKED
CONFIDENCE: high. Every other criterion and both gates passed on 656c179, and the one failure is reproduced and traced to the two design lines that cause it.
ESCALATIONS:
- The NEW criterion "A stopped driver ends its role process, records the run as killed and resumes from the stored state" expects `running=1`. With the approved design it prints `running=2`. Design.md A.7 makes `last` the start step line `… start triage run-0001-triage`, and the `running` list also names that run, so the command's `grep -c 'run-0001-triage'` counts both lines. A ruling is needed. I recommend amending the scenario to count only the `running` list, for example `grep -c '^- run: run-0001-triage'`. The alternative is to change A.7 so that `last` or the start step leaves out the run id. The implementation is complete at 656c179 and needs no further change under the recommended amendment.
