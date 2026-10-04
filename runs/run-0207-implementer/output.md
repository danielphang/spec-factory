Sub-ticket: T-0023.3 (T-0023-S2, "Dispatcher park reasons and a redispatch that keeps passing rows", parts B and D of the approved spec v2 of T-0023, issue #39). Branch `factory/T-0023.3` in `/Users/dphang/dev/spec-factory/.factory/state/worktrees/T-0023.3`, one commit `7463a1e` on base `a6e9e10`.

## What changed

This sub-ticket fixes two harness defects. First, when a store command was refused, a parked ticket's reason could end blank, so the operator had to dig through run logs to learn why it stopped. A ticket is parked when the harness stops and waits for a human. Second, re-running a sub-ticket's checks threw away a verifier result that was still valid for the same commit, which wasted a verifier run of about 10 minutes.

**B. A park reason always carries the error** (item H2). The change is in `clerk()` in `factory/workflows/build.js` and `factory/workflows/intake.js`. The clerk is the small agent that runs one store command and relays its stdout, stderr and exit code. Both copies get the same two edits.
- B1. When stdout holds no JSON, `stderr` becomes the relayed stderr, else `exit <n>, no JSON on stdout`.
- B2. When the parsed result has `ok: false` and no stderr, `stderr` becomes the refusal's JSON `error`, else `exit <n>, no error text`.
- B3. No reason template changed. All 26 sites still read `${x.stderr || ''}`, and with B1 and B2 none of them can end blank.

**D. A redispatch keeps rows that passed** (item H4). `factory resolve <id> --redispatch` is the command a human runs to re-run a sub-ticket's checks on the same commit after an outside fix. A row is one checker's recorded result for one commit, kept at `results/<head>/<role>.yaml`.
- D1. The change is in the `--redispatch` branch of `resolve`, `factory/cli.py` lines 764-789. The reviewer's row is set aside unless it is `APPROVE`. The verifier's and gate (`ci`) rows are set aside together unless they are `VERIFIED` and `PASS`, because one verifier run writes both. Set-aside rows still go to `superseded-<n>/`. That directory is created only when a row moves. The `results.superseded` log event and the resolve record list only the roles that moved. The comment above the branch now says this.
- D2. The change is in `buildOne` in `factory/workflows/build.js`. A pass that ran the implementer still runs both checkers. A pass that entered at `checks-in-flight` first runs `results show ST` through the clerk. That pass is a redispatch or a resumed sub-ticket. The reviewer then runs only if `missing` contains `reviewer`. The verifier runs only if `missing` contains `verifier` or `ci`. When no checker is needed, the build goes straight to `ticket join`. A refused `results show` parks as `harness-bug: results show: <error>`. `results show` runs after `ticket head`, so it reads the rows for the head the checkers would see.
- D3. New test file `tests/factory/test_redispatch_rows.py`. See "Tests added/changed".

**J1, this seam's clause.** The S2 clause goes on the same line as changelog entry 51 in `docs/changelog.md`, using the parent's wording.

Callers of the code I changed, found with grep (coding standard rule 2):
- Both `clerk()` functions are the only path from either workflow script to the store: 28 calls in `build.js` and 10 in `intake.js`. A fix in `clerk()` reaches every park reason once. Editing 26 templates would not.
- `buildOne` is called only from the build phase loop (`build.js:244`).
- `resolve --redispatch` is reached only through the CLI. In the suite it is reached from `test_shepherd.py:581,583`, `test_decision_log.py:141` (a refusal, unaffected) and the new file.

## Acceptance results

Each command was run from the worktree root through the wrapper `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; …)`, with node v24.14.0. `TMPDIR` was set to this run's scratch directory, where the parent's GIVEN block wrote `t0023-parent.sh`, `t0023-closed.sh` and `t0023-wf.mjs` verbatim. The "after" results are on commit `7463a1e`.

- A redispatch after a killed reviewer keeps the verifier's passing rows. NEW.
  Before: `kept: ` / `set aside: ci.yaml reviewer.yaml verifier.yaml `. Every row was set aside.
  After: `kept: ci.yaml verifier.yaml ` / `set aside: reviewer.yaml `. Matches.
- A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval. NEW.
  Before: `kept: ` / `set aside: ci.yaml reviewer.yaml verifier.yaml `.
  After: `kept: reviewer.yaml ` / `set aside: ci.yaml verifier.yaml `. Matches.
- A refused archive or sub-ticket add parks with the refusal text. NEW.
  Before: `park: archive: `, `start: planner`, `park: harness-bug: subticket add: `. Both reasons were blank.
  After: `park: archive: no spec store (factory init not run)`, `start: planner`, `park: harness-bug: subticket add: ST-2: no Depends on line`. Matches.
- A refused run start during intake parks with the refusal text. NEW.
  Before: `start: triage`, `park: harness-bug: run start triage: `.
  After: `start: triage`, `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`. Matches.
- A command that prints no JSON parks with its exit code. NEW.
  Before: `park: archive: `. After: `park: archive: exit 1, no JSON on stdout`. Matches.
- A redispatched sub-ticket runs only the checker whose row was set aside. NEW.
  Before: `start: reviewer`, `start: verifier`, `park: stub stop`. The verifier ran again for nothing.
  After: `start: reviewer`, `park: stub stop`. Matches.
- After an implementer run both checkers run. REGRESSION.
  After: `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`. Matches.
- Intermediate check: the changelog entry carries this seam's clause. NEW.
  Before: `51 CONTIGUOUS`, `4`. After: `51 CONTIGUOUS`, `6`. Entry 51 is still numbered without a gap, and it now holds `error text` and `redispatch` as well as the four words from the earlier seams.
- Intermediate check: the new test file and the edited shepherd test pass, and the shepherd edit stays inside its test. NEW.
  After: `7 passed in 7.29s`, `pytest_exit=0`. The hunk headers are `@@ -572 +572 @@`, `@@ -585 +585 @@` and `@@ -587 +586,0 @@`. These are the docstring line, line 585 and line 587, all between 570 and 590.
- The harness suite passes with an uncommitted harness edit. REGRESSION. Run exactly as written.
  After: `241 passed in 221.32s (0:03:41)`. No `failed` or `error`. `ls /tmp | grep t0023-suite` printed nothing afterwards, so the scenario removed its temporary directory.
- The change adds no whitespace errors. REGRESSION.
  After: `exit=0` only.

I also ran three stub cases of my own with `t0023-wf.mjs`, each on a sub-ticket entered at `checks-in-flight`:
- A refused `results show` printed `park: harness-bug: results show: no such ticket`.
- All three rows present printed only `park: stub stop`: no checker ran, and the build went straight to the join.
- Only `ci` missing printed `start: verifier`, then `park: stub stop`.

Gates, each run once from the worktree exactly as written, on `7463a1e`:
- `(export HOME=…; git diff --check main...HEAD)` printed nothing and exited 0.
- `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `241 passed in 184.04s (0:03:04)` and exited 0.

## Tests added/changed

- Added `tests/factory/test_redispatch_rows.py`, 6 tests. Each drives `bin/factory` on a throwaway store and covers one D1 case:
  - A KILLED reviewer with a passing verifier: only `reviewer.yaml` moves, and `results show` reports `missing: [reviewer]`.
  - A SPEC-DEFECT verifier with an approving reviewer: `verifier.yaml` and `ci.yaml` move together.
  - `VERIFIED` with a gate row of `FAIL`: both verifier rows move. This is the T-0012.5 case in the parent's evidence.
  - All rows passing: nothing moves, and no `superseded-*` directory is created.
  - No rows at all: nothing moves, and no results directory is created.
  - A second redispatch: its rows go to `superseded-2`.
  Before the fix, the first five tests failed. "No rows at all" already passed, because it describes today's behaviour as well.
- Changed `tests/factory/test_shepherd.py` `test_redispatch_re_runs_the_checks_on_the_same_head_after_a_harness_fix`, exactly as the parent's "Tests to change" lists it:
  - Line 585 now expects `{"reviewer": "APPROVE"}` and `superseded-1` holding `["ci.yaml", "verifier.yaml"]`.
  - Line 587, the reviewer re-dispatch, is removed.
  - The docstring's "the old rows are set aside" now reads "the rows that did not pass are set aside".
  The edit is needed because part D now keeps the approving reviewer row. The test still ends with the sub-ticket `merged` after the verifier alone re-runs.

## Known gaps and uncertainties

- The workflow-script changes (B, D2) have no suite test. The parent's Decisions rule that out, because the suite does not need node. Their only checks are the acceptance scenarios and my three extra stub cases, all run under node with the parent's stub clerk.
- In D2, a sub-ticket that the implementer just moved to `checks-in-flight` counts as "implementer ran", so both checkers run, as the spec requires. A sub-ticket that enters `checks-in-flight` without an implementer pass asks `results show`. The second case covers a redispatch and a resumed sub-ticket. I found no third way into that state in `buildOne`.
- D1 now moves only the three role rows (`reviewer`, `verifier`, `ci`). Before, it moved every `*.yaml` under `results/<head>/`. `results record` writes only those three roles (`factory/cli.py` `results_record`), so no other file is expected there.
- `factory:` markers added: none.

## Out-of-scope observations

- README line 317 describes `--redispatch` as "re-run the checks on the same commit after an outside fix". It is still true, but it does not say that rows which passed are kept. The parent assigns README edits to S1 and S3 only (J2, J3), so I left it.
- `dev/build-harness.spec.md` line 195 names a state `ready-for-checks` that a redispatch would move to. The harness moves a redispatched sub-ticket to `checks-in-flight`, as it did before this change. Line 292 of the same file already says that "only the missing checker runs", which this change now implements. The parent says not to change that file (J5), so I left it.

## Responses to findings

None. This is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high: every acceptance command printed its expected output, and both gates passed on the committed head.
ESCALATIONS: none
