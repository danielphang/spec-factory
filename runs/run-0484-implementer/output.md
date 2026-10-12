Sub-ticket: T-0047.2, Move instance and store setup to factory/setup.py (parent T-0047, spec `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0047/v2.md`)
Branch: `factory/T-0047.2` in `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0047.2`, base `700ce73e216d1fe5d218a9fe9b46e53545cf6674`, head `634117766e31f55980921ec1f9250d3d40e07c04` (one commit).

## What changed

This PR moves the harness's setup commands out of `factory/cli.py` into a new module, `factory/setup.py`. The setup commands are `factory init` (prepare a repository for the factory), `factory store migrate` (move the store, the factory's on-disk record of tickets and runs) and `factory paths` (print the paths a dispatcher needs). No command's behaviour changes. This is part C of the T-0047 split of `factory/cli.py`.

**C. `factory/setup.py`.**
- New module. It has a one-line docstring, `from __future__ import annotations`, and the imports its definitions use: `json`, `os`, `re`, `shutil`, `subprocess`, `sys`, `Path`, `yaml`, `factory.{gitops, instance, specstore, store}`, `_in_flight`, `fence` and `out` from `factory.common`, and `Refused`.
- The body is the block from `def _git_toplevel(` up to the blank lines before `def stats_cmd(`. That is 331 lines, copied byte for byte by a script that slices the file, in their original order: `_git_toplevel`, `_new_instance_yaml`, `_revision`, `_refuse_inside_store`, `_head_branch`, `_add_store_checkout`, `_exclude_store`, `_store_hint`, `init_cmd`, `STATE_DIR_LINE`, `_ignored_files`, `_copy_mismatch`, `store_migrate`, `paths_cmd`.
- It uses `import shutil` and still calls `shutil.copy2` through the module (Decision 6). The test in `tests/factory/test_store_migrate.py` that replaces `shutil.copy2` therefore still reaches the moved code. That test passed in every suite run below.
- `factory/cli.py` drops those 333 lines, which are the 331 moved lines and the two blank lines after them. It adds `from factory.setup import init_cmd, paths_cmd, store_migrate` for `build_parser`, and drops two imports it no longer uses: `import os` and `_in_flight`. The other imports it shared with the moved code (`json`, `shutil`, `subprocess`, `sys`, `yaml`, `specstore`) are still used in `factory/cli.py`, and ruff F401 confirms it.
- `stats_cmd` stays in `factory/cli.py` (Decision 4).
- `factory/cli.py` goes from 1,841 to 1,508 lines.

## Acceptance results

Each command ran through the fresh-HOME wrapper from the worktree root. Results are the actual output.

- NEW, Instance and store setup live in factory/setup.py.
  - Before: `ModuleNotFoundError: No module named 'factory.setup'`, nothing printed, exit 1.
  - After: `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate`, which matches exactly.
- Intermediate (NEW), `uv run --frozen python -B -c 'import factory.setup'`. Before: the same ModuleNotFoundError. After: exit 0, nothing printed.
- REGRESSION, drift scenario (T-0047.1): `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section`.
- REGRESSION, common scenario (T-0047.1): `_add_spec_version _in_flight _integration_head _rel fence out`.
- REGRESSION, M, the check that the split moves code without rewriting it. Its GIVEN block was extracted verbatim from v2.md into the scratch directory and run with `TMPDIR` set to that directory. Output: `pairs=2 added=0 removed=0 lines=35`, and nothing after it. The 35 lines are 19 from T-0047.1 and 16 from this sub-ticket, so the total is within the 100-line limit.
- R1: `factory/__main__.py factory/drive.py factory/stats.py`
- R2: `7 True True`
- R3: `All checks passed!`, exit 0
- R4:
  - First run on HEAD: `1 failed, 575 passed in 549.04s`. Gloss: R4 is the full harness suite run under its own `/tmp` directory, plus a check that no test file changed.
  - The same command on base `700ce73` (a temporary checkout in scratch, since removed): `576 passed in 591.45s`, with nothing after it.
  - Rerun on HEAD: `576 passed in 552.33s (0:09:12)`, with nothing after it. See Known gaps.
- R5: `0 0`
- R6: `0`
- R7: `0 2 2`. The `store.ensure_gitignore(root)` call that moved with `init_cmd` is still counted, because R7 reads `factory/setup.py`.
- R8: `0`
- R9: `0`
- R10: `0 12 1`
- R11: `All checks passed!`, exit 0
- R12: `576 passed in 572.85s (0:09:32)`, with no later lines (no file under `tests/` changed).
- R13: `0`
- R14: `0 1`
- R15: `1 1`
- R16: `0`
- R17: `1 1`
- R18: `0 1 1 1`
- R19: `1 1 2`

Gates, each run exactly as written:
- `git diff --check main...HEAD`: exit 0, no output.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`:
  - First run: `1 failed, 575 passed in 555.53s`, with the failure `tests/factory/test_drive_build.py::test_build_step_lines_and_the_status_file_name_the_subticket_in_flight`.
  - Rerun: `576 passed in 550.28s (0:09:10)`, exit 0.

## Tests added/changed

None. The sub-ticket says "Interim tests: none" and "Tests to change: none". The behaviour under test is where code lives, which the acceptance commands check directly. `git diff --name-only main...HEAD -- tests` prints nothing.

## Known gaps and uncertainties

- **One timing test failed in two of four full-suite runs on HEAD.** The test is `test_drive_build.py::test_build_step_lines_and_the_status_file_name_the_subticket_in_flight`.
  - Both failures had the same cause. The test's two checker runs (reviewer and verifier) each sleep 2 seconds. In both failures, T-0001.2's reviewer ended `KILLED` before the expected line `T-0001.2 "Two": parked: SPEC-DEFECT from verifier` was printed. The earlier assertion on the order the runs were seen passed.
  - Run on its own on HEAD, the test passed 3 times out of 3, in about 6 seconds each.
  - The full suite passed on base once (576 passed). On HEAD, the next two full runs passed: R12 and the R4 rerun. The gate rerun passed too.
  - The machine's load average was about 3 on 10 cores throughout.
  - The parent spec reports the same test failing once under load on the prototype (v2.md, around line 98). T-0047.1's implementer reported it failing once as well (run-0474).
  - This change only moves definitions between modules, and M shows that no definition's text changed. So I read the failures as the known timing flake, not a regression. I did not prove that: a failure 2 times in 4 on HEAD against 0 in 1 on base is weak evidence either way.
- **The `# -----` section comment stays in `factory/cli.py`.** The comment is `# ----- spec store (doc §Harness, Spec store; part K) ---...`. The design says to move a section comment with its code, or drop it where its section is now empty. Here that section is not empty in `factory/cli.py`: `stats_cmd`, `spec_tasks` and the gate helpers still follow it. So I left the comment there, and `factory/setup.py` relies on its module docstring instead. Moving the comment would leave `stats_cmd` under the "human surface" header.
- **One script ran without the wrapper.** My one-off move script (`scratch/move.py`) ran through plain `uv run`, without the fresh-HOME wrapper. It only reads and writes `factory/cli.py` and `factory/setup.py` in the worktree. Every test and check above did run through the wrapper.
- **A temporary base checkout was added and removed.** To run R4 on base, I added a detached git worktree at `scratch/base`, then removed and pruned it. `git worktree list` no longer shows it.

## Out-of-scope observations

- One full suite run takes about 9 to 10 minutes on this machine, close to the 10-minute limit a single tool call allows. I had to run it in the background and wait for it.
- The timing test above is fragile under CPU load. It may deserve its own issue: its 2-second sleeps decide whether a checker is killed. I did not change it.

## Responses to findings

Not applicable (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The move is checked by machine (M: added=0 removed=0), all acceptance commands and both gates passed on HEAD, and the one failing test is a timing test known to be unreliable under load that passed on rerun.
ESCALATIONS: none
