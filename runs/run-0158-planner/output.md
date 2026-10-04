T-0018.1 / Intake stops at the spec gate, the build repairs or parks a planned parent with no sub-tickets, a thrown agent call parks its ticket, and the gate line is read in heading and bold forms
  Parent: T-0018, approved spec v2 (`.factory/state/specs/T-0018/v2.md`). Read it for context. Do NOT implement parts outside this sub-ticket.
  Depends on: none
  Parallel-safe: yes (it is the only sub-ticket)
  Scope: parts A, B, C, D, E and F of the parent, all of them.
    - A: `factory/workflows/intake.js` loses phase 3, Plan (lines 172-189), its `meta.phases` entry (line 7), "-> Planner" in `meta.description`, and `planner` in `AGENT_NAME` (line 35). A `ready-for-planner` ticket falls through to the existing `nothing to dispatch from this state` return (line 191).
    - B1: `factory/cli.py` `subticket_add` (line 366) and its parser entry: with neither `--run` nor `--file`, take the run from the `source` of the parent's latest `plan.added` event and continue exactly as `--run` does; refuse with exit 2, store unchanged, when there is no such event or its source is not a run directory of this store.
    - B2: `factory/cli.py` `ticket_ready_implementers` (line 406): add a `subtickets` key, every sub-ticket id of the parent in id order; existing keys unchanged.
    - B3: `factory/workflows/build.js` phase 2, before the loop's first `parallel`: an empty `subtickets` list on the first `ready-implementers` answer runs clerk `subticket add PARENT` once per build run; on refusal, park the parent with a reason containing `no sub-tickets` and return `parked`; on success, log the count and continue.
    - C1: `build.js` lines 212-213: a refused `parent-check` parks the parent with `parent-check refused: <stderr>` and returns `parked`.
    - C2: `runRole` in `intake.js` (lines 74-104) and `build.js` (lines 64-101): a thrown `agent()` call, stub branch and real branch, finishes the run with `--status-override KILLED`, runs `run cleanup` for a reviewer or verifier in `build.js`, parks the ticket with `agent call failed: <role>: <error message>` through the existing `park()`, and returns `null`. A null or empty result keeps today's path.
    - D1: `factory/cli.py` `results_record` line 480: the regex `^[ \t#*]*Gate suite:[ \t*]*(PASS|FAIL)\b(.*)$` (`re.M`), detail stripped of spaces and `*` at both ends, `None` when empty; no-match unchanged.
    - D2: the two-line replacement of `Gate suite: PASS/FAIL, with failing output` at `docs/design.md` line 644, the same in `factory/prompts/verifier.md` line 38 (its step 4 stays different on purpose), and `docs/prompts/07-verifier.md` re-copied verbatim from the design block.
    - D3: `docs/changelog.md` entry `47. After issue #33 (2026-10-04), ...` after entry 46 (line 50) and before `Declined:`, covering the three points the parent lists.
    - E: `README.md` lines 83-85 and 275-276 replaced with the parent's exact sentences (the line-276 sentence starts at the end of line 275, "Start the"), the status-header date kept current; `dev/build-harness.spec.md` lines 275, 285 and 320 as the parent describes, line 320 using the phrase "heading or emphasis marks".
    - F: one new file, `tests/factory/test_build_startup.py`, through `bin/factory` on a scratch store, covering `subticket add` with no source (success and refusal), the `subtickets` key, and the D1 gate-line forms.
  Acceptance (all from the parent's `verification.md`; run every WHEN from the root of the checkout under test after `uv sync --frozen`, with node 18 or later on the PATH. The workflow-dispatch scenarios first need the parent's GIVEN block run once: the `sh` block at `.factory/state/specs/T-0018/v2.md` lines 153-201, which writes `${TMPDIR:-/tmp}/t0018-drive.js`, `t0018-approved.sh` and `t0018-handplan.sh`.)
    - Intake leaves an approved ticket for the build workflow (NEW)
      WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && node $DRV factory/workflows/intake.js T-0001 tests/factory/fixtures/stubs/accept-approve $W/t)`
      THEN the output contains `returned ready-for-planner` and `ticket T-0001 ready-for-planner in_flight=0 reason=-`, and no line starting `run run-0004-planner`
    - Build plans a gate-approved parent and creates its sub-tickets (REGRESSION)
      WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && mkdir $W/p && cp tests/factory/fixtures/stubs/accept-approve/planner-1.md $W/p/ && node $DRV factory/workflows/build.js T-0001 $W/p $W/t; grep '^source:' $FACTORY_STATE/tickets/T-0001.1.yaml)`
      THEN the output contains `run run-0004-planner PLANNED`, `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer` and `source: plan:run-0004-planner`
    - Build creates the missing sub-tickets from the recorded planner run (NEW)
      WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && . ${TMPDIR:-/tmp}/t0018-handplan.sh && node $DRV factory/workflows/build.js T-0001 $W/none $W/t; grep '^source:' $FACTORY_STATE/tickets/T-0001.1.yaml)`
      THEN the output contains `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer`, `run run-0005-implementer KILLED` and `source: plan:run-0004-planner`
    - Build parks a planned parent it cannot give sub-tickets (NEW)
      WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && bin/factory plan add T-0001 --file tests/factory/fixtures/stubs/accept-approve/planner-1.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by workflow >/dev/null && node $DRV factory/workflows/build.js T-0001 $W/none $W/t)`
      THEN the output contains `returned parked` and a line starting `ticket T-0001 parked in_flight=0 reason=` that contains `no sub-tickets`, and no line starting `ticket T-0001.1`
    - subticket add without a source uses the recorded planner run (NEW)
      WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && . ${TMPDIR:-/tmp}/t0018-handplan.sh && bin/factory subticket add T-0001; echo "exit=$?"; grep '^source:' $FACTORY_STATE/tickets/T-0001.1.yaml)`
      THEN stdout's last JSON line has `"ok": true` and names `T-0001.1`, followed by `exit=0` and `source: plan:run-0004-planner`
    - subticket add without a source refuses when the plan came from a file (NEW)
      WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && bin/factory plan add T-0001 --file tests/factory/fixtures/stubs/accept-approve/planner-1.md >/dev/null && bin/factory subticket add T-0001; echo "exit=$?"; ls $FACTORY_STATE/tickets)`
      THEN the output contains `exit=2` and no `TypeError`, and the listing is `T-0001.yaml` alone
    - A failed agent call in intake parks the ticket (NEW)
      WHEN `(DRV=${TMPDIR:-/tmp}/t0018-drive.js; W=$(mktemp -d); export FACTORY_STATE=$W/store; printf '# Fixture\n\nThe bot should do the thing.\n' > $W/req.md && bin/factory ticket new --file $W/req.md >/dev/null && node $DRV factory/workflows/intake.js T-0001 tests/factory/fixtures/stubs/accept-approve $W triage)`
      THEN the output contains `returned parked`, a line starting `ticket T-0001 parked in_flight=0 reason=` that contains `agent type 'factory-triage' not found`, and `run run-0001-triage KILLED`
    - A failed agent call in the build parks the sub-ticket (NEW)
      WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && node $DRV factory/workflows/build.js T-0001 tests/factory/fixtures/stubs/accept-approve $W/t implementer)`
      THEN the output contains a line starting `ticket T-0001.1 parked in_flight=0 reason=` that contains `agent type 'factory-implementer' not found`, and `run run-0005-implementer KILLED`
    - The harness suite passes (REGRESSION)
      WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`
      THEN it exits 0 with no failures
    - The change adds no whitespace errors (REGRESSION)
      WHEN `git diff --check main...HEAD; echo "exit=$?"`
      THEN it prints only `exit=0`
    - Heading and emphasis gate lines are read (NEW)
      WHEN `(W=$(mktemp -d); export FACTORY_STATE=$W/store; printf '# Fixture\n\nThe bot should do the thing.\n' > $W/req.md && bin/factory ticket new --file $W/req.md >/dev/null && H=$(printf 'a%.0s' $(seq 40)) && for form in '## Gate suite: PASS' '**Gate suite:** PASS' '### **Gate suite: PASS**' '**Gate suite: FAIL** 2 failed'; do printf 'Commit: %s\n%s\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n' $H "$form" > $W/v.md && bin/factory results record T-0001 --head $H --role verifier --output $W/v.md >/dev/null && echo "$form => $(sed -n 's/^status: //p' $FACTORY_STATE/results/$H/ci.yaml)|$(sed -n 's/^detail: //p' $FACTORY_STATE/results/$H/ci.yaml)"; done)`
      THEN it prints `## Gate suite: PASS => PASS|`, `**Gate suite:** PASS => PASS|`, `### **Gate suite: PASS** => PASS|` and `**Gate suite: FAIL** 2 failed => FAIL|2 failed`
    - Plain gate lines and prose read as before (REGRESSION)
      WHEN `(W=$(mktemp -d); export FACTORY_STATE=$W/store; printf '# Fixture\n\nThe bot should do the thing.\n' > $W/req.md && bin/factory ticket new --file $W/req.md >/dev/null && H=$(printf 'a%.0s' $(seq 40)) && for form in 'Gate suite: PASS' 'Gate suite: FAIL 1 failed' 'The Gate suite: PASS line was missing'; do printf 'Commit: %s\n%s\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n' $H "$form" > $W/v.md && bin/factory results record T-0001 --head $H --role verifier --output $W/v.md >/dev/null && echo "$form => $(sed -n 's/^status: //p' $FACTORY_STATE/results/$H/ci.yaml)|$(sed -n 's/^detail: //p' $FACTORY_STATE/results/$H/ci.yaml)"; done)`
      THEN it prints `Gate suite: PASS => PASS|`, `Gate suite: FAIL 1 failed => FAIL|1 failed` and `The Gate suite: PASS line was missing => FAIL|missing Gate suite line`
    - The verifier prompt pins the gate line in all three copies (NEW)
      WHEN `for f in docs/design.md docs/prompts/07-verifier.md factory/prompts/verifier.md; do echo "$f $(grep -cxF 'Gate suite: PASS/FAIL, with failing output on the lines below it' $f) $(grep -cxF '  (a plain line starting "Gate suite:", never a heading or bold)' $f) $(grep -cx 'Gate suite: PASS/FAIL, with failing output' $f)"; done`
      THEN it prints `docs/design.md 1 1 0`, `docs/prompts/07-verifier.md 1 1 0` and `factory/prompts/verifier.md 1 1 0`
    - The design block and its prompt copy stay identical (REGRESSION)
      WHEN `awk 'BEGIN{q=sprintf("%c%c%c",96,96,96)} /^## 7\. Verifier/{f=1;next} f&&index($0,q"text")==1{p=1;next} p&&index($0,q)==1{exit} p' docs/design.md | diff - docs/prompts/07-verifier.md && echo SAME`
      THEN it prints `SAME`
    - The README says intake stops at the spec gate (NEW)
      WHEN `grep -cF 'The intake script stops at the spec gate; the build script runs the planner.' README.md; grep -c 'intake script also contains' README.md`
      THEN it prints `1` then `0`
    - The changelog records the change (NEW)
      WHEN `grep -c '^47\. After issue #33 (2026-10-04)' docs/changelog.md; grep '^47\. ' docs/changelog.md | grep -c 'Gate suite:'`
      THEN it prints `1` then `1`
    - The build spec names the accepted gate line forms (NEW)
      WHEN `grep -c "heading or emphasis marks" dev/build-harness.spec.md`
      THEN it prints a number of 1 or more
    - Intermediate checks: none. The suite gate covers the new `tests/factory/test_build_startup.py`. Three behaviours have no runnable scenario and are left to the reviewer against the parent's text: C1 (the `parent-check` refusal park; no scenario reaches a refused `parent-check` once B3 repairs or parks an empty parent), the "at most once per build run" limit in B3, and the C2 `run cleanup` for a reviewer or verifier whose call throws.
  Tests to change: none. The parent names why the existing ones stay green: no test asserts on intake's Plan phase, the `ready-implementers` tests (`tests/factory/test_subtickets.py` lines 119-152, `tests/factory/test_shepherd.py` lines 194, 299, 384, 466) read only existing keys, and the gate-line tests use plain lines.
  Protected paths: harness: `factory/workflows/intake.js`, `factory/workflows/build.js`, `factory/cli.py`, `factory/prompts/verifier.md` (also a guardrail path, an agent prompt; the parent asks for this change); generated: `docs/prompts/07-verifier.md` (re-copied from the changed `docs/design.md` block only, never hand-edited). All are declared in the parent's Risk section.
  Out of scope: the planner's output format (#13); a `resolve` verb that resumes a ticket parked by a failed agent call or for having no sub-tickets; a clerk call whose own `agent()` throws; which gate line counts when there are several (the first match stays); the build's quiet `planned` return when every remaining sub-ticket is parked; agent definitions for the build roles (#24 part A); keeping the node driver as a permanent test; `dev/issues.md` and #21's dead-code list; describing the new park reasons in README's present-tense sections; `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**`, `~/.nanobot/**`; the operator steps (the prompt acceptance test before the runtime moves, `--accept-harness` on each instance, telling the Nanobot Driver session).

Coverage map:
  Intake leaves an approved ticket for the build workflow → T-0018.1
  Build plans a gate-approved parent and creates its sub-tickets → T-0018.1
  Build creates the missing sub-tickets from the recorded planner run → T-0018.1
  Build parks a planned parent it cannot give sub-tickets → T-0018.1
  subticket add without a source uses the recorded planner run → T-0018.1
  subticket add without a source refuses when the plan came from a file → T-0018.1
  A failed agent call in intake parks the ticket → T-0018.1
  A failed agent call in the build parks the sub-ticket → T-0018.1
  The harness suite passes → T-0018.1
  The change adds no whitespace errors → T-0018.1
  Heading and emphasis gate lines are read → T-0018.1
  Plain gate lines and prose read as before → T-0018.1
  The verifier prompt pins the gate line in all three copies → T-0018.1
  The design block and its prompt copy stay identical → T-0018.1
  The README says intake stops at the spec gate → T-0018.1
  The changelog records the change → T-0018.1
  The build spec names the accepted gate line forms → T-0018.1

Why one sub-ticket. The parent estimates about 170 changed lines. I considered two splits, and neither makes review or rollback easier.
- Gate line (D) apart from the workflow fixes (A, B, C). Both halves edit `factory/cli.py` (B1, B2 and D1), the one new test file (F), `dev/build-harness.spec.md` (E) and the single changelog entry 47 (D3), so they could not run in parallel. The parent asks for one entry 47 that covers all three changes. With a split, either the first half changes the design doc with no changelog entry, which breaks the design doc's own convention, or the second half rewrites the first half's entry.
- Intake (A) apart from the build (B, C). A alone is safe to merge, but B3 needs B1 and B2, and C2 edits `runRole` in both scripts, so every split shares a file.
- Rollback is by moving the runtime (the pinned harness checkout at `~/dev/spec-factory-harness` that runs tickets) back to an earlier revision; a merge into `main` never reaches it on its own. The operator's acceptance test of the prompt change (operator step 1) runs before the runtime moves and does not need a separate merge.

What I checked, read-only except for scratch stores under my scratchpad, on `main` at `d0300d3`:
- Every cited location exists as the parent says: `intake.js` line 7 (Plan phase entry), line 35 (`AGENT_NAME` with `planner`), lines 172-189 (phase 3), line 191 (the fall-through return); `build.js` line 190 (`subticket add`), lines 205-207 and 212-213; `cli.py` line 366 `subticket_add`, line 406 `ticket_ready_implementers`, line 480 (the anchored regex), line 594 (`has no sub-tickets`); `Gate suite: PASS/FAIL, with failing output` at `docs/design.md:644`, `docs/prompts/07-verifier.md:37`, `factory/prompts/verifier.md:38`; `README.md` lines 83-85 and the sentence across lines 275-276; changelog entry 46 at line 50 and `Declined:` at line 52; `tests/factory/test_build_startup.py` does not exist yet.
- I wrote the GIVEN fixtures and ran every scenario on the base. Each printed what `verification.md` says it prints today: intake `returned planned` with `run run-0004-planner PLANNED`; the REGRESSION build scenario already passes; the repair scenario `returned planned` with no `T-0001.1`; the file-plan build `returned planned` with no park; both `subticket add` scenarios the `TypeError` with `exit=1`; the intake throw `run run-0001-triage running` with `in_flight=1`; the build throw `run run-0005-implementer running`; all four heading or bold gate lines `FAIL|missing Gate suite line`; the plain and prose lines as expected; each prompt copy `0 0 1`; the design-block diff `SAME`; README `0` then `1`; changelog `0`; build spec `0`.
- Baseline gates: `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `157 passed in 94.81s (0:01:34)`; `git diff --check` printed nothing and exited 0.

STATUS: PLANNED
CONFIDENCE: high, every cited location and every scenario's base output checked on `d0300d3`, and no split reduces shared files.
ESCALATIONS: none
