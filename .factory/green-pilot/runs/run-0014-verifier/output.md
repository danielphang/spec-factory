Commit: e28db6a255e8cd0032c67ada62b74b6681cd511d

Checkout: `/Users/dphang/dev/spec-factory/intake/green-pilot/runs/run-0014-verifier/wt`, detached at `e28db6a25`. `git status` was clean before any run. The PR diff (`b551d97cd...e28db6a25`) matches `../diff.patch` except for a trailing newline. It touches three files: `factory/cli.py` (+15/-3), `tests/factory/test_shepherd.py` (one line, :268, `--output` only) and the new file `tests/factory/test_results_commit.py` (131 lines).

Base note: the base I was given, `b551d97cd`, is the tip of the integration branch. It is NOT an ancestor of the head. The branch forked at `f8f40e0c5`, which is 8 commits behind `b551d97cd`. `results_record` is the same at both commits (`git diff f8f40e0c5 b551d97cd -- factory/cli.py` does not touch it). I ran the base column on a `git archive` of `b551d97cd` (scratch copy). `git merge-tree --write-tree b551d97cd e28db6a25` merges cleanly (tree `940fc7432`), and I also ran the factory suite on that merged tree.

Acceptance commands: I extracted all 9 WHEN commands verbatim from input.md lines 174-209 into a script. I ran each line from the repo root under bash and under zsh. Both shells gave the same output on both trees.

Per criterion: NEW/REGRESSION | command | base (b551d97cd) | PR (e28db6a25) | PASS/FAIL
- no-commit-line-is-refused | NEW | WHEN verbatim | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS
- non-hex-commit-value-is-refused | NEW | WHEN verbatim | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS
- later-commit-line-naming-another-commit-is-refused | NEW | WHEN verbatim | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=2 rows=[] events=0` | PASS
- verifier-without-commit-line-writes-no-ci-row | NEW | WHEN verbatim | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=2 rows=[] events=0` | PASS
- earlier-commit-line-naming-another-commit-is-refused | REGRESSION | WHEN verbatim | `exit=2 rows=[] events=0` | `exit=2 rows=[] events=0` | PASS
- full-head-sha-is-recorded | REGRESSION | WHEN verbatim | `exit=0 rows=[reviewer.yaml ] events=1` | `exit=0 rows=[reviewer.yaml ] events=1` | PASS
- abbreviated-sha-in-backticks-is-recorded | REGRESSION | WHEN verbatim | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | `exit=0 rows=[ci.yaml verifier.yaml ] events=2` | PASS
- killed-without-output-records-killed | REGRESSION | WHEN verbatim | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS
- killed-with-cut-off-output-records-killed | REGRESSION | WHEN verbatim | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` | PASS
- factory-suite-still-passes | REGRESSION | `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory` | `59 passed in 108.21s`, exit 0 | `64 passed in 93.69s`, exit 0 | PASS
  - The count differs from the spec's "today 55" because the base moved. `f8f40e0c5` has 55 tests and `b551d97cd` has 59 (4 tests added in test_shepherd.py and test_spec_store.py). The head is 55 + the 9 new tests = 64.
  - Merged tree `940fc7432` (b551d97cd + this PR): `68 passed in 106.37s`, exit 0, which is 59 + 9. The base's new `test_redispatch_...` uses `Commit: HEAD` only through `dispatch`, which substitutes the head, so the new strict check does not break it.
- Intermediate check (gate) | REGRESSION | see Gate suite | not run on base | PASS on head | PASS

Each NEW criterion fails on base for the reason the spec states (the verdict is recorded), not because a fixture is missing. Each REGRESSION criterion passes on both trees.

Gate suite: PASS
- `uv run ruff check nanobot/` → `All checks passed!`, exit 0.
- `uv run --extra dev --with neonize==0.3.18.post0 /Users/dphang/dev/nanobot-upstream/scripts/full_suite_gate.py --root . --isolated-home --pytest-args "-n 2 --dist loadfile"` → `5 failed, 7167 passed, 25 skipped in 133.46s`, then `the suite ran (7197 tests) ... and its failure set is within the baseline (5 known failure(s))`, exit 0. The 5 failures were:
  - tests/gateway/test_runtime.py::test_default_instance_preserves_released_gateway_paths
  - tests/cli/test_tui_launcher.py::test_launcher_keeps_the_tui_alive_while_an_existing_gateway_recovers
  - two in tests/lionbot/test_service_log_paths.py::TestLogPathsFollowTheInstance
  - tests/config/test_config_paths.py::test_shared_and_legacy_paths_remain_global
- I ran the gate commands exactly as given, with no changes to the environment. Unlike the implementer, I did not need to install anything by hand: `--with neonize` and `--extra dev` covered the environment.
- I did not run the full gate on the merged tree. Only the factory suite was run there.

Probes: these used a non-zero head, `abcdef0123456789abcdef0123456789abcdef01`, to rule out special-casing of the all-zero head the tests use. Each ran `results record` from the wt with `bin/factory`.
- Uppercase abbreviated `Commit: ABCDEF0` → exit 0, recorded → OK (case-insensitive, as decided)
- `Commit: <head> (verified on a clean checkout)` (trailing text) → exit 0, recorded → OK
- Two lines, `Commit: <head>` and ``Commit: `abcdef01` `` → exit 0, recorded → OK
- CRLF line endings, `Commit: <head>\r\n` → exit 0, recorded → OK
- `Commit: <head>0` (41 hex) → exit 2, `... is not a commit id`, nothing written → OK
- `Commit: abcdef` (6 hex) → exit 2, nothing written → OK
- `Commit: abcdef1` (7 hex, wrong prefix) → exit 2, `the output says Commit: abcdef1, not the head abcdef012345` → OK
- Empty output file, not killed → exit 2, `no Commit: line` → OK
- `**Commit:** <head>` → exit 2, `no Commit: line` → OK per spec. The parent's Risk already declares this format would park a ticket.
- `commit: <head>` (lowercase key) → exit 2 → OK (case-sensitive, as decided)
- `Commit:` with the hex on the next line → exit 2, message `Commit:  is not a commit id` (empty value) → OK by spec. The implementer disclosed this. The message is unhelpful but correct.
- `Commit: <head>` then an indented `  Commit: deadbeef00` → exit 0, recorded → CONCERN (minor). Only lines that start at column 0 are checked, which matches the spec's "a line that starts with `Commit:`" and today's anchor. So an indented mismatching line is ignored. This is within the spec, not a FAIL.
- `--killed` with `Commit: deadbeef00` → exit 2, same as before. `--killed` with `Commit: HEAD` → exit 0, KILLED row. Both match today's code: the killed branch is a byte-identical copy of the old check (cli.py:431-434) → OK
- Verifier `Commit: <head>` with `Gate suite: FAIL` → exit 0, rows ci+verifier, 2 events → OK (status parsing unchanged)

Nothing suggests special-casing: the code at `factory/cli.py:431-444` is a general per-line check, and it behaves correctly for a head other than the tested one.

Out-of-scope observations:
- The head is not rebased on the integration tip. It lacks `tests/cli/conftest.py`, which the base added in b7d09a8db and which sets `NANOBOT_SKIP_WEBUI_BUILD=1`. So the gate run on this head ran a real webui build. That build rewrote `webui/package-lock.json` in my verifier worktree (43 deletions) and created `webui/node_modules/`. I left both as the gate left them: my role may only write output.md. This is the cause of the lockfile rewrite the implementer escalated, and it is already fixed on the integration branch. Once merged into `b551d97cd` the conftest will be present.
- The parent's two observations were not exercised here and still stand: the `--killed --output <missing>` crash with FileNotFoundError, and the dead `wrong.md` call at test_shepherd.py:333.

STATUS: VERIFIED
CONFIDENCE: high. I ran all 9 WHEN commands verbatim under bash and zsh on base and head, ran the factory suite on base, head and the merged tree, ran both gate commands as written, and ran 15 probes. Only one minor concern came up, and it is within the spec.
ESCALATIONS: (1) The base I was given (`b551d97cd`) is not an ancestor of the head (which forked at `f8f40e0c5`). The merge is clean and the merged factory suite passes 68/68, but the full-suite gate has not been run on the merged tree. (2) Running the gate on this head rewrote the protected `webui/package-lock.json` in the verifier worktree, because the head predates the base's `tests/cli/conftest.py`. That file is uncommitted and lives only in this run's `wt`. Whoever cleans up the worktree should discard it, and nothing should commit it.
