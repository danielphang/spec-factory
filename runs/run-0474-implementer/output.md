Sub-ticket: T-0046.1 (parent T-0046, approved spec v3). Branch `factory/T-0046.1`, commit `b1123b0` on base `34de412`.

## What changed

The harness is the Python code under `factory/` that runs the factory. Before this change, seven small operations were written out by hand in several places each. Each one now has a single definition, and every copy calls it. Nothing a user or operator sees has changed. The REGRESSION scenarios print byte-identical refusals, events, history entries and park reasons, and the spec parser gives the same result on all 4034 calls checked. The changes, by lettered part of the design:

| Part | New definition | Callers that now use it |
|---|---|---|
| A. List a ticket's runs | `store.ticket_runs(root, ticket, role=None, finished=False)`, which yields `(run_id, meta)` in run-id order and skips a run whose `meta.yaml` is missing or empty | `compose.py` (every former `_runs_for` call, plus `_last_run_meta`); `specstore.critic_rounds`; `cli._parent_close_verified`; `store.clear_scratch`; **and three `cli.py` callers of `compose._runs_for` that the spec did not list** (see Known gaps). `compose._runs_for` is deleted. |
| B. Read the event log | `store.log_lines(root)` (raw lines); `cost._log_records(store)` (parsed records, malformed lines skipped) | `cli._recorded_plan_run` and `cli.log_tail` use `log_lines`. `cost._store_paths` and `stats._load` use `_log_records`. `stats.py` imports `_log_records` in place of `_records`. |
| C. Record a status transition | `store.record_transition(root, t, to, by, history=None, event=None)`, which returns the status the ticket left | `cli.ticket_transition`, `ticket_ready_implementers`, the dependant release in `merge`, `ticket_parent_check`. `approve_spec` is unchanged. |
| D. List runs in flight | `store.in_flight_runs(root, t)` | `cli.spec_amend` and `drive._same_ticket_guard` |
| E. Read the integration-branch tip | `gitops.integration_tip(cfg, repo)` | the four `cli.py` sites (`_check_sibling_tests`, `_test_drift`, `_integration_head`, `_reused_subticket_run`) |
| F. Four smaller `cli.py` repeats | `_copy_record`, `_supersede`, `_planner_run`, `_refuse_unless_applies` | `request_changes` and the four ruling copies in `resolve`; the reviewer-ESCALATE ruling and `--redispatch`; `subticket_add` and `spec_tasks`; `approve_spec` ("spec not pinned") and `spec_amend` ("spec not amended") |
| G. Dispatcher parks (the dispatcher is `factory/drive.py`, which runs each role and parks the ticket when a store command fails) | `drive._harness_bug(what, res)` formats the park reason; `drive._cleanup_checker(role, rid)` cleans up a checker run | all 18 `harness-bug: <what>: <stderr>` reasons, including the three inside conditional expressions and the loop over `what`; the three checker clean-ups |

`git diff --stat main...HEAD -- factory`, the line change per file, as the design asks:
```
 factory/cli.py       | 137 ++++++++++++++++++++++++---------------------------
 factory/compose.py   |  33 ++++---------
 factory/cost.py      |  23 +++++----
 factory/drive.py     |  58 ++++++++++++----------
 factory/gitops.py    |   5 ++
 factory/specstore.py |  17 ++-----
 factory/stats.py     |   9 ++--
 factory/store.py     |  46 ++++++++++++++---
 8 files changed, 175 insertions(+), 153 deletions(-)
```

Callers of each changed function were found with grep (coding rule 2). `grep -rn "_runs_for\|_last_run_meta" factory bin agents tests docs README.md` found the three extra `cli.py` callers. After the change, `_runs_for` appears nowhere. `README.md` is not updated: no command, state, stop or path changed.

## Acceptance results

Every command ran from the worktree inside the fresh-HOME wrapper. For the GIVEN fixtures, `TMPDIR` pointed at this run's scratch directory.

NEW, before (base `34de412`) and after (`b1123b0`):

| Scenario | Before | After | Expected after |
|---|---|---|---|
| Only the store module lists a ticket's runs | `3` | `0` | `0` |
| The CLI and the stats report read the event log through a shared reader | `3 0` | `0 1` | `0 1` |
| One function records a status transition outside spec approval | `5 0` | `1 1` | `1 1` |
| Neither spec amend nor the dispatcher builds the in-flight list itself | `2` | `0` | `0` |
| One function reads the integration-branch tip | `4 0` | `1 1` | `1 1` |
| Record copies, row set-asides, planner-run checks and spec apply checks each have one definition | `5 2 2 2` | `0 1 1 1` | `0 1 1 1` |
| One line formats a failed-command park and one call cleans up a checker | `18 3 0` | `1 1 2` | `1 1 2` |

Each "before" value matches what verification.md predicted for this base.

REGRESSION, after:
- **Status transitions write the same events and history entries.** The 14 lines are byte-identical to the spec's expected block. The comparison was a Python string equality against the block extracted from `specs/T-0046/v3.md`, and it printed `1 SAME 14`. This means the four rewritten transition sites write the same history entries and log events, with the same fields in the same order.
- **Spec pinning and planner-run refusals keep their text.** The 4 lines are byte-identical (`2 SAME 4`), so the refusals from `_refuse_unless_applies` and `_planner_run` keep their text.
- **The dispatcher parks a refused store command with the same reason.** The 3 lines are byte-identical (`3 SAME 3`), so `_harness_bug` keeps every park reason's text, including the `harness-bug: run start implementer:` prefix that `resolve --ruling` matches. The first run of this scenario failed and caught a real defect, covered in Known gaps.
- **The spec parser gives the same result as the base on every spec in the store.** It printed `files=272 checks=4034 differ=0` and nothing after it. This means the edit to `critic_rounds` (part A) leaves every parse result as it was on the base.
- **The refactored harness has no unused imports or variables.** `uvx ruff check --select F401,F841 factory tests` printed `All checks passed!` and exited 0. As an extra check, a full default `ruff check factory` reports the same findings as on the base. The two lists, with line numbers stripped, have an empty diff.
- **The harness suite passes and no existing test file changes.** It printed `576 passed in 464.24s (0:07:44)`. The `git diff --name-only --diff-filter=DMR main...HEAD -- tests` part printed nothing, so no existing test file changed.

Gate commands on `b1123b0`, each as written:
- `git diff --check main...HEAD` exited 0 with no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: the first run reported `1 failed, 575 passed`. The failure was `test_drive_build.py::test_build_step_lines_and_the_status_file_name_the_subticket_in_flight`. That test passes only if a 50 ms poll sees all four checker runs at once inside a 2-second window. I was running the spec-parser comparison and ruff alongside it during that run. Run alone, it passed 3 times out of 3. A second full gate run with nothing alongside it printed `576 passed in 468.06s`, and the REGRESSION suite command above passed too. I read this as a timing flake under CPU load, not a regression. I did not prove that, so it is also listed under Known gaps.

## Tests added/changed

None. Every behaviour is covered by the existing suite and the spec's scenarios. No existing test file was touched.

## Known gaps and uncertainties

- **The spec missed three callers of `compose._runs_for`.** Design.md says `_runs_for` has "two uses", all in `compose.py`, and tells me to delete it. In fact it had 8 call sites in `compose.py` and 3 more in `cli.py`: `_check_drift`, `_planner_needed` and the conflict-run counter in `ticket_head` (base lines 288, 754 and 845). Deleting the function as the spec says broke those `cli.py` callers. The first run of the dispatcher-park scenario caught it, printing `AttributeError: module 'factory.compose' has no attribute '_runs_for'` in T-0001.1's park reason. I pointed all three at `store.ticket_runs(..., finished=True)`, the same filter `_runs_for` applied. The spec's requirement says "Every caller MUST use that definition", so I treated this as within scope, not a new design. After this, all three REGRESSION command scenarios were byte-identical. `compose._last_run_meta` stays: it is still called from `compose.py` and `cli._planner_needed`, and it now reads its meta from `ticket_runs`.
- **The net line change is +22, not the spec's estimated fall of about 70.** `factory/` has 175 insertions and 153 deletions. The spec estimated a net fall of about 70. Three things account for most of the gap. Each new helper has a one-line docstring. Deleting `_runs_for` as the design says leaves 11 inline list comprehensions in its place. The estimate may also predate the cut of part H. I did not add anything outside the design to close the gap.
- **`clear_scratch` acts slightly differently on edge cases, as the design specifies.** It now unlinks a scratch entry that is a symlink, even a broken one. Before, `glob("*/scratch")` may not have matched a broken symlink. A scratch entry that is a regular file is now left alone, where `shutil.rmtree` would have raised before. Both changes follow design.md part A. Neither can happen to a scratch directory the harness creates itself.
- **An empty `meta.yaml` is now skipped.** This is the one behaviour change the spec's Decisions accept. The other run listers would have raised `AttributeError` on a run whose record is still being written.
- **`cost._store_paths` now reads the log files in sorted order.** Before, it used an unsorted glob. Its result is a set, so the order cannot change what it returns.
- **The flaky test is not proven flaky.** See the gate results above: one failure under load, then 3 of 3 passes alone and two clean full runs.
- `factory:` markers added: none. The existing marker in `clear_scratch` is kept.

## Out-of-scope observations

- The verification.md evidence for part A named only the run-directory listings in `compose.py`, `specstore.py` and `cli.py`. A later spec that deletes a helper might grep for qualified uses (`module._name`) too, since that is what the "two uses" count missed.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW and REGRESSION scenario was run on the head, and the three REGRESSION command outputs are byte-identical to the spec. The one open point is a timing test that failed once under load and then passed three times alone and in two full runs.
ESCALATIONS: none
