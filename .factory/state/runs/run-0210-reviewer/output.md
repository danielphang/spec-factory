Commit: 7463a1e5ad82c68d5a156ebb4d34689b890e09a1 (branch `factory/T-0023.3`, merge-base with `main` a6e9e10; `main` is at 5ea66e9, which differs from the merge-base by store commits only, so `main...HEAD` is the six files below)

## What I checked, in the role's order

1. Test integrity. One existing test file changed, `tests/factory/test_shepherd.py`, and only inside `test_redispatch_re_runs_the_checks_on_the_same_head_after_a_harness_fix`. `git diff -U0 main...HEAD -- tests/factory/test_shepherd.py | grep '^@@'` printed `@@ -572 +572 @@`, `@@ -585 +585 @@` and `@@ -587 +586,0 @@`: the docstring line, the line-585 expectation and the removed line 587, exactly the three edits the parent's "Tests to change" lists. The new assertion is more specific than the old one (it names the kept row and the two set-aside files), not less. No skip, xfail or swallowed error anywhere in the diff. Not blocking.
2. Correctness, against the spec's intent.
   - D1 (`factory/cli.py:764-789`): the reviewer row is set aside unless `APPROVE`; verifier and ci rows go together unless `VERIFIED` and `PASS`; `store.results_for` globs only the top level of `results/<head>/`, so earlier `superseded-*/` rows never count as current; `todo` filters by `r in rows`, so a missing row is never "moved"; the directory is created only when `todo` is non-empty; the log event and the resolve record carry only the moved roles. Edge cases I traced: all rows passing (nothing moved, no directory), no rows and no results directory (nothing moved, no directory), reviewer `APPROVE` with the verifier rows absent (nothing moved), a second redispatch (numbering from the existing `superseded-*` count). The new test file covers each.
   - D2 (`factory/workflows/build.js:127-158`): `implemented` is taken from the state at the top of each loop pass, so after a `revise` or `conflict` `continue` the next pass sees `ready-for-implementer`, runs the implementer and then both checkers; a pass that enters at `checks-in-flight` asks `results show` after `ticket head`, so it reads rows for the head the checkers will see. With `roles` empty, `parallel([])` yields `[]`, `checked.some(r => !r)` is false and the build goes straight to `ticket join`, which is what the parent's Risk section says for a sub-ticket with every row passing. A refused `results show` parks as `harness-bug: results show: <error>`.
   - B1/B2 (`clerk()` in both scripts, identical edits): a no-JSON result gets `exit <n>, no JSON on stdout`; a refusal with empty relayed stderr gets the JSON `error`, else `exit <n>, no error text`. No reason template changed.
   - I ran every acceptance scenario of this sub-ticket from the worktree root through the wrapper, with `TMPDIR` set to this run's scratch directory, where I wrote the parent's `t0023-parent.sh` and `t0023-wf.mjs` verbatim (node v24.14.0):
     - killed reviewer: `kept: ci.yaml verifier.yaml ` / `set aside: reviewer.yaml `. Matches.
     - SPEC-DEFECT verifier: `kept: reviewer.yaml ` / `set aside: ci.yaml verifier.yaml `. Matches.
     - refused archive, then planner and refused subticket add: `park: archive: no spec store (factory init not run)`, `start: planner`, `park: harness-bug: subticket add: ST-2: no Depends on line`. Matches.
     - refused run start in intake: `start: triage`, `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`. Matches.
     - no JSON: `park: archive: exit 1, no JSON on stdout`. Matches.
     - redispatched, only reviewer missing: `start: reviewer`, `park: stub stop`. Matches.
     - after an implementer run: `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`. Matches.
     - my own stub case, every row present at `checks-in-flight`: `park: stub stop` only, so no checker ran and the join was asked. Matches the Risk section's intent.
     - changelog: `51 CONTIGUOUS`, then `6`. Matches.
3. Scope. Six files: `docs/changelog.md` (entry 51, S2 clause appended to the same line), `factory/cli.py` (redispatch branch and its comment only), `factory/workflows/build.js` (`clerk` and `buildOne` only), `factory/workflows/intake.js` (`clerk` only), the new `tests/factory/test_redispatch_rows.py`, and the listed `test_shepherd.py` edit. Nothing from S1, S3 or S4, no README edit, no `--roles` flag.
4. Silent behavior changes. Two, both intended by the parent and both stated in the PR description's Known gaps: a redispatch now moves only the three role rows rather than every `*.yaml` under `results/<head>/` (and `results_record` writes only those three roles); and a sub-ticket parked from `ready-for-merge` and redispatched with every row passing now runs no checker and goes to the join. Callers: both `clerk()` functions are the sole path to the store from each script; `buildOne` is called only from the build loop (`build.js:244`); `resolve --redispatch` is reached only from the CLI, and in the suite from `test_shepherd.py`, `test_decision_log.py` (a refusal) and the new file. I confirmed each by grep.
5. Security and data safety. No new input reaches a shell; the `rename` stays inside `results/<head>/`; the new tests use `tmp_path` stores through `FACTORY_STATE`. Nothing destructive.
6. Protected paths. `factory/cli.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`: all three declared by the sub-ticket. Listed under ESCALATIONS; the merge gate needs a human approval.
7. Coding standard. Rule 1: no new helper in harness code; D1 reuses `store.results_for` and `store.result_path`; D2 is a filter on the existing `roles` list. Rule 2: callers named in the PR description, checked above. Rule 3: no shortcut with a known limit; "factory: markers added: none" stated. Rule 5: names match the spec (`superseded`, `missing`, `rows`). Rule 6: no patched path. Lean already.
8. PR description. What changed opens with the two problems and who has them, glosses parked, clerk, row and redispatch at first use, and says in words what each part does. Known gaps names the no-suite-test gap for the workflow scripts and the two behavior changes above. Acceptance outputs are each followed by what they mean. No finding.

Gates, run from the worktree exactly as written on 7463a1e:
- `(export HOME=…; git diff --check main...HEAD)` printed nothing, `exit=0`.
- `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `241 passed in 182.53s (0:03:02)`, exit 0.

I did not re-run the "suite passes with an uncommitted harness edit" REGRESSION scenario; the implementer reports `241 passed in 221.32s` for it, and the suite gate above passes on the same tree.

## Findings

None.

## Prior findings

None. This is round 1.

## Out-of-scope observations

- `tests/factory/test_redispatch_rows.py:28-35` repeats the `run` and `js` helpers that eight other test modules each define for themselves (`test_resolve_rulings.py:22-29` is one), and `tests/factory/conftest.py` holds no fixtures. The per-module copy is this suite's established pattern, so I do not tag it; a conftest consolidation would be its own cleanup across nine files.
- `factory/workflows/build.js:181` still says a `wait` decision means "a row is missing after both checkers reported". After this change the join may be asked after one checker, or none, ran. The sentence's claim (a missing row at the join is a harness bug) still holds.

STATUS: APPROVE
CONFIDENCE: high: every acceptance scenario of the sub-ticket printed its expected output when I ran it, both gates passed on the reviewed head, and the one test edit is exactly the one the parent lists.
ESCALATIONS: protected paths touched, all declared by the sub-ticket: harness `factory/cli.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`. The merge gate needs a human approval for them; the code earns APPROVE.
