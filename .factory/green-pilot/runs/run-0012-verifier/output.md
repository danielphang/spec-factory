Commit: e28db6a255e8cd0032c67ada62b74b6681cd511d

Bottom line: the code change works. All nine scenario commands, run as written, give the THEN output on the head under bash and under zsh. The four NEW criteria fail on base for the reason the spec gives, and the five REGRESSION criteria pass on both. `tests/factory` passes. Probes show the check is general and not tailored to the tested inputs. The status is still SPEC-DEFECT, because the full-suite gate command cannot run as written. On this checkout it exits 2 before running any test. Even with that fixed, its pytest run uses the integration checkout (`/Users/dphang/dev/nanobot-upstream`), not this head. So the gate as specified does not check this PR. When I ran the same gate script and baseline against the head tree and against base+head, both passed (details below).

Setup. Verifier worktree `/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0012-verifier/wt`, detached at e28db6a25, `git status` clean before and after.
- Base b7d09a8db, taken with `git archive` into `scratchpad/v12/base`.
- The branch is 5 commits behind base. The merge-base is f8f40e0c5. `git diff --stat b7d09a8db...HEAD` shows only `factory/cli.py` (+17/-4), `tests/factory/test_results_commit.py` (new, 131 lines) and `tests/factory/test_shepherd.py` (1 line).
- `git merge-tree --write-tree b7d09a8db e28db6a25` merges cleanly, giving tree 3b823cc1b. I extracted it to `scratchpad/v12/merged`.
- The nine scenario commands are in `scratchpad/v12/cmds.txt`. A `diff` against the WHEN text pulled out of input.md printed `IDENTICAL`.
- (scratchpad = `/private/tmp/claude-501/-Users-dphang-dev-nanobot/c69bfd1d-97a6-43e3-9d5a-a517c28d382c/scratchpad`)

## Per criterion
The scenario commands were run from the repo root, under both bash and zsh. Both shells gave identical output on base and on PR.

| Kind | Criterion | base (b7d09a8db) | PR (e28db6a25) | Result |
|---|---|---|---|---|
| NEW | no-commit-line-is-refused | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS |
| NEW | non-hex-commit-value-is-refused | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS |
| NEW | later-commit-line-naming-another-commit-is-refused | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS |
| NEW | verifier-without-commit-line-writes-no-ci-row | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=2 rows=[] events=0` | PASS |
| REGRESSION | earlier-commit-line-naming-another-commit-is-refused | `exit=2 rows=[] events=0` | `exit=2 rows=[] events=0` | PASS |
| REGRESSION | full-head-sha-is-recorded | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=0 rows=[reviewer.yaml ] events=1` | PASS |
| REGRESSION | abbreviated-sha-in-backticks-is-recorded | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | PASS |
| REGRESSION | killed-without-output-records-killed | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS |
| REGRESSION | killed-with-cut-off-output-records-killed | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS |
| REGRESSION | factory-suite-still-passes (`PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory`) | `58 passed in 107.57s`, exit 0 | `64 passed in 97.00s`, exit 0 | PASS |
| REGRESSION | Intermediate gate check (lint + full-suite gate, as written) | not run on base | lint: `All checks passed!` exit 0. Full-suite gate: exit 2 (below) | SPEC-DEFECT |

The scenario WHEN lines run `bin/factory`. No `.venv` existed at first, so `bin/factory` fell back to `python3`. Later runs used the worktree's `.venv`. The results were the same in both cases.

Notes on factory-suite-still-passes:
- The criterion says the count is "55 + new". 55 is the merge-base f8f40e0c5 count. Base b7d09a8db has 58. The head has 64 = 55 + 9. The base+head merge tree, with the same command, gives `67 passed in 110.56s`, exit 0, which is 58 + 9. The "55" in the criterion is stale but harmless.
- Environment caveat: the command as written ran blue's pytest, `/Users/dphang/dev/nanobot/.venv-test/bin/pytest`, under python3.14. `uv run which pytest` shows this, and it happens because `pytest` is only in the `dev` optional extra and is not installed by plain `uv run`. Collection and imports still came from the worktree, since rootdir and the conftest are in the worktree.
- I re-ran it with the project interpreter: `uv run --extra dev pytest -q -p no:cacheprovider tests/factory` gave `64 passed in 64.17s`, and `which pytest` was `wt/.venv/bin/pytest`.

Check that part B was needed: in a scratch copy of the head, I reverted only line 268 of test_shepherd.py back to `str(red)`. `test_a_merge_waits_for_every_checker_and_refuses_a_red_gate` then fails with `results record: Commit: HEAD is not a commit id`. So the one declared guardrail edit is required, and it is the only existing-test change in the diff.

## Gate suite: FAIL as written (harness defect, not the PR). The substitute runs PASS.

1. `uv run ruff check nanobot/` printed `All checks passed!`, exit 0. Ruff on the three changed files: `All checks passed!`.
2. `uv run --with neonize==0.3.18.post0 /Users/dphang/dev/nanobot-upstream/scripts/full_suite_gate.py --isolated-home --pytest-args "-n 2 --dist loadfile"`, run from the worktree, exited 2:
   ```
   [full-suite-gate] FAIL: pytest is not importable under /Users/dphang/.cache/uv/builds-v0/.tmpW6ZtnV/bin/python
   ```
   Cause: pyproject.toml puts pytest under `[project.optional-dependencies]` (line 93), and `uv run` without `--extra dev` does not install it. That makes this fail on every fresh worktree, at base too. The implementer hit the same error on its first attempt.
3. A second defect would remain even with pytest present. The gate script runs pytest with `cwd=REPO_ROOT` (`scripts/full_suite_gate.py`, `_run_pytest`: `subprocess.run(cmd, cwd=REPO_ROOT, ...)`), and `REPO_ROOT = Path(__file__).resolve().parent.parent` is `/Users/dphang/dev/nanobot-upstream`. So the "gate on the head" collects and imports the integration checkout. Shown with the gate's interpreter (`uv run --extra dev --with neonize==0.3.18.post0`) from the worktree:
   - `pytest --collect-only tests/factory/test_results_commit.py` with cwd=upstream gives `ERROR: file or directory not found` (rc 4).
   - `tests/factory` from upstream gives `58 tests collected`, the base count, not the head's 64.
   - `import factory.cli, nanobot` with cwd=upstream resolves to `/Users/dphang/dev/nanobot-upstream/factory/cli.py` and `/Users/dphang/dev/nanobot-upstream/nanobot/__init__.py`.

   Even when it passes, this command certifies the integration branch, not the PR.
4. Substitute evidence. I used the same gate script and baseline. Upstream's working copies of `scripts/full_suite_gate.py` and `full_suite_baseline.txt` are identical to b7d09a8db (`git diff --quiet`). The command was `uv run --extra dev --with neonize==0.3.18.post0 scripts/full_suite_gate.py --isolated-home --pytest-args "-n 2 --dist loadfile"`, run with green's `uv.lock` copied in, as `environment_files` does:
   - Head tree (git archive of e28db6a25, plus the integration gate script and baseline): `5 failed, 7167 passed, 25 skipped`, `the suite ran (7197 tests) and its failure set is within the baseline (5 known failure(s))`. PASS.
   - Base+head merge tree 3b823cc1b: `5 failed, 7170 passed, 25 skipped`, `the suite ran (7200 tests) and its failure set is within the baseline (5 known failure(s))`. PASS.
   - The 5 failures were the same in both runs: `tests/gateway/test_runtime.py::test_default_instance_preserves_released_gateway_paths`, `tests/cli/test_tui_launcher.py::test_launcher_keeps_the_tui_alive_while_an_existing_gateway_recovers`, the two `tests/lionbot/test_service_log_paths.py::TestLogPathsFollowTheInstance` tests, and `tests/config/test_config_paths.py::test_shared_and_legacy_paths_remain_global`. All are within the baseline.
   - Exit codes are inferred from the gate's success line. I ran it under zsh, where `${PIPESTATUS[0]}` printed empty.

## Probes
Each probe used a fresh store, head = forty zeros unless stated, and `bin/factory results record` without `--killed` unless stated. Format: input → result → verdict.
- No `Commit:` line → exit 2, stderr `results record: the output has no Commit: line`, no rows or events → OK
- `Commit: HEAD` → exit 2, `Commit: HEAD is not a commit id` → OK
- `Commit: 000000` (6 hex) → exit 2, not a commit id → OK
- `Commit: 0000000` (7 hex, no backticks) → exit 0, reviewer.yaml, 1 event → OK
- 41 hex characters → exit 2, not a commit id → OK
- `Commit:` with an empty value → exit 2 (`Commit:  is not a commit id`) → OK
- The value on the next line (`Commit:\n<sha>`) → exit 2 → OK. The old regex accepted this across the newline. The implementer flagged the change, and it matches the spec's "a line starting with Commit:".
- `Commit: <sha> (head of factory/T-0001.1)` (trailing text) → exit 0 → OK, as the spec decided
- `Commit: <sha>xyz` → exit 2 → OK
- `Commit: <full sha>` then ``Commit: `0000000` `` (two lines, both naming the head) → exit 0 → OK
- `Commit: <sha>` then `Commit: HEAD` → exit 2 → OK
- `verifier`, `Commit: <sha>`, then `Gate suite: PASS`, then `Commit: deadbeef00` → exit 2, no ci row → OK
- Head `abcdef01…`, `Commit: ABCDEF0` (uppercase) → exit 0 → OK. Head `abcdef01…`, `Commit: abcdef1` → exit 2 with the mismatch message → OK. The check is not tied to the all-zero test head.
- CRLF line endings → exit 0 → OK
- Empty file → exit 2 → OK
- `**Commit:** <sha>`, `  Commit: <sha>` (indented) and `commit: <sha>` (lower case) as the only line → exit 2, "no Commit: line" → CONCERN, but it is the spec's declared Risk and is out of scope. A real checker that formats the line this way will park its ticket.
- `Commit: <sha>` then an indented `  Commit: deadbeef00` → exit 0 → CONCERN, minor. An indented line is not a "line that starts with `Commit:`", so this follows the spec. It is a narrow way to get a second commit id past the every-line rule.
- `--killed` with `Commit: HEAD` → exit 0, KILLED. `--killed` with `Commit: deadbeef00` → exit 2. `--killed` with `<sha>` then `deadbeef00` → exit 0. All OK: these match the old first-match code, which is kept verbatim under `if a.killed:` (cli.py:431-434). A KILLED row cannot satisfy the merge gate.
- Code reading: every new `Refused` is raised at cli.py:435-444, before `store.record_result` (:446) and `store.log_event` (:451). That agrees with `rows=[] events=0` in every refusal probe.

Side effects: `/Users/dphang/dev/nanobot-upstream/webui/package-lock.json` was already modified before my runs (43 deletions; md5 `3419bc2b522d6c82bc3704ba41714ba4`). It was byte-identical after my runs. I did not touch it. The verifier worktree's tracked files are clean. Untracked `.venv/` and `.ruff_cache/` were created there. All other work was in the scratchpad.

STATUS: SPEC-DEFECT
CONFIDENCE: high. Every scenario command was run verbatim on base and head in two shells, and the head's code passed the integration gate script on both the head tree and the base+head merge tree. The only blocker is a gate command that cannot test this head as written. I reproduced that and traced it to two specific lines.
ESCALATIONS:
- The gate command in `factory/config.yaml` `gate_commands` (a protected path, so this needs the operator) is defective in two ways:
  - (a) A plain `uv run --with neonize…` on a fresh checkout has no pytest, because it is in the `dev` optional extra, so the gate exits 2 before running anything. This happens at base too.
  - (b) `{integration}/scripts/full_suite_gate.py` runs pytest with `cwd=REPO_ROOT` = the integration checkout, so it tests the integration branch and not the branch under test.
  - A likely fix, for the operator to decide: add `--extra dev`, and let the gate take a target root (or run it with cwd = the worktree) while it keeps reading its baseline from the integration checkout.
  - Until then, a gate PASS on any sub-ticket proves nothing about that sub-ticket. Earlier `Gate suite: PASS` results recorded by this harness should be read with this in mind.
- The `tests/factory` acceptance command as written picks up blue's `/Users/dphang/dev/nanobot/.venv-test/bin/pytest` (python3.14) from PATH, because the worktree venv has no pytest. It passed here, but it is not hermetic. Adding `--extra dev` would fix this too.
- The count "today: 55" in factory-suite-still-passes is the merge-base count. The integration base now has 58, so after the merge it is 67.
- The probe concern about indented or bold `Commit:` lines is the parent's declared Risk, and is noted only.
