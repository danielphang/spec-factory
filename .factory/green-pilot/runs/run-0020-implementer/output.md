Sub-ticket: T-0002.1 (ST-1, parent: danielphang/spec-factory#18). Branch `factory/T-0002.1`, worktree `/Users/dphang/dev/spec-factory/intake/green-pilot/worktrees/T-0002.1`, base `dd09a7cb1`, head `d8a117927`.

What changed:
- A. `factory/cli.py`, `results_record`:
  - The output read is now `Path(a.output).read_text(encoding="utf-8") if a.output and not a.killed else ""`, with a one-line comment saying why. With `--killed`, the `--output` file is never opened.
  - #16's killed-only `Commit:` branch (`if a.killed:  # a killed run's output may be cut off: ...`, 4 lines) is removed. With `--killed` the text is always `""`, so that branch could never fire.
  - The unkilled `Commit:` checks are untouched. Only their `else:` became `if not a.killed:`.
  - Nothing else changed. The killed path still writes no `ci` row (`if a.role == "verifier" and not a.killed`, unchanged).
  - Diff: 3 insertions, 6 deletions.
- B. New file `tests/factory/test_killed_checker.py`, 35 lines. One test, parametrized over `verifier` and `reviewer`. It:
  - calls `built_to_implementer`, dispatches the implementer, then the other checker normally, and asserts the join says `wait`;
  - runs the killed checker the way `build.js` does: `ticket head`, `run start`, `run compose`, `run finish <id> --status-override KILLED`, `run cleanup <id>`;
  - asserts `<store>/runs/<id>/output.md` does not exist;
  - runs `results record <st> --head <head> --role <role> --output <that path> --run <id> --killed`, then `act_on_join(st, rid)`;
  - asserts the results row is `KILLED`, the state is `parked`, and the reason is `budget kill: <role>`.
  Every CLI call goes through `Shepherd.ok()`.

Acceptance results (WHEN lines run verbatim from the worktree root; script at scratchpad `acc.sh`, which copies the spec's WHEN lines one for one):

| Criterion | Before (base dd09a7cb1) | After (d8a117927, bash and zsh) |
|---|---|---|
| killed-verifier-without-output-file-parks-as-budget-kill (NEW) | `reviewer=0 verifier=1 decision=wait reason=results missing for the current head: verifier, ci` | `reviewer=0 verifier=0 decision=park reason=budget kill: verifier` |
| killed-reviewer-without-output-file-parks-as-budget-kill (NEW) | `verifier=0 reviewer=1 decision=wait reason=results missing for the current head: reviewer` | `verifier=0 reviewer=0 decision=park reason=budget kill: reviewer` |
| killed-record-without-output-flag-still-records-killed (REGRESSION) | `exit=0 rows=[verifier.yaml ] status=KILLED` | `exit=0 rows=[verifier.yaml ] status=KILLED` |
| killed-output-naming-another-commit-records-killed (NEW) | `exit=2 rows=[] status=` | `exit=0 rows=[verifier.yaml ] status=KILLED` |
| unkilled-record-with-missing-output-file-still-fails (REGRESSION) | `exit=1 rows=[] events=0` | `exit=1 rows=[] events=0` |

Every base result matches the spec's "today" result, so no criterion was already passing before the fix.

- Intermediate (NEW), `pytest ... tests/factory/test_killed_checker.py`:
  - Before part A: `2 failed in 6.09s`. Both cases failed in `Shepherd.ok` on `results record ... --killed: factory: FileNotFoundError: [Errno 2] No such file or directory: '.../state/runs/run-0007-verifier/output.md'` (and `run-0007-reviewer`).
  - After part A: `2 passed in 6.18s`.
- Intermediate (REGRESSION), `pytest ... tests/factory/test_results_commit.py`, unedited: `9 passed in 1.47s` after the change.
- factory-suite-passes-with-killed-checker-change (REGRESSION), `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory`: `70 passed in 71.76s`, exit 0.
- Gate suite (REGRESSION), each command run from the worktree exactly as written:
  - `uv run ruff check nanobot/`: `All checks passed!`, exit 0.
  - The full-suite gate: exit 0, `5 failed, 7173 passed, 25 skipped in 126.21s`, and "its failure set is within the baseline (5 known failure(s))". The 5 known failures are:
    - `tests/gateway/test_runtime.py::test_default_instance_preserves_released_gateway_paths`
    - `tests/cli/test_tui_launcher.py::test_launcher_keeps_the_tui_alive_while_an_existing_gateway_recovers`
    - `tests/lionbot/test_service_log_paths.py::...test_the_default_instance_is_unchanged`
    - `tests/lionbot/test_service_log_paths.py::...test_an_explicit_default_config_resolves_the_same_way`
    - `tests/config/test_config_paths.py::test_shared_and_legacy_paths_remain_global`
  - I also ran `uv run ruff check tests/factory/test_killed_checker.py factory/cli.py` (not a gate): `All checks passed!`

Tests added/changed:
- Added `tests/factory/test_killed_checker.py`. This is part B. It is the only in-suite test that uses the build loop's call shape (`--output` naming a missing file, plus `--killed`).
- Changed: none. `tests/factory/test_shepherd.py` and `tests/factory/test_results_commit.py` are unedited.

Known gaps and uncertainties:
- After this change, a killed run's partial output is not checked at all, including its `Commit:` line. This is intended (spec Decisions), and it changes one case #16 kept: a killed output naming another commit is now recorded KILLED instead of refused (exit 2). #16's two killed scenarios in `test_results_commit.py` (no `--output`, and a cut-off output with no `Commit:` line) still pass.
- The new test imports `built_to_implementer` from `.test_shepherd`, as the design says. If that helper's signature changes, this test breaks with it.
- The test does not run `build.js`, which needs the Workflow runtime. It copies the build loop's call sequence by hand from `build.js` lines 91-94 and 139, read on this head. If `build.js` changes its call shape, this test will not notice.
- The full-suite gate runs with `--isolated-home`. Its own footer says it does not certify the bash `[U*]` units or HOME hermeticity. Neither is touched by this change.

Out-of-scope observations:
- The gate run did not leave `webui/package-lock.json` or `webui/node_modules/` staged or modified in `git status` here. After the commit, `git status --short` was empty. Only `factory/cli.py` and `tests/factory/test_killed_checker.py` were staged, by name.
- `tests/factory/test_shepherd.py`'s `dispatch(..., killed=True)` still records without `--output`, unlike `build.js`. I left it as it is, as the ticket says.

Responses to findings (round 2+): n/a (round 1).

STATUS: READY-FOR-REVIEW
CONFIDENCE: high, every acceptance command was run before and after the change and matched the spec's results exactly (under bash and zsh), the new test was seen red with the expected FileNotFoundError, and both gates passed.
ESCALATIONS: none
