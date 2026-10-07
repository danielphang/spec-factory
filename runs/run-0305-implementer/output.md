Sub-ticket: T-0032.1 (branch `factory/T-0032.1`, head `c01e7c2`, base `97becfd`; worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0032.1`)

This round applies the operator's ruling of 2026-10-06 on the BLOCKED round (run-0304). The branch now passes every acceptance scenario and both gate commands: `360 passed`.

## What changed

The first commit, `679dccc`, holds the whole change as the spec describes it. The second commit, `c01e7c2`, applies the ruling and changes 2 files.

**A. Every role is told to wait for its own commands.** The shared preamble is the rule text every role reads first. It gains one bullet in its RUNNING CODE section: run every command in the foreground, and never end the turn while one is still running, because the final message ends the run. The bullet follows the one ending "check command your briefing, ticket or spec gives you.". All three copies stay byte-identical: the `docs/design.md` block, `docs/prompts/00-preamble.md` and `factory/prompts/preamble.md`.

**B. The code reviewer judges the diff.**
- B.1: the reviewer prompt gains a WHAT YOU RUN section before CHECK, IN THIS ORDER, in all three copies. The reviewer reads the diff. It does not run the test suite or the gate commands, because the verifier runs them on the same head. A narrow command that confirms one finding is allowed. No existing line changed, and the run copy keeps its "After round 2" fill.
- B.2: `factory/compose.py` builds each run's input. The reviewer's "Where you work" paragraph keeps the worktree and branch sentence and the no-remote sentence. Its gate-commands sentence is replaced with "The verifier runs the gate commands on this head; you do not run them." The implementer's and the verifier's paragraphs are unchanged. As the ruling directs (item 3), the reviewer's input still lists the "SKIPPED by the harness for this diff, do not run: `<cmd>`: <reason>" lines. T-0028 added these lines, one for each gate command whose paths the diff does not touch. They come after the new sentence and are worded exactly as before (`c01e7c2`).

**C. A run with no output is EMPTY-OUTPUT.**
- C.1: `run finish` records a run with a missing or blank `output.md`, and no override, as `EMPTY-OUTPUT`, logged as `run.finished`. Before this change, it recorded `KILLED`. `--status-override KILLED` is unchanged: it still records `KILLED` and logs `run.killed`.
- C.2: the new command `factory run last-message RUN --text=T` writes `runs/<RUN>/last-message.md`, which holds T plus a newline. It does this only when the run's status is `EMPTY-OUTPUT`. Otherwise it exits 2 and writes nothing. The command is not on the read-only list, so the live-store fence treats it as a write. The fence is the guard that refuses unmarked writes to a store while a run is in flight.
- C.3: the change is the same in both workflow scripts, `build.js` and `intake.js`. Today's `runRole` body is now `runOnce`. `runOnce` always calls a plain `run finish`, and the scripts no longer send a KILLED override for an empty return. The clerk is the low-effort agent that runs one store command for the script. When `run finish` returns `EMPTY-OUTPUT` and the agent returned non-blank text, the clerk keeps that text with `run last-message`. It keeps the last 4000 characters, shell single-quoted. A failure of this call is ignored. The new `runRole` runs `runOnce` and, on `EMPTY-OUTPUT`, runs it once more. A second `EMPTY-OUTPUT` parks the ticket as `EMPTY-OUTPUT from <role>`, with both run ids as outputs. The path for a thrown agent call is unchanged. In `build.js`, the `budget kill: implementer` park is deleted.
- C.4: new test file `tests/factory/test_empty_output.py`, with 6 tests.

**D. Documents.**
- `docs/design.md`: "a second EMPTY-OUTPUT in a row" joins the park reasons, and a new rule bullet follows them. The resolution bullet now covers a ticket parked on a second EMPTY-OUTPUT. The routing table gains two `Any role | EMPTY-OUTPUT` rows.
- `dev/build-harness.spec.md`: `run finish` now names `EMPTY-OUTPUT`, and `run last-message` is listed. The `runRole` step, I.5 and item 49 describe the EMPTY-OUTPUT route. No line says "KILLED condition" or "KILLED seam".
- `README.md`: the budget park becomes the empty-output park, in the text and in the diagram edge. The Unstick row's `--redispatch` gloss is extended. A new Built bullet, **Empty output.**, is added. The status date is now 2026-10-06.
- `docs/changelog.md`: new entry 57, "After issue #41 (2026-10-04), …".

None of these documents says the reviewer loses its SKIPPED lines. A grep of the branch's diff for "skip" finds only the changed I.5 text, which is about the user skipping an agent. So the restored lines need no document change. The current-truth `gate-commands` requirement says a reviewer or verifier run "MUST list that command apart from the commands to run". It holds again, so the pinned spec needs no MODIFIED delta.

Callers of the changed functions, found by grep in the first round, are unchanged by this round. `runRole` is called in `build.js` (planner, implementer, both checkers, parent-close verifier) and in `intake.js` (triage, spec writer, critic). `compose.compose` has one caller, `run_compose` in `factory/cli.py`.

## Acceptance results

I ran every command from the worktree, with a throwaway HOME and with `TMPDIR` set to this run's scratch directory. The GIVEN fixtures were extracted verbatim from current truth and from the pinned spec: `t0023-parent.sh`, `t0023-wf.mjs`, `t0022-sib.sh`, `t0022-build.mjs`, `t0029-prompt.sh`, `t0032-checks.sh` and `t0032-build.mjs`. The WHEN commands were extracted verbatim from `specs/T-0032/v1.md`, all 14 of them. The "Before" column is run-0304's output on base `97becfd`. Each value there matches the "fails today" text in verification.md. The "After" column is this round's output on the committed head `c01e7c2`, and each value matches its THEN exactly.

| # | Scenario | Label | Before (`97becfd`) | After (`c01e7c2`) |
|---|---|---|---|---|
| 1 | Reviewer ends its turn waiting: re-dispatched once, then parks | NEW | `park T-0001.1: budget kill: reviewer` / `reviewer: KILLED ` / `verifier: VERIFIED ` / `kept=0 "rows": {"ci": "PASS", "verifier": "VERIFIED", "reviewer": "KILLED"}` | `park T-0001.1: EMPTY-OUTPUT from reviewer` / `reviewer: EMPTY-OUTPUT EMPTY-OUTPUT ` / `verifier: VERIFIED ` / `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` |
| 2 | One empty reviewer run, then a real one | NEW | `park T-0001.1: budget kill: reviewer` / `reviewer: KILLED ` | `park T-0001.1: SPEC-DEFECT from verifier` / `reviewer: EMPTY-OUTPUT APPROVE ` |
| 3 | Implementer returns nothing twice | NEW | `park T-0001.2: budget kill: implementer` / `implementer: KILLED ` | `park T-0001.2: EMPTY-OUTPUT from implementer` / `implementer: EMPTY-OUTPUT EMPTY-OUTPUT ` |
| 4 | Intake role empty twice | NEW | `start: triage` / `park: harness-bug: unknown STATUS EMPTY-OUTPUT from triage` | `start: triage` / `start: triage` / `park: EMPTY-OUTPUT from triage` |
| 5 | Reviewer that writes its output runs once | REGRESSION | n/a | `park T-0001.1: SPEC-DEFECT from verifier` / `reviewer: APPROVE ` |
| 6 | Preamble copies carry the wait rule, identical | NEW | `fg=0 end=0` ×3 / `verbatim` | `fg=1 end=1` ×3 / `verbatim` |
| 7 | Run prompts: wait rule for all three, judge rule for the reviewer only | NEW | `implementer fg=0 judge=0` / `reviewer fg=0 judge=0` / `verifier fg=0 judge=0` | `implementer fg=1 judge=0` / `reviewer fg=1 judge=1` / `verifier fg=1 judge=0` |
| 8 | Reviewer copies carry the rule, no line removed, verifier unchanged | NEW | `judge=0 narrow=0` ×3 / `copy=SAME fill=unchanged removed=0 verifier_changed=0` | `judge=1 narrow=1` ×3 / `copy=SAME fill=unchanged removed=0 verifier_changed=0` |
| 9 | Reviewer input no longer lists the gate commands | NEW | `reviewer gates=1 told=0` / `verifier gates=1 told=0` / `implementer gates=1 told=0` | `reviewer gates=0 told=1` / `verifier gates=1 told=0` / `implementer gates=1 told=0` |
| 10 | Design doc states the rule, rows and park | NEW | `rule=0 rows=0 parks=0 kill=0` | `rule=1 rows=2 parks=1 kill=1` |
| 11 | Build spec: EMPTY-OUTPUT, no KILLED condition | NEW | `stale=3 empty=0 note=0` | `stale=0 empty=1 note=1` |
| 12 | README drops the budget park | NEW | `budget=2 built=0 unstick=0` | `budget=0 built=1 unstick=1` |
| 13 | Changelog records issue 41, no gap | NEW | `CONTIGUOUS` / `0` | `CONTIGUOUS` / `5` |
| 14 | No whitespace errors | REGRESSION | n/a | `exit=0` |

I ran each gate command exactly as written, from the worktree, on `c01e7c2`:
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; git diff --check main...HEAD)`: exit 0.
- `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; uv run --frozen pytest -q -p no:cacheprovider tests/factory)`: `360 passed in 218.78s (0:03:38)`. The one failure from run-0304, `test_gate_paths.py::test_a_diff_that_touches_a_scoped_command_s_paths_runs_it`, now passes.

I also checked the restored SKIPPED lines directly, outside the gates. A scratch script (`scratch/check_reviewer_skipped.py`) used the suite's own `Target` helper from `test_gate_paths.py` to compose a reviewer input and a verifier input for a diff that skips the scoped command. Both inputs printed the same single line, `SKIPPED by the harness for this diff, do not run: `sh -c 'exit 7'`: the diff <base>...<head> touches none of its paths: src/`, and the same `gate_skipped` entry in `meta.yaml`. The reviewer's paragraph ends "The verifier runs the gate commands on this head; you do not run them." The verifier's paragraph still lists the commands to run.

## Tests added/changed

- Added `tests/factory/test_empty_output.py`, a new file in `679dccc`, unchanged this round. It has 6 tests covering 4 cases:
  - `run finish` with no output, an empty output or a whitespace-only output gives `EMPTY-OUTPUT` in its JSON and in `meta.yaml`, and logs `run.finished`, never `run.killed`.
  - `--status-override KILLED` still gives `KILLED` and logs `run.killed`.
  - `run last-message` writes the file for an `EMPTY-OUTPUT` run and prints the spec's JSON.
  - `run last-message` exits 2 and writes nothing for a run that finished with an output.

  Before the change, 5 of the 6 failed. The override test already passed, because that behaviour does not change.
- Changed `tests/factory/test_gate_paths.py::test_a_diff_that_touches_a_scoped_command_s_paths_runs_it`, under ruling item 1. Its `t.checker("reviewer")` is now `t.checker()`, which composes a verifier input. Nothing else in the file changed (`git diff 679dccc c01e7c2 -- tests/factory/test_gate_paths.py` is one line). The change was needed because B.2 removes the gate commands from the reviewer's input. The test checks that a scoped command whose paths the diff touches is listed to run. It now checks that on the verifier, the role that still receives the gate commands. Its assertions are unchanged.

## Known gaps and uncertainties

- No suite test asserts that the reviewer's input carries the SKIPPED lines. The only test for that case, `test_a_scoped_command_is_skipped_for_a_diff_that_touches_none_of_its_paths`, composes a verifier input. I checked the reviewer case once by hand (above). The ruling said "Nothing else changes", so I added no test. If a later change drops the lines for the reviewer again, the suite will not notice.
- The `results record … --killed` suffix in `build.js` can no longer be reached from the workflow, because `run finish` without an override can no longer return `KILLED`. The spec keeps `--killed` for rows a human records by hand and does not ask to remove the suffix, so it stays.
- `factory:` markers added: none.
- The clerk receives the last message inside its prompt as one shell single-quoted word of up to 4000 characters, possibly with newlines. The scenarios pass this through a real `sh -c`. No real clerk agent has yet relayed a long multi-line argument. If a clerk mangles one, the call fails and is ignored, as specified, and only the kept message is lost.
- Changelog entry 57 is one long line, like entries 54 to 56. Its wording is mine, written to the five terms scenario 13 checks.

## Out-of-scope observations

- `dev/build-harness.spec.md` item 59 ("Wall-clock kill … `time_budget_s: 1800` → `status: KILLED`") and item 83 (`--redispatch --budget`) describe a budget mechanism that does not exist: the spec's evidence shows `grep -rn "time_budget\|budget_usd" factory/*.py` prints nothing. I rewrote I.5 as the spec asks, so it no longer claims a wall-clock kill. I left items 59 and 83 alone.
- `tests/factory/test_shepherd.py` and `test_killed_checker.py` still model the old killed path through the CLI, and they pass, as the spec predicted. The comment in the current-truth fixture `t0022-build.mjs` still says "the workflow records as a killed run". The spec lists both as observed, not changed.
- T-0030 overlaps this change: it also edits `factory/prompts/reviewer.md`, the design doc's §6 block and `factory/compose.py`. Whichever merges second will hit a text conflict in the reviewer's "Where you work" paragraph.

Protected paths this change touches, all declared in the parent's Risk list:
- harness: `factory/cli.py`, `factory/compose.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`, `factory/prompts/preamble.md`, `factory/prompts/reviewer.md`;
- generated: `docs/prompts/00-preamble.md`, `docs/prompts/06-code-reviewer.md`.

## Responses to the ruling (2026-10-06, on run-0304's BLOCKED)

1. Retarget the test: DONE in `c01e7c2`. `t.checker("reviewer")` became `t.checker()`, and nothing else in `tests/factory/test_gate_paths.py` changed.
2. Keep B.2's gate-commands sentence: DONE. It is unchanged from `679dccc`, and scenario 9 prints `reviewer gates=0 told=1`.
3. Restore the reviewer's SKIPPED lines: DONE in `c01e7c2`. They are added after the gate sentence for every role, worded exactly as before. Checked by hand as described in Acceptance results.
4. Re-run the gate commands: DONE. `git diff --check` exited 0, and the suite printed `360 passed`.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. All 14 scenarios print their THEN on `c01e7c2`, both gates pass (360 tests), and this round's change is the two edits the ruling names.
ESCALATIONS: none
