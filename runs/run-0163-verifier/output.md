Commit: 7a4967a055bc40e3839c65fc00416299d90db350

Setup. PR: the given worktree `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0163-verifier/wt`, clean, `HEAD` = 7a4967a, `main` = merge base = d0300d3. Base: a fresh `git archive d0300d3127fdd257d725ecb996b4fe9df282cef9` extracted to a scratch directory. `uv sync --frozen` ran in both trees. Node is v24.14.0. The GIVEN block (`.factory/state/specs/T-0018/v2.md` lines 154-200, between the fences) ran once with `TMPDIR` set to a scratch directory. It wrote `t0018-drive.js`, `t0018-approved.sh` and `t0018-handplan.sh`. Each WHEN ran under bash from the root of its tree, exactly as written, and I read the outputs below directly.

Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL
- NEW | Intake leaves an approved ticket for the build workflow | `returned planned`, `ticket T-0001 planned in_flight=0 reason=-`, `run run-0004-planner PLANNED` (fails for the stated reason) | `returned ready-for-planner`, `ticket T-0001 ready-for-planner in_flight=0 reason=-`, no `run run-0004-planner` line | PASS
- REGRESSION | Build plans a gate-approved parent and creates its sub-tickets | not run | `run run-0004-planner PLANNED`, `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer`, `source: plan:run-0004-planner` | PASS
- NEW | Build creates the missing sub-tickets from the recorded planner run | `returned planned`, `ticket T-0001 planned in_flight=0 reason=-`, no T-0001.1 line, `grep: …/T-0001.1.yaml: No such file or directory` (stated reason) | `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer`, `run run-0005-implementer KILLED`, `source: plan:run-0004-planner` | PASS
- NEW | Build parks a planned parent it cannot give sub-tickets | `returned planned`, `ticket T-0001 planned in_flight=0 reason=-` (stated reason) | `returned parked`, `ticket T-0001 parked in_flight=0 reason=no sub-tickets, and none could be created from the recorded plan: no recorded planner run found for T-0001 (latest plan.added source: tests/factory/fixtures/stubs/accept-approve/planner-1.md); pass --run RUN or --file F`, no `ticket T-0001.1` line | PASS
- NEW | subticket add without a source uses the recorded planner run | `factory: TypeError: argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'NoneType'`, `exit=1`, no T-0001.1.yaml (stated reason) | last JSON line `{"ok": true, "parent": "T-0001", "subtickets": [{"id": "T-0001.1", …}]}`, `exit=0`, `source: plan:run-0004-planner` | PASS
- NEW | subticket add without a source refuses when the plan came from a file | the same `TypeError`, `exit=1`, listing `T-0001.yaml` (stated reason) | `no recorded planner run found for T-0001 …`, `exit=2`, no `TypeError`, listing `T-0001.yaml` alone | PASS
- NEW | A failed agent call in intake parks the ticket | `threw agent type 'factory-triage' not found`, `ticket T-0001 ready-for-triage in_flight=1 reason=-`, `run run-0001-triage running` (stated reason) | `returned parked`, `ticket T-0001 parked in_flight=0 reason=agent call failed: triage: agent type 'factory-triage' not found`, `run run-0001-triage KILLED` | PASS
- NEW | A failed agent call in the build parks the sub-ticket | `ticket T-0001.1 ready-for-implementer in_flight=1 reason=-`, `run run-0005-implementer running` (stated reason) | `ticket T-0001.1 parked in_flight=0 reason=agent call failed: implementer: agent type 'factory-implementer' not found`, `run run-0005-implementer KILLED` | PASS
- REGRESSION | The harness suite passes | not run | `171 passed in 110.28s (0:01:50)` (this is also the gate run) | PASS
- REGRESSION | The change adds no whitespace errors | not run | printed only `exit=0` (this is also the gate run) | PASS
- NEW | Heading and emphasis gate lines are read | all four lines `=> FAIL|missing Gate suite line` (stated reason) | `## Gate suite: PASS => PASS|`, `**Gate suite:** PASS => PASS|`, `### **Gate suite: PASS** => PASS|`, `**Gate suite: FAIL** 2 failed => FAIL|2 failed` | PASS
- REGRESSION | Plain gate lines and prose read as before | not run (it also printed the expected three lines on base) | `Gate suite: PASS => PASS|`, `Gate suite: FAIL 1 failed => FAIL|1 failed`, `The Gate suite: PASS line was missing => FAIL|missing Gate suite line` | PASS
- NEW | The verifier prompt pins the gate line in all three copies | `0 0 1` for each file (stated reason) | `docs/design.md 1 1 0`, `docs/prompts/07-verifier.md 1 1 0`, `factory/prompts/verifier.md 1 1 0` | PASS
- REGRESSION | The design block and its prompt copy stay identical | not run (it also printed `SAME` on base) | `SAME` | PASS
- NEW | The README says intake stops at the spec gate | `0` then `1` (stated reason) | `1` then `0` | PASS
- NEW | The changelog records the change | `0` then `0` (stated reason) | `1` then `1` | PASS
- NEW | The build spec names the accepted gate line forms | `0` (stated reason) | `1` | PASS

Every NEW criterion failed on base for the reason `verification.md` states and passes on the PR. No NEW criterion passes on both.

Gate suite: PASS
- `git diff --check main...HEAD` printed nothing, and `echo "exit=$?"` printed `exit=0`.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `171 passed in 110.28s (0:01:50)`, with no failures or errors. My `${PIPESTATUS[0]}` capture printed empty under this zsh shell, so I have no separate exit code. A pytest run with every test passing exits 0.

Probes:
- Gate-line forms near the tested ones, in one scratch store on the PR:
  - `  Gate suite: PASS` → `PASS|` → OK
  - `Gate suite:PASS` → `PASS|` → OK
  - a tab, then `# Gate suite: FAIL 3 failed **` → `FAIL|3 failed` → OK
  - `Gate suite: **FAIL** — 3 failed` → `FAIL|— 3 failed` → OK
  - These are not read, each giving `FAIL|missing Gate suite line`, as the spec's regex intends (only spaces, tabs, `#` and `*` may come before `Gate suite:`) → OK: `- Gate suite: PASS`, `> Gate suite: PASS`, `__Gate suite:__ PASS`, `**Gate suite**: PASS`, `Gate suite: PASSED` and `Gate suite: pass`.
  - `Gate suite:` with `PASS` on the next line → `FAIL|missing Gate suite line` → OK. On base, `\s*` crossed the newline and read this as PASS. The implementer disclosed the narrowing. It errs toward FAIL, and the new prompt pins the one-line form.
- `subticket add` with no source when a `--from-run` plan is followed by a later `--file` plan: refused with `no recorded planner run found for T-0001 (latest plan.added source: …planner-1.md)`, and only `T-0001.yaml` is left. The latest event wins, not just any recorded run, as B1 requires → OK.
- `subticket add T-0001` a second time after it succeeded: refused `{"ok": false, "error": "T-0001.1 already exists"}`, with no duplicate ticket → OK.
- `build.js` run twice on a hand-planned parent: the second run did not add sub-tickets again. The log holds 2 `ticket.created` events (the parent and T-0001.1), and the second run went straight to the existing T-0001.1 → OK.
- `build.js` with the verifier's `agent()` throwing (C2 for a checker, which no acceptance scenario covers): `ticket T-0001.1 parked in_flight=0 reason=agent call failed: verifier: agent type 'factory-verifier' not found` and `run run-0007-verifier KILLED`. The run's `wt/` directory no longer exists, so `run cleanup` ran → OK.
- Read only, not run: C1 (`build.js`: `if (!pc.ok) { await park(TICKET, \`parent-check refused: …\`); return {…, state: 'parked'} }`) matches the parent's text. B3's at-most-once limit is held by the `first` flag, which is set false before the `subticket add` call and on every later iteration → OK.

STATUS: VERIFIED
CONFIDENCE: high. Every acceptance command ran as written on both trees, every NEW criterion failed on base for its stated reason, both gates passed on the PR, and no probe found behaviour special-cased to the tested inputs.
ESCALATIONS: none
