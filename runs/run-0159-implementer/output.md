Sub-ticket: T-0018.1 (parent T-0018 = issue #33, approved spec v2 at `.factory/state/specs/T-0018/v2.md`)
Branch: `factory/T-0018.1`, base `d0300d3127fdd257d725ecb996b4fe9df282cef9`, head `7a4967a055bc40e3839c65fc00416299d90db350` (one commit). There is no remote, so the PR is this branch plus this description.

## What changed

Before this change, the factory's two workflow scripts could stop a ticket and leave no record of why. Intake could plan a parent ticket without creating its sub-tickets. The build then exited silently on that parent. An agent call that threw left its run marked "in flight" for good. And a verifier's `## Gate suite: PASS` line was recorded as a test-suite failure. With this change, each of those cases either finishes the work or parks the ticket with a reason. To park a ticket is to stop it and put it in the human queue with its reason.

- **A. Intake ends at the spec gate** (`factory/workflows/intake.js`). I deleted phase 3 (Plan), its `meta.phases` entry, "-> Planner" in `meta.description`, and `planner` in `AGENT_NAME`. A `ready-for-planner` ticket now falls through to the existing final `return {…, note: 'nothing to dispatch from this state'}`.
- **B1** (`factory/cli.py`). When `subticket add PARENT` gets neither `--run` nor `--file`, it calls a new `_recorded_plan_run()`. That function reads the store's `log/*.jsonl` in file order and takes the `source` of the parent's last `plan.added` event. When that source is a run directory of this store, the command sets `a.run` to it and goes on through the existing `--run` path unchanged: the PLANNED-planner check, parsing, and `source: plan:<run>`. The command refuses with exit 2 and writes nothing in three cases: there is no such event, the source contains `/`, or the source has no `runs/<source>/meta.yaml`. The refusal says `no recorded planner run found for <parent> (latest plan.added source: …); pass --run RUN or --file F`. I also gave the parser entry a help line.
- **B2** (`factory/cli.py` `ticket_ready_implementers`). The output gains `"subtickets"`: every sub-ticket id of the parent, in id order, from `store.subtickets_of`. Existing keys are unchanged.
- **B3** (`factory/workflows/build.js`, phase 2, before the loop's first `parallel`). The loop starts with `first = true`. If the first `ready-implementers` answer has an empty `subtickets`, the build runs clerk `subticket add PARENT` with no `--run`. The clerk is the agent that runs one store command and reports its output. A refusal parks the parent with `no sub-tickets, and none could be created from the recorded plan: <stderr>` and returns `{state: 'parked'}`. On success the build logs the count and `continue`s. Because `first` is then false, the repair runs at most once per build run.
- **C1** (`build.js`, after the loop). A refused `parent-check` now parks the parent with `parent-check refused: <stderr>` and returns `parked`. A successful check that reports any state other than `ready-for-parent-verify` still returns as before.
- **C2** (`runRole` in both scripts). A `try`/`catch` now wraps both the stub `agent()` branch and the real one. On a throw, the script finishes the run with `--status-override KILLED`. In `build.js` it then runs `run cleanup` for a reviewer or verifier. It parks the ticket through the existing `park()` with `agent call failed: <role>: <message>` and the run id as outputs, then returns `null`. A null or empty result still takes the old KILLED path. In `build.js` I moved the stub-script seam (`<role>-<n>.sh`) out of the stub branch to just after the `try`, now guarded by `args.stubs &&`. That keeps the `try` around the `agent()` calls only, so a throwing clerk call in the seam is not reported as a failed role call.
- **D1** (`factory/cli.py` `results_record`). The regex is now `^[ \t#*]*Gate suite:[ \t*]*(PASS|FAIL)\b(.*)$` (`re.M`). The detail is group 2 with spaces, tabs, `\r` and `*` stripped from both ends, or `None` when that leaves nothing. When no line matches, the result is still `FAIL`, `missing Gate suite line`.
- **D2**. In three places, the line `Gate suite: PASS/FAIL, with failing output` is replaced by the two lines the spec pins: `docs/design.md` (§7 Verifier block) and `factory/prompts/verifier.md`, each by an exact-string replacement, and `docs/prompts/07-verifier.md`, re-copied from the design block with the acceptance check's own `awk` extraction. Step 4 of `factory/prompts/verifier.md` is untouched.
- **D3**. `docs/changelog.md` gains entry `47. After issue #33 (2026-10-04), …` after entry 46 and before `Declined:`. It covers the three points: intake ends at the gate and the build owns planning; a thrown agent call or a refused `parent-check` parks with the reason; and the verifier writes a plain `Gate suite:` line, which the harness also reads in heading or bold form.
- **E. Documents**
  - `README.md` "How a ticket moves" now ends its paragraph with `The intake script stops at the spec gate; the build script runs the planner.`, on its own line.
  - The "Start the…" sentence in "Starting a run" now reads `Start the build script after the spec gate; the intake script has nothing to do past it.`
  - The status-header date already reads 2026-10-04, which is today, so it is unchanged.
  - `dev/build-harness.spec.md` H `runRole` (line 275) now covers a thrown `agent()`. H `build.js` step 2 (line 285) now covers the `subtickets` key, the B3 repair and the C1 park. L (line 320) now says the gate line "may carry leading heading or emphasis marks".
- **F**. One new file, `tests/factory/test_build_startup.py`. It imports `run`, `js`, `ticket` and `PLAN_LETTERS` from `test_subtickets.py`, the way `test_killed_checker.py` imports from `test_shepherd.py`.

Callers of each changed function, found by grep (coding standard rule 2):
- `runRole` has 3 callers in `intake.js` and 4 in `build.js` (lines 125, 148, 191, 248 after the change). Each already returns on `null`.
- `results record` is called only from `build.js:150`.
- `ready-implementers` is called only from `build.js:210`, plus tests.
- `subticket add` is called from `build.js:199` with `--run`, unchanged, and from the new `build.js:216`.

## Acceptance results

I ran every command from the worktree root under `bash`, after `uv sync --frozen`, with node v24.14.0. First I ran the parent's GIVEN block once (`v2.md` lines 154-200, between the fences). It wrote `$TMPDIR/t0018-drive.js`, `t0018-approved.sh` and `t0018-handplan.sh`. "Before" means the code at base `d0300d3`; "after" means the code at head `7a4967a`, whose tree is the one I tested.

| Scenario | Kind | Before (base) | After (head) |
|---|---|---|---|
| Intake leaves an approved ticket for the build workflow | NEW | `returned planned`, `ticket T-0001 planned in_flight=0 reason=-`, `run run-0004-planner PLANNED`: intake ran the planner | `returned ready-for-planner`, `ticket T-0001 ready-for-planner in_flight=0 reason=-`, no `run run-0004-planner` line: PASS |
| Build plans a gate-approved parent and creates its sub-tickets | REGRESSION | not run | `run run-0004-planner PLANNED`, `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer`, `source: plan:run-0004-planner`: PASS |
| Build creates the missing sub-tickets from the recorded planner run | NEW | `returned planned`, `ticket T-0001 planned … reason=-`, no `T-0001.1` line, `grep: …/T-0001.1.yaml: No such file or directory` | `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer`, `run run-0005-implementer KILLED`, `source: plan:run-0004-planner`: PASS |
| Build parks a planned parent it cannot give sub-tickets | NEW | `returned planned`, `ticket T-0001 planned in_flight=0 reason=-`: no park | `returned parked`, `ticket T-0001 parked in_flight=0 reason=no sub-tickets, and none could be created from the recorded plan: no recorded planner run found for T-0001 (latest plan.added source: tests/factory/fixtures/stubs/accept-approve/planner-1.md); …`, no `ticket T-0001.1` line: PASS |
| subticket add without a source uses the recorded planner run | NEW | `factory: TypeError: argument should be a str or an os.PathLike object … not 'NoneType'`, `exit=1`, no `T-0001.1.yaml` | last JSON line `{"ok": true, "parent": "T-0001", "subtickets": [{"id": "T-0001.1", …}]}`, `exit=0`, `source: plan:run-0004-planner`: PASS |
| subticket add without a source refuses when the plan came from a file | NEW | same `TypeError`, `exit=1`, listing `T-0001.yaml` | `no recorded planner run found for T-0001 …`, `exit=2`, no `TypeError`, listing `T-0001.yaml` alone: PASS |
| A failed agent call in intake parks the ticket | NEW | `threw agent type 'factory-triage' not found`, `ticket T-0001 ready-for-triage in_flight=1 reason=-`, `run run-0001-triage running` | `returned parked`, `ticket T-0001 parked in_flight=0 reason=agent call failed: triage: agent type 'factory-triage' not found`, `run run-0001-triage KILLED`: PASS |
| A failed agent call in the build parks the sub-ticket | NEW | `ticket T-0001.1 ready-for-implementer in_flight=1 reason=-`, `run run-0005-implementer running` | `ticket T-0001.1 parked in_flight=0 reason=agent call failed: implementer: agent type 'factory-implementer' not found`, `run run-0005-implementer KILLED`: PASS |
| The harness suite passes | REGRESSION | not run (`157 passed` per the spec) | `171 passed in 110.99s`: the 157 existing tests plus the 14 new ones. PASS |
| The change adds no whitespace errors | REGRESSION | not run | `git diff --check main...HEAD; echo "exit=$?"` printed only `exit=0`. PASS |
| Heading and emphasis gate lines are read | NEW | all four lines `=> FAIL\|missing Gate suite line` | `## Gate suite: PASS => PASS\|`, `**Gate suite:** PASS => PASS\|`, `### **Gate suite: PASS** => PASS\|`, `**Gate suite: FAIL** 2 failed => FAIL\|2 failed`: PASS |
| Plain gate lines and prose read as before | REGRESSION | not run | `Gate suite: PASS => PASS\|`, `Gate suite: FAIL 1 failed => FAIL\|1 failed`, `The Gate suite: PASS line was missing => FAIL\|missing Gate suite line`: PASS |
| The verifier prompt pins the gate line in all three copies | NEW | `0 0 1` for each file | `docs/design.md 1 1 0`, `docs/prompts/07-verifier.md 1 1 0`, `factory/prompts/verifier.md 1 1 0`: PASS |
| The design block and its prompt copy stay identical | REGRESSION | not run | `SAME`: PASS |
| The README says intake stops at the spec gate | NEW | `0` then `1` | `1` then `0`: PASS |
| The changelog records the change | NEW | `0` then `0` | `1` then `1`: PASS |
| The build spec names the accepted gate line forms | NEW | `0` | `1`: PASS |

Gate commands, run from the worktree exactly as written on head `7a4967a`:
- `git diff --check main...HEAD` printed nothing and exited 0 (`main` = merge base = `d0300d3`).
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `171 passed in 110.99s`.
- `uv run --frozen ruff check factory/cli.py tests/factory/test_build_startup.py` printed `All checks passed!`.

Behaviour the spec leaves to the reviewer, as far as I checked it:
- C2 cleanup for a checker. With the driver set to throw on `verifier`, the result was `ticket T-0001.1 parked in_flight=0 reason=agent call failed: verifier: agent type 'factory-verifier' not found` and `run run-0007-verifier KILLED`. The run's `wt/` directory is gone, and `run start` creates that directory for every checker (`factory/cli.py:253-254`). So `run cleanup` ran on the throw path.
- C1 (the `parent-check` refusal park) has no runnable scenario. I checked it by reading only: `build.js` lines 233-234 after the change.
- B3's "at most once per build run" is held by the `first` flag. I checked it by reading only.

## Tests added/changed

Added: `tests/factory/test_build_startup.py`, 14 cases. On base `factory/cli.py`, 10 of them fail and 4 pass. The 4 that pass are the plain-line, prose and `- Gate suite:` cases, which are meant to read the same before and after. With the change, all 14 pass.

| Test | What it checks |
|---|---|
| `test_subticket_add_without_a_source_uses_the_recorded_planner_run` | `ok`, the three sub-ticket ids, and `source: plan:<run>` |
| `test_subticket_add_without_a_source_takes_the_latest_plan` | With two planner runs and two `plan add`s, the second run is used |
| `test_subticket_add_without_a_source_refuses_with_no_recorded_planner_run[none\|file]` | With no `plan.added` event, or a plan added with `--file`: exit 2, the refusal text, no `TypeError`, only `T-0001.yaml` in `tickets/`, and the log byte-for-byte unchanged |
| `test_ready_implementers_lists_every_sub_ticket_in_id_order` | `subtickets` is `[]` before `subticket add`. It lists all three ids afterwards, a merged sub-ticket included, while `remaining` is unchanged in meaning |
| `test_the_gate_line_is_read_under_heading_and_emphasis_marks_only` (9 lines) | The 4 D1 forms, a leading-space form, the 2 plain forms, the prose line, and `- Gate suite: PASS`, which is not read: a list marker is not one of the allowed marks |

Changed: none. No existing test file was touched.

## Known gaps and uncertainties

- **A gate line split over two lines is no longer read.** The old regex's `\s*` after the colon could cross a newline, so a `Gate suite:` line with `PASS` on the next line used to be read as PASS. The spec's pinned `[ \t*]*` does not cross a newline, so that form is now `missing Gate suite line`. I found no output or test that writes it that way: the existing tests put the detail on the next line, not the verdict. The prompt now pins the one-line form.
- **The `subticket add` source lookup reads the whole log on every call.** That is a linear scan of every `log/*.jsonl` file. It is cheap at today's store sizes, and `log_tail` reads the log the same way. I did not add a `factory:` marker because it is not a deliberate shortcut with a known limit beyond that.
- **The README sentence describes behaviour no real ticket has run yet.** README's "Maintaining this page" says a behaviour appears in the present tense only after it has run on a real ticket. The spec pins the exact sentence, and it describes intake doing less, so I followed the spec. A reviewer may judge it against that rule.
- **The C2 throw path is checked only under the node driver.** The real Workflow runtime might not surface an unknown agent type as a throw inside `runRole`, for example if it threw synchronously outside the awaited promise. The parent's Evidence makes the same inference. `try`/`await` catches both synchronous throws and rejections, so the catch holds either way.
- factory: markers added: none.

## Out-of-scope observations

- Park reasons built from a clerk's stderr keep the trailing newline. Examples are the new `no sub-tickets…` and `parent-check refused: …` reasons, and every existing `harness-bug: …: ${stderr}` reason. The driver's listing therefore shows an empty line after such a reason. Trimming them would be a change across every `park()` caller.
- `park()` in both scripts puts the reason inside a double-quoted shell argument and escapes only `"`. An error message that contains `` ` `` or `$(` would be expanded by the shell. The new `agent call failed: …` reason carries a free-form runtime error message, which makes this more reachable than before. `agent type '…' not found` itself is safe.

## Responses to findings

n/a: this is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW check failed on base as the spec says and passes on head, the regression checks pass, and the suite passes (171). C1 and the B3 once-per-run limit are checked by reading only, as the spec says.
ESCALATIONS: none
