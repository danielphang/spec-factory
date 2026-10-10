Sub-ticket: T-0040.2 (T-0040.B, the build phase). Parent spec: `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0040/v4.md`
Branch: `factory/T-0040.2`, head `4bfedc74920c11f0b8ccdde14ec02d6b04a74ab8`, base `2ad4d8c5288474b823d4571ba03de82a706eabdf`
Commit: 4bfedc74920c11f0b8ccdde14ec02d6b04a74ab8

## What changed

`factory drive TICKET` can now take an approved ticket through the build, so the operator no longer needs the build Workflow script and its clerk for that half. The build is the half of the pipeline that splits an approved spec into sub-tickets and implements, checks and merges each one. Before this change the driver refused any ticket in a build state. Part A's interim refusal is gone, and so is its `factory:` marker.

All changes are in `factory/drive.py`, plus one new test file. They follow part B, items 1 to 4 of design.md.

1. **Build routing** (`Driver.build` and `Driver.build_one`). This is a branch-for-branch port of `factory/workflows/build.js` from `// --- start`, with its `buildOne`. It issues the same store commands with the same arguments, and makes the same transitions with `--by workflow`. Its park reasons are the same.
   - Plan phase: `plan whole-spec`, either the planner-skipped step or the planner run, then `spec tasks`, `plan add` and `subticket add`, then `-> planned`.
   - Build phase: the `ready-implementers` loop. That includes the one-time `subticket add` for a parent planned with no sub-tickets, the park when a human closed a sub-ticket, `resumable` sub-tickets, the `remaining` result, then `parent-check`.
   - Close phase: `parent-check` again with its `reuse`, the parent-close verifier, `archive`, then `-> closed`.
   - `build_one`: the implementer, then `ticket head` with `merge_refused`, then `-> checks-in-flight` with `pr:init`. It then picks which checkers run: both after an implementer run, otherwise those `results show` lists as missing, with `ci` meaning the verifier. Next come `results record` with the head (and `--killed` for a KILLED run), then `ticket join` and its five decisions: merge, revise, conflict, wait and park. After a merge decision it runs `merge`. A `BLOCKED ` merge refusal is parked verbatim. Any other refusal asks the join a second time.
   - `run_once` now also returns the run's `outputPath`, which `results record --output` needs.
2. **Concurrency.** A head's two checkers, the reviewer and the verifier, run through `asyncio.gather` inside a small helper, `_all`. Both finish and record their results before the join. If either checker ends with no result, the sub-ticket's pass ends only after both have returned, as `parallel()` does in the script. The sub-tickets of one `ready-implementers` answer run as tasks behind an `asyncio.Semaphore(--parallel)`, which defaults to 2. The driver waits for all of them, then asks `ready-implementers` again.
   - Why `_all` and not a bare `gather`: if one awaitable raises, `_all` cancels the others and waits for them before re-raising. Without that, a sibling task could still be routing while the stop sequence finishes its run as KILLED, and its later `run finish` would be refused and would park the ticket. That would break the rule that a stop parks nothing. Rejected: `asyncio.TaskGroup`. It cancels the same way, but it wraps the error in an `ExceptionGroup`, which hides the real message in the driver's `error` result.
3. **Progress.** `step()` now names each sub-ticket with that sub-ticket's own title, which `build_one` reads from `ticket show --json`. `transition()` gains an optional `ticket` argument, so a sub-ticket's transitions print under the sub-ticket. Before this change it always moved the parent. `step()` also joins a multi-line step text onto one line. A park reason built from stderr ends in a newline, and in the build route this printed a blank, untagged stdout line, so "Build step lines name the sub-ticket they concern" printed `untagged=1` before this fix. The reason stored with the ticket is unchanged, so the records still match the script's. The status file's `running` list already held every role run in flight with its ticket. It now holds both checkers of each sub-ticket in flight.
4. **Phase.** The driver now picks build for `--phase build`, or, without `--phase`, for a stored state of `ready-for-planner`, `planned` or `ready-for-parent-verify`. The phase it picks is written to the status file.

Callers (coding standard rule 2): `step`, `transition` and `run_once` are called only inside `factory/drive.py`. `factory/cli.py` calls only `drive.drive`. A's intake calls keep working unchanged: `transition(to, round_op)` still defaults to the parent.

## Acceptance results

I extracted the GIVEN blocks verbatim and ran them once, with `TMPDIR` set to this run's scratch directory:
- `t0023-*` from `openspec/specs/human-resolution/spec.md`;
- `t0024-*` from `openspec/specs/live-store-guard/spec.md`;
- the six `t0040-*` files from `openspec/changes/T-0040/specs/build-dispatch/spec.md`, whose block matches v4's exactly by `diff`.

Every WHEN command below was copied from that change spec and ran unchanged, from the worktree, under bash, through the running-code wrapper, with the same `TMPDIR`. The full "after" log is `scratch/acceptance-after.txt`.

| Scenario | Kind | Before (2ad4d8c) | After (4bfedc7) |
|---|---|---|---|
| The driver takes the build fixtures through the same routes as the build script | NEW | `ready-for-planner script=4/4 drive=0/0 differ`, `ready-for-planner script=6/6 drive=0/0 differ`, `ready-for-planner script=4/4 drive=0/0 differ`, `ready-for-planner script=1/1 drive=0/0 differ` | `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same` |
| Each role runs as one claude process with its prompt, model and tool limits | NEW | `critic ok`, `spec_writer ok`, `triage ok`, then a blank line | `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok` |
| The checkers run at once, and sub-tickets up to the parallel limit | NEW | `parallel=1: calls=0 max=0 checks-in-flight checks-in-flight`, `parallel=default: calls=0 max=0 checks-in-flight checks-in-flight` | `parallel=1: calls=4 max=2 parked parked`, `parallel=default: calls=4 max=4 parked parked` |
| Build step lines name the sub-ticket they concern | NEW | `untagged=0 sub=no last=0` | `untagged=0 sub=yes last=1` |
| The driver takes the intake fixtures through the same routes as the intake script | REGRESSION | not run | `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same` |
| Each role run records its process's reply | REGRESSION | not run | `triage=ok spec_writer=ok critic=ok` |
| Every intake step line names its ticket and title, and the status file shows the end | REGRESSION | not run | `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1` |
| A stopped driver ends its role process, records the run as killed and resumes from the stored state | REGRESSION | not run | `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1`, `resumed: exit=0 closed calls=2` |
| The driver marks its own store calls, never its roles', and passes a configured effort | REGRESSION | not run | `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2` |
| The Workflow scripts still take both fixtures to the end of their routes | REGRESSION | not run | `T-0001.1 merged T-0001 parked`, `T-0001 awaiting-spec-gate` |

Every "after" line is exactly what the sub-ticket's Acceptance and the parent's scenarios expect. The "before" lines match the "today" figures in verification.md. The one exception is the claude-process check, whose intake half A had already made pass.

Gates. I ran each one exactly as written, from the worktree, on 4bfedc7:
- `git diff --check main...HEAD` exited 0 with no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `520 passed in 453.62s (0:07:33)` and exited 0. That is A's 511 plus the 9 new tests. This run is also the intermediate check that the suite passes with `tests/factory/test_drive_build.py`.

`ruff check` with default rules found nothing in the two changed files. `ruff` is not in this repo's environment, so I ran a copy already installed on the machine. It is not a gate command here.

## Tests added and changed

Added: `tests/factory/test_drive_build.py`, 9 tests. Each test drives `bin/factory` as a black box on part A's `Store`, which the file imports from `test_drive.py` as the sub-ticket allows. The store is taken past the spec gate, and a scratch git repository serves as the target. The file has its own Python stand-in `claude`, which extends A's in two ways:
- a written output carries a `Commit:` line with the run's head, and a verifier's output also carries `Gate suite: PASS`, so that `results record` accepts the checkers' outputs;
- each call logs its start and end time, so a test can count the role processes that ran at once.

The tests:
- the four build routes of the parity table: merge then the parent-close verifier, review rounds to the limit, two empty reviews, and a BLOCKED implementer reached with no `--phase`;
- a failed reviewer, after which the verifier still finishes and records its result before the sub-ticket parks (the gather semantics);
- the implementer's `Edit` tool, its worktree `Edit` rule and `--add-dir` in a real build, and the checkers' rules: no `Edit` tool, and `Edit` rules on their own run only;
- the `--parallel` bound: at most 2 role processes at once under `--parallel 1`, and 4 at the default;
- step lines that name `T-0001.1 "One"` and `T-0001.2 "Two"`, and a status file whose `running` list shows all four checker runs with their sub-tickets;
- a SIGTERM while both checkers run: both runs are recorded KILLED, the sub-ticket stays `checks-in-flight` and unparked, and a re-run with no `--phase` re-runs both checkers and merges.

I wrote the driver code before these tests, not after, so the order of process step 3 was not kept. To check the tests still discriminate, I swapped base `factory/drive.py` back in. The first 8 tests all failed (`8 failed`), and with the new code they all pass. I added the stop test after that check and did not re-run it against base. On base, the driver refuses every build state, so it cannot pass there.

Changed: none. No existing test file was touched.

## Known gaps and uncertainties

- `factory:` markers added: none. One was removed: A's interim build refusal at the old `factory/drive.py:390`.
- No test reaches `_all`'s path for a raised exception, where it cancels the sibling tasks. Only outer cancellation (the stop test) and normal completion are exercised.
- These branches of the port are untested in the suite and were not reached by the acceptance fixtures: the planner route (`ESCALATE`, unknown status, `spec tasks`, `plan add` and `subticket add` refusals), the one-time recorded-plan `subticket add`, the closed-sub-ticket park, `merge_refused` and conflict runs, a `BLOCKED ` merge refusal, a merge refusal that asks the join again, `reuse` at parent close, and `archive` success leading to `closed`. Each is a line-for-line port of the script, and I read each against `build.js`, but none has run.
- Two small departures from the script, where the script would misbehave:
  - When `ticket join` succeeds with no `reason`, the driver parks with an empty reason. In the script, `park()` would throw on `undefined.replace`.
  - The `join:` step line prints an empty reason in place of `undefined`.
  Neither path is reachable with the current `ticket join`, which always returns a reason with each decision.
- `step()` now joins a multi-line step text onto one line. This also changes part A's intake step lines when a park reason carries stderr's trailing newline. No intake scenario or test depends on the old blank line.
- A store call captures `sys.stdout` and `sys.stderr` only. `gitops.head_contains` runs `git merge-base --is-ancestor` without capturing, so a git error there would reach the driver's stderr, not its stdout. Stdout's line format is not at risk. I saw no such output in any run.
- The stand-in role processes return almost at once, so the bound under `--parallel` is tested only with role processes that sleep. Real concurrent `claude -p` processes are untested, as the spec's Risk section says (Operator step 2).

## Out-of-scope observations

- The README is unchanged. The parent assigns the documents, including the README's "Starting a run" and "Built" entries, to part C.
- The fixture files the scenarios write live under this run's scratch directory (`TMPDIR=<scratch>/tmp`), so they cannot collide with another run's copies in the shared `$TMPDIR`.

Protected paths touched: `factory/drive.py`, under `factory/**`. The sub-ticket declares it.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW and REGRESSION scenario printed exactly its expected lines on 4bfedc7, and both gates passed. Several rare build branches are ported but have never run (Known gaps).
ESCALATIONS: none
