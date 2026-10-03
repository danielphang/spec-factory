## Plan: one sub-ticket

The spec fits in one PR: about 20 lines in `factory/cli.py`, 1 line in `tests/factory/test_shepherd.py` and one new test file. It cannot be split so that each piece can be merged on its own. Part A without part B fails `tests/factory`: `test_shepherd.py:264` writes `Commit: HEAD` into `red.md` and `:268` records it through `f.ok`. The spec's scratch run says this exits 2 under A. Part B without A changes nothing. Part C's tests fail until A lands. Splitting off C as a follow-up would only add one more merge and re-verify cycle, so A, B and C stay together.

Cited code confirmed on this checkout (HEAD `f8f40e0c5`, branch `feat/lionbot-v3`):
- `factory/cli.py:419` `def results_record`, with the first-match check at `:431-433`.
- `tests/factory/test_shepherd.py:264` (`red.md` with `Commit: HEAD`) and `:268` (the direct `results record ... --output str(red)` call).
- `:648` (the dispatcher replaces `Commit: HEAD` with the head in the run's `output.md`).
- `bin/factory` exists.
- `tests/factory/test_results_commit.py` does not exist yet.

---

### ST-1 / `results record` refuses a checker output whose `Commit:` lines do not all name the head

Parent: the approved spec "checker-output-must-name-the-head" (v1, pinned: proposal.md, design.md, specs/checker-results/spec.md, verification.md in this change). Read it for context. Do NOT implement parts outside this sub-ticket.

Depends on: none
Parallel-safe: yes (it is the only sub-ticket)
Scope: design parts A, B, C. All of the parent.
- A: `factory/cli.py` `results_record`. Without `--killed`, there must be at least one `Commit:` line. Every `Commit:` line must parse as 7-40 hex characters (optionally in backticks) and be a prefix of `--head`. Each refusal raises `Refused` before any `store.record_result` or `store.log_event` call. With `--killed`, keep today's check exactly.
- B: in the merge-gate story of `tests/factory/test_shepherd.py`, change the `results record --role verifier` call at line 268 so its `--output` is `f.store / "runs" / ver.run_id / "output.md"` instead of `red.md`. Assertions are unchanged.
- C: new file `tests/factory/test_results_commit.py`. It drives `bin/factory` as a subprocess against a temporary `FACTORY_STATE` and covers each scenario below.

Acceptance (each WHEN is run verbatim from the repo root, exactly as written in the parent's specs/checker-results/spec.md):
- no-commit-line-is-refused: WHEN reviewer output with no `Commit:` line is recorded. THEN `exit=2 rows=[] events=0`. NEW
- non-hex-commit-value-is-refused: WHEN reviewer output with `Commit: HEAD` is recorded. THEN `exit=2 rows=[] events=0`. NEW
- later-commit-line-naming-another-commit-is-refused: WHEN the output has `Commit: <head>`, then later `Commit: deadbeef00`. THEN `exit=2 rows=[] events=0`. NEW
- verifier-without-commit-line-writes-no-ci-row: WHEN verifier output with `Gate suite: PASS` and no `Commit:` line is recorded. THEN `exit=2 rows=[] events=0`. NEW
- earlier-commit-line-naming-another-commit-is-refused: WHEN the output has `Commit: deadbeef00`, then `Commit: <head>`. THEN `exit=2 rows=[] events=0`. REGRESSION
- full-head-sha-is-recorded: WHEN the output has `Commit: <40-hex head>`. THEN `exit=0 rows=[reviewer.yaml ] events=1`. REGRESSION
- abbreviated-sha-in-backticks-is-recorded: WHEN verifier output has ``Commit: `0000000` ``. THEN `exit=0 rows=[ci.yaml verifier.yaml ] events=2`. REGRESSION
- killed-without-output-records-killed: WHEN `--killed` is passed with no `--output`. THEN `exit=0 rows=[verifier.yaml ] status=KILLED`. REGRESSION
- killed-with-cut-off-output-records-killed: WHEN `--killed` is passed with an `--output` that has no `Commit:` line. THEN `exit=0 rows=[verifier.yaml ] status=KILLED`. REGRESSION
- factory-suite-still-passes: WHEN `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory`. THEN it exits 0 with no failed tests. The count grows from today's 55 by the number of tests in the new file. REGRESSION
- Intermediate check (gate suite, not a parent scenario): WHEN `uv run ruff check nanobot/` and the full-suite gate. THEN lint is clean and no test fails outside the port's known-failure baseline. REGRESSION

Tests to change: `tests/factory/test_shepherd.py` line 268 only (parent's Tests to change). The other `Commit: HEAD` fixtures go through `dispatch`, which substitutes the head. They stay untouched: lines 327, 408-409 and 489, and the stubs under `tests/factory/fixtures/stubs/`.
Protected paths: none. The parent's Risk declares none, and `factory/cli.py` is not under `factory/workflows/**` or `factory/config.yaml`.
Out of scope:
- `factory/workflows/build.js` (protected), roles, prompts, routing and every other `factory` command.
- `--head` validation.
- The stale-result rule (`result.stale-discarded`).
- Status parsing and the derived `ci` row for accepted outputs.
- The `--killed --output <missing file>` `FileNotFoundError` crash (parent's out-of-scope observation).
- The dead `results record` call on `wrong.md` at `test_shepherd.py:333` (parent's out-of-scope observation).
- Accepting other `Commit:` formats (for example `**Commit:**`). The parent's Risk notes this as a possible way to park a ticket. It is not a change to make here.

---

Coverage map: parent scenario → sub-ticket ID
- no-commit-line-is-refused → ST-1
- non-hex-commit-value-is-refused → ST-1
- later-commit-line-naming-another-commit-is-refused → ST-1
- verifier-without-commit-line-writes-no-ci-row → ST-1
- earlier-commit-line-naming-another-commit-is-refused → ST-1
- full-head-sha-is-recorded → ST-1
- abbreviated-sha-in-backticks-is-recorded → ST-1
- killed-without-output-records-killed → ST-1
- killed-with-cut-off-output-records-killed → ST-1
- factory-suite-still-passes → ST-1

What I verified: I read `factory/cli.py:415-446`, `tests/factory/test_shepherd.py:260-272` and `:644-650` on `~/dev/nanobot-upstream` at HEAD `f8f40e0c5`, and listed `tests/factory/` and `bin/factory`. I did not run the WHEN commands. Their today-results are the parent's evidence, not mine.
