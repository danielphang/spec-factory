Type: chore

Title: De-bloat B: one shared helper module for the harness tests, shared fixture helpers, and the duplicate test removed

Summary:
The harness test suite (`tests/factory/`) repeats the same scaffolding in most of its files, and many test files import helpers from other test files. That means editing one test can break another. The requester wants one non-test helper module that the test files import from, and no test file importing from another. The shared helpers would be the repo and entry-point constants, the subprocess wrapper for `bin/factory`, the JSON helper, the ticket reader, an "approved parent" setup and a "git repo with an empty commit on main" setup. They also want three cleanups: drop the one duplicate test, stop the suite from writing `.pyc` files into the harness tree, and confirm no test still writes into the working tree. They set limits on the merge. Every distinct assertion survives, and no test that is the only guard for a refusal, verdict or regression is removed. Each file keeps its own extra environment and the `clean_harness_cli` split. Asserting on the return code inside `js` stays opt-in per caller. The test count drops only by the one named test.

Evidence (from the request, issue #98 / #96 row 2a; checked on `~/dev/spec-factory` at `0ba4e4f`, which changes only `dev/` after the requester's `927bc53`):
- Size: `cat tests/factory/*.py | wc -l` gives 9710, matching the request. 47 `.py` files.
- `run(...)` wrapper: `grep -n "^def run(" tests/factory/*.py` finds exactly the 10 definitions the request lists, at the stated lines (8 take a store path, 2 take an env dict).
- `js()` is defined in 11 files and `ticket()` in 13, and 30 files assign `REPO =`. All three counts match the request.
- Cross-test imports: `grep -nE "^from \.test_" tests/factory/*.py` finds 14 importing files, not the "twelve" the request states: test_build_startup, test_drift_siblings, test_drive_guard, test_drive_build, test_killed_checker, test_live_store_guard, test_parent_close_reuse, test_role_inputs, test_plan_fields, test_stats, test_spec_drift, test_store_branch, test_store_migrate and test_whole_spec_plan. The four lines the request cites are correct.
- The duplicate test: `test_run_finish_without_output_is_killed` is at `test_p0_cli.py:119` (the request says 118). It asserts return code 0, `status == "KILLED"` and meta status KILLED. `test_status_override_killed_still_records_killed` (`test_empty_output.py:61`) asserts the same three things through `Store.ok`, which asserts the return code (`test_empty_output.py:38-40`). On reading, the subset claim holds.
- `.pyc` leak: `role_argv` at `test_drive.py:199-204` runs `subprocess.run([sys.executable, "-c", ...], cwd=REPO)` with no `env=`, so `PYTHONDONTWRITEBYTECODE` is not set. `git status --porcelain --ignored` already lists `!! factory/__pycache__/`.
- Stray directory: `~/dev/spec-factory/core/b.py/` exists, is empty and is dated Oct 7 07:58. `test_merge_protected_paths.py:73-76` writes `core/b.py` under `self.target`. I did not confirm whether any path can resolve `self.target` to the repo root.

Capabilities: harness-suite

Assumptions (inferences, not stated by the requester):
- This is a test-only refactor. No harness behaviour, command, state or document changes, so no README or design-doc update is expected. One exception: the `PYTHONDONTWRITEBYTECODE` fix is in test code, not in `factory/`.
- The acceptance check "`git status --porcelain --ignored` unchanged by a suite run" cannot catch either problem as written. Git does not list empty directories, so `core/b.py/` never shows. `factory/__pycache__/` is already listed as ignored, so a new `.pyc` inside it leaves that output unchanged. The spec writer needs a check that would fail today, for example a file listing of the harness tree taken before and after a suite run, or clearing `factory/__pycache__` first. The briefing warns that a new criterion that already passes proves nothing.
- The suite size quoted ("451 tests, 577 passing") was not re-run in triage. A plain count of `def test_` finds 447 definitions, and parametrisation explains the difference from 577. The spec writer should take the baseline count from a run on the base commit.
- Overlap with sibling tickets from the same sweep, to settle in sequencing (suggestion only):
  - T-0044 (De-bloat A) is planned. It edits `tests/factory/test_instance.py:109,354`, a file whose helpers this ticket moves.
  - T-0047 (#100) changes the in-process uses of `factory.cli` in `clean_harness_cli.py` and `test_store_migrate.py`.
  - T-0046 (#99) requires existing tests to pass "without edits to their assertions".
  - The request says #83 parts C and D will change the four design-block tests and remove `store migrate`.
  None of these duplicates this ticket. They touch the same files, so the order of these tickets matters.
- Suggested priority: medium. It costs nothing at runtime but lowers the cost of every later ticket that touches tests. This is a suggestion only, and priority is a human call.

Reason: ACCEPT. The intent, the rules for what must survive and the out-of-scope items are explicit, and the evidence checks out apart from the small count and line drifts noted above. No product decision is needed. Duplicate search: `.factory/store/tickets/` and `dev/issues.md` rows 97-101 hold no other ticket for a shared test helper module. This request is T-0045 itself.

STATUS: ACCEPT
CONFIDENCE: high. The request's specific claims were checked with grep and by reading the file lines. Only the suite baseline count was not re-run.
ESCALATIONS: none
