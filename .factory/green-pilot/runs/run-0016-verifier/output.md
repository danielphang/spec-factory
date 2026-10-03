Commit: a946681a611133793f703f8ea616fcb60ce3c900

Environment: worktree `/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0016-verifier/wt`, detached at head `a946681a6` (merge of integration tip `b551d97cd` into `e28db6a25`). `git merge-base --is-ancestor b551d97cd HEAD` succeeds. `git diff --stat b551d97cd HEAD` lists only `factory/cli.py` (+14/-3), `tests/factory/test_results_commit.py` (+131 new) and `tests/factory/test_shepherd.py` (1 line, line 269 in the merged file, the `--output` argument of the merge-gate story's verifier `results record` call). Base runs used `git checkout --detach b551d97cd9797c72aa2f4b20170a7b2690ff2e58` in the same worktree, and then I returned to the head. The worktree had no `.venv` at the start. The first `uv run` created one from the lock. I installed nothing by hand. `git status --short` was empty at the end.

The nine WHEN commands were run verbatim from the worktree root under bash, on base and on head. I ran them again on head under `zsh -f`, and zsh gave the same output as bash.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
- no-commit-line-is-refused | NEW | spec WHEN (reviewer, no `Commit:`) | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS
- non-hex-commit-value-is-refused | NEW | spec WHEN (`Commit: HEAD`) | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS
- later-commit-line-naming-another-commit-is-refused | NEW | spec WHEN (`Commit: <head>` … `Commit: deadbeef00`) | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS
- verifier-without-commit-line-writes-no-ci-row | NEW | spec WHEN (verifier, `Gate suite: PASS`, no `Commit:`) | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=2 rows=[] events=0` | PASS
- earlier-commit-line-naming-another-commit-is-refused | REGRESSION | spec WHEN | `exit=2 rows=[] events=0` | `exit=2 rows=[] events=0` | PASS
- full-head-sha-is-recorded | REGRESSION | spec WHEN | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=0 rows=[reviewer.yaml ] events=1` | PASS
- abbreviated-sha-in-backticks-is-recorded | REGRESSION | spec WHEN | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | PASS
- killed-without-output-records-killed | REGRESSION | spec WHEN | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS
- killed-with-cut-off-output-records-killed | REGRESSION | spec WHEN | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS
- factory-suite-still-passes | REGRESSION | `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory` | `59 passed in 115.42s`, exit 0 | `68 passed in 112.80s`, exit 0 | PASS. The count is 59 + 9 new tests. The spec's "today's 55" was written before the integration tip added 4 factory tests, so the stated rule (base count + number of new tests) holds.
- Intermediate check (gate suite) | REGRESSION | see Gate suite | not run on base | PASS on head | PASS

Each NEW criterion failed on base in the way verification.md predicts: the verdict was recorded. Each REGRESSION criterion passed on both. No SPEC-DEFECT.

Extra red check (not required): I put back base `factory/cli.py` alone (`git checkout b551d97cd -- factory/cli.py`) and ran `tests/factory/test_results_commit.py` plus the merge-gate story `test_shepherd.py::test_a_merge_waits_for_every_checker_and_refuses_a_red_gate`. Result: `4 failed, 6 passed`. The 4 failures are exactly the 4 NEW-scenario tests, so the new tests can fail for what they claim. I then restored the file with `git checkout HEAD -- factory/cli.py`, and the tree was clean again.

Gate suite: PASS
- `uv run ruff check nanobot/`: `All checks passed!`, exit 0.
- `uv run --extra dev --with neonize==0.3.18.post0 /Users/dphang/dev/nanobot-upstream/scripts/full_suite_gate.py --root . --isolated-home --pytest-args "-n 2 --dist loadfile"`: exit 0. Summary: `5 failed, 7171 passed, 25 skipped in 137.17s`, `tests run: 7201`, `its failure set is within the baseline (5 known failure(s))`. All 5 failures are in the baseline: `tests/gateway/test_runtime.py::test_default_instance_preserves_released_gateway_paths`, `tests/cli/test_tui_launcher.py::test_launcher_keeps_the_tui_alive_while_an_existing_gateway_recovers`, two in `tests/lionbot/test_service_log_paths.py::TestLogPathsFollowTheInstance`, and `tests/config/test_config_paths.py::test_shared_and_legacy_paths_remain_global`. `git status --short` was empty after the gate, so `webui/package-lock.json` was not rewritten.
- My totals (7201 run, 25 skipped) differ from the implementer's reported 7326 run, 20 skipped. The gate still passes, so this does not change the verdict. I did not investigate why; the likely cause is environment differences in which tests are collected or skipped.

Probes (head, throwaway store, same harness shape as the WHEN lines). Each line is input → result → OK / CONCERN:
- P1: bare `Commit:` with the hex on the next line → exit 2, no rows, 0 events, stderr `Commit:  is not a commit id` → OK. This is the multi-line change the implementer disclosed. It matches the spec's per-line rule. The message shows an empty value with a double space, which is cosmetic (the reviewer's NIT).
- P2: head `abcdef01…`, `Commit: ABCDEF01` (uppercase abbreviation) → exit 0, `reviewer.yaml`, 1 event → OK. The value is lowercased before the prefix check.
- P3: `Commit: 0000000 (merge of x)` (trailing text) → exit 0, recorded → OK. The spec keeps trailing text allowed.
- P4: `Commit: 000000` (6 hex, below the minimum) → exit 2, nothing written, `is not a commit id` → OK.
- P5: 41 hex characters → exit 2, nothing written, `is not a commit id` → OK.
- P6: `**Commit:** <head>` → exit 2, `the output has no Commit: line` → OK per spec. This confirms the Risk the parent already declared: a checker that bolds the label will park its ticket.
- P7: indented `  Commit: <head>` only → exit 2, `no Commit: line` → OK per spec ("starts with `Commit:`").
- P8: CRLF line endings with `Commit: <head>\r\n` → exit 0, recorded → OK.
- P9: head `abcdef…`, `Commit: 0000000` → exit 2, `not the head abcdef012345` → OK. The check is not tied to the all-zero test head.
- P10: three `Commit:` lines naming the same head (full, abbreviated, backticked) → exit 0, recorded → OK.
- P11: lowercase `commit: <head>` only → exit 2, `no Commit: line` → OK. The match is case-sensitive, as the spec states.
- P12: `--killed` with `Commit: deadbeef00` → exit 2, nothing written → OK. This is today's killed-path refusal, and that code is unchanged in the diff.
- P13: `--killed` with `Commit: HEAD` → exit 0, `verifier.yaml`, 1 event → OK. Today's killed behaviour is kept, as the spec requires.
- P14: empty output file, no `--killed` → exit 2, `no Commit: line` → OK.

The probes show the check is general rather than fitted to the test inputs: it works with a non-zero head, either case, CRLF, multiple lines and length bounds.

STATUS: VERIFIED
CONFIDENCE: high. I ran every acceptance command verbatim on both base `b551d97cd` and head `a946681a6`. NEW criteria failed on base and passed on head, and REGRESSION criteria passed on both. Both gate commands exited 0 as written, the new tests fail against the base code, and 14 boundary probes behaved as the spec says.
ESCALATIONS: none
