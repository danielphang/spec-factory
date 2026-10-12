Commit: 9349e5762e727e570bf0bd0e7ceb90c865387a71 (branch `factory/T-0047.4`, worktree `.factory/store/runs/run-0493-verifier/wt`, clean). Base: 43265a02f3ad943ebed963d7246495418c3d2ee8, which is also `main`'s tip and `git merge-base HEAD main`. I ran the base checks in an extracted copy of that commit (`git archive 43265a0`, in `scratch/base`). Every command went through the "Running code" wrapper. Raw logs are in `scratch/pr.out`, `scratch/base.out`, `scratch/r4.out`, `scratch/r12.out` and `scratch/gate.out`.

Per criterion:
- NEW | human.py module scenario (`import factory.human && grep ... factory/human.py ...`) | base: `ModuleNotFoundError: No module named 'factory.human'`, nothing printed, exit 1 | PR: `_approval_dir _by _copy_record _next_n _refuse_unless_applies _restart_note _set_aside_failed_rows _supersede approve_spec decision_add request_changes resolve spec_amend` (exact match) | PASS
- NEW | `echo "$(wc -l < factory/cli.py ...) $(grep -cE '^(def build_parser\(|def main\(|ROLES = )' factory/cli.py)"` | base: `1198 3` | PR: `882 3` (882 is below 900, and the count is 3) | PASS
- NEW (intermediate) | `uv run --frozen python -B -c 'import factory.human'` | base: `ModuleNotFoundError`, exit 1 | PR: prints nothing, exit 0 | PASS
- REGRESSION | drift module scenario | base: not run | PR: `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section` | PASS
- REGRESSION | common module scenario | base: not run | PR: `_add_spec_version _in_flight _integration_head _rel fence out` | PASS
- REGRESSION | setup module scenario | base: not run | PR: `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate` | PASS
- REGRESSION | gates module scenario | base: not run | PR: `DECLARED_RE MAX_CONFLICT_RUNS REVIEWER_STATUSES VERIFIER_STATUSES _branch_tip _in_repo _parent_close_verified _reused_subticket_run _verifier_rows archive_cmd declared_paths merge_cmd results_record results_show ticket_head ticket_join ticket_parent_check undeclared_protected` | PASS
- REGRESSION | README and principles scenario | base: not run | PR: `1 0 1 0 3` | PASS
- REGRESSION | M (`uv run --frozen python -B ${TMPDIR:-/tmp}/t0047-moved.py`). I wrote the script from the parent spec v2.md lines 328-357, verbatim, with TMPDIR set to scratch | base: not run | PR: `pairs=4 added=0 removed=0 lines=54`, and nothing after it. No definition's text changed, and 54 is at most 100. This sub-ticket's own share is +8 lines: cli.py goes from 1198 to 882 (-316) and human.py is new at 324 lines | PASS
- REGRESSION | R1 | base: not run | PR: `factory/__main__.py factory/drive.py factory/stats.py` | PASS
- REGRESSION | R2 | base: not run | PR: `7 True True` | PASS
- REGRESSION | R3 `uvx ruff check --select F factory` | base: not run | PR: `All checks passed!`, exit 0 | PASS
- REGRESSION | R4 (suite in `/tmp/t0047-suite.*`, then `git diff --name-only main...HEAD -- tests`) | base: not run | PR: `576 passed in 599.38s (0:09:59)`, and nothing after it | PASS
- REGRESSION | R5 | base: not run | PR: `0 0` | PASS
- REGRESSION | R6 | base: not run | PR: `0` | PASS
- REGRESSION | R7 | base: not run | PR: `0 2 2` | PASS
- REGRESSION | R8 | base: not run | PR: `0` | PASS
- REGRESSION | R9 | base: not run | PR: `0` | PASS
- REGRESSION | R10 | base: not run | PR: `0 12 1` | PASS
- REGRESSION | R11 `uvx ruff check --select F401,F841 factory tests` | base: not run | PR: `All checks passed!`, exit 0 | PASS
- REGRESSION | R12 (suite in `/tmp/t0044-suite.*`, then the tests diff) | base: not run | PR: `576 passed in 599.38s (0:09:59)`, and nothing after it | PASS
- REGRESSION | R13 | base: not run | PR: `0` | PASS
- REGRESSION | R14 | base: not run | PR: `0 1` | PASS
- REGRESSION | R15 | base: not run | PR: `1 1`. The approve_spec transition now counts from factory/human.py | PASS
- REGRESSION | R16 | base: not run | PR: `0` | PASS
- REGRESSION | R17 | base: not run | PR: `1 1` | PASS
- REGRESSION | R18 | base: not run | PR: `0 1 1 1` | PASS
- REGRESSION | R19 | base: not run | PR: `1 1 2` | PASS

Gate suite: PASS
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 603.73s (0:10:03)`, exit 0.

How the suites were run: R4, R12 and the gate suite ran at the same time, as background processes, and I waited for all three to finish before writing this. Running them together put the machine under load, and the concurrent-checker test that the spec calls flaky still passed in all three runs.

Probes:
- The whole argparse tree, base against PR. I walked every one of the 47 subparsers and compared their `format_help()` output and the handler bound to each (`scratch/helpwalk.py`, run with COLUMNS=100) → the help text is identical. Exactly five handlers changed module, from `factory.cli.X` to `factory.human.X`: approve-spec, request-changes, resolve, decision add and spec amend. The CLI surface is unchanged → OK
- I called each moved command (`approve_spec`, `request_changes`, `resolve`, `decision_add`, `spec_amend`) with a missing ticket `T-9999` on an empty temp store. I also called the helpers on these inputs: `_next_n` on an empty directory and on one with 3 records, `_refuse_unless_applies` on an empty spec and on a malformed one with NUL bytes, and `_approval_dir`. Each call went through `factory.cli` on base and `factory.human` on the PR (`scratch/probe.py`) → the outputs are byte-identical. All five commands raise `factory.store.Refused: no ticket T-9999`, `_next_n` returns 1 and then 4, and both specs raise the same refusal text → OK
- The `fence` import. The sub-ticket says human.py imports `fence` from `factory.common`, and it does not. `spec_amend` assigns a local `fence = "```"` (human.py:86-88), so inside that function the name is always the local. No other moved definition calls `fence`, and ruff F821 reports no undefined names. Adding the import would only produce the F401 that R3 and R11 forbid. This disagrees with the scope text but harms nothing, and the implementer disclosed it → OK
- Files changed: `git diff --stat` base..HEAD shows only `factory/cli.py` and `factory/human.py`, the two protected paths the sub-ticket declares. Nothing under tests/ or docs changed → OK

STATUS: VERIFIED
CONFIDENCE: high. All three NEW criteria failed on base and pass on the PR, every regression check and both gates passed on head 9349e57, and probes show the moved commands behave the same as on base.
ESCALATIONS: none
