Commit: 1f3a58e52f8cba5d651aca2c89bf0a07b2b9a25b

Parent-close run. Head = `1f3a58e52` (merge of factory/T-0001.1), detached in `/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0018-verifier/wt`. Base = `b551d97cd`, the main SHA before the parent's first merge, exported with `git archive b551d97cd` into a scratch directory (no new worktree). `git diff --stat b551d97cd 1f3a58e52` changes 3 files: `factory/cli.py` (+17/-4), `tests/factory/test_shepherd.py` (1 line, the declared fixture change at line 269), and a new `tests/factory/test_results_commit.py` (131 lines). No protected or guardrail paths are touched beyond the declared fixture line.

How I ran the commands: I copied the 9 WHEN shell commands into a script, one per line, and checked them against input.md with a programmatic comparison (`9 9 True`). I ran each from the repo root of head and of base, under both bash and zsh, with the same results in both shells. I re-ran the head set after the gate created `.venv`, so that `bin/factory` used the venv interpreter instead of `python3`. The results did not change.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
- no-commit-line-is-refused | NEW | reviewer, no Commit: line | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS
- non-hex-commit-value-is-refused | NEW | `Commit: HEAD` | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS
- later-commit-line-naming-another-commit-is-refused | NEW | `Commit: <head>` … `Commit: deadbeef00` | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS
- verifier-without-commit-line-writes-no-ci-row | NEW | verifier, no Commit:, Gate suite: PASS | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=2 rows=[] events=0` | PASS
- earlier-commit-line-naming-another-commit-is-refused | REGRESSION | `Commit: deadbeef00` … `Commit: <head>` | `exit=2 rows=[] events=0` | `exit=2 rows=[] events=0` | PASS
- full-head-sha-is-recorded | REGRESSION | `Commit: <head>` | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=0 rows=[reviewer.yaml ] events=1` | PASS
- abbreviated-sha-in-backticks-is-recorded | REGRESSION | ``Commit: `0000000` `` verifier | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | PASS
- killed-without-output-records-killed | REGRESSION | `--killed`, no `--output` | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS
- killed-with-cut-off-output-records-killed | REGRESSION | `--killed`, output with no Commit: | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS
- factory-suite-still-passes | REGRESSION | `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory` | `59 passed in 104.47s` (exit 0) | `68 passed in 105.18s` (exit 0) | PASS

The NEW criteria fail on base for exactly the reason the spec gives: the verdict is recorded. They pass on the PR. The REGRESSION criteria pass on both. The spec says "today: 55 passed" for the factory suite. Base now has 59 tests, because commits landed on main after the spec was written at `f8f40e0c5`. The PR adds 9 tests, for 68. The criterion is "exits 0, no failed tests", and that criterion holds. The 55 count is out of date but is not a defect in the criterion.

Gate suite: PASS
- `uv run ruff check nanobot/` → `All checks passed!`, exit 0.
- `uv run --extra dev --with neonize==0.3.18.post0 /Users/dphang/dev/nanobot-upstream/scripts/full_suite_gate.py --root . --isolated-home --pytest-args "-n 2 --dist loadfile"` → exit 0. Result: `5 failed, 7171 passed, 25 skipped in 123.74s`, with the message "failure set is within the baseline (5 known failure(s))". The 5 failures:
  - tests/gateway/test_runtime.py::test_default_instance_preserves_released_gateway_paths
  - tests/cli/test_tui_launcher.py::test_launcher_keeps_the_tui_alive_while_an_existing_gateway_recovers
  - tests/lionbot/test_service_log_paths.py (2 tests)
  - tests/config/test_config_paths.py::test_shared_and_legacy_paths_remain_global

  None are under tests/factory or related to this change.

Probes: input → result → OK / CONCERN
All probes ran on head with `--head abcdef0123456789abcdef0123456789abcdef01`, role verifier, plus a `Gate suite: PASS` / `STATUS: VERIFIED` body.
- `Commit: ABCDEF0` (uppercase prefix) → exit 0, ci+verifier rows → OK (case-insensitive hex, as designed)
- `Commit: abcdef` (6 hex) → exit 2, `Commit: abcdef is not a commit id`, nothing written → OK
- `Commit: <head> (merge)` (trailing text) → exit 0, recorded → OK (trailing text allowed, as designed)
- `Commit: <head>ab` (42-hex run) → exit 2, `is not a commit id` → OK (no truncating a longer id to a 40-char prefix)
- `Commit: bcdef01` (7 hex that are not a prefix of the head) → exit 2, `the output says Commit: bcdef01, not the head abcdef012345` → OK
- abbreviated `Commit: abcdef01` plus a later full ``Commit: `<head>` `` → exit 0 → OK (every line checked, both match)
- CRLF line endings with the full head → exit 0, recorded → OK
- `Commit:` with an empty value → exit 2, `Commit:  is not a commit id` → OK (refused; the message has a double space)
- empty output file → exit 2, `the output has no Commit: line` → OK
- `**Commit:** <head>` (markdown bold) → exit 2, `the output has no Commit: line` → CONCERN, not a fail. This is the behaviour the spec's Risk section predicts and accepts: a checker that bolds the label will park its ticket.
- `  Commit: <head>` (indented only) → exit 2, no Commit: line → OK under the spec's "line starts with `Commit:`" rule
- `Commit: <head>` plus `commit: deadbeef00` (lowercase label) → exit 0, recorded → OK under the spec's case-sensitive decision. The lowercase line naming another commit is not checked.
- `--killed` with `Commit: deadbeef00` → exit 2, nothing written; `--killed` with `Commit: HEAD` → exit 0, KILLED row → OK. Both match today's killed path.

The fix is not special-cased to the tested inputs. Different head values, prefix lengths, letter cases and line endings all behave as the requirement states.

Out-of-scope observations:
- The spec's "today: 55 passed" for tests/factory is out of date. Base `b551d97cd` has 59 tests.
- Running the gate created `wt/.venv`, which is ignored. `git status --short` on the verifier worktree was clean afterwards.

STATUS: VERIFIED
CONFIDENCE: high. I ran all 10 criteria verbatim on head and base under bash and zsh, the results matched the spec's base and PR expectations exactly, both gates exited 0, and 13 probes behaved per the stated decisions.
ESCALATIONS: none
