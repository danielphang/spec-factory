Commit: 359b3c6c88c10f308523d7d733baf60b5797cdcc (branch `factory/T-0047.1`, worktree clean; `git merge-base HEAD main` = `6203096`, which is also `main`'s tip)

Base checkout for the "base" column: a fresh `git clone` of the repo in this run's scratch directory, detached at `62030967710765e996fb3d752386f9ce8dec6abc` (its `main` resolves to the same SHA). Every command below ran through the "Running code" wrapper (fresh HOME), from the checkout's root, with `TMPDIR` pointed at a per-checkout directory under scratch so the M heredoc wrote `t0047-moved.py` there. Logs: `scratch/quick-pr.log`, `scratch/quick-base.log`, `scratch/suite.log`, `scratch/gate-full.log`.

Per criterion:
- NEW | drift module names (`uv run --frozen python -B -c 'import factory.drift' && grep ... | paste -sd' ' -`) | base: `ModuleNotFoundError: No module named 'factory.drift'`, exit 1, nothing printed | PR: `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section` | PASS
- NEW | common module names (`uv run --frozen python -B -c 'import factory.common' && grep ... | paste -sd' ' -`) | base: `ModuleNotFoundError: No module named 'factory.common'`, exit 1, nothing printed | PR: `_add_spec_version _in_flight _integration_head _rel fence out` | PASS
- NEW | M (`(uv run --frozen python -B ${TMPDIR:-/tmp}/t0047-moved.py)`, after the GIVEN heredoc run once at column 0) | base: `pairs=0 added=0 removed=0 lines=0` (fails "n at least 1", as the sub-ticket states) | PR: `pairs=1 added=0 removed=0 lines=19`, nothing after it | PASS
- NEW (intermediate) | `uv run --frozen python -B -c 'import factory.drift' && uv run --frozen python -B -c 'import factory.common'` | base: `ModuleNotFoundError: No module named 'factory.drift'`, exit 1 | PR: exit 0, nothing printed | PASS
- REGRESSION | R1 | base: not run | PR: `factory/__main__.py factory/drive.py factory/stats.py` | PASS
- REGRESSION | R2 | base: not run | PR: `7 True True` | PASS
- REGRESSION | R3 `uvx ruff check --select F factory` | base: not run | PR: `All checks passed!`, exit 0 | PASS
- REGRESSION | R4 | base: not run | PR: `576 passed in 563.27s (0:09:23)`, nothing after it | PASS
- REGRESSION | R5 | base: not run | PR: `0 0` | PASS
- REGRESSION | R6 | base: not run | PR: `0` | PASS
- REGRESSION | R7 | base: not run | PR: `0 2 2` | PASS
- REGRESSION | R8 | base: not run | PR: `0` | PASS
- REGRESSION | R9 | base: not run | PR: `0` | PASS
- REGRESSION | R10 | base: not run | PR: `0 12 1` | PASS
- REGRESSION | R11 `uvx ruff check --select F401,F841 factory tests` | base: not run | PR: `All checks passed!`, exit 0 | PASS
- REGRESSION | R12 | base: not run | PR: `576 passed in 552.92s (0:09:12)`, nothing after it | PASS
- REGRESSION | R13 | base: not run | PR: `0` | PASS
- REGRESSION | R14 | base: not run | PR: `0 1` | PASS
- REGRESSION | R15 | base: not run | PR: `1 1` | PASS
- REGRESSION | R16 | base: not run | PR: `0` | PASS
- REGRESSION | R17 | base: not run | PR: `1 1` | PASS
- REGRESSION | R18 | base: not run | PR: `0 1 1 1` | PASS
- REGRESSION | R19 | base: not run | PR: `1 1 2` | PASS

(The same R1-R3 and R5-R19 commands were also run on the base clone as a side effect of the shared script and printed the same values there; R4/R12 were not run on base.)

Gate suite: PASS
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 555.55s (0:09:15)`, exit 0 (full log `scratch/gate-full.log`). This is a separate run from R4 and R12, as written, without `TMPDIR` or `tail`.

Probes:
- Byte-for-byte beyond the M script (M compares definitions only, not the comments and blank lines between them): `diff` of `git show 6203096:factory/cli.py | sed -n '249,370p'` against `sed -n '11,132p' factory/drift.py`, and of base lines 30-35, 548-567 and 1964-1988 against `factory/common.py` lines 12-17, 20-39 and 42-66 → all four diffs empty; both new files end in a newline → OK
- What `factory/cli.py` gained: `git diff main...HEAD -- factory/cli.py | grep '^+'` → exactly the two import lines (`from factory.common import _add_spec_version, _in_flight, _rel, fence, out`, `from factory.drift import _check_drift, _check_sibling_tests`); 181 removed lines. Line counts: cli.py 1841, common.py 66, drift.py 132, total 2039 against 2020 on base, which is the `lines=19` M reports → OK
- Names resolve to the new modules and nothing imports `factory.cli` indirectly: from a fresh interpreter, `cli._check_drift.__module__` = `factory.drift`; `cli.fence`, `cli.out`, `cli._in_flight` → `factory.common`; `common.fence` reads `common._in_flight`; `sys.modules` after `import factory.cli` holds no module outside the expected set. `cli.py` still calls `_in_flight` at line 1390 (`store_migrate`), so importing it is needed, as the PR description says → OK
- Fence behaviour on a throwaway store (temp dir, `instance` checks stubbed in-process only): `_in_flight` returns `['run-0001-x']` for a store with one run in flight and `[]` for a store with no `tickets/` dir; `fence` refuses with `role runs may not write the live store (...; in flight: ...)`, passes with `FACTORY_DISPATCH=1`, and refuses by location from inside `runs/` with `in_flight=False` → OK
- Parser still builds: `uv run --frozen python -B -m factory --help` prints the usage with all 20 subcommands; `run start --help` prints its usage → OK
- `git diff --name-only main...HEAD -- tests` empty on the PR; no test names any moved `cli.` attribute (grep of `tests/factory` for `cli.(fence|_in_flight|out|_rel|_check_drift|...)` and `setattr(cli` → no hits), so the by-name imports move no patch point → OK

Out-of-scope observations:
- The PR description says `factory/cli.py` "is now 1,839 lines"; `wc -l` gives 1841. The M total (`lines=19`) is consistent with 1841. Description-only inaccuracy; no criterion depends on it.
- Running the acceptance commands created `.venv` in the worktree (uv's default); it is ignored by git and the worktree stays clean.

STATUS: VERIFIED
CONFIDENCE: high. Every NEW criterion fails on base for the reason the spec states and passes on 359b3c6; all nineteen REGRESSION checks, both gates and three independent full suite runs (576 passed each) pass; a line-range diff confirms the moved ranges are identical to base including the text between definitions.
ESCALATIONS: none
