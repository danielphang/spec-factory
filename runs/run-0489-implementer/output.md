Sub-ticket: T-0047.3 (`/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`, part D). Branch `factory/T-0047.3`, head `c30b80f45a39824b71c7064cc22e2563a53f9438`, base `57b46e18ca48c71254487dec086b27c3d34ec79c`. Worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0047.3`.

## What changed

The gates are the harness commands that record review and verification results and refuse a merge or a ticket close that those results do not support. This change moves them out of `factory/cli.py` into a new module, `factory/gates.py`. No gate's behaviour changes. The README and the principles page now name the new module.

**Part D, the code.** These 18 definitions moved byte for byte, in the order they had in `factory/cli.py`:
- the first block, `ticket_head` through `ticket_parent_check`: `ticket_head`, `results_record`, `results_show`, `DECLARED_RE`, `_in_repo`, `declared_paths`, `undeclared_protected`, `_branch_tip`, `merge_cmd`, `REVIEWER_STATUSES`, `VERIFIER_STATUSES`, `MAX_CONFLICT_RUNS`, `ticket_join` and `ticket_parent_check`;
- the second block, `_verifier_rows` through `archive_cmd`: `_verifier_rows`, `_reused_subticket_run`, `_parent_close_verified` and `archive_cmd`.

The move was made by a script that cut both blocks between fixed anchors. It did not retype them.
- `factory/gates.py` starts with a one-line docstring and `from __future__ import annotations`. Its only imports are `re`, `Path`, `gitops`, `specstore`, `status`, `store`, `subtickets`, `out` from `factory.common` and `Refused`. It does not import `factory.cli`.
- `factory/cli.py` imports these names from `factory.gates`:
  - `_parent_close_verified`, for `ticket_transition`;
  - the seven commands, for `build_parser`;
  - `_branch_tip` and `undeclared_protected`, for `resolve`. The sub-ticket does not list these two. See Known gaps.
- No other import in `factory/cli.py` became unused. `ruff --select F` passes.
- No `# -----` section comment moved or was dropped, because each section still holds code in `factory/cli.py`.
- `factory/cli.py` went from 1,508 to 1,198 lines, and `factory/gates.py` has 321.

**Part D, the docs.**
- `README.md:9`: the status date is now 2026-10-12, the day of this change.
- `README.md:1171`: "`factory/cli.py` `ticket_join`, `merge_cmd`, `archive_cmd`" now reads "`factory/gates.py` `ticket_join`, `merge_cmd`, `archive_cmd`".
- `docs/principles.md:106-109`: the sentence now reads "…the guards in `factory/cli.py` (`ticket transition`, `run start`) and `factory/gates.py` (`merge`); …".
  - I re-wrapped only that sentence's lines, at 100 columns, so the paragraph went from 3 lines to 4. The longest line is 99 columns. "`factory/gates.py` (`merge`)" stays on one line.
  - The lines above it in the same block each begin their own sentence, so I left them as they were.

## Acceptance results

All commands ran from the worktree through the "Running code" wrapper with a fresh HOME, on head `c30b80f`. The full log is `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0489-implementer/scratch/checks.log`.

**NEW: The gates live in factory/gates.py.**
- Before: `ModuleNotFoundError: No module named 'factory.gates'`, exit 1, nothing printed.
- After: `DECLARED_RE MAX_CONFLICT_RUNS REVIEWER_STATUSES VERIFIER_STATUSES _branch_tip _in_repo _parent_close_verified _reused_subticket_run _verifier_rows archive_cmd declared_paths merge_cmd results_record results_show ticket_head ticket_join ticket_parent_check undeclared_protected`. This is exactly the expected list.

**NEW: The README and the principles name gates.py for the moved gate commands.**
- Before: `0 1 0 1 ` (the last field is empty because `factory/gates.py` did not exist).
- After: `1 0 1 0 3`, as expected.

**Intermediate checks (NEW).**
- `uv run --frozen python -B -c 'import factory.gates'` exits 0 and prints nothing.
- `git diff --check main...HEAD -- README.md docs/principles.md` exits 0 and prints nothing.

**REGRESSION: the parent's module scenarios for drift, common and setup.**
- drift: `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section`
- common: `_add_spec_version _in_flight _integration_head _rel fence out`
- setup: `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate`

All three match the expected lists.

**REGRESSION M: every moved definition keeps its exact text, and the split adds at most 100 lines.** I copied the script verbatim from the parent spec's scenario block into the scratch directory rather than `/tmp`, because of the scratch-file rule.
- Before (on base): `pairs=2 added=0 removed=0 lines=35`.
- After: `pairs=3 added=0 removed=0 lines=46`, and nothing after it.
- What it shows: no definition's text changed. This sub-ticket adds 11 lines. The split has now used 46 of its 100 lines, which leaves 54 for T-0047.4.

**REGRESSION R1 to R19.** Each printed the expected value.

| Check | Output |
|---|---|
| R1 | `factory/__main__.py factory/drive.py factory/stats.py` |
| R2 | `7 True True` |
| R3 | `All checks passed!`, exit 0 |
| R4 | `576 passed in 571.88s (0:09:31)`, and no line after it |
| R5 | `0 0` |
| R6 | `0` |
| R7 | `0 2 2` |
| R8 | `0` |
| R9 | `0` |
| R10 | `0 12 1` |
| R11 | `All checks passed!`, exit 0 |
| R12 | `576 passed in 582.65s (0:09:42)`, and no line after it |
| R13 | `0` |
| R14 | `0 1` |
| R15 | `1 1` |
| R16 | `0` |
| R17 | `1 1` |
| R18 | `0 1 1 1` |
| R19 | `1 1 2` |

In R4 and R12, nothing after the pytest line means no file under `tests/` changed.

**Gate commands, exactly as written** (log: `scratch/gates.log`):
- `git diff --check main...HEAD`: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: exit 0, `576 passed in 572.55s (0:09:32)`.

## Tests added/changed

None. The sub-ticket says "Interim tests: none" and "Tests to change: none".
- The behaviour this sub-ticket must keep is covered by the existing suite: 576 passed, three times.
- The acceptance commands check where the code now lives.
- No test patches a name that moved. A grep of `tests/factory` for `monkeypatch`, `mock.patch` and `setattr` found none aimed at the CLI module, and no test imports a moved name from `factory.cli`.

## Known gaps and uncertainties

- `factory/cli.py` also imports `_branch_tip` and `undeclared_protected` from `factory.gates`. The sub-ticket lists only `_parent_close_verified` and the commands.
  - These two are needed because `resolve` calls both of them. `resolve` stays in `factory/cli.py` until part E (T-0047.4) moves it to `factory/human.py`.
  - Without the two imports, `ruff` flags both names as undefined (F821), and `factory resolve --accept-paths` fails when it runs.
  - Part E's text already says `human.py` will import these same two names from `factory.gates`. After that move, T-0047.4 should drop them from `factory/cli.py`, and R11 (unused imports) will catch it if it does not.
  - I read this as the only way the sub-ticket can work, not as a change of design.
- In `factory/cli.py`, the new `from factory.gates import (...)` line is wrapped over two lines with a hanging indent. Its first line is 107 columns.
  - The other import lines in the file are single lines.
  - `ruff` here checks only F rules, so line length is not enforced.
  - Putting it on one line would save one line of the 100-line budget, but that line would be about 200 columns.

## Out-of-scope observations

- `factory/cli.py` still has the section comment `# ----- build half: sub-tickets, results, merge (parts B, D, G; local stand-in)`. After this move, that section holds only the sub-ticket and planning commands, so the words "results, merge" no longer describe it.
  - The design's rule is to move a section comment with its code, or drop it when its section is empty. This section is not empty.
  - Rewording the comment is outside this sub-ticket, so I left it.
- `docs/principles.md:106` still names `factory/cli.py` for the `ticket transition` and `run start` guards. That is still true, so Decision 11 leaves it alone.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW, REGRESSION and gate command passed on `c30b80f`, and M shows no moved definition changed its text.
ESCALATIONS: none
