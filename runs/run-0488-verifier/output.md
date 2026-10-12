Commit: 634117766e31f55980921ec1f9250d3d40e07c04 (branch `factory/T-0047.2`, base `700ce73e216d1fe5d218a9fe9b46e53545cf6674`, which is also `main`'s tip and `git merge-base HEAD main`)

Every command ran from the worktree root (or from a detached base worktree at `700ce73` in my scratch directory, now removed), through the fresh-HOME wrapper. The M script was taken from the GIVEN block of `.factory/store/specs/T-0047/v2.md` by an awk extract and written with `TMPDIR` set to my scratch directory.

Per criterion:
- NEW | setup.py scenario (`import factory.setup && grep ... factory/setup.py | ... | paste`) | base: `ModuleNotFoundError: No module named 'factory.setup'`, nothing printed, exit 1 (the reason the spec states) | PR: `STATE_DIR_LINE _add_store_checkout _copy_mismatch _exclude_store _git_toplevel _head_branch _ignored_files _new_instance_yaml _refuse_inside_store _revision _store_hint init_cmd paths_cmd store_migrate`, an exact match, exit 0 | PASS
- NEW (intermediate) | `uv run --frozen python -B -c 'import factory.setup'` | base: the same ModuleNotFoundError, exit 1 | PR: no output, exit 0 | PASS
- REGRESSION | drift scenario | base: not run | PR: `TEST_FILE_RE TICK_RE _check_drift _check_sibling_tests _sibling_drift _test_drift _tests_to_change_section` | PASS
- REGRESSION | common scenario | base: not run | PR: `_add_spec_version _in_flight _integration_head _rel fence out` | PASS
- REGRESSION | M, `(uv run --frozen python -B ${TMPDIR:-/tmp}/t0047-moved.py)` | base: not run | PR: `pairs=2 added=0 removed=0 lines=35` and nothing after it (35 is at most 100) | PASS
- REGRESSION | R1 | base: not run | PR: `factory/__main__.py factory/drive.py factory/stats.py` | PASS
- REGRESSION | R2 | base: not run | PR: `7 True True` | PASS
- REGRESSION | R3 `uvx ruff check --select F factory` | base: not run | PR: `All checks passed!`, exit 0 | PASS
- REGRESSION | R4 (suite in `/tmp/t0047-suite.*`, then `git diff --name-only main...HEAD -- tests`) | base: not run | PR: `576 passed in 583.67s (0:09:43)`, nothing after it | PASS
- REGRESSION | R5 | base: not run | PR: `0 0` | PASS
- REGRESSION | R6 | base: not run | PR: `0` | PASS
- REGRESSION | R7 | base: not run | PR: `0 2 2`. The `store.ensure_gitignore(root)` call that moved with `init_cmd` is counted through `factory/setup.py` | PASS
- REGRESSION | R8 | base: not run | PR: `0` | PASS
- REGRESSION | R9 | base: not run | PR: `0` | PASS
- REGRESSION | R10 | base: not run | PR: `0 12 1` | PASS
- REGRESSION | R11 `uvx ruff check --select F401,F841 factory tests` | base: not run | PR: `All checks passed!`, exit 0 | PASS
- REGRESSION | R12 (suite in `/tmp/t0044-suite.*`, then the tests diff) | base: `576 passed in 551.60s (0:09:11)`, nothing after it | PR: first run `1 failed, 575 passed in 552.80s (0:09:12)`. Rerun `576 passed in 547.63s (0:09:07)`, nothing after it | PASS on rerun (see ESCALATIONS)
- REGRESSION | R13 | base: not run | PR: `0` | PASS
- REGRESSION | R14 | base: not run | PR: `0 1` | PASS
- REGRESSION | R15 | base: not run | PR: `1 1` | PASS
- REGRESSION | R16 | base: not run | PR: `0` | PASS
- REGRESSION | R17 | base: not run | PR: `1 1` | PASS
- REGRESSION | R18 | base: not run | PR: `0 1 1 1` | PASS
- REGRESSION | R19 | base: not run | PR: `1 1 2` | PASS

Gate suite: PASS
- `git diff --check main...HEAD`: no output, exit 0.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `576 passed in 576.98s (0:09:36)`, exit 0.

Probes:
- I ran `bin/factory` from the PR head and from the base in matching throwaway git repositories under my scratch directory, then compared the outputs. The comparison masked checkout paths and SHAs. The calls were `init --repo-name probe`, `init` again, `paths` and `store migrate --to elsewhere`. The outputs match line for line. The first `init` writes `.gitattributes`, `.gitignore`, `openspec/config.yaml`, the schema and `decisions.md`, and adds the `factory-store` worktree at `.factory/state`. The second `init` writes nothing (`"written": []`), so it is still idempotent. `paths` prints the same keys. `store migrate` gives the same refusal, `the store ... is already the checkout of factory-store`, with exit 2. → OK
- I ran `init` from a directory inside the spec-factory store checkout. Both heads refuse it the same way, with `... is inside the store checkout ... (branch factory-store); run init from the repository root` and exit 2. This exercises the moved `_refuse_inside_store`. → OK
- I checked whether the test patch for `shutil.copy2` still applies. `tests/factory/test_store_migrate.py:157-163` patches the module attribute itself (`shutil.copy2 = altering`). `factory/setup.py` uses `import shutil` (line 7) and calls `shutil.copy2` through the module, so the patch reaches the moved code. That test passed in every suite run above. `factory/cli.py:24` imports `init_cmd, paths_cmd, store_migrate` from `factory.setup`, and `build_parser` wires them at lines 1400, 1405 and 1407. → OK

Protected paths the sub-ticket declares, both touched: `factory/cli.py` and `factory/setup.py`. The diff touches no other path.

Housekeeping: the first `uv run` created an untracked `.venv` in the worktree. `git status --short` there is empty, so `.venv` is ignored. I removed and pruned the base worktree.

STATUS: VERIFIED
CONFIDENCE: medium. Every acceptance command and both gates passed, M shows no definition text changed, and the probes behave the same on both heads. But one full-suite run on HEAD failed one test that I could not identify (see ESCALATIONS).
ESCALATIONS:
- One full-suite run on the PR head failed one test, and passed on rerun. My first R12 run printed `1 failed, 575 passed`. R12 runs the harness suite and prints only its last line, so I don't know which test failed. The rerun on HEAD passed, and so did R12 on the base, my gate run and my R4 run. Counting the implementer's runs too, the full suite failed 3 times out of 8 on this head and 0 times out of 2 on the base. The implementer named the failing test both times: `tests/factory/test_drive_build.py::test_build_step_lines_and_the_status_file_name_the_subticket_in_flight`, a timing-sensitive test. The parent spec and T-0047.1 record the same test failing once under load. A change that only moves definitions between modules, with M at `added=0 removed=0`, cannot plausibly change that test's timing. So I count R12 as passing on rerun, as the spec's note on R4 allows. The failure rate is still high enough to deserve its own issue, because it makes every harness verification depend on reruns.
