Commit: a1b271843cb2e99f2d4f845c57e0f47ec3799031

How I ran it. The PR side ran in the given worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0213-verifier/wt`. `git status --short` was empty and HEAD was `a1b2718`. I ran `uv sync --frozen` there, under a throwaway HOME. The base side ran in a clean clone at `5ea66e917b6c7be13e4c24ca4aedc83da936bd49`, in `scratch/base`, with a local `main` at that SHA and `.venv` linked to the worktree's (`uv.lock` is not in the diff). Every command ran through the wrapper `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; …)`, under node v24.14.0, with `TMPDIR` set to this run's scratch directory. That scratch directory is where I wrote the parent's GIVEN block, extracted verbatim from the spec, which created `t0023-parent.sh`, `t0023-closed.sh` and `t0023-wf.mjs`. I took each WHEN verbatim from the sub-ticket (input.md lines 85-115) and ran it with `bash -c`. The merge commit brings in store files only: `git diff --stat 7463a1e HEAD -- . ':!.factory'` prints nothing.

Per criterion:
- NEW | A redispatch after a killed reviewer keeps the verifier's passing rows | base: `kept: ` / `set aside: ci.yaml reviewer.yaml verifier.yaml ` | PR: `kept: ci.yaml verifier.yaml ` / `set aside: reviewer.yaml ` | PASS
- NEW | A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval | base: `kept: ` / `set aside: ci.yaml reviewer.yaml verifier.yaml ` | PR: `kept: reviewer.yaml ` / `set aside: ci.yaml verifier.yaml ` | PASS
- NEW | A refused archive or sub-ticket add parks with the refusal text | base: `park: archive: `, `start: planner`, `park: harness-bug: subticket add: ` | PR: `park: archive: no spec store (factory init not run)`, `start: planner`, `park: harness-bug: subticket add: ST-2: no Depends on line` | PASS
- NEW | A refused run start during intake parks with the refusal text | base: `start: triage`, `park: harness-bug: run start triage: ` | PR: `start: triage`, `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage` | PASS
- NEW | A command that prints no JSON parks with its exit code | base: `park: archive: ` | PR: `park: archive: exit 1, no JSON on stdout` | PASS
- NEW | A redispatched sub-ticket runs only the checker whose row was set aside | base: `start: reviewer`, `start: verifier`, `park: stub stop` | PR: `start: reviewer`, `park: stub stop` | PASS
- REGRESSION | After an implementer run both checkers run | base: not run | PR: `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop` | PASS
- NEW | Intermediate check, the changelog entry carries this seam's clause | base: `51 CONTIGUOUS` / `4` | PR: `51 CONTIGUOUS` / `6` | PASS
- NEW | Intermediate check, the new test file and the edited shepherd test pass, and the shepherd edit stays inside its test | base: `ERROR: file or directory not found: tests/factory/test_redispatch_rows.py`, `no tests ran` (pytest exit 4), and no hunk headers, because base is `main`. That failure is what this criterion expects on base: it is about a new file. To check that the tests themselves fail on base behaviour, I copied the PR's `test_redispatch_rows.py` and `test_shepherd.py` (as `test_shepherd_pr.py`) into the base clone and ran the same targets. They gave `6 failed, 1 passed in 11.44s`. The one pass is `test_no_rows_at_all_moves_nothing`, which describes base behaviour too. I then removed both copies. | PR: `7 passed in 7.44s`, and a separate run gave pytest exit 0. Hunk headers: `@@ -572 +572 @@`, `@@ -585 +585 @@` and `@@ -587 +586,0 @@`, all between 570 and 590. They are the docstring line, line 585 and line 587. I read the hunks: they match "Tests to change" (expects `{"reviewer": "APPROVE"}` and `["ci.yaml", "verifier.yaml"]`, drops the reviewer re-dispatch, and the docstring now reads "the rows that did not pass are set aside"). | PASS
- REGRESSION | The harness suite passes with an uncommitted harness edit | base: not run | PR: `241 passed in 218.77s (0:03:38)`, with no `failed` or `error` | PASS
- REGRESSION | The change adds no whitespace errors | base: not run | PR: `exit=0` only | PASS

Gate suite: PASS
  `git diff --check main...HEAD`: printed only `exit=0` (run as the last criterion above, exactly as written).
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`: `241 passed in 179.71s (0:02:59)`, exit=0.

Probes. All are on the PR head. The workflow probes use the parent's stub clerk, with a sub-ticket that enters at `checks-in-flight`:
- `results show` reports `missing: []` → `park: stub stop`. No checker runs, and the build goes straight to the join → OK
- `missing: ["ci"]` only → `start: verifier`, `park: stub stop` → OK
- `missing: ["reviewer","verifier","ci"]` → `start: reviewer`, `start: verifier`, `park: stub stop` → OK
- `results show` refused with JSON `error` "no such ticket T-0001.1", exit 2 → `park: harness-bug: results show: no such ticket T-0001.1` → OK
- `results show` prints `Traceback`, no JSON, exit 1 → `park: harness-bug: results show: exit 1, no JSON on stdout` → OK
- `results show` prints `{"ok": true, "rows": {}}`, malformed, with no `missing` key → `park: stub stop`. No checker runs, and the join gets the decision. The real `results show` always prints `missing` (`factory/cli.py` line 523), and the store's join refuses to merge without all three rows, so this is not a defect → OK
- An archive that exits 2 with `{"ok": true}` and no error → `park: archive: exit 2, no error text`. Also `{"ok": false}` with exit 0 → `park: archive: exit 0, no error text` → OK (the B2 fallback)
- intake, `run start` with no output and exit 3 → `park: harness-bug: run start triage: exit 3, no JSON on stdout` → OK
- An archive refusal with a different message ("change folder T-0001 has unmerged deltas") → `park: archive: change folder T-0001 has unmerged deltas`. The fix is not special-cased to the tested text → OK
- A copy of the stub that relays a non-empty stderr ("stderr text") together with a JSON `error` → `park: archive: stderr text`. The relayed stderr still wins → OK
- CLI `resolve --redispatch`, reviewer `REQUEST-CHANGES` with VERIFIED/PASS → only `reviewer.yaml` moves (`superseded: ["reviewer"]`), and `missing: ["reviewer"]` → OK
- CLI: the verifier's STATUS is `FAILED` with gate PASS, and the reviewer is APPROVE → `ci.yaml` and `verifier.yaml` move together, and the approval is kept → OK
- CLI: only an approving reviewer row exists → nothing moves, no `superseded-*` directory is created, and `missing: ["verifier","ci"]` → OK
- CLI: only VERIFIED/PASS rows exist, with no reviewer → nothing moves, no directory is created, and `missing: ["reviewer"]` → OK

Out-of-scope observations:
- `/tmp/t0023-suite.g5G5PW` exists with mtime 08:28 today. That is before this run, whose suite scenario ran at about 09:50 and removed its own directory. An earlier run of the suite scenario (another role's run, judging by the time) seems to have left it behind. I did not delete it, because it is not this run's.

STATUS: VERIFIED
CONFIDENCE: high, every acceptance command ran verbatim with its expected output. The six NEW behaviour criteria printed the parent's stated "today" output on base, and both gates passed on `a1b2718`. The probes showed the fix is general, not special-cased to the tested inputs.
ESCALATIONS: none
