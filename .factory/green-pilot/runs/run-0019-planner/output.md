## Plan

The spec fits one PR: about 3-10 changed lines in one function (`results_record` in `factory/cli.py`) plus one new test file of about 35 lines. Part A without part B would leave the fix with no in-suite test of the build loop's call shape, and part B without part A fails (the spec's own check (ii): `2 failed`). Splitting the two would make neither half independently mergeable with a passing suite, and gives no easier review or rollback. One sub-ticket.

Sequencing precondition (spec Decisions: "build after #16 merges"): checked on this checkout, and it is met. `git log` on `feat/lionbot-v3` shows `1f3a58e52 Merge factory/T-0001.1: results record refuses a checker output whose Commit: lines do not all name the head (T-0001.1)`, and HEAD is `dd09a7cb1`. `factory/cli.py:424-449` now holds #16's version: line 430 `text = Path(a.output).read_text(encoding="utf-8") if a.output else ""`, and lines 436-439 hold the killed-only `Commit:` branch (`if a.killed:  # a killed run's output may be cut off: ...`). This is the branch the spec's Risk section says to remove once it is unreachable. `tests/factory/test_killed_checker.py` does not exist yet. `built_to_implementer` (`tests/factory/test_shepherd.py:390`), `ok` (`:631`) and `act_on_join` (`:763`) exist.

---

### ST-1 / A killed checker records KILLED without reading its output, so the ticket parks as `budget kill: <role>`

Depends on: none. The parent's external precondition, #16 (T-0001.1) merged, is already met at `1f3a58e52`.
Parallel-safe: yes. It is the only sub-ticket.

Parent: the approved spec v1 above (proposal.md, design.md, specs/checker-results/spec.md, verification.md for the change "killed checker parks as budget kill", GitHub danielphang/spec-factory#18). Read it for context. Do NOT implement parts outside this sub-ticket.

Scope: design parts A and B.
- A. `factory/cli.py`, `results_record`: read the `--output` file only when `--killed` is not given (today line 430). With `--killed`, record the KILLED row (and no `ci` row, as today) without opening or checking the output. Remove #16's killed-only `Commit:` branch (today lines 436-439), so that the `Commit:` checks run only for unkilled runs. Leave the unkilled path unchanged.
- B. New file `tests/factory/test_killed_checker.py`: one test, parametrized over `verifier` and `reviewer`. It brings a sub-ticket to checks with `built_to_implementer` and dispatches the implementer and the other checker normally. It then runs the killed checker the way `build.js:91-94` and `:139` do: `run start`, `run compose`, `run finish <id> --status-override KILLED`, `run cleanup <id>`, assert `<store>/runs/<id>/output.md` does not exist, `results record ... --output <that path> --run <id> --killed`, and `act_on_join`. Finally it asserts the sub-ticket is parked with reason `budget kill: <role>`. Every CLI call goes through the shepherd's `ok()`.

Acceptance (each WHEN runs verbatim from the parent's specs/checker-results/spec.md, from the repo root):
- killed-verifier-without-output-file-parks-as-budget-kill (NEW). WHEN: the parent's scenario command (a reviewer APPROVE is recorded, then the verifier is recorded with `--output $S/runs/R2/output.md --run R2 --killed`, then `ticket join`). THEN it prints `reviewer=0 verifier=0 decision=park reason=budget kill: verifier`.
- killed-reviewer-without-output-file-parks-as-budget-kill (NEW). WHEN: the parent's scenario command (a verifier VERIFIED is recorded, then the reviewer is recorded with `--output $S/runs/R2/output.md --run R2 --killed`, then `ticket join`). THEN it prints `verifier=0 reviewer=0 decision=park reason=budget kill: reviewer`.
- killed-record-without-output-flag-still-records-killed (REGRESSION). WHEN: the parent's scenario command (`results record ... --role verifier --run R1 --killed`, no `--output`). THEN it prints `exit=0 rows=[verifier.yaml ] status=KILLED`.
- killed-output-naming-another-commit-records-killed (NEW). WHEN: the parent's scenario command (`--output $S/o.md --killed`, where o.md holds `Commit: deadbeef00`). THEN it prints `exit=0 rows=[verifier.yaml ] status=KILLED`.
- unkilled-record-with-missing-output-file-still-fails (REGRESSION). WHEN: the parent's scenario command (`--role reviewer --output $S/missing.md --run R1`, no `--killed`). THEN it prints `exit=1 rows=[] events=0`.
- factory-suite-passes-with-killed-checker-change (REGRESSION). WHEN `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory`. THEN it exits 0 and reports no failed tests. The count now includes #16's `tests/factory/test_results_commit.py` and the new `test_killed_checker.py`, so it is above the spec's earlier `55 passed`.
- Intermediate check (NEW): `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory/test_killed_checker.py`. THEN it reports `2 passed` (verifier and reviewer). Before part A is applied, it fails in both cases with `FileNotFoundError`. The implementer shows that red run, so the test is known to catch the bug.
- Intermediate check (REGRESSION): `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory/test_results_commit.py` still passes, unedited. #16's killed scenarios (no `--output`, and a cut-off output with no `Commit:` line) still record KILLED, and its unkilled `Commit:` checks are unchanged.
- Gate suite (REGRESSION): `uv run ruff check nanobot/` and the full-suite gate pass. The verifier reports `Gate suite: PASS`.

Tests to change: none. The parent's list is "none". `tests/factory/test_shepherd.py` and `tests/factory/test_results_commit.py` stay unedited. Only the new file `tests/factory/test_killed_checker.py` is added.
Protected paths: none. The parent's Risk section says "Protected paths touched: none". `factory/workflows/build.js` is not edited. Do not stage `webui/package-lock.json` (already `M` in this checkout) or `webui/node_modules/`. Stage by name.
Out of scope: `factory/workflows/build.js` and its call shape. The unkilled `results record` path, including #16's `Commit:` checks and the error for a missing `--output` file. The join's routing and reasons, the merge gate, and the rule that a killed verifier writes no `ci` row. The `--head` validation and the stale-result rule. The killed path of the existing fixture at `tests/factory/test_shepherd.py` (it records without `--output`), which stays as it is.

---

Coverage map:
- killed-verifier-without-output-file-parks-as-budget-kill → ST-1
- killed-reviewer-without-output-file-parks-as-budget-kill → ST-1
- killed-record-without-output-flag-still-records-killed → ST-1
- killed-output-naming-another-commit-records-killed → ST-1
- unkilled-record-with-missing-output-file-still-fails → ST-1
- factory-suite-passes-with-killed-checker-change → ST-1
- Design part A → ST-1. Design part B → ST-1.

Out-of-scope observations:
- The parent's evidence cites line numbers from `f8f40e0c5` (for example, the read at `cli.py:425`). Since #16 merged, the read is at line 430 and the killed `Commit:` branch is at lines 436-439. The intent and the design are unchanged. Only the line anchors moved.
- `webui/package-lock.json` shows as modified in this checkout. It was there before this run, and this run did not touch it.

STATUS: PLANNED
CONFIDENCE: high. The change is one function plus one new test file, #16's merge (the spec's precondition) was checked in git, and every helper and line the sub-ticket names was read on HEAD `dd09a7cb1`.
ESCALATIONS: none
