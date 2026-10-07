Sub-ticket: T-0032.1 (branch `factory/T-0032.1`, head `679dccc`, base `97becfd`; worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0032.1`)

## Blocked: one existing test contradicts part B.2, and the spec lists no test to change

The change is built and committed, and all 14 acceptance scenarios print what the spec says. The test gate fails on one existing test. That test was added after the spec was written, and it asserts the opposite of part B.2.

Part B.2 says the code reviewer's input (the `input.md` the harness composes for that run) no longer lists the gate commands. The gate commands are the checks a change must pass before it merges. The input now says the verifier runs them. `tests/factory/test_gate_paths.py:121-126` (`test_a_diff_that_touches_a_scoped_command_s_paths_runs_it`) composes a **reviewer** input and asserts that its gate commands are listed there. The test came from commit `0e99fa7` (T-0028.1, 2026-10-04 16:50). The spec's evidence was taken on `a69aaf4` (16:37), where this file did not exist (`git cat-file -e a69aaf4:tests/factory/test_gate_paths.py` fails). So the spec's "Tests to change: none" and its "310 passed" were true when it was written, but they are not true on this base. My role forbids changing a test the spec does not list, so I stopped there.

The ruling needed is in ESCALATIONS. Recommended: list that one test under "Tests to change" and change its `t.checker("reviewer")` to `t.checker()`. `t.checker()` composes a verifier input. The test then checks the same behaviour, that a scoped command whose paths the diff touches is listed to run, on the role that still receives the commands. With that ruling, the fix is one line and one gate run.

## What changed

**A. Every role is told to wait for its own commands.** The shared preamble is the rule text every role reads first. It gains one RUNNING CODE bullet: run every command in the foreground, and never end the turn while one is still running, because the final message ends the run. The bullet sits after the "check command your briefing, ticket or spec gives you." bullet. All three copies stay byte-identical: the `docs/design.md` block, `docs/prompts/00-preamble.md` and `factory/prompts/preamble.md`.

**B. The code reviewer judges the diff.**
- B.1: the reviewer prompt gains a WHAT YOU RUN section before CHECK, IN THIS ORDER, in all three copies. The reviewer reads the diff. It does not run the test suite or the gate commands, because the verifier runs them on the same head. A narrow command that confirms one finding is allowed. No existing line changed, and the run copy keeps its "After round 2" fill.
- B.2: in `factory/compose.py`, the reviewer's "Where you work" paragraph keeps the worktree and branch sentence and the no-remote sentence. Its gate-commands sentence is replaced with "The verifier runs the gate commands on this head; you do not run them." The implementer's and the verifier's paragraphs are unchanged. The reviewer also no longer gets the "SKIPPED by the harness" lines. The spec did not name these lines, because they arrived with T-0028 after it was written. See Known gaps.

**C. A run with no output is EMPTY-OUTPUT.**
- C.1: `run finish` records a run with a missing or blank `output.md`, and no override, as `EMPTY-OUTPUT`, logged as `run.finished`. Before this change, it recorded `KILLED`. `--status-override KILLED` is unchanged: it still records `KILLED` and logs `run.killed`.
- C.2: the new command `factory run last-message RUN --text=T` writes `runs/<RUN>/last-message.md` (T plus a newline), but only when the run's status is `EMPTY-OUTPUT`. Otherwise it exits 2 and writes nothing. The command is not on the read-only list, so the live-store fence treats it as a write. The fence is the guard that refuses unmarked writes to a store while a run is in flight.
- C.3: in both workflow scripts (`build.js` and `intake.js`), today's `runRole` body is now `runOnce`. `runOnce` always calls a plain `run finish`; the scripts no longer send a KILLED override for an empty return. When `run finish` returns `EMPTY-OUTPUT` and the agent returned non-blank text, the clerk keeps the text with `run last-message`. The text is the last 4000 characters, shell single-quoted, and a failure of this call is ignored. The clerk is the low-effort agent that runs one store command for the script. The new `runRole` runs `runOnce` and, on `EMPTY-OUTPUT`, runs it once more. A second `EMPTY-OUTPUT` parks the ticket as `EMPTY-OUTPUT from <role>`, with both run ids as outputs. The path for a thrown agent call is unchanged. In `build.js`, the `budget kill: implementer` park is deleted.
- C.4: new test file `tests/factory/test_empty_output.py` (6 tests).

**D. Documents.**
- `docs/design.md`: "a second EMPTY-OUTPUT in a row" joins the park reasons. A new rule bullet follows them. The resolution bullet now covers a ticket parked on a second EMPTY-OUTPUT. The routing table gains two `Any role | EMPTY-OUTPUT` rows.
- `dev/build-harness.spec.md`: `run finish` now names `EMPTY-OUTPUT`, and `run last-message` is listed. The `runRole` step, I.5 and item 49 describe the EMPTY-OUTPUT route. No line says "KILLED condition" or "KILLED seam".
- `README.md`: the budget park becomes the empty-output park, in the text and in the diagram edge. The Unstick row's `--redispatch` gloss is extended. A new Built bullet, **Empty output.**, is added. The status date is now 2026-10-06.
- `docs/changelog.md`: new entry 57, "After issue #41 (2026-10-04), …".

Callers of the changed functions, found by grep: `runRole` in `build.js` (planner :231, implementer :151, checkers :182, parent-close verifier :289) and in `intake.js` (triage :150, spec writer :164, critic :178). Each now gets one re-dispatch on an empty output, as the spec requires for every role. `compose.compose` has one caller, `run_compose` (`factory/cli.py:325`). `run_finish` is called only through the CLI. The fix sits in `run finish` because the spec decides `EMPTY-OUTPUT` there, in one place.

## Acceptance results

Every command was run from the worktree with a throwaway HOME and with `TMPDIR` set to this run's scratch directory. The fixtures for the GIVEN blocks were extracted verbatim from current truth and from the pinned spec. They are `t0023-parent.sh`, `t0023-wf.mjs`, `t0022-sib.sh`, `t0022-build.mjs`, `t0029-prompt.sh`, `t0032-checks.sh` and `t0032-build.mjs`. The "Before" column is the output on base `97becfd`, and each one matches the "fails today" text in verification.md. The "After" column is the output on `679dccc`, and each one matches its THEN.

| # | Scenario | Label | Before | After |
|---|---|---|---|---|
| 1 | Reviewer ends its turn waiting: re-dispatched once, then parks | NEW | `park T-0001.1: budget kill: reviewer` / `reviewer: KILLED ` / `verifier: VERIFIED ` / `kept=0 "rows": {"ci": "PASS", "verifier": "VERIFIED", "reviewer": "KILLED"}` | `park T-0001.1: EMPTY-OUTPUT from reviewer` / `reviewer: EMPTY-OUTPUT EMPTY-OUTPUT ` / `verifier: VERIFIED ` / `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` |
| 2 | One empty reviewer run, then a real one | NEW | `park T-0001.1: budget kill: reviewer` / `reviewer: KILLED ` | `park T-0001.1: SPEC-DEFECT from verifier` / `reviewer: EMPTY-OUTPUT APPROVE ` |
| 3 | Implementer returns nothing twice | NEW | `park T-0001.2: budget kill: implementer` / `implementer: KILLED ` | `park T-0001.2: EMPTY-OUTPUT from implementer` / `implementer: EMPTY-OUTPUT EMPTY-OUTPUT ` |
| 4 | Intake role empty twice | NEW | `start: triage` / `park: harness-bug: unknown STATUS EMPTY-OUTPUT from triage` | `start: triage` / `start: triage` / `park: EMPTY-OUTPUT from triage` |
| 5 | Reviewer that writes its output runs once | REGRESSION | — | `park T-0001.1: SPEC-DEFECT from verifier` / `reviewer: APPROVE ` |
| 6 | Preamble copies carry the wait rule, identical | NEW | `fg=0 end=0` ×3 / `verbatim` | `fg=1 end=1` ×3 / `verbatim` |
| 7 | Run prompts: wait rule for all three, judge rule for the reviewer only | NEW | `implementer fg=0 judge=0` / `reviewer fg=0 judge=0` / `verifier fg=0 judge=0` | `implementer fg=1 judge=0` / `reviewer fg=1 judge=1` / `verifier fg=1 judge=0` |
| 8 | Reviewer copies carry the rule, no line removed, verifier unchanged | NEW | `judge=0 narrow=0` ×3 / `copy=SAME fill=unchanged removed=0 verifier_changed=0` | `judge=1 narrow=1` ×3 / `copy=SAME fill=unchanged removed=0 verifier_changed=0` |
| 9 | Reviewer input no longer lists the gate commands | NEW | `reviewer gates=1 told=0` / `verifier gates=1 told=0` / `implementer gates=1 told=0` | `reviewer gates=0 told=1` / `verifier gates=1 told=0` / `implementer gates=1 told=0` |
| 10 | Design doc states the rule, rows and park | NEW | `rule=0 rows=0 parks=0 kill=0` | `rule=1 rows=2 parks=1 kill=1` |
| 11 | Build spec: EMPTY-OUTPUT, no KILLED condition | NEW | `stale=3 empty=0 note=0` | `stale=0 empty=1 note=1` |
| 12 | README drops the budget park | NEW | `budget=2 built=0 unstick=0` | `budget=0 built=1 unstick=1` |
| 13 | Changelog records issue 41, no gap | NEW | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `5` |
| 14 | No whitespace errors | REGRESSION | — | `exit=0` |

Gate commands, each run exactly as written, from the worktree, on `679dccc`:
- `(export HOME=…; git diff --check main...HEAD)` exited 0: the change adds no whitespace errors.
- `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `1 failed, 359 passed in 225.79s`. The only failure is `test_gate_paths.py::test_a_diff_that_touches_a_scoped_command_s_paths_runs_it`, at `assert UNSCOPED in line and "exit 7" in line`, because the reviewer's line now reads "The verifier runs the gate commands on this head; you do not run them." The same test on base `97becfd`, in a detached scratch worktree since removed, printed `1 passed`. So the failure is caused by this change, as part B.2 requires, and not by the environment.

## Tests added/changed

- Added `tests/factory/test_empty_output.py`, a new file. It covers four cases. `run finish` with no output, an empty output or a whitespace-only output gives `EMPTY-OUTPUT` in its JSON and in `meta.yaml`, and logs `run.finished`, never `run.killed`. `--status-override KILLED` still gives `KILLED` and `run.killed`. `run last-message` writes the file for an `EMPTY-OUTPUT` run and prints the spec's JSON. `run last-message` refuses with exit 2, and writes nothing, for a run that finished with an output. Before the change, 5 of the 6 tests failed. The override test passed, as it should, because that behaviour does not change. After the change, all 6 pass.
- No existing test was changed. One existing test now fails; see the blocker above.

## Known gaps and uncertainties

- **The reviewer's SKIPPED lines.** T-0028 added "SKIPPED by the harness for this diff, do not run: `<cmd>`" lines for each gate command whose paths the diff does not touch. Current truth (`openspec/specs/gate-commands/spec.md`, first requirement) says a reviewer or verifier run "MUST list that command apart from the commands to run". B.2's requirement says the reviewer's input "MUST NOT list the gate commands". I dropped the SKIPPED lines for the reviewer, because listing commands it should not run, to a role that runs none, contradicts B.2. The skip is still decided at the reviewer's run start and recorded in its `meta.yaml` (`gate_skipped`), as before. This choice is part of the ruling below. If the gate-commands requirement should change to match, the pinned spec needs a MODIFIED delta for `gate-commands`. Otherwise the requirement still says "reviewer or verifier" when this change archives.
- The `results record … --killed` suffix in `build.js:184` is now unreachable from the workflow. `run finish` without an override can no longer return `KILLED`. The spec keeps `--killed` for rows a human records by hand and does not ask to remove the suffix, so it stays.
- `factory:` markers added: none.
- The clerk receives the last message as one shell single-quoted word of up to 4000 characters, possibly with newlines, inside its prompt. The scenarios pass this through a real `sh -c`. A real clerk agent has not yet relayed a long multi-line argument. If one mangles it, the call fails and is ignored, as specified, and only the kept message is lost.
- Changelog entry 57 is one long line, like entries 54–56. Its wording is mine, written to the five terms scenario 13 checks.

## Out-of-scope observations

- `dev/build-harness.spec.md` item 59 ("Wall-clock kill … `time_budget_s: 1800` → `status: KILLED`") and item 83 (`--redispatch --budget`) describe a budget mechanism that the spec's evidence shows is not built (`grep -rn "time_budget\|budget_usd" factory/*.py` prints nothing). I rewrote I.5 as the spec asks, and it no longer claims a wall-clock kill. I left items 59 and 83 alone.
- `tests/factory/test_shepherd.py` and `test_killed_checker.py` still model the old killed path through the CLI. They pass, as the spec predicted. The comment in the current-truth fixture `t0022-build.mjs` still says "the workflow records as a killed run". Both were noted in the spec as observed, not changed.
- Overlap noted by the spec: T-0030 also edits `factory/prompts/reviewer.md`, the design doc's §6 block and `factory/compose.py`. Whichever merges second will hit a text conflict in the reviewer's "Where you work" paragraph.

Protected paths this change touches, all declared in the parent's Risk list:
- harness: `factory/cli.py`, `factory/compose.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`, `factory/prompts/preamble.md`, `factory/prompts/reviewer.md`;
- generated: `docs/prompts/00-preamble.md`, `docs/prompts/06-code-reviewer.md`.

STATUS: BLOCKED
CONFIDENCE: high. All 14 scenarios and 359 of 360 suite tests pass on the commit, and the one failure is shown to be the spec's B.2 against a test added after the spec was written.
ESCALATIONS:
- The test gate cannot pass as the spec is written. Part B.2 removes the gate commands from the code reviewer's input. The existing test `tests/factory/test_gate_paths.py::test_a_diff_that_touches_a_scoped_command_s_paths_runs_it` (lines 121-126) asserts that the reviewer's input lists them. The test arrived with T-0028 (`0e99fa7`) after this spec's evidence was taken on `a69aaf4`, so the spec's "Tests to change: none" is out of date. Decide one of these. (1) Recommended: rule that this test is a test to change, and that its `t.checker("reviewer")` becomes `t.checker()` (the verifier). The test keeps its intent on the role that still receives the commands, and the next implementer round changes that one line and re-runs the gate. (2) Drop B.2, so the reviewer keeps receiving the gate commands. The prompt's WHAT YOU RUN section would then contradict its own input, which is the cause of the incident.
- With the same ruling, confirm that the reviewer also gets no "SKIPPED by the harness" lines, as built on this branch. That narrows the current-truth `gate-commands` requirement ("When a reviewer or verifier run starts … MUST list that command apart from the commands to run") to the verifier only. If you confirm it, the pinned spec should carry a MODIFIED `gate-commands` requirement so current truth matches when this change archives. If you do not, the next round restores those lines for the reviewer.
