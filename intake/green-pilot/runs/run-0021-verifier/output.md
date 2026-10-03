Commit: d8a11792727455830cb78d4417f56a51104e0120

Environment: head checked out (detached, clean) in `/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0021-verifier/wt`. Changed files vs base `dd09a7cb1242d1e6e4637817498f5eae9f55a2f8` (`git diff --name-status`): `M factory/cli.py`, `A tests/factory/test_killed_checker.py`. No other file changed. `test_shepherd.py`, `test_results_commit.py` and `factory/workflows/build.js` are not edited. For base runs I extracted `factory/` and `bin/` at the base SHA with `git archive` into a scratch dir and ran the commands from its root. The five WHEN lines went into a script. A `diff` against spec lines 160/165/169/176/180 of the input showed they match character for character. I ran them under both bash and zsh.

Per criterion:
| Type | Command | Base (dd09a7cb1) | PR (d8a117927) | Result |
|---|---|---|---|---|
| NEW | killed-verifier-without-output-file-parks-as-budget-kill (WHEN verbatim) | `reviewer=0 verifier=1 decision=wait reason=results missing for the current head: verifier, ci` (the record exits 1 with `factory: FileNotFoundError: ... runs/R2/output.md`. I confirmed that by rerunning the record with stderr shown) | `reviewer=0 verifier=0 decision=park reason=budget kill: verifier` | PASS |
| NEW | killed-reviewer-without-output-file-parks-as-budget-kill (WHEN verbatim) | `verifier=0 reviewer=1 decision=wait reason=results missing for the current head: reviewer` | `verifier=0 reviewer=0 decision=park reason=budget kill: reviewer` | PASS |
| REGRESSION | killed-record-without-output-flag-still-records-killed (WHEN verbatim) | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS |
| NEW | killed-output-naming-another-commit-records-killed (WHEN verbatim) | `exit=2 rows=[] status=` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS |
| REGRESSION | unkilled-record-with-missing-output-file-still-fails (WHEN verbatim) | `exit=1 rows=[] events=0` | `exit=1 rows=[] events=0` | PASS |
| REGRESSION | factory-suite-passes-with-killed-checker-change: `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory` | `68 passed in 100.95s`, exit 0 (base code with the base test set. The new file does not exist at base) | `70 passed in 115.11s (0:01:55)`, exit 0 | PASS |
| NEW (intermediate) | `... uv run pytest -q -p no:cacheprovider tests/factory/test_killed_checker.py` | `2 failed in 6.34s`. Both cases fail in `Shepherd.ok` with `results record ... --killed: factory: FileNotFoundError: [Errno 2] No such file or directory: '.../state/runs/run-0007-verifier/output.md'` (and `run-0007-reviewer`). This is the reason the spec states. I got it by running the head's test file against the base `factory/cli.py` in a scratch copy, because the file does not exist at base. | `2 passed in 6.80s` | PASS |
| REGRESSION (intermediate) | `... uv run pytest -q -p no:cacheprovider tests/factory/test_results_commit.py` (unedited) | n/a (#16's file is in base. It was covered by the 68-pass base suite run) | `9 passed in 1.43s` | PASS |

Each NEW criterion fails on base for the reason the spec states (`FileNotFoundError` for the first two and the intermediate check, and the killed `Commit:` refusal, exit 2, for the fourth). Each one passes on the PR. Each REGRESSION criterion passes on both. Bash and zsh gave the same output on both trees. I also re-ran the five WHEN lines on head after uv had created the worktree `.venv`, and the results were the same. The first run used `python3` from PATH, because `bin/factory` falls back to it when there is no `.venv`.

Gate suite: PASS
- `uv run ruff check nanobot/`: `All checks passed!`, exit 0.
- `uv run --extra dev --with neonize==0.3.18.post0 /Users/dphang/dev/nanobot-upstream/scripts/full_suite_gate.py --root . --isolated-home --pytest-args "-n 2 --dist loadfile"`: exit 0. Result: `5 failed, 7173 passed, 25 skipped in 134.67s`, with the message "its failure set is within the baseline (5 known failure(s))". The 5 failures are the known baseline set: `tests/gateway/test_runtime.py::test_default_instance_preserves_released_gateway_paths`, `tests/cli/test_tui_launcher.py::test_launcher_keeps_the_tui_alive_while_an_existing_gateway_recovers`, two in `tests/lionbot/test_service_log_paths.py::TestLogPathsFollowTheInstance`, and `tests/config/test_config_paths.py::test_shared_and_legacy_paths_remain_global`. None is in `tests/factory`.
- `git status --short` in the worktree was empty after all runs. Nothing is staged or modified.

Probes (run from head and from base, each in a throwaway `FACTORY_STATE`):
- P1: killed verifier, `--output` is a directory → head `exit=0 status=KILLED`, base `exit=1 IsADirectoryError` → OK. The killed path never opens the file, whatever the path is. It is not special-cased to a missing file.
- P2: killed verifier, `--output` holds a full `Commit: <head>` / `Gate suite: PASS` / `STATUS: VERIFIED` output → head `exit=0 rows=[verifier.yaml ] status=KILLED`, with no `ci.yaml` row → OK. A killed run still writes no `ci` row and cannot be turned into a pass.
- P3: killed reviewer, `--output` holds bytes that are not UTF-8 → head `exit=0 status=KILLED`, base `exit=1 UnicodeDecodeError` → OK.
- P4: unkilled verifier whose output says `Commit: deadbeef00` → head and base both `exit=2`, `the output says Commit: deadbeef00, not the head 000000000000` → OK. The unkilled `Commit:` check is unchanged.
- P5: unkilled reviewer with no `Commit:` line → head and base both `exit=2`, `the output has no Commit: line` → OK.
- P6: unkilled verifier with a valid head `Commit:` and `Gate suite: PASS` → head and base both write `ci.yaml` and `verifier.yaml`, with `ci=PASS` → OK. The verifier status was `UNKNOWN` on both trees because my probe output had no full trailer. That is the same on both, so it is not a change.
- P7: killed verifier with `--head abc` → head and base both `exit=2`, `--head must be a full commit SHA` → OK. Validation still runs before the killed path.

The killed path is general: it records KILLED for any `--output` and does not read it. The unkilled path behaves the same on base and head in every probe. I also read `factory/workflows/build.js:91-95` and `:139-140` on head. The new test's call sequence matches them: `run finish --status-override KILLED`, `run cleanup` for checkers, and `results record ... --output ${r.outputPath} --run ${r.runId} --killed`.

Out-of-scope observations:
- Running the gate made uv create `.venv` in the verifier worktree, and `uv run --extra dev` synced 25 dev packages into it. It is gitignored, and `git status` stays clean.
- The new test hand-copies the build loop's call shape. A later change to `build.js` would not be caught by it, as the PR description itself notes.

STATUS: VERIFIED
CONFIDENCE: high. I ran every acceptance command verbatim on head and on base under bash and zsh, and each matched its expected result. The new test fails on base with the stated `FileNotFoundError`. Both gate commands exited 0, and the probes show the fix is not tied to the tested inputs.
ESCALATIONS: none
