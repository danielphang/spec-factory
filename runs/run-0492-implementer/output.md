Sub-ticket: T-0047.4 (Move the human decisions to factory/human.py, leaving factory/cli.py under 900 lines). Parent T-0047, spec v2 at `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`. Branch `factory/T-0047.4`, head `9349e5762e727e570bf0bd0e7ceb90c865387a71`, one commit on base `43265a02f3ad`.

## What changed

**Part E, `factory/human.py`, the human decisions.** "Human decisions" are the commands a person uses to approve a spec, send it back, or rule on a stopped ticket.
- New `factory/human.py` (324 lines). It holds the 13 definitions in the order they had in `factory/cli.py`: `_restart_note` and `spec_amend` first, then `_by` through `decision_add`.
- The definitions were moved by a script that cuts exact line ranges, so no body was edited. Check M confirms this with `added=0 removed=0`.
- The module header is a one-line docstring, then `from __future__ import annotations`, then the imports its code uses:
  - `difflib`, `getpass`, `shutil` and `Path`;
  - `gitops`, `specstore`, `store` and `subtickets`;
  - `_add_spec_version`, `_rel` and `out` from `factory.common`;
  - `_branch_tip` and `undeclared_protected` from `factory.gates`;
  - `Refused` from `factory.store`.
- The `# ----- human surface (K-lite)` section comment was dropped. The design allows dropping a section comment when its section in `factory/cli.py` is empty, and the module docstring now says what the code is for.
- `factory/cli.py` drops 316 lines. It goes from 1,198 to 882 lines.
  - It imports `approve_spec`, `decision_add`, `request_changes`, `resolve` and `spec_amend` from `factory.human`, for `build_parser`.
  - It drops the imports that nothing in it uses any more: `difflib`, `getpass`, `shutil`, and `_branch_tip` and `undeclared_protected` from `factory.gates`.
  - The `factory.gates` import was re-wrapped onto two lines after those two names were removed.
- Nothing under `tests/` changed, and no doc changed.

## Acceptance results

All commands were run from the worktree through the "Running code" wrapper. `TMPDIR` was set to the run's scratch directory for check M's script. The full log is `scratch/checks.out`.

NEW: The human decisions live in factory/human.py
- Before: `ModuleNotFoundError: No module named 'factory.human'`, nothing printed, exit 1.
- After: `_approval_dir _by _copy_record _next_n _refuse_unless_applies _restart_note _set_aside_failed_rows _supersede approve_spec decision_add request_changes resolve spec_amend`

NEW: factory/cli.py keeps the parser, the entry point and the role list, in under 900 lines
- Before: `1198 3`
- After: `882 3`

Intermediate check (NEW): `uv run --frozen python -B -c 'import factory.human'`
- Before: `ModuleNotFoundError`, exit 1.
- After: prints nothing, exit 0.

REGRESSION, the module scenarios from T-0047.1 to T-0047.3. All match their expected text exactly:
- drift: `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section`
- common: `_add_spec_version _in_flight _integration_head _rel fence out`
- setup: `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate`
- gates: `DECLARED_RE MAX_CONFLICT_RUNS REVIEWER_STATUSES VERIFIER_STATUSES _branch_tip _in_repo _parent_close_verified _reused_subticket_run _verifier_rows archive_cmd declared_paths merge_cmd results_record results_show ticket_head ticket_join ticket_parent_check undeclared_protected`
- README and principles: `1 0 1 0 3`

REGRESSION, check M (every moved definition keeps its exact text). The script was copied verbatim from the parent spec.
- Output: `pairs=4 added=0 removed=0 lines=54`, and nothing after it.
- The four pairs are the merges of T-0047.1, .2 and .3, plus this branch against `main`.
- This sub-ticket adds 8 of the 54 lines.

REGRESSION, the shared set R1 to R19 (R1 to R3, R5 to R11 and R13 to R19 are in `scratch/checks.out`; R4 and R12 are in `scratch/suites.out`):

| Check | Output |
|---|---|
| R1 | `factory/__main__.py factory/drive.py factory/stats.py` |
| R2 | `7 True True` |
| R3 | `All checks passed!`, exit 0 |
| R4 | `576 passed in 583.66s (0:09:43)`, and nothing after it (no test file changed) |
| R5 | `0 0` |
| R6 | `0` |
| R7 | `0 2 2` |
| R8 | `0` |
| R9 | `0` |
| R10 | `0 12 1` |
| R11 | `All checks passed!`, exit 0 |
| R12 | `576 passed in 564.04s (0:09:24)`, and nothing after it |
| R13 | `0` |
| R14 | `0 1` |
| R15 | `1 1` |
| R16 | `0` |
| R17 | `1 1` |
| R18 | `0 1 1 1` |
| R19 | `1 1 2` |

R15, R16 and R18 now find `approve_spec`, `spec_amend` and the record-copy, set-aside, planner-run and apply checks in `factory/human.py`. Their counts are the same as before the move.

Gates. Each was run exactly as written in the input:
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 563.81s (0:09:23)`, exit 0.

## Tests added/changed

None. The sub-ticket lists no interim tests and no tests to change, and this is a move with no new behaviour. The existing suite covers the moved commands (576 passed).

## Known gaps and uncertainties

- **`fence` is not imported into `factory/human.py`, although the scope line names it.** The sub-ticket and design part E say human.py imports `fence` from `factory.common`. No moved definition uses that function. `spec_amend` assigns a local variable also named `fence` (a run of backticks for the diff record), and that local hides the imported name. Importing it would leave an unused import, which fails R3 and R11. I checked this by adding the import to a scratch copy: `ruff check --select F` reported `F401 factory.common.fence imported but unused`. I followed the design's general rule, "the imports its definitions use". `factory/cli.py` still imports `fence`, because `main` uses it.
- **One step ran without the wrapper.** The move script `scratch/move.py` was run once with `uv run --frozen python -B` outside the "Running code" wrapper. It only reads and writes `factory/cli.py` and `factory/human.py` by relative path inside the worktree. Every check and test above ran through the wrapper.
- **The suite is slow.** Each suite run took about 9.5 minutes. The flaky concurrent-checker test that the spec mentions did not fail in any of the three runs.

## Out-of-scope observations

- `stats_cmd` sits under the `# ----- spec store (doc §Harness, Spec store; part K)` section comment in `factory/cli.py`, which no longer describes it. This was true before this change, and the design keeps `stats_cmd` where it is (Decision 4). I left it alone.

## Responses to findings

Not applicable (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance, regression and gate command was run on head `9349e57` and printed the expected result, and check M shows no definition text changed.
ESCALATIONS: none
