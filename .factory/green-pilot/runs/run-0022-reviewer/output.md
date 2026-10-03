Commit: d8a11792727455830cb78d4417f56a51104e0120

Round: 1 (no prior findings).

Reviewed against sub-ticket T-0002.1 (parts A and B) and the parent spec v1. Diff range `dd09a7cb1...d8a117927`: `factory/cli.py` (+3/-6) and new `tests/factory/test_killed_checker.py` (+35). Worktree `git status --short` was empty at review start; the head commit touches only those two files (`git show d8a117927 --stat`).

1. Test integrity: no existing test file changed (`git diff --name-status` shows `M factory/cli.py`, `A tests/factory/test_killed_checker.py` only). `tests/factory/test_shepherd.py` and `tests/factory/test_results_commit.py` are unedited, as the sub-ticket requires. No assertion weakened, no skip/xfail, no swallowed error. The new test asserts the exact row status (`KILLED`), state (`parked`) and reason string (`budget kill: {role}`), and its CLI calls go through `Shepherd.ok()` (`tests/factory/test_shepherd.py:631`), which fails on any non-zero exit with stderr.

2. Correctness (verified, not inferred):
   - `factory/cli.py:433` now reads the output only when `a.output and not a.killed`. With `--killed`, `text == ""`, `st = "KILLED"` (`:434-435`), the `Commit:` checks are gated by `if not a.killed:` (`:439`), and the `ci` row is still skipped (`:452`, unchanged). The removed killed-only `Commit:` branch could never fire once `text` is always empty for killed runs, so its removal is dead-code deletion, as the parent's Risk section asked.
   - Ran all five black-box WHEN lines verbatim from the worktree root on the head:
     - killed-verifier-without-output-file-parks-as-budget-kill: `reviewer=0 verifier=0 decision=park reason=budget kill: verifier`
     - killed-reviewer-without-output-file-parks-as-budget-kill: `verifier=0 reviewer=0 decision=park reason=budget kill: reviewer`
     - killed-record-without-output-flag-still-records-killed: `exit=0 rows=[verifier.yaml ] status=KILLED`
     - killed-output-naming-another-commit-records-killed: `exit=0 rows=[verifier.yaml ] status=KILLED`
     - unkilled-record-with-missing-output-file-still-fails: `exit=1 rows=[] events=0`
     All match the spec's THEN lines.
   - `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory/test_killed_checker.py tests/factory/test_results_commit.py` → `11 passed in 7.82s` (2 new + 9 from #16).
   - `... uv run pytest -q -p no:cacheprovider tests/factory` → `70 passed in 77.00s`, exit 0.
   - `uv run ruff check nanobot/ factory/cli.py tests/factory/test_killed_checker.py` → `All checks passed!`
   - The test mirrors `factory/workflows/build.js:91-94` (`run finish --status-override KILLED`, `run cleanup` for reviewer/verifier) and `:139` (`results record ... --output <outputPath> --run <id> --killed`), read on this head. `run finish` writes `output.md` only with `--output-file` (`cli.py:257-259`) and `run cleanup` removes only the worktree (`cli.py:231-237`), so the `assert not output.exists()` at `test_killed_checker.py:30` is a real precondition, not a tautology. Edge case the spec implies (a killed run whose partial output exists and holds a stale `Commit:`) is covered by the fourth WHEN above.
   - I did not re-run the red state myself (doing so would mean modifying `factory/cli.py` in this worktree, which my role may not do). The base version read `Path(a.output).read_text(...) if a.output else ""`, so a missing path raises `FileNotFoundError` by construction, and the implementer's "Before" column matches the spec's "today" results.

3. Scope: both changed files are inside parts A and B. Nothing else touched.

4. Silent behavior changes: one, and the spec declares it (Decisions): a killed run's output naming another commit is now recorded KILLED (exit 0) instead of refused (exit 2). A KILLED row cannot satisfy the merge gate (`cli.py:479`: `ci PASS`, `APPROVE`, `VERIFIED` all required), so nothing is weakened downstream.

5. Security and data safety: nothing new. The change removes a file read on one path; no new inputs, no destructive ops.

6. Protected paths: none touched. `factory/workflows/build.js` unchanged (read only); no `pyproject.toml`, `uv.lock`, `webui/package-lock.json`, `nanobot/api/**`, or `~/.nanobot/` involvement. Guardrail paths: none.

7. Maintainability: the relative import `from .test_shepherd import built_to_implementer` works because `tests/factory/__init__.py` exists; the full gate with `-n 2 --dist loadfile` is the verifier's to confirm, but the serial factory run above passes.

Findings: none.

Prior findings: n/a (round 1).

Out-of-scope observations:
- `tests/factory/test_shepherd.py:692-695`: `dispatch(..., killed=True)` still records without `--output`, unlike `build.js:139`. Already noted by the spec and the PR; left as the ticket says.
- `factory/cli.py:432` comment line is over 100 columns; E501 is ignored by the repo's ruff config, so it is not a lint failure. Not a finding.

STATUS: APPROVE
CONFIDENCE: high, every acceptance WHEN re-run verbatim on the head matched its THEN, the factory suite passes at 70, lint is clean, and the diff is confined to the two files the sub-ticket names.
ESCALATIONS: none
