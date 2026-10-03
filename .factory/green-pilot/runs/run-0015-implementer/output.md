Sub-ticket: T-0001.1 (ST-1, "`results record` refuses a checker output whose `Commit:` lines do not all name the head"). Parent: approved spec "checker-output-must-name-the-head" v1.
Branch: `factory/T-0001.1` in `/Users/dphang/dev/spec-factory/intake/green-pilot/worktrees/T-0001.1`, base `f8f40e0c550c86d34a5b80ef273c7b4943abf412`, head `e28db6a25` (one commit). Nothing was pushed.

## What changed

- **A. `factory/cli.py` `results_record` (lines 431-444 at head).** The first-match check is now split on `--killed`:
  - With `--killed`, the old code is kept exactly: first hex `Commit:` line, refuse only on a mismatch, and no check when there is no line.
  - Without `--killed`:
    1. Collect every line matching `^Commit:.*$` (re.M). If there are none, refuse with `results record: the output has no Commit: line`.
    2. Match each line with the existing grammar, now anchored to that line: `Commit:\s*`?([0-9a-fA-F]{7,40})`?\b`. If a line does not match, refuse with `results record: Commit: <value> is not a commit id`. If it matches but the lowercased value is not a prefix of `--head`, refuse with the existing message `the output says Commit: <v>, not the head <head[:12]>`.
    3. Every refusal raises `Refused` (exit 2) before any `store.record_result` or `store.log_event` call, in the same place as the old check.
- **B. `tests/factory/test_shepherd.py:268`.** The merge-gate story's direct `results record --role verifier` call now passes `--output str(f.store / "runs" / ver.run_id / "output.md")` instead of `str(red)`. No assertions changed. This is the only line changed in that file.
- **C. New file `tests/factory/test_results_commit.py`** with 9 tests, one per scenario. Each test runs `bin/factory` as a subprocess against a temporary `FACTORY_STATE` (one ticket, head = forty zeros).
  - Refusal tests check: exit 2, the reason on stderr, no files under `results/<head>/`, and no `result.*` log events.
  - Accept tests check: the rows written, the `result.recorded` events, and the row statuses.
  - Killed tests check for a single `verifier.yaml` row with status KILLED.

## Acceptance results

I ran all nine WHEN commands verbatim from the worktree root under both bash and zsh. Both shells gave the same output, before and after. The script is at `/private/tmp/claude-501/-Users-dphang-dev-nanobot/c69bfd1d-97a6-43e3-9d5a-a517c28d382c/scratchpad/acc.sh`.

| Scenario | Kind | Before (base f8f40e0c5) | After (head e28db6a25) |
|---|---|---|---|
| no-commit-line-is-refused | NEW | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` |
| non-hex-commit-value-is-refused | NEW | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` |
| later-commit-line-naming-another-commit-is-refused | NEW | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` |
| verifier-without-commit-line-writes-no-ci-row | NEW | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=2 rows=[] events=0` |
| earlier-commit-line-naming-another-commit-is-refused | REGRESSION | `exit=2 rows=[] events=0` | `exit=2 rows=[] events=0` |
| full-head-sha-is-recorded | REGRESSION | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=0 rows=[reviewer.yaml ] events=1` |
| abbreviated-sha-in-backticks-is-recorded | REGRESSION | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` |
| killed-without-output-records-killed | REGRESSION | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` |
| killed-with-cut-off-output-records-killed | REGRESSION | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` |

The NEW criteria failed before as the spec describes, and the REGRESSION criteria passed before. The spec matches reality.

**factory-suite-still-passes:** `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory`
- Before: `55 passed in 92.01s`.
- After: `64 passed in 62.69s (0:01:02)`, exit 0. That is 55 + the 9 new tests. I ran it with the worktree's own `.venv/bin/pytest` (checked with `uv run which pytest`).

**Red step:** the new test file run against the base code gave `4 failed, 5 passed`. The 4 failures were the 4 NEW scenarios, all at the `returncode == 2` assertion.

**Gate: lint.** `uv run ruff check nanobot/` printed `All checks passed!` (exit 0). I also ran ruff on `factory/cli.py` and the new test file: `All checks passed!`.

**Gate: full suite.** `uv run scripts/full_suite_gate.py --isolated-home --pytest-args "-n 2 --dist loadfile"` passed in the end, but only after I changed the worktree's environment. In order:
1. **First attempt: exit 2.** `pytest is not importable under .../T-0001.1/.venv/bin/python3`. The fresh worktree `.venv` had no dev extra installed. I ran `uv sync --frozen --all-extras`, which does not change `uv.lock` or `pyproject.toml`.
2. **Second attempt: exit 1, `FAIL: 10 failure(s) NOT in the baseline`.**
   - 9 failed with `ModuleNotFoundError: No module named 'neonize'`: in `tests/lionbot/test_upstream_seams.py` (5), `tests/lionbot/test_auto_mention.py` (3) and `test_typing_hooks.py::...test_a_connected_channel_does_send` (1).
   - `tests/agent/test_mcp_reconnect_crash.py::test_mcp_reconnect_during_shutdown_does_not_crash` failed with a TimeoutError.
   - I checked out base `f8f40e0c5` (detached, in this worktree) and ran the same 4 files there: the same 10 tests failed in the same way (`10 failed, 57 passed, 1 skipped`). They fail without this change, so it did not cause them.
   - The cause is the environment. `neonize` is in neither `pyproject.toml` nor `uv.lock`, but the green checkout's `.venv` has `neonize 0.3.18.post0` and `mcp 1.29.1`. The lock pins `mcp 1.30.0`.
3. **Third attempt: exit 0.** I installed those two versions into this worktree's `.venv` only, with `uv pip install --python .venv/bin/python "neonize==0.3.18.post0" "mcp==1.29.1"`, which changes no project file. The 10 tests then passed (`67 passed, 1 skipped`). I ran the gate as `.venv/bin/python scripts/full_suite_gate.py --isolated-home --pytest-args "-n 2 --dist loadfile"` (the form the gate's own error message gives), so that `uv run` would not re-sync `mcp` back to 1.30.0. Result: `5 failed, 7297 passed, 20 skipped`, `the suite ran (7322 tests) and its failure set is within the baseline (5 known failure(s))`, exit 0.

## Tests added/changed

- **Added:** `tests/factory/test_results_commit.py`, 9 tests, one per parent scenario (factory-suite-still-passes is the suite run itself). This is part C.
- **Changed:** `tests/factory/test_shepherd.py:268`, the `--output` argument only. This is the one line listed under "Tests to change". The story's `red.md` has a literal `Commit: HEAD`, which part A now correctly refuses (exit 2), and that would break `f.ok`. The dispatched run's `output.md` has the same content with the real head substituted (`test_shepherd.py:648`). The behaviour under test is unchanged: a red verifier and a red ci row block the merge.
- No other existing test, fixture or stub was touched. Lines 327, 408-409 and 489 and `tests/factory/fixtures/stubs/` are unchanged.

## Known gaps and uncertainties

- **One change beyond the spec's list (multi-line `Commit:`).** The old regex `^Commit:\s*...` with re.M could match across a newline, so a bare `Commit:` with the hex on the next line was accepted. The new check matches within one line, so that output is now refused, with a message whose value is empty (`Commit:  is not a commit id`). Under the spec ("a line that starts with `Commit:`" whose value must parse) this is intended, but it is a change the spec does not list. The `--killed` path keeps the old cross-line behaviour exactly.
- **Not run: A without B.** I did not separately confirm that part A fails the merge-gate story when part B is left out. The parent's scratch run reports this. I relied on reading `test_shepherd.py:264-268` together with the new refusal.
- **The gate depends on the environment.** On a `.venv` synced strictly from `uv.lock` (no `neonize`, `mcp 1.30.0`), the full-suite gate FAILs with 10 tests outside the baseline, and it does so at base too. A verifier running the gate on this head will see the same result unless its environment matches the green checkout's `.venv`. I changed no project dependency file. I only installed packages into this worktree's untracked `.venv`.
- **How real checkers write the line is still unverified.** As the parent's Risk says, a checker that writes `**Commit:** ...` will now be refused and its ticket parked. I did not change that, since it is out of scope.

## Out-of-scope observations

- **The full-suite gate rewrites a protected file.** Something in the gate's pytest run executes a real JS package install in `webui/`. It created `webui/node_modules/` and rewrote `webui/package-lock.json` (a protected path): 43 lines deleted, dropping `@radix-ui/react-separator`. The mtimes, 18:48:26, fall inside the gate run, and it happened again on the third gate run. I restored the file both times with `git checkout -- webui/package-lock.json`. It is not in the commit, and the working tree is clean at `e28db6a25`. I did not identify which test does this. The likely area is the webui auto-build path (`ensure_webui_bundle`) reached through a test that is not mocked. This needs a look: any role that runs the gate and then commits with `-a` would commit a protected-path change.
- **`neonize` is missing from the lock.** Both lionbot seam tests and production code need it, but it is in neither `pyproject.toml` nor `uv.lock`, and green's `.venv` also drifts from the lock on `mcp` (1.29.1 vs 1.30.0). A worktree synced from the lock cannot pass the gate.
- The parent's own observations stand untouched: `--killed --output <missing file>` crashes with `FileNotFoundError`, and the `results record` call on `wrong.md` at `test_shepherd.py:333` is dead.

## Conflict resolution note (conflict run)

The merge gate refused the branch because head `e28db6a25` did not contain the integration tip `b551d97cd` (`feat/lionbot-v3`; the branch had forked at `f8f40e0c5`, 8 commits behind). I merged it in with `git merge --no-ff b551d97cd` (no rebase, nothing pushed). Merge commit: `a946681a611133793f703f8ea616fcb60ce3c900`. There was no conflict: git auto-merged `factory/cli.py` and `tests/factory/test_shepherd.py`, and the hunks do not overlap. The merged tree is `940fc7432`, the same tree the verifier got from `git merge-tree --write-tree b551d97cd e28db6a25`. `git merge-base --is-ancestor b551d97cd HEAD` succeeds. `git diff b551d97cd HEAD --stat` lists only this PR's three files (`factory/cli.py` +14/-3, `tests/factory/test_results_commit.py` +131, `tests/factory/test_shepherd.py` 1 line). No code, test or description content changed beyond this note. The reviewer's round-1 NIT (empty-value message) is not addressed, because a conflict run changes nothing else.

Gates re-run on `a946681a6`, from the worktree, exactly as written in the input:
- `uv run ruff check nanobot/`: `All checks passed!`, exit 0.
- `uv run --extra dev --with neonize==0.3.18.post0 /Users/dphang/dev/nanobot-upstream/scripts/full_suite_gate.py --root . --isolated-home --pytest-args "-n 2 --dist loadfile"`: `5 failed, 7301 passed, 20 skipped in 127.55s`, `the suite ran (7326 tests) ... and its failure set is within the baseline (5 known failure(s))`, exit 0. The 5 failures are the same 5 the verifier listed for the old head (test_runtime, test_tui_launcher, two in test_service_log_paths, test_config_paths). I made no change to the environment by hand this time. `git status --short` was empty after the gate, so the `webui/package-lock.json` rewrite I escalated in round 1 did not recur (the merged-in `tests/cli/conftest.py` sets `NANOBOT_SKIP_WEBUI_BUILD=1`).
- `tests/factory`: `68 passed in 83.94s`, exit 0. That is the integration tip's 59 tests plus the 9 new ones.
- All nine acceptance WHEN commands, verbatim, under bash: the five refusals print `exit=2 rows=[] events=0`; full-head prints `exit=0 rows=[reviewer.yaml ] events=1`; abbreviated-in-backticks prints `exit=0 rows=[ci.yaml verifier.yaml ] events=2`; both killed scenarios print `exit=0 rows=[verifier.yaml ] status=KILLED`.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. The merge of `b551d97cd` was clean (merged tree `940fc7432`, the one the verifier predicted), and on merge head `a946681a6` lint passed, the full-suite gate passed as written (5 failures, all in the baseline), `tests/factory` passed 68/68, and all nine WHEN commands gave the required output.
ESCALATIONS: none. The two round-1 escalations (the `webui/package-lock.json` rewrite, and the gate depending on a hand-patched `.venv`) did not recur on the merged head with the input's gate command. They are kept in the description above as the record of round 1.
