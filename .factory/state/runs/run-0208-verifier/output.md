Commit: 7463a1e5ad82c68d5a156ebb4d34689b890e09a1

How I ran it. PR side: the given worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0208-verifier/wt` at `7463a1e`, after `uv sync --frozen`. Base side: a clean clone at `a6e9e10` (the given base, which is also `main`), in `scratch/base`, after `uv sync --frozen`. I ran the parent's GIVEN block verbatim once, with `TMPDIR` set to this run's scratch directory. It wrote `t0023-parent.sh`, `t0023-closed.sh` and `t0023-wf.mjs` there. I copied each WHEN out of the input with `sed` and ran it unchanged under bash, through the wrapper `(export HOME="$(cd "$(mktemp -d)" && pwd -P)"; …)`, from the checkout root, with node v24.14.0. The worktree was clean before and after (`git status --short` printed nothing). The diff touches only `docs/changelog.md`, `factory/cli.py`, `factory/workflows/build.js`, `factory/workflows/intake.js`, the new `tests/factory/test_redispatch_rows.py` and `tests/factory/test_shepherd.py`. The harness files are the protected paths this sub-ticket declares.

Per criterion:
- NEW | A redispatch after a killed reviewer keeps the verifier's passing rows | base: `kept: ` / `set aside: ci.yaml reviewer.yaml verifier.yaml ` | PR: `kept: ci.yaml verifier.yaml ` / `set aside: reviewer.yaml ` | PASS
- NEW | A redispatch after a verifier SPEC-DEFECT keeps the reviewer's approval | base: `kept: ` / `set aside: ci.yaml reviewer.yaml verifier.yaml ` | PR: `kept: reviewer.yaml ` / `set aside: ci.yaml verifier.yaml ` | PASS
- NEW | A refused archive or sub-ticket add parks with the refusal text | base: `park: archive: `, `start: planner`, `park: harness-bug: subticket add: ` | PR: `park: archive: no spec store (factory init not run)`, `start: planner`, `park: harness-bug: subticket add: ST-2: no Depends on line` | PASS
- NEW | A refused run start during intake parks with the refusal text | base: `start: triage`, `park: harness-bug: run start triage: ` | PR: `start: triage`, `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage` | PASS
- NEW | A command that prints no JSON parks with its exit code | base: `park: archive: ` | PR: `park: archive: exit 1, no JSON on stdout` | PASS
- NEW | A redispatched sub-ticket runs only the checker whose row was set aside | base: `start: reviewer`, `start: verifier`, `park: stub stop` | PR: `start: reviewer`, `park: stub stop` | PASS
- REGRESSION | After an implementer run both checkers run | base (run anyway): `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop` | PR: the same four lines | PASS
- NEW | Intermediate check, the changelog entry carries this seam's clause | base: `51 CONTIGUOUS` / `4` | PR: `51 CONTIGUOUS` / `6` | PASS
- NEW | Intermediate check, the new test file and the edited shepherd test pass, and the shepherd edit stays inside its test | base: the pytest part printed `no tests ran`, because `tests/factory/test_redispatch_rows.py` does not exist there yet, and the `git diff main...HEAD` part has nothing to diff (base is `main`). That is the expected failure for a criterion about a new file. To show the tests mean something, I copied the PR's `test_redispatch_rows.py` and `test_shepherd.py` into a second clean clone at base and ran the same two targets. They gave `6 failed, 1 passed`, and the one pass is `test_no_rows_at_all_moves_nothing`, which also describes base behaviour. The other five failed on behaviour, for example `['ci', 'reviewer', 'verifier'] == ['reviewer']`. | PR: `7 passed in 7.81s`, pytest exit 0. Hunk headers: `@@ -572 +572 @@`, `@@ -585 +585 @@`, `@@ -587 +586,0 @@`. Those are the docstring line, line 585 and line 587, all between 570 and 590. The diff matches "Tests to change": line 585 expects `{"reviewer": "APPROVE"}` and `["ci.yaml", "verifier.yaml"]`, the reviewer dispatch on 587 is removed, and the docstring reads "the rows that did not pass are set aside". | PASS
- REGRESSION | The harness suite passes with an uncommitted harness edit | base: not run | PR: `241 passed in 219.06s (0:03:39)` | PASS
- REGRESSION | The change adds no whitespace errors | base: not run | PR: `exit=0` only | PASS

Gate suite: PASS
  `(export HOME=…; git diff --check main...HEAD)` printed nothing and exited 0.
  `(export HOME=…; uv run --frozen pytest -q -p no:cacheprovider tests/factory)` printed `241 passed in 165.43s`. I ran it again to capture the exit code: `241 passed in 163.99s (0:02:43)`, `gate2_exit=0`.

Probes:
Workflow scripts, run under node with the parent's stub clerk:
- A refusal whose JSON has no `error` field, exit 2 → `park: archive: exit 2, no error text` → OK
- `{"ok": false, "error": ""}` with exit 0 → `park: archive: exit 0, no error text` → OK. The reason is not blank.
- Exit 3 with JSON `{"ok": true}` → `park: archive: exit 3, no error text` → OK. The existing line forces `ok` to false, and the new fallback fills the reason.
- A non-empty relayed stderr together with a JSON `error`, using a scratch copy of the stub that relays stderr → `park: archive: factory: stderr text` → OK. Stderr still wins when it is present.
- intake.js `run start` printing no JSON, exit 137 → `park: harness-bug: run start triage: exit 137, no JSON on stdout` → OK
- Entered at `checks-in-flight`, `results show` reports all three rows missing → `start: reviewer`, `start: verifier`, `park: stub stop` → OK
- Entered at `checks-in-flight`, `missing: ["verifier", "ci"]` with the reviewer row APPROVE → `start: verifier`, `park: stub stop` → OK
- `results show` prints no JSON, exit 1 → `park: harness-bug: results show: exit 1, no JSON on stdout` → OK

CLI `resolve --redispatch` on scratch stores, with row sets next to the tested ones:
- Reviewer REQUEST-CHANGES, verifier VERIFIED and gate PASS → superseded `["reviewer"]`; `missing: ["reviewer"]` → OK
- Killed verifier, which writes no ci row, with reviewer APPROVE → superseded `["verifier"]`; `missing: ["verifier", "ci"]`, so the build would run the verifier → OK
- Verifier FAILED with gate PASS and no reviewer row → superseded `["verifier", "ci"]`; all three missing → OK
- Verifier VERIFIED with no `Gate suite:` line, so ci is FAIL, plus reviewer APPROVE → superseded `["verifier", "ci"]`, reviewer kept → OK

None of the probes shows behaviour tied to the tested inputs. The keep rule depends only on the row statuses, and the checker choice depends only on `missing`.

Note: after the suite scenario, `/tmp/t0023-suite.g5G5PW` was still present. It was created at 08:28, after my run had started (my run took 3:39 and ended about 08:31), and its contents were still changing at 08:30. So it belongs to a concurrent run, most likely `run-0209-reviewer`, and does not show that the scenario skips its cleanup.

STATUS: VERIFIED
CONFIDENCE: high, every acceptance command and both gates ran on `7463a1e` and printed the expected output; each NEW command printed the old behaviour on base; and nine edge probes behaved as the spec requires.
ESCALATIONS: none
