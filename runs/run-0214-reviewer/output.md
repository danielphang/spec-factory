Commit: a1b271843cb2e99f2d4f845c57e0f47ec3799031 (merge of `main` at `5ea66e9` into `7463a1e`; `git diff --stat 5ea66e9 HEAD -- . ':!.factory'` lists the same six files as `main...HEAD`, so the code under review is the ticket's own commit)

## What I checked

1. Test integrity. `git diff main...HEAD -- tests/factory/test_shepherd.py` shows three hunks, `@@ -572 +572 @@`, `@@ -585 +585 @@`, `@@ -587 +586,0 @@`: the docstring wording, the line-585 expectation (`{"reviewer": "APPROVE"}`, `superseded-1` = `["ci.yaml", "verifier.yaml"]`) and the removed reviewer re-dispatch. That is exactly the edit the sub-ticket's "Tests to change" names. The test still asserts `merged` at its end, so nothing is weakened. No other existing test changed. `tests/factory/test_redispatch_rows.py` is new; its six tests assert exact row sets, exact `superseded` lists, the log event and the absence of a directory, with no hard-coded tolerance.
2. Correctness, run in the worktree through the wrapper with `TMPDIR` set to this run's scratch directory, where I wrote `t0023-parent.sh` and `t0023-wf.mjs` verbatim from the parent's GIVEN block (node v24.14.0):
   - Killed reviewer: `kept: ci.yaml verifier.yaml ` / `set aside: reviewer.yaml `. Matches.
   - Verifier SPEC-DEFECT: `kept: reviewer.yaml ` / `set aside: ci.yaml verifier.yaml `. Matches.
   - Refused archive and sub-ticket add: `park: archive: no spec store (factory init not run)`, `start: planner`, `park: harness-bug: subticket add: ST-2: no Depends on line`. Matches.
   - Refused intake run start: `start: triage`, `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`. Matches.
   - No JSON: `park: archive: exit 1, no JSON on stdout`. Matches.
   - Redispatched sub-ticket: `start: reviewer`, `park: stub stop`. Matches.
   - After implementer: `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`. Matches.
   - Changelog: `51 CONTIGUOUS`, `6`. Matches.
   - `pytest … test_redispatch_rows.py …test_shepherd.py::test_redispatch_re_runs…`: `7 passed in 10.70s`; hunk headers as above, all between 570 and 590.
   - `git diff --check main...HEAD; echo exit=$?`: `exit=0` only.
   - Three extra stub cases of my own at `checks-in-flight`: all three rows present printed only `park: stub stop` (straight to the join); only `ci` missing printed `start: verifier`, `park: stub stop`; a refused `results show` printed `park: harness-bug: results show: no such ticket`.
   Edge cases read in the code: a KILLED verifier (no `ci` row) is set aside alone because `todo` keeps only roles in `rows` (`factory/cli.py:777`), and the build then runs the verifier because `missing` holds `verifier` and `ci` (`build.js:157`); a redispatch from `ready-for-merge` with every row passing moves nothing and the build goes to `ticket join`, as the parent's Risk section says. `results show` runs after `ticket head`, which refreshes the ticket's head from the branch (`factory/cli.py:463-465`), so the rows read are for the head the checkers would check.
3. Scope: only parts B, D, J1's S2 clause and the listed shepherd test. No reason template changed (B3): both diffs touch `clerk()` only.
4. Silent behaviour changes: two, both declared by the spec. `--redispatch` now moves only `reviewer`, `verifier` and `ci` rows, not every `*.yaml`; `results_record` writes only those three (`factory/cli.py:482-512`, `store.RESULT_ROLES`), so nothing else can be there. A `clerk()` no-JSON result on exit 0 now carries `exit 0, no JSON on stdout` instead of an empty string, which only makes a park reason less blank.
5. Security and data safety: file renames stay inside `results/<head>/`; no new input reaches a shell. The new test drives `bin/factory` with `FACTORY_STATE` under `tmp_path`, the same pattern as `tests/factory/test_resolve_rulings.py:24`.
6. Protected paths: `factory/cli.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`, all declared by the sub-ticket. Listed under ESCALATIONS.
7. Coding standard: no new helper or dependency; the change reuses `store.results_for` and `store.result_path`. Callers are named in the PR description (rule 2). `factory:` markers: none, and the PR says so (rule 3). No synonym introduced (rule 5). No patched paths (rule 6). Lean already.
8. Gate suite, run from the worktree exactly as written: `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `241 passed in 176.62s (0:02:56)`, no `failed` or `error`. (`PIPESTATUS` is not set under zsh, so I did not capture the exit code separately; the summary line is the evidence.) The gate's `git diff --check main...HEAD` printed nothing and exited 0.

## Findings

- [SHOULD-FIX] PR description: What changed: `harness`, `store`, `sub-ticket` and `checker` are used from the first sentence without a gloss (`parked`, `clerk` and `row` are glossed) → a technical reader new to the project cannot tell from this description what the harness or the store is, which the writing standard's rule 2 requires at first use. One clause each would do, e.g. "the harness, the code that moves a ticket between agents" and "the store, the folder holding its records".

Prior findings: none (round 1).

## Out-of-scope observations

- A resumed sub-ticket (one that re-enters `checks-in-flight` without a redispatch) whose reviewer row is `KILLED` now skips the reviewer, because `missing` does not list a role with any row, and `ticket join` then parks it as `budget kill: reviewer`. Before this change the resume re-ran both checkers. The parent's D2 rule asks for exactly this, and a `--redispatch` on that park sets the KILLED row aside, so it costs one extra park, not a wrong result.
- README line 317 still describes `--redispatch` only as "re-run the checks on the same commit after an outside fix"; it does not say passing rows are kept. The parent assigns README edits to S1 and S3.

STATUS: APPROVE
CONFIDENCE: high: every acceptance scenario of this sub-ticket printed its expected output when I ran it, the gate suite passed, and the one finding is prose.
ESCALATIONS: protected paths touched, all declared by the sub-ticket: harness `factory/cli.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`. The merge gate needs a human approval for them.
