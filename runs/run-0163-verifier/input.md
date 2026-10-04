## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `state/`.
  The store is tracked on `main` and the operator commits it between steps, so `main` moves even
  when no ticket merges.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0163-verifier/output.md`

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/state/runs/run-0163-verifier/wt` (branch `factory/T-0018.1`, base `d0300d3127fdd257d725ecb996b4fe9df282cef9`, head `7a4967a055bc40e3839c65fc00416299d90db350`). There is no remote: commit on the branch; the PR is the branch plus the description you return. Gate commands (run each from your worktree, exactly as written): `git diff --check main...HEAD`; `uv run --frozen pytest -q -p no:cacheprovider tests/factory`

## Sub-ticket T-0018.1

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

## Parent spec (v2, pinned)

=== proposal.md
## Problem

The spec factory runs each ticket (a requested change) through AI agents, driven by two workflow scripts: the intake script (triage, then writing and critiquing a spec) and the build script (planning, building, checking and merging). A human signs off each spec at the spec gate before any code is written. Today both scripts can stop a ticket and leave no record of why. The operator then finds a ticket that has not moved and has to dig through the store, the directory of files where the factory keeps every ticket, run and result, to learn what happened. On the factory's other instance, the Nanobot repository, this stalled six approved tickets at once on 2026-10-04.

Some terms used below. A role is one agent job, such as the planner or the verifier. A run is one call of a role; the store records each run and marks it "in flight" until it finishes. The planner splits an approved spec, the parent ticket, into sub-tickets that are built and merged one by one. To park a ticket is to stop it and put the reason in the human queue, the list a human works through.

Four defects, each seen on a real ticket:

1. **Intake plans without creating sub-tickets.** If the intake script is started on a ticket that has already passed the spec gate, it runs the planner and marks the parent "planned", but it never creates the sub-tickets. Only the build script has that step.
2. **The build then exits silently.** On a planned parent with no sub-tickets, the build script finds nothing to build. It asks the store whether the parent is finished, gets a refusal ("has no sub-tickets"), and returns after about 30 seconds. Nothing is parked and nothing is logged.
3. **A failed agent call leaves a run in flight forever.** If launching a role's agent fails with an error, for example because the agent type is not installed, the script stops. The run stays marked in flight and the ticket is not parked. Every later attempt on that ticket is refused because a run is still in flight.
4. **The verifier's test-suite result is misread when written as a heading.** The verifier reports the test-suite result on a line `Gate suite: PASS` or `Gate suite: FAIL`, and the harness records that line as the CI result. A verifier that wrote `## Gate suite: PASS` had its pass recorded as a failure. Each time this has cost a full revision round: another implementer run and another pair of checks.

The fix: intake stops at the spec gate and only the build script plans. A build that finds a planned parent with no sub-tickets creates them from the planner run already recorded for that parent, or parks the parent with the reason. A failed agent call records its run as killed and parks the ticket with the error. The harness reads the gate line in heading and bold forms, and the verifier's prompt states the exact form.

## Evidence

All reproductions below ran on `main` at `429d218` in this checkout. Each used a scratch store and a scratch target repository. The workflow scripts need Claude Code's Workflow runtime, so they were run under node with a small driver. The driver models that runtime's documented `agent()` and `parallel()` behaviour, runs every store command for real through `bin/factory`, and answers role calls from the repo's stub fixtures. It is given in full in the first scenario of `specs/workflow-dispatch/spec.md`.

- **Intake plans a gate-approved ticket without sub-tickets.** A ticket was taken through intake to the spec gate, approved with `bin/factory approve-spec T-0001`, then given to the intake script again. The driver printed `returned planned`, `ticket T-0001 planned` and `run run-0004-planner PLANNED`, and the store held only `T-0001.yaml`. So the planner ran and the parent is planned with no sub-tickets. The cause is `factory/workflows/intake.js` lines 172-189: the Plan phase runs `spec tasks` and `plan add`, then moves the ticket to `planned`, with no `subticket add`. `factory/workflows/build.js` line 190 is the only place that runs `subticket add`.
- **The build exits silently on that parent.** The build script on the same store printed `returned planned`. The last log line was still the `ready-for-planner → planned` transition, with no park and no `ticket.parked` event. So the build ended with no record of why. Cause: `build.js` lines 205-207 break out of the build loop when nothing is ready or remaining. Line 212 then calls `ticket parent-check`, which refuses with `T-0001 has no sub-tickets` (`factory/cli.py` line 594). Line 213 returns `{state: 'planned'}` without parking.
- **The Nanobot store shows the same thing at scale** (from triage, read only): six parents planned on 2026-10-04 with no sub-tickets (T-0001, T-0004, T-0007, T-0008, T-0011, T-0012). The Nanobot Driver session, which runs that instance's builds, created them by hand with `subticket add <parent> --run <planner run>`, taking each run id from the parent's `plan.added` log event. `plan.added` is the event the store writes when a plan is recorded, and its `source` field names the planner run.
- **There is no way to create sub-tickets without naming the run.** `bin/factory subticket add T-0001` with neither `--run` nor `--file` printed `factory: TypeError: argument should be a str or an os.PathLike object ... not 'NoneType'` and exited 1. So the command crashes instead of using the plan the store already recorded.
- **A failed agent call orphans its run (intake).** The driver made the triage role's `agent()` call throw `agent type 'factory-triage' not found`. It printed `threw agent type 'factory-triage' not found`, `ticket T-0001 ready-for-triage in_flight=1` and `run run-0001-triage running`. So the script died, the run stayed in flight, and the ticket was not parked.
- **The same happens in the build.** With the implementer's call throwing, the driver printed `ticket T-0001.1 ready-for-implementer in_flight=1 reason=-` and `run run-0005-implementer running`. The build returned `planned` and logged "1 sub-ticket(s) parked or waiting on a human", which was false. This matches the issue #24 comment from 2026-10-04: "left the sub-ticket holding an orphan in-flight run and returned without parking", after "agent type 'factory-implementer' not found".
- **How `agent()` fails.** The Workflow reference says `agent()` returns null when the user skips it or after a terminal API error, and that a thunk which throws inside `parallel()` resolves to null. If the #24 call had returned null, `runRole` would have finished the run as KILLED (`build.js` lines 93-96). The run stayed `running`, so the call threw. `build.js` calls `buildOne` inside `parallel()` (line 210), so the throw was absorbed there and the build carried on. The reference does not say in so many words that an unknown agent type throws. That part is inferred from the #24 symptoms, which the reproduction above matches exactly.
- **Gate line read as a heading.** The store keeps one result row per checker for each commit it checks; the ci row is the test-suite verdict, which the harness reads from the verifier's `Gate suite:` line. spec-factory `run-0073-verifier` (T-0012.5), `output.md` line 21, reads `## Gate suite: PASS`. The store logged `result.recorded ... role: ci, status: FAIL` for that run (log line 378), and `results/302f70bb…/ci.yaml` and `results/7090d9d2…/superseded-2/ci.yaml` both hold `detail: missing Gate suite line`: the verifier's pass was recorded as a fail. On a scratch store, `results record` gave ci `FAIL|missing Gate suite line` for each of `## Gate suite: PASS`, `**Gate suite:** PASS`, `### **Gate suite: PASS**` and `**Gate suite: FAIL** 2 failed`. Plain `Gate suite: PASS` gave `PASS|`. So any leading mark hides the verdict. The parser is `factory/cli.py` line 480, `re.search(r"^Gate suite:\s*(PASS|FAIL)\b(.*)$", text, re.M)`, which is anchored at the start of the line. The second occurrence was Nanobot v3.5 T-0012.1 (run-0052), as reported in the issue; I did not open that run.
- **The documents already expect this.** `README.md` lines 83-85 say intake's planning step "only runs when a ticket is already past the gate at launch; in practice the build script runs the planner". Line 276 says to start the build script after the gate, "never the intake script (#33)". `dev/build-harness.spec.md` lines 277-281 describe `intake.js` as triage and spec phases only. Removing the phase brings the code in line with the build spec.
- **Baseline gates.** `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `157 passed in 97.42s`: the suite is green before the change. `git diff --check` printed nothing: no whitespace errors.

## Root cause

- `factory/workflows/intake.js` lines 172-189 (phase 3, Plan) is a second, incomplete planning path. It lacks `subticket add`, which `build.js` line 190 has.
- `factory/workflows/build.js` lines 197-215 have no case for a `planned` parent with no sub-tickets. They also drop a `parent-check` refusal on the floor at line 213: `if (!pc.ok || pc.state !== 'ready-for-parent-verify') return {...}`.
- `runRole` in both scripts (`intake.js` lines 74-104, `build.js` lines 64-101) handles a null or empty `agent()` result as KILLED, but nothing catches a thrown `agent()`. The run is never finished and the ticket is never parked. In `build.js` the throw is absorbed by `parallel()`, so the build goes on as if nothing happened.
- `factory/cli.py` `subticket_add` (lines 366-403) reads `Path(a.file)` when `--run` is absent, so a call with neither flag raises `TypeError`.
- `factory/cli.py` `results_record` line 480 anchors the gate-line regex at the start of the line, so heading (`#`) and emphasis (`*`) marks hide the verdict. The verifier prompt (`docs/design.md` line 644, `docs/prompts/07-verifier.md` line 37, `factory/prompts/verifier.md` line 38) says only `Gate suite: PASS/FAIL, with failing output` and does not forbid formatting.

## Out of scope

- The planner's output format (#13).
- A `resolve` verb that resumes a ticket parked by a failed agent call, or a parent parked for having no sub-tickets. A budget-killed implementer has the same gap today (README §"Where a human decides", "Gap, as of today").
- A clerk call whose own `agent()` throws. Parking needs the clerk, so there is nothing to park with.
- Which gate line counts when there are several. The parser keeps taking the first matching line, as today.
- The build's quiet `planned` return when every remaining sub-ticket is parked. Each of those sub-tickets is already in the queue with its own reason.
- Agent definitions for the build roles (#24 part A).
- Keeping the node driver as a permanent test. It is used here only as an inline acceptance fixture.
- `dev/issues.md` and #21's dead-code list. The operator maintains these.
- Describing the new park reasons in README's present-tense sections before they have run on a real ticket (README "Maintaining this page").

## Open questions

none

## Decisions

- Intake ends at the spec gate. The build script is the only path that runs the planner, so there is one planning path.
- `factory subticket add PARENT` with neither `--run` nor `--file` uses the planner run named by the parent's latest `plan.added` event. Rejected: picking the newest PLANNED planner run of the parent, because it could pick a run whose plan was never recorded.
- The build detects a parent with no sub-tickets from a new `subtickets` list in `ticket ready-implementers` output. Rejected: routing on the text of `parent-check`'s refusal, because refusal text is for humans and changes freely.
- When an `agent()` call throws, its run is recorded KILLED and the ticket parks with `agent call failed: <role>: <error>`. That reason is distinct from `budget kill`, so the operator can tell a missing agent from a budget overrun. A null or empty return keeps today's route.
- A `parent-check` refusal in the build parks the parent with the refusal text. It is not a silent return.
- The gate-line parser accepts leading whitespace, `#` and `*` before `Gate suite:`, and `*` and whitespace between the colon and the verdict. Emphasis marks are stripped from the detail. The verifier prompt pins the plain form. The two are kept together: the parser tolerates drift, and the prompt states the contract.

## Risk

Blast radius: every intake and build run on both instances after the runtime moves to this change. The runtime is the pinned checkout of the harness that runs tickets; a merge into `main` does not reach it until the operator moves it. All changes can be undone by moving the runtime back. Behaviour changes, in brief:
- Intake on a `ready-for-planner` ticket now does nothing.
- A build on a planned parent with no sub-tickets now creates them or parks the parent.
- A thrown agent call now parks instead of orphaning its run.
- More verifier outputs now yield a ci row of PASS. The verdict is unchanged: PASS and FAIL are read from the same word, so no check is loosened. Only lines that start with `#`, `*` or whitespace before `Gate suite:` are newly read.

Protected paths touched, all declared:
- harness `factory/**`: `factory/workflows/intake.js`, `factory/workflows/build.js`, `factory/cli.py`, `factory/prompts/verifier.md`. The last is also a guardrail path, an agent prompt, and the ticket asks for this change to it.
- generated `docs/prompts/**`: `docs/prompts/07-verifier.md`, re-copied verbatim from the design doc's verifier block.

No `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**` or `~/.nanobot/**` path is touched. Existing tests are unchanged. New tests go in a new file.

The spec gate is pre-approved under `.factory/answers/queue-preapproval-policy.md`. The policy names #33's parts A, B and C1; C2 and D fall under its small-blast-radius rule (no loosened check, a handful of files, reversible by moving the runtime back). The same policy says a prompt change still gets the operator's acceptance test before the runtime moves. See Operator steps.

## Operator steps

The runtime is the pinned checkout of the harness that runs tickets. A merge into `main` reaches it only when the operator moves it. After that, each instance accepts the new revision with `--accept-harness <revision>`, and refuses to run until it does. The store keeps one result row per checker for a sub-ticket's latest commit, its head. The ci row is the test-suite verdict read from the verifier's `Gate suite:` line.

1. Before the runtime moves to this change, run the acceptance test that the pre-approval policy requires for a prompt change. Take the next real verifier run on the new prompt and check two things: its output carries a plain `Gate suite: PASS` or `Gate suite: FAIL` line, and the ci row recorded for that head matches it (`bin/factory results show <sub-ticket>`).
2. After moving the runtime, accept the new harness revision on each instance with `--accept-harness <revision>`. Tell the Nanobot Driver session that intake no longer plans, and that a parent planned by an older runtime gets its sub-tickets from the build script.

=== design.md
## Proposed change

Size estimate: about 170 changed lines, including new tests.

**A. Intake ends at the spec gate** (`factory/workflows/intake.js`)
- Delete phase 3, Plan (lines 172-189).
- Remove the `Plan` entry from `meta.phases` (line 7). End `meta.description` at the human gate: drop "-> Planner".
- Drop `planner` from `AGENT_NAME` (line 35).
- A ticket in `ready-for-planner`, or in any state intake does not dispatch, falls through to the existing final `return { ticket, state, note: 'nothing to dispatch from this state' }` (line 191). No planner run starts.

**B. The build creates missing sub-tickets from the recorded plan**
- B1 (`factory/cli.py` `subticket_add` and its parser entry). With neither `--run` nor `--file`, take the run from the `source` of the parent's latest `plan.added` log event. Then proceed exactly as `--run <that run>` does today: the PLANNED-planner-run check, parsing, the `ticket.created` events, and the sub-ticket `source: plan:<run>`. Refuse with exit 2 and the store unchanged in two cases: when the parent has no `plan.added` event, or when its latest one names something that is not a run directory of this store (a plan added with `--file`). The refusal text names the parent and says no recorded planner run was found.
- B2 (`factory/cli.py` `ticket_ready_implementers`). Add `"subtickets"` to the output: every sub-ticket id of the parent, in id order. Existing keys are unchanged.
- B3 (`factory/workflows/build.js`, phase 2, before the loop's first `parallel`). If the first `ready-implementers` answer has an empty `subtickets` list, run clerk `subticket add PARENT` with no `--run`, at most once per build run. When that is refused, park the parent with a reason containing `no sub-tickets`, for example `no sub-tickets, and none could be created from the recorded plan: <stderr>`, and return `{ticket, state: 'parked'}`. When it succeeds, log how many sub-tickets were created and continue the loop.

**C. No silent exits**
- C1 (`build.js` lines 212-213). When `parent-check` is refused (`!pc.ok`), park the parent with `parent-check refused: <stderr>` and return `{ticket, state: 'parked'}`. When it succeeds with a state other than `ready-for-parent-verify`, return as today.
- C2 (`runRole` in both `intake.js` and `build.js`). Wrap the role's `agent()` call, in both the stub branch and the real branch, in `try`/`catch`. On a throw:
  - clerk `run finish RUN --status-override KILLED`;
  - in `build.js`, for a reviewer or verifier, clerk `run cleanup RUN` as today;
  - park the ticket with `agent call failed: <role>: <error message>` and the run id as outputs;
  - return `null`. Every caller already returns on `null`.

  A null or empty result keeps today's KILLED path. Pass the reason through the existing `park()`, which already replaces double quotes.

**D. Gate line**
- D1 (`factory/cli.py` `results_record`, line 480). Match the first line of the form `^[ \t#*]*Gate suite:[ \t*]*(PASS|FAIL)\b(.*)$` (`re.M`). The detail is group 2 with spaces and `*` stripped from both ends, or `None` when that leaves it empty. A line where `Gate suite:` follows anything other than spaces, tabs, `#` or `*` still does not match, so prose that mentions the gate suite is not read as a verdict. The no-match case is unchanged: `FAIL`, `missing Gate suite line`.
- D2 (the verifier prompt). In the `## 7. Verifier` block of `docs/design.md` (line 644), replace the line `Gate suite: PASS/FAIL, with failing output` with these two lines:
  ```
  Gate suite: PASS/FAIL, with failing output on the lines below it
    (a plain line starting "Gate suite:", never a heading or bold)
  ```
  Re-copy the block verbatim into `docs/prompts/07-verifier.md`. Make the same two-line replacement at `factory/prompts/verifier.md` line 38, whose step 4 differs from the design block on purpose and stays as it is.
- D3 (`docs/changelog.md`). Add entry `47. After issue #33 (2026-10-04), ...` after entry 46 and before "Declined:". It says three things: intake ends at the spec gate and the build owns planning; a failed agent call or a `parent-check` refusal parks with the reason; and the verifier writes `Gate suite:` as a plain line, which the harness also reads in heading or bold form.

**E. Documents that describe the changed behaviour**
- `README.md` lines 83-85: replace the two sentences "The intake script also contains a planning step, but it only runs when a ticket is already past the gate at launch; in practice the build script runs the planner." with exactly this sentence: `The intake script stops at the spec gate; the build script runs the planner.` Rewrap the paragraph as needed, but keep that sentence on one line so it can be found by grep.
- `README.md` line 276: replace "Start the build script after the spec gate, never the intake script (#33)." with `Start the build script after the spec gate; the intake script has nothing to do past it.` This drops the issue number from the body, as "Maintaining this page" asks. Keep the status-header date current (it reads 2026-10-04 today), as "Maintaining this page" requires.
- `dev/build-harness.spec.md`:
  - line 275 (`runRole`): add that a thrown `agent()` is finished KILLED and parks `agent call failed: <role>: <error>`;
  - line 285 (build.js step 2): add the missing-sub-ticket repair (B3) and the `parent-check` refusal park (C1);
  - line 320 (L): say the `Gate suite:` line may carry leading heading or emphasis marks, and use the phrase "heading or emphasis marks".

**F. New tests** in a new file, `tests/factory/test_build_startup.py`, driven through `bin/factory` on a scratch store:
- `subticket add` with no source, in both the success case and the refusal case;
- the new `subtickets` key in `ready-implementers`;
- the gate-line forms in D1.

The workflow-script behaviour (A, B3, C) is covered by the acceptance driver only.

## Tests to change

none. No existing test asserts on intake's Plan phase. The `ready-implementers` tests read only `ready` and other existing keys (`tests/factory/test_subtickets.py` lines 119-152, `tests/factory/test_shepherd.py` lines 194, 299, 384, 466). The gate-line tests use plain `Gate suite:` lines, which still parse the same way.

=== specs/workflow-dispatch/spec.md
## ADDED Requirements

### Requirement: Intake stops at the spec gate
The intake workflow MUST NOT run the planner; a ticket that has passed the spec gate SHALL be left in `ready-for-planner` for the build workflow.

#### Scenario: Intake leaves an approved ticket for the build workflow
Run every command in this file from the repository root of the checkout under test, after `uv sync --frozen`, with node 18 or later on the PATH. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (later scenarios reuse them)

```sh
cat > ${TMPDIR:-/tmp}/t0018-drive.js <<'EOF'
// Acceptance driver for T-0018: runs a factory workflow script under node, with the Workflow API
// modelled as documented: agent() returns the agent's text (a schema'd call returns the object);
// a thunk that throws inside parallel() resolves to null. Clerk calls run their command for real.
// Role calls follow the script's stub prompt; the role named by the fifth argument throws instead.
// usage (repo root, FACTORY_STATE set): node DRV <workflow.js> <ticket> <stubs> <target repo> [throw role]
const fs = require('fs'), cp = require('child_process')
const [script, ticket, stubs, target, throwRole] = process.argv.slice(2)
const state = process.env.FACTORY_STATE
const body = fs.readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const c = /nothing else:\n\n([\s\S]*)\n\nReport its stdout/.exec(prompt)
  if (c) { const r = cp.spawnSync('sh', ['-c', c[1]], { encoding: 'utf8' }); return { stdout: r.stdout, exit: r.status, stderr: r.stderr } }
  const s = /Stub file: (\S+)\nOutput file: (\S+)/.exec(prompt)
  const role = s[1].split('/').pop().replace(/-\d+\.md$/, '')
  if (role === throwRole) throw new Error(`agent type 'factory-${role}' not found`)
  if (!fs.existsSync(s[1])) return ''
  const text = fs.readFileSync(s[1], 'utf8'); fs.writeFileSync(s[2], text); return text
}
const parallel = thunks => Promise.all(thunks.map(t => t().catch(() => null)))
const run = new (Object.getPrototypeOf(async function () {}).constructor)('args', 'agent', 'phase', 'log', 'parallel', body)
run({ ticket, repo: process.cwd(), state, stubs, target, integration: 'main', inlineRoles: true }, agent, () => {}, () => {}, parallel)
  .then(r => console.log(`returned ${r.state || r.error}`), e => console.log(`threw ${e.message}`))
  .then(() => {
    for (const f of fs.readdirSync(`${state}/tickets`).sort()) {
      const t = JSON.parse(cp.execSync(`bin/factory ticket show ${f.slice(0, -5)} --json`, { encoding: 'utf8' }).trim().split('\n').pop())
      console.log(`ticket ${t.id} ${t.state} in_flight=${t.in_flight.length} reason=${t.parked ? t.parked.reason : '-'}`)
    }
    for (const r of fs.readdirSync(`${state}/runs`).sort())
      console.log(`run ${r} ${/^status: (.*)$/m.exec(fs.readFileSync(`${state}/runs/${r}/meta.yaml`, 'utf8'))[1]}`)
  })
EOF
cat > ${TMPDIR:-/tmp}/t0018-approved.sh <<'EOF'
# Sourced from the repo root: a scratch store whose T-0001 has passed the spec gate, and a scratch target repo.
DRV=${TMPDIR:-/tmp}/t0018-drive.js; W=$(mktemp -d); export FACTORY_STATE=$W/store; mkdir $W/none
git init -q -b main $W/t && git -C $W/t -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
printf '# Fixture\n\nThe bot should do the thing.\n' > $W/req.md && bin/factory ticket new --file $W/req.md >/dev/null
node $DRV factory/workflows/intake.js T-0001 tests/factory/fixtures/stubs/accept-approve $W/t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0018-handplan.sh <<'EOF'
# Sourced after t0018-approved.sh: plans T-0001 the way intake's Plan phase did (a planner run, plan add, planned), with no sub-tickets.
R=$(bin/factory run start --role planner --ticket T-0001 | tail -1 | sed 's/.*"run_id": "\([^"]*\)".*/\1/')
bin/factory run compose $R >/dev/null && cp tests/factory/fixtures/stubs/accept-approve/planner-1.md $FACTORY_STATE/runs/$R/output.md
bin/factory run finish $R >/dev/null && bin/factory plan add T-0001 --from-run $R >/dev/null
bin/factory ticket transition T-0001 --to planned --by workflow >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && node $DRV factory/workflows/intake.js T-0001 tests/factory/fixtures/stubs/accept-approve $W/t)`
- THEN the output contains `returned ready-for-planner` and `ticket T-0001 ready-for-planner in_flight=0 reason=-`, and no line starting `run run-0004-planner`

### Requirement: The build workflow plans and creates sub-tickets
The build workflow SHALL plan a parent in `ready-for-planner` and create its sub-tickets from that planner run.

#### Scenario: Build plans a gate-approved parent and creates its sub-tickets
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && mkdir $W/p && cp tests/factory/fixtures/stubs/accept-approve/planner-1.md $W/p/ && node $DRV factory/workflows/build.js T-0001 $W/p $W/t; grep '^source:' $FACTORY_STATE/tickets/T-0001.1.yaml)`
- THEN the output contains `run run-0004-planner PLANNED`, `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer` (the stub directory has no implementer answer) and `source: plan:run-0004-planner`

### Requirement: A planned parent without sub-tickets is repaired or parked
A build that starts on a `planned` parent with no sub-tickets SHALL create them from the planner run named by the parent's recorded plan, or park the parent with a reason containing `no sub-tickets` when it cannot.

#### Scenario: Build creates the missing sub-tickets from the recorded planner run
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && . ${TMPDIR:-/tmp}/t0018-handplan.sh && node $DRV factory/workflows/build.js T-0001 $W/none $W/t; grep '^source:' $FACTORY_STATE/tickets/T-0001.1.yaml)`
- THEN the output contains `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer`, `run run-0005-implementer KILLED` and `source: plan:run-0004-planner`

#### Scenario: Build parks a planned parent it cannot give sub-tickets
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && bin/factory plan add T-0001 --file tests/factory/fixtures/stubs/accept-approve/planner-1.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by workflow >/dev/null && node $DRV factory/workflows/build.js T-0001 $W/none $W/t)`
- THEN the output contains `returned parked` and a line starting `ticket T-0001 parked in_flight=0 reason=` that contains `no sub-tickets`, and no line starting `ticket T-0001.1`

### Requirement: subticket add can use the recorded plan
`factory subticket add PARENT` with neither `--run` nor `--file` SHALL create the sub-tickets from the planner run named by the parent's latest `plan.added` event, and SHALL refuse with exit 2 and the store unchanged when no such run is recorded.

#### Scenario: subticket add without a source uses the recorded planner run
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && . ${TMPDIR:-/tmp}/t0018-handplan.sh && bin/factory subticket add T-0001; echo "exit=$?"; grep '^source:' $FACTORY_STATE/tickets/T-0001.1.yaml)`
- THEN stdout's last JSON line has `"ok": true` and names `T-0001.1`, followed by `exit=0` and `source: plan:run-0004-planner`

#### Scenario: subticket add without a source refuses when the plan came from a file
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && bin/factory plan add T-0001 --file tests/factory/fixtures/stubs/accept-approve/planner-1.md >/dev/null && bin/factory subticket add T-0001; echo "exit=$?"; ls $FACTORY_STATE/tickets)`
- THEN the output contains `exit=2` and no `TypeError`, and the listing is `T-0001.yaml` alone

### Requirement: A failed agent call is recorded and parked
When a role's `agent()` call throws, the workflow SHALL finish that run as KILLED and park the ticket with a reason that contains the error.

#### Scenario: A failed agent call in intake parks the ticket
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(DRV=${TMPDIR:-/tmp}/t0018-drive.js; W=$(mktemp -d); export FACTORY_STATE=$W/store; printf '# Fixture\n\nThe bot should do the thing.\n' > $W/req.md && bin/factory ticket new --file $W/req.md >/dev/null && node $DRV factory/workflows/intake.js T-0001 tests/factory/fixtures/stubs/accept-approve $W triage)`
- THEN the output contains `returned parked`, a line starting `ticket T-0001 parked in_flight=0 reason=` that contains `agent type 'factory-triage' not found`, and `run run-0001-triage KILLED`

#### Scenario: A failed agent call in the build parks the sub-ticket
- GIVEN the fixture files from "Intake leaves an approved ticket for the build workflow"
- WHEN `(. ${TMPDIR:-/tmp}/t0018-approved.sh && node $DRV factory/workflows/build.js T-0001 tests/factory/fixtures/stubs/accept-approve $W/t implementer)`
- THEN the output contains a line starting `ticket T-0001.1 parked in_flight=0 reason=` that contains `agent type 'factory-implementer' not found`, and `run run-0005-implementer KILLED`

### Requirement: The harness stays green
The harness suite SHALL pass and the change SHALL add no whitespace errors.

#### Scenario: The harness suite passes
- WHEN `uv run --frozen pytest -q -p no:cacheprovider tests/factory`
- THEN it exits 0 with no failures

#### Scenario: The change adds no whitespace errors
- WHEN `git diff --check main...HEAD; echo "exit=$?"`
- THEN it prints only `exit=0`

=== specs/verifier-gate-line/spec.md
## ADDED Requirements

### Requirement: The gate line is read in heading and emphasis forms
`factory results record --role verifier` SHALL read the verdict from the first line that starts with optional spaces, tabs, `#` or `*` followed by `Gate suite:`, optional `*` or spaces, and `PASS` or `FAIL`; prose that mentions the gate suite mid-line MUST NOT count.

#### Scenario: Heading and emphasis gate lines are read
- WHEN `(W=$(mktemp -d); export FACTORY_STATE=$W/store; printf '# Fixture\n\nThe bot should do the thing.\n' > $W/req.md && bin/factory ticket new --file $W/req.md >/dev/null && H=$(printf 'a%.0s' $(seq 40)) && for form in '## Gate suite: PASS' '**Gate suite:** PASS' '### **Gate suite: PASS**' '**Gate suite: FAIL** 2 failed'; do printf 'Commit: %s\n%s\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n' $H "$form" > $W/v.md && bin/factory results record T-0001 --head $H --role verifier --output $W/v.md >/dev/null && echo "$form => $(sed -n 's/^status: //p' $FACTORY_STATE/results/$H/ci.yaml)|$(sed -n 's/^detail: //p' $FACTORY_STATE/results/$H/ci.yaml)"; done)`
- THEN it prints `## Gate suite: PASS => PASS|`, `**Gate suite:** PASS => PASS|`, `### **Gate suite: PASS** => PASS|` and `**Gate suite: FAIL** 2 failed => FAIL|2 failed`

#### Scenario: Plain gate lines and prose read as before
- WHEN `(W=$(mktemp -d); export FACTORY_STATE=$W/store; printf '# Fixture\n\nThe bot should do the thing.\n' > $W/req.md && bin/factory ticket new --file $W/req.md >/dev/null && H=$(printf 'a%.0s' $(seq 40)) && for form in 'Gate suite: PASS' 'Gate suite: FAIL 1 failed' 'The Gate suite: PASS line was missing'; do printf 'Commit: %s\n%s\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n' $H "$form" > $W/v.md && bin/factory results record T-0001 --head $H --role verifier --output $W/v.md >/dev/null && echo "$form => $(sed -n 's/^status: //p' $FACTORY_STATE/results/$H/ci.yaml)|$(sed -n 's/^detail: //p' $FACTORY_STATE/results/$H/ci.yaml)"; done)`
- THEN it prints `Gate suite: PASS => PASS|`, `Gate suite: FAIL 1 failed => FAIL|1 failed` and `The Gate suite: PASS line was missing => FAIL|missing Gate suite line`

### Requirement: The verifier prompt states the gate line format
The verifier prompt SHALL tell the verifier to write the gate result as a plain line starting `Gate suite:`, never a heading or bold, in the design doc's block, its generated copy and the harness's role prompt.

#### Scenario: The verifier prompt pins the gate line in all three copies
- WHEN `for f in docs/design.md docs/prompts/07-verifier.md factory/prompts/verifier.md; do echo "$f $(grep -cxF 'Gate suite: PASS/FAIL, with failing output on the lines below it' $f) $(grep -cxF '  (a plain line starting "Gate suite:", never a heading or bold)' $f) $(grep -cx 'Gate suite: PASS/FAIL, with failing output' $f)"; done`
- THEN it prints `docs/design.md 1 1 0`, `docs/prompts/07-verifier.md 1 1 0` and `factory/prompts/verifier.md 1 1 0`

#### Scenario: The design block and its prompt copy stay identical
- WHEN `awk 'BEGIN{q=sprintf("%c%c%c",96,96,96)} /^## 7\. Verifier/{f=1;next} f&&index($0,q"text")==1{p=1;next} p&&index($0,q)==1{exit} p' docs/design.md | diff - docs/prompts/07-verifier.md && echo SAME`
- THEN it prints `SAME`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents describe the changed behaviour
The README SHALL say the intake script stops at the spec gate and SHALL no longer say it contains a planning step, the changelog SHALL record the change as entry 47, and the build spec SHALL name the accepted gate line forms.

#### Scenario: The README says intake stops at the spec gate
- WHEN `grep -cF 'The intake script stops at the spec gate; the build script runs the planner.' README.md; grep -c 'intake script also contains' README.md`
- THEN it prints `1` then `0`

#### Scenario: The changelog records the change
- WHEN `grep -c '^47\. After issue #33 (2026-10-04)' docs/changelog.md; grep '^47\. ' docs/changelog.md | grep -c 'Gate suite:'`
- THEN it prints `1` then `1`

#### Scenario: The build spec names the accepted gate line forms
- WHEN `grep -c "heading or emphasis marks" dev/build-harness.spec.md`
- THEN it prints a number of 1 or more

=== verification.md
## Acceptance

All workflow-dispatch scenarios need the GIVEN of the first one run once (it writes `${TMPDIR:-/tmp}/t0018-drive.js`, `t0018-approved.sh` and `t0018-handplan.sh`). Every command runs from the repository root of the checkout under test, after `uv sync --frozen`.

- Intake leaves an approved ticket for the build workflow → NEW. Today it prints `returned planned`, `ticket T-0001 planned in_flight=0 reason=-` and `run run-0004-planner PLANNED`: intake runs the planner.
- Build plans a gate-approved parent and creates its sub-tickets → REGRESSION. Today it prints `run run-0004-planner PLANNED`, `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer`, `run run-0005-implementer KILLED` and `source: plan:run-0004-planner`.
- Build creates the missing sub-tickets from the recorded planner run → NEW. Today it prints `returned planned` and `ticket T-0001 planned in_flight=0 reason=-`, with no `T-0001.1` line, and grep reports `T-0001.1.yaml: No such file or directory`.
- Build parks a planned parent it cannot give sub-tickets → NEW. Today it prints `returned planned` and `ticket T-0001 planned in_flight=0 reason=-`: no park.
- subticket add without a source uses the recorded planner run → NEW. Today it prints `factory: TypeError: argument should be a str or an os.PathLike object ... not 'NoneType'` and `exit=1`, and no `T-0001.1.yaml` exists.
- subticket add without a source refuses when the plan came from a file → NEW. Today it prints the same `TypeError` and `exit=1`, not a refusal with exit 2. The listing is already `T-0001.yaml` alone.
- A failed agent call in intake parks the ticket → NEW. Today it prints `threw agent type 'factory-triage' not found`, `ticket T-0001 ready-for-triage in_flight=1 reason=-` and `run run-0001-triage running`.
- A failed agent call in the build parks the sub-ticket → NEW. Today it prints `ticket T-0001.1 ready-for-implementer in_flight=1 reason=-` and `run run-0005-implementer running`.
- The harness suite passes → REGRESSION. Today: `157 passed in 97.42s`.
- The change adds no whitespace errors → REGRESSION.
- Heading and emphasis gate lines are read → NEW. Today all four lines end `=> FAIL|missing Gate suite line`.
- Plain gate lines and prose read as before → REGRESSION. Today it prints exactly the expected three lines.
- The verifier prompt pins the gate line in all three copies → NEW. Today each file prints `0 0 1`: the new lines are absent and the old line is present.
- The design block and its prompt copy stay identical → REGRESSION. Today it prints `SAME`.
- The README says intake stops at the spec gate → NEW. Today it prints `0` then `1`: the pinned sentence is absent and README line 83 still says "The intake script also contains a planning step".
- The changelog records the change → NEW. Today it prints `0` then `0`: there is no entry 47.
- The build spec names the accepted gate line forms → NEW. Today it prints `0`.

## Responses

- [BLOCKING] Operator steps gloss: FIXED. Operator steps now opens with a paragraph that glosses the runtime (the pinned checkout of the harness that runs tickets, moved only by the operator), `--accept-harness <revision>` (each instance refuses to run until it accepts the new revision), the head (a sub-ticket's latest commit) and the ci row (the test-suite verdict read from the `Gate suite:` line). Risk now glosses the runtime at its first use too, and the Evidence gate-line bullet glosses result rows and the ci row before quoting `role: ci, status: FAIL`.
- [SHOULD-FIX] Problem paragraph 1, "store files" and "the Nanobot port": FIXED. Now "the store, the directory of files where the factory keeps every ticket, run and result" and "On the factory's other instance, the Nanobot repository, this stalled six approved tickets at once on 2026-10-04." The Evidence bullet that said "that port's builds" now says "that instance's builds", so one name is used throughout.
- [SHOULD-FIX] README scenario tested a phrase, not the behaviour: FIXED. Design part E now pins the replacement sentence exactly (`The intake script stops at the spec gate; the build script runs the planner.`, kept on one line) and also pins the line-276 replacement, which drops the in-body issue number. The scenario is renamed "The README says intake stops at the spec gate". It checks that the pinned sentence counts `1` and that `intake script also contains` counts `0`. On `429d218` it prints `0` then `1` (both greps run by hand), so it is NEW for the stated reason.
- [NIT] Risk pre-approval sentence overstated the policy: FIXED. Now: "The policy names #33's parts A, B and C1; C2 and D fall under its small-blast-radius rule (no loosened check, a handful of files, reversible by moving the runtime back)." Checked against `.factory/answers/queue-preapproval-policy.md`: the #33 entry and the small-blast-radius rule are both in the "Policy:" list as quoted.

## PR description (the implementer's output)

Sub-ticket: T-0018.1 (parent T-0018 = issue #33, approved spec v2 at `.factory/state/specs/T-0018/v2.md`)
Branch: `factory/T-0018.1`, base `d0300d3127fdd257d725ecb996b4fe9df282cef9`, head `7a4967a055bc40e3839c65fc00416299d90db350` (one commit). There is no remote, so the PR is this branch plus this description.

## What changed

Before this change, the factory's two workflow scripts could stop a ticket and leave no record of why. Intake could plan a parent ticket without creating its sub-tickets. The build then exited silently on that parent. An agent call that threw left its run marked "in flight" for good. And a verifier's `## Gate suite: PASS` line was recorded as a test-suite failure. With this change, each of those cases either finishes the work or parks the ticket with a reason. To park a ticket is to stop it and put it in the human queue with its reason.

- **A. Intake ends at the spec gate** (`factory/workflows/intake.js`). I deleted phase 3 (Plan), its `meta.phases` entry, "-> Planner" in `meta.description`, and `planner` in `AGENT_NAME`. A `ready-for-planner` ticket now falls through to the existing final `return {…, note: 'nothing to dispatch from this state'}`.
- **B1** (`factory/cli.py`). When `subticket add PARENT` gets neither `--run` nor `--file`, it calls a new `_recorded_plan_run()`. That function reads the store's `log/*.jsonl` in file order and takes the `source` of the parent's last `plan.added` event. When that source is a run directory of this store, the command sets `a.run` to it and goes on through the existing `--run` path unchanged: the PLANNED-planner check, parsing, and `source: plan:<run>`. The command refuses with exit 2 and writes nothing in three cases: there is no such event, the source contains `/`, or the source has no `runs/<source>/meta.yaml`. The refusal says `no recorded planner run found for <parent> (latest plan.added source: …); pass --run RUN or --file F`. I also gave the parser entry a help line.
- **B2** (`factory/cli.py` `ticket_ready_implementers`). The output gains `"subtickets"`: every sub-ticket id of the parent, in id order, from `store.subtickets_of`. Existing keys are unchanged.
- **B3** (`factory/workflows/build.js`, phase 2, before the loop's first `parallel`). The loop starts with `first = true`. If the first `ready-implementers` answer has an empty `subtickets`, the build runs clerk `subticket add PARENT` with no `--run`. The clerk is the agent that runs one store command and reports its output. A refusal parks the parent with `no sub-tickets, and none could be created from the recorded plan: <stderr>` and returns `{state: 'parked'}`. On success the build logs the count and `continue`s. Because `first` is then false, the repair runs at most once per build run.
- **C1** (`build.js`, after the loop). A refused `parent-check` now parks the parent with `parent-check refused: <stderr>` and returns `parked`. A successful check that reports any state other than `ready-for-parent-verify` still returns as before.
- **C2** (`runRole` in both scripts). A `try`/`catch` now wraps both the stub `agent()` branch and the real one. On a throw, the script finishes the run with `--status-override KILLED`. In `build.js` it then runs `run cleanup` for a reviewer or verifier. It parks the ticket through the existing `park()` with `agent call failed: <role>: <message>` and the run id as outputs, then returns `null`. A null or empty result still takes the old KILLED path. In `build.js` I moved the stub-script seam (`<role>-<n>.sh`) out of the stub branch to just after the `try`, now guarded by `args.stubs &&`. That keeps the `try` around the `agent()` calls only, so a throwing clerk call in the seam is not reported as a failed role call.
- **D1** (`factory/cli.py` `results_record`). The regex is now `^[ \t#*]*Gate suite:[ \t*]*(PASS|FAIL)\b(.*)$` (`re.M`). The detail is group 2 with spaces, tabs, `\r` and `*` stripped from both ends, or `None` when that leaves nothing. When no line matches, the result is still `FAIL`, `missing Gate suite line`.
- **D2**. In three places, the line `Gate suite: PASS/FAIL, with failing output` is replaced by the two lines the spec pins: `docs/design.md` (§7 Verifier block) and `factory/prompts/verifier.md`, each by an exact-string replacement, and `docs/prompts/07-verifier.md`, re-copied from the design block with the acceptance check's own `awk` extraction. Step 4 of `factory/prompts/verifier.md` is untouched.
- **D3**. `docs/changelog.md` gains entry `47. After issue #33 (2026-10-04), …` after entry 46 and before `Declined:`. It covers the three points: intake ends at the gate and the build owns planning; a thrown agent call or a refused `parent-check` parks with the reason; and the verifier writes a plain `Gate suite:` line, which the harness also reads in heading or bold form.
- **E. Documents**
  - `README.md` "How a ticket moves" now ends its paragraph with `The intake script stops at the spec gate; the build script runs the planner.`, on its own line.
  - The "Start the…" sentence in "Starting a run" now reads `Start the build script after the spec gate; the intake script has nothing to do past it.`
  - The status-header date already reads 2026-10-04, which is today, so it is unchanged.
  - `dev/build-harness.spec.md` H `runRole` (line 275) now covers a thrown `agent()`. H `build.js` step 2 (line 285) now covers the `subtickets` key, the B3 repair and the C1 park. L (line 320) now says the gate line "may carry leading heading or emphasis marks".
- **F**. One new file, `tests/factory/test_build_startup.py`. It imports `run`, `js`, `ticket` and `PLAN_LETTERS` from `test_subtickets.py`, the way `test_killed_checker.py` imports from `test_shepherd.py`.

Callers of each changed function, found by grep (coding standard rule 2):
- `runRole` has 3 callers in `intake.js` and 4 in `build.js` (lines 125, 148, 191, 248 after the change). Each already returns on `null`.
- `results record` is called only from `build.js:150`.
- `ready-implementers` is called only from `build.js:210`, plus tests.
- `subticket add` is called from `build.js:199` with `--run`, unchanged, and from the new `build.js:216`.

## Acceptance results

I ran every command from the worktree root under `bash`, after `uv sync --frozen`, with node v24.14.0. First I ran the parent's GIVEN block once (`v2.md` lines 154-200, between the fences). It wrote `$TMPDIR/t0018-drive.js`, `t0018-approved.sh` and `t0018-handplan.sh`. "Before" means the code at base `d0300d3`; "after" means the code at head `7a4967a`, whose tree is the one I tested.

| Scenario | Kind | Before (base) | After (head) |
|---|---|---|---|
| Intake leaves an approved ticket for the build workflow | NEW | `returned planned`, `ticket T-0001 planned in_flight=0 reason=-`, `run run-0004-planner PLANNED`: intake ran the planner | `returned ready-for-planner`, `ticket T-0001 ready-for-planner in_flight=0 reason=-`, no `run run-0004-planner` line: PASS |
| Build plans a gate-approved parent and creates its sub-tickets | REGRESSION | not run | `run run-0004-planner PLANNED`, `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer`, `source: plan:run-0004-planner`: PASS |
| Build creates the missing sub-tickets from the recorded planner run | NEW | `returned planned`, `ticket T-0001 planned … reason=-`, no `T-0001.1` line, `grep: …/T-0001.1.yaml: No such file or directory` | `ticket T-0001.1 parked in_flight=0 reason=budget kill: implementer`, `run run-0005-implementer KILLED`, `source: plan:run-0004-planner`: PASS |
| Build parks a planned parent it cannot give sub-tickets | NEW | `returned planned`, `ticket T-0001 planned in_flight=0 reason=-`: no park | `returned parked`, `ticket T-0001 parked in_flight=0 reason=no sub-tickets, and none could be created from the recorded plan: no recorded planner run found for T-0001 (latest plan.added source: tests/factory/fixtures/stubs/accept-approve/planner-1.md); …`, no `ticket T-0001.1` line: PASS |
| subticket add without a source uses the recorded planner run | NEW | `factory: TypeError: argument should be a str or an os.PathLike object … not 'NoneType'`, `exit=1`, no `T-0001.1.yaml` | last JSON line `{"ok": true, "parent": "T-0001", "subtickets": [{"id": "T-0001.1", …}]}`, `exit=0`, `source: plan:run-0004-planner`: PASS |
| subticket add without a source refuses when the plan came from a file | NEW | same `TypeError`, `exit=1`, listing `T-0001.yaml` | `no recorded planner run found for T-0001 …`, `exit=2`, no `TypeError`, listing `T-0001.yaml` alone: PASS |
| A failed agent call in intake parks the ticket | NEW | `threw agent type 'factory-triage' not found`, `ticket T-0001 ready-for-triage in_flight=1 reason=-`, `run run-0001-triage running` | `returned parked`, `ticket T-0001 parked in_flight=0 reason=agent call failed: triage: agent type 'factory-triage' not found`, `run run-0001-triage KILLED`: PASS |
| A failed agent call in the build parks the sub-ticket | NEW | `ticket T-0001.1 ready-for-implementer in_flight=1 reason=-`, `run run-0005-implementer running` | `ticket T-0001.1 parked in_flight=0 reason=agent call failed: implementer: agent type 'factory-implementer' not found`, `run run-0005-implementer KILLED`: PASS |
| The harness suite passes | REGRESSION | not run (`157 passed` per the spec) | `171 passed in 110.99s`: the 157 existing tests plus the 14 new ones. PASS |
| The change adds no whitespace errors | REGRESSION | not run | `git diff --check main...HEAD; echo "exit=$?"` printed only `exit=0`. PASS |
| Heading and emphasis gate lines are read | NEW | all four lines `=> FAIL\|missing Gate suite line` | `## Gate suite: PASS => PASS\|`, `**Gate suite:** PASS => PASS\|`, `### **Gate suite: PASS** => PASS\|`, `**Gate suite: FAIL** 2 failed => FAIL\|2 failed`: PASS |
| Plain gate lines and prose read as before | REGRESSION | not run | `Gate suite: PASS => PASS\|`, `Gate suite: FAIL 1 failed => FAIL\|1 failed`, `The Gate suite: PASS line was missing => FAIL\|missing Gate suite line`: PASS |
| The verifier prompt pins the gate line in all three copies | NEW | `0 0 1` for each file | `docs/design.md 1 1 0`, `docs/prompts/07-verifier.md 1 1 0`, `factory/prompts/verifier.md 1 1 0`: PASS |
| The design block and its prompt copy stay identical | REGRESSION | not run | `SAME`: PASS |
| The README says intake stops at the spec gate | NEW | `0` then `1` | `1` then `0`: PASS |
| The changelog records the change | NEW | `0` then `0` | `1` then `1`: PASS |
| The build spec names the accepted gate line forms | NEW | `0` | `1`: PASS |

Gate commands, run from the worktree exactly as written on head `7a4967a`:
- `git diff --check main...HEAD` printed nothing and exited 0 (`main` = merge base = `d0300d3`).
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `171 passed in 110.99s`.
- `uv run --frozen ruff check factory/cli.py tests/factory/test_build_startup.py` printed `All checks passed!`.

Behaviour the spec leaves to the reviewer, as far as I checked it:
- C2 cleanup for a checker. With the driver set to throw on `verifier`, the result was `ticket T-0001.1 parked in_flight=0 reason=agent call failed: verifier: agent type 'factory-verifier' not found` and `run run-0007-verifier KILLED`. The run's `wt/` directory is gone, and `run start` creates that directory for every checker (`factory/cli.py:253-254`). So `run cleanup` ran on the throw path.
- C1 (the `parent-check` refusal park) has no runnable scenario. I checked it by reading only: `build.js` lines 233-234 after the change.
- B3's "at most once per build run" is held by the `first` flag. I checked it by reading only.

## Tests added/changed

Added: `tests/factory/test_build_startup.py`, 14 cases. On base `factory/cli.py`, 10 of them fail and 4 pass. The 4 that pass are the plain-line, prose and `- Gate suite:` cases, which are meant to read the same before and after. With the change, all 14 pass.

| Test | What it checks |
|---|---|
| `test_subticket_add_without_a_source_uses_the_recorded_planner_run` | `ok`, the three sub-ticket ids, and `source: plan:<run>` |
| `test_subticket_add_without_a_source_takes_the_latest_plan` | With two planner runs and two `plan add`s, the second run is used |
| `test_subticket_add_without_a_source_refuses_with_no_recorded_planner_run[none\|file]` | With no `plan.added` event, or a plan added with `--file`: exit 2, the refusal text, no `TypeError`, only `T-0001.yaml` in `tickets/`, and the log byte-for-byte unchanged |
| `test_ready_implementers_lists_every_sub_ticket_in_id_order` | `subtickets` is `[]` before `subticket add`. It lists all three ids afterwards, a merged sub-ticket included, while `remaining` is unchanged in meaning |
| `test_the_gate_line_is_read_under_heading_and_emphasis_marks_only` (9 lines) | The 4 D1 forms, a leading-space form, the 2 plain forms, the prose line, and `- Gate suite: PASS`, which is not read: a list marker is not one of the allowed marks |

Changed: none. No existing test file was touched.

## Known gaps and uncertainties

- **A gate line split over two lines is no longer read.** The old regex's `\s*` after the colon could cross a newline, so a `Gate suite:` line with `PASS` on the next line used to be read as PASS. The spec's pinned `[ \t*]*` does not cross a newline, so that form is now `missing Gate suite line`. I found no output or test that writes it that way: the existing tests put the detail on the next line, not the verdict. The prompt now pins the one-line form.
- **The `subticket add` source lookup reads the whole log on every call.** That is a linear scan of every `log/*.jsonl` file. It is cheap at today's store sizes, and `log_tail` reads the log the same way. I did not add a `factory:` marker because it is not a deliberate shortcut with a known limit beyond that.
- **The README sentence describes behaviour no real ticket has run yet.** README's "Maintaining this page" says a behaviour appears in the present tense only after it has run on a real ticket. The spec pins the exact sentence, and it describes intake doing less, so I followed the spec. A reviewer may judge it against that rule.
- **The C2 throw path is checked only under the node driver.** The real Workflow runtime might not surface an unknown agent type as a throw inside `runRole`, for example if it threw synchronously outside the awaited promise. The parent's Evidence makes the same inference. `try`/`await` catches both synchronous throws and rejections, so the catch holds either way.
- factory: markers added: none.

## Out-of-scope observations

- Park reasons built from a clerk's stderr keep the trailing newline. Examples are the new `no sub-tickets…` and `parent-check refused: …` reasons, and every existing `harness-bug: …: ${stderr}` reason. The driver's listing therefore shows an empty line after such a reason. Trimming them would be a change across every `park()` caller.
- `park()` in both scripts puts the reason inside a double-quoted shell argument and escapes only `"`. An error message that contains `` ` `` or `$(` would be expanded by the shell. The new `agent call failed: …` reason carries a free-form runtime error message, which makes this more reachable than before. `agent type '…' not found` itself is safe.

## Responses to findings

n/a: this is round 1.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every NEW check failed on base as the spec says and passes on head, the regression checks pass, and the suite passes (171). C1 and the B3 once-per-run limit are checked by reading only, as the spec says.
ESCALATIONS: none

## Diff `d0300d3127fdd257d725ecb996b4fe9df282cef9...7a4967a055bc40e3839c65fc00416299d90db350`

diff --git a/README.md b/README.md
index 4de7ab5..d471629 100644
--- a/README.md
+++ b/README.md
@@ -80,9 +80,8 @@ state "ready for triage". The intake workflow runs triage. On accept, the spec w
 the repo and writes the spec. The critic judges it and approves, asks for a revision (at most
 twice), or escalates. On approve, the ticket waits at the **spec gate**. A human reads the spec,
 edits it if needed, and approves it (pinning that version) or sends it back with notes. Nothing
-downstream runs until this happens. The intake script also contains a planning step, but it only
-runs when a ticket is already past the gate at launch; in practice the build script runs the
-planner.
+downstream runs until this happens.
+The intake script stops at the spec gate; the build script runs the planner.
 
 The build workflow runs the planner, which splits the spec into sub-tickets with dependencies.
 When a sub-ticket's dependencies are merged, an implementer builds it on a branch in its own
@@ -273,7 +272,7 @@ It then calls the Workflow tool with `scriptPath` set to the intake script and a
 script. Add `inlineRoles: true` on every target for now: `agents/` ships agent definitions only for
 the intake roles, so a build without it fails at the first implementer call (#24). With it, roles
 read their prompt from the run's `system-prompt.txt`, and run without per-role tool limits. Start the
-build script after the spec gate, never the intake script (#33).
+build script after the spec gate; the intake script has nothing to do past it.
 
 ### Running many tickets: runner and operator sessions
 
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index ec64614..1ebdae5 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -272,7 +272,7 @@ Both scripts are plain JS per E7; they hold the routing, the join and the round
 
 **STATUS parser** (`factory/status.py`, used by `run finish` and `results record`; doc §Routing rules): the **last** line matching `^STATUS:\s*(\S+)` gives the STATUS. CONFIDENCE is the first line after it matching `^CONFIDENCE:`, and ESCALATIONS the first line after that matching `^ESCALATIONS:`; lines between labelled lines are continuation (a wrapped CONFIDENCE reason, commentary between STATUS and CONFIDENCE), never a parse failure. No `CONFIDENCE:` line after the last STATUS, or no `ESCALATIONS:` line after that CONFIDENCE → parse failure → unknown STATUS. The **head** is the rest of the `ESCALATIONS:` line, trimmed; the list is the head plus every non-blank line after it to EOF, each item as written (a leading `- ` or `* ` marker stripped, item 8). A **`none` head** matches `(?i)^none\s*($|[.,;:—–-])`: `none` in any case, then end of line or punctuation, never a space and a word, so `none`, `none.` and `none. The boundary was observed` are `none` heads and `Nonetheless …`, `None of …` are not. The list is empty iff nothing non-blank follows the head and the head is empty or a `none` head; a `none` head with prose after it on its line therefore routes as no escalation, and `run finish` writes that head verbatim to the run's `meta.yaml` as `escalations_note:` (written only when the list is empty and prose follows the `none` head; every other shape, including bare `none` and a `none` head with lines below it, writes `null`) so an auditor reads it with the run. A `none` head followed by any further non-blank line is a real list, every line from the head on an item, verbatim (a wrapped `none` prose line is such a line: when the parser is unsure, the text goes to the human queue). The parser reads no severities: doc §Human gates' rule that REVISE and REQUEST-CHANGES carry at least one BLOCKING finding is the checker's to keep, and every stub that models them (items 38, 44, 46) includes a BLOCKING line.
 
-Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run start … --model MODELS[role]` (prints `run_id`; exit 2 from a guard → park `harness-bug: <stderr>` and return); clerk `factory run compose RUN_ID` (writes `input.md`, I.2); `const out = await agent('Your entire input is ~/factory/state/runs/' + runId + '/input.md; read it first.', {agentType: args.stubs ? 'factory-stub' : 'factory-' + role, model: MODELS[role], label: role + ' ' + ticket, isolation: role in {implementer, retro} ? 'worktree' : undefined})`; **KILLED condition** `out === null || out.trim() === ''` (I.5) → clerk `factory run finish RUN --status-override KILLED`; else clerk `factory run finish RUN --output-file -` with `out`. The clerk returns only `{stdout, exit, stderr}`; the script parses `run_id` from `run start`'s JSON and `{status, escalations}` from `run finish`'s. The stub agent definition reads `args.stubs/<role>-<n>.md` (n = how many times that role has run in this workflow, counted in the script) and returns it verbatim, or **returns an empty string when the file is absent** (the KILLED seam): the only test seam. The CLI guards (B) are authoritative over the script's `round < MAX` checks: a `transition` the routing table or `max_rounds` forbids exits 2 with the store unchanged, and the script treats that as `park --reason 'harness-bug: <stderr>'`.
+Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run start … --model MODELS[role]` (prints `run_id`; exit 2 from a guard → park `harness-bug: <stderr>` and return); clerk `factory run compose RUN_ID` (writes `input.md`, I.2); `const out = await agent('Your entire input is ~/factory/state/runs/' + runId + '/input.md; read it first.', {agentType: args.stubs ? 'factory-stub' : 'factory-' + role, model: MODELS[role], label: role + ' ' + ticket, isolation: role in {implementer, retro} ? 'worktree' : undefined})`; **KILLED condition** `out === null || out.trim() === ''` (I.5) → clerk `factory run finish RUN --status-override KILLED`; else clerk `factory run finish RUN --output-file -` with `out`. **A thrown `agent()`** (stub or real call) is finished the same way, clerk `factory run finish RUN --status-override KILLED` (in `build.js`, then clerk `factory run cleanup RUN` for a reviewer or verifier), and parks the ticket `agent call failed: <role>: <error>` with the run id as outputs; `runRole` returns `null`, on which every caller returns. The clerk returns only `{stdout, exit, stderr}`; the script parses `run_id` from `run start`'s JSON and `{status, escalations}` from `run finish`'s. The stub agent definition reads `args.stubs/<role>-<n>.md` (n = how many times that role has run in this workflow, counted in the script) and returns it verbatim, or **returns an empty string when the file is absent** (the KILLED seam): the only test seam. The CLI guards (B) are authoritative over the script's `round < MAX` checks: a `transition` the routing table or `max_rounds` forbids exits 2 with the store unchanged, and the script treats that as `park --reason 'harness-bug: <stderr>'`.
 
 `intake.js` (`args: {ticket, stubs?}`):
 1. `phase('Triage')`: `runRole('triage', …)` with input = request, answers appended (+ after an `--answer`: Triage's previous output, K); `ACCEPT` → clerk `transition --to ready-for-spec-writer` (title/type from the output); `REJECT` → `closed`; `NEEDS-HUMAN` → `park --question`; `CLARIFY` → `transition --to waiting-requester` + clerk `factory reply ID --file -` (piece 9: writes `<source dir>/<file>.reply.md` next to the request, appends to `queue.md`, event `reply.sent`); then **return**. Unknown STATUS → `park --reason 'harness-bug: unknown STATUS <s>'` + `harness-bug` event; always return.
@@ -282,7 +282,7 @@ Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run st
 
 `build.js` (`args: {ticket}`), run after `factory approve-spec`:
 1. `phase('Plan')` (only when the parent is `ready-for-planner`; a re-run starts from the stored state, so a `--ruling` on a planner ESCALATE re-runs the planner with the ruling in its input): `runRole('planner')` with the pinned spec; `PLANNED` → clerk `factory spec tasks PARENT --run RUN` (B), then `subticket add` per sub-ticket (`depends_on`, `parallel_safe`); `ESCALATE` → park, return.
-2. `phase('Build')`: `while` any sub-ticket is not `merged|parked|closed`: `ready = ` clerk `factory ticket ready-implementers PARENT` (JSON: sub-tickets in `ready-for-implementer` whose deps are merged, minus any with a run in flight on its branch; a `parallel_safe: false` sub-ticket runs alone: it is listed only when no sibling of the same parent is in flight — any role: `in_flight` non-empty or `checks-in-flight` — and nothing else is listed with it, and while it is in flight no sibling is listed; doc §Routing table, Planner row; item 79); `await parallel(ready.map(st => () => buildOne(st)))`; if `ready` is empty and nothing is in flight, return (the rest is parked or waiting on a human). When the parent reaches `ready-for-parent-verify` (G), or a re-run finds it there: clerk `factory ticket parent-check PARENT` first. Its `reuse` field names a run when the parent has exactly one sub-ticket and it is merged, `main` is still at that sub-ticket's merge commit, the results row for the merged head is VERIFIED from a run whose base is the parent's `parent_base`, and the sub-ticket's text names every scenario of the pinned spec; that run stands for the parent-close run: no verifier run starts, the build goes to `factory archive PARENT` with that run id as the park outputs, and the close records it as `verified_by` (`null` → as follows). Otherwise `runRole('verifier', PARENT, <main SHA>)` — the parent-close run, whose inputs doc §Routing table (merge-gate row) declares: the pinned parent spec (every delta scenario with its `## Acceptance` label), head = current `main`, base = the parent's `parent_base`, `{gate commands}`; `run compose` supplies exactly these four (no sub-ticket text), the clerk makes the checkout of that head, and the verifier definition (rendered verbatim from the doc) checks out the head it was given and runs the base it was given; `VERIFIED` → clerk `factory archive PARENT` (K), then `closed`, or on its exit 2 `park --reason 'archive: <stderr>'`; `FAILED`/`SPEC-DEFECT` → `park --reason 'parent verify: <STATUS>'` with the output (human queue); then return.
+2. `phase('Build')`: `while` any sub-ticket is not `merged|parked|closed`: `ready = ` clerk `factory ticket ready-implementers PARENT` (JSON: sub-tickets in `ready-for-implementer` whose deps are merged, minus any with a run in flight on its branch; a `parallel_safe: false` sub-ticket runs alone: it is listed only when no sibling of the same parent is in flight — any role: `in_flight` non-empty or `checks-in-flight` — and nothing else is listed with it, and while it is in flight no sibling is listed; doc §Routing table, Planner row; item 79; its `subtickets` lists every sub-ticket id of the parent in id order); when the first `ready` of a build run has an empty `subtickets` (a parent planned with none), clerk `factory subticket add PARENT` with no `--run`, once per build run: it takes the planner run named by the parent's latest `plan.added` event; on its refusal park the parent `no sub-tickets, and none could be created from the recorded plan: <stderr>` and return, on success continue the loop; `await parallel(ready.map(st => () => buildOne(st)))`; if `ready` is empty and nothing is in flight, return (the rest is parked or waiting on a human). When nothing is left to build, clerk `factory ticket parent-check PARENT`; a refusal parks the parent `parent-check refused: <stderr>` and returns. When the parent reaches `ready-for-parent-verify` (G), or a re-run finds it there: clerk `factory ticket parent-check PARENT` first. Its `reuse` field names a run when the parent has exactly one sub-ticket and it is merged, `main` is still at that sub-ticket's merge commit, the results row for the merged head is VERIFIED from a run whose base is the parent's `parent_base`, and the sub-ticket's text names every scenario of the pinned spec; that run stands for the parent-close run: no verifier run starts, the build goes to `factory archive PARENT` with that run id as the park outputs, and the close records it as `verified_by` (`null` → as follows). Otherwise `runRole('verifier', PARENT, <main SHA>)` — the parent-close run, whose inputs doc §Routing table (merge-gate row) declares: the pinned parent spec (every delta scenario with its `## Acceptance` label), head = current `main`, base = the parent's `parent_base`, `{gate commands}`; `run compose` supplies exactly these four (no sub-ticket text), the clerk makes the checkout of that head, and the verifier definition (rendered verbatim from the doc) checks out the head it was given and runs the base it was given; `VERIFIED` → clerk `factory archive PARENT` (K), then `closed`, or on its exit 2 `park --reason 'archive: <stderr>'`; `FAILED`/`SPEC-DEFECT` → `park --reason 'parent verify: <STATUS>'` with the output (human queue); then return.
 3. `buildOne(st)`: loop:
    - `runRole('implementer', st, …, {isolation: 'worktree'})`; the implementer's worktree is created on current `main` at dispatch (doc §Routing table, Planner row), input = sub-ticket, pinned parent spec, AGENTS.md (+ round ≥ 2: both checker outputs, CI result, or the human ruling); `BLOCKED` → park, return; `READY-FOR-REVIEW` → clerk `factory ticket head ST` (from `git ls-remote`), `transition --to checks-in-flight --round pr:init`.
    - **Checkers in parallel, fresh contexts** (`parallel` is the join barrier, E7): `[rev, ver] = await parallel([() => runRole('reviewer', …), () => runRole('verifier', …)])` with input = `git diff main...head`, PR description, sub-ticket, parent spec (+ round ≥ 2: both prior outputs, the implementer's Responses); the clerk makes each a fresh checkout `~/factory/runs/<run_id>/wt` of the head; each result → clerk `results record` (stale rule applies; the `Commit:` line must equal the current head).
@@ -317,7 +317,7 @@ No API key in any run: the CLI authenticates from the owner's login. Keys only i
 
 ### L. Verifier as gate runner (piece 11)
 
-No separate CI service. For sub-ticket PRs, `results record --role verifier` writes `results/<head>/ci.yaml` from the `Gate suite: PASS|FAIL` line; missing → `FAIL`, `detail: missing Gate suite line`. For no-sub-ticket PRs (retro, revert), which have no verifier, `factory gate-run ID --head H` is the gate runner: a clean checkout of `H` in `~/factory/runs/gate-<n>/wt`, `{gate commands}` run there, `results/H/ci.yaml` `PASS`/`FAIL` (the failing output as `detail`) written under the harness identity, checkout removed. The routing dispatches it, not the operator: `ticket new --type retro|revert` runs it on the branch head (B), and `factory merge` on a retro/revert ticket whose current head has no ci row runs it before judging (G); the explicit command remains for a re-run.
+No separate CI service. For sub-ticket PRs, `results record --role verifier` writes `results/<head>/ci.yaml` from the first `Gate suite: PASS|FAIL` line, which may carry leading heading or emphasis marks (`## Gate suite: PASS`, `**Gate suite:** PASS`; `*` around the verdict and the detail is stripped) but no other text before `Gate suite:`; missing → `FAIL`, `detail: missing Gate suite line`. For no-sub-ticket PRs (retro, revert), which have no verifier, `factory gate-run ID --head H` is the gate runner: a clean checkout of `H` in `~/factory/runs/gate-<n>/wt`, `{gate commands}` run there, `results/H/ci.yaml` `PASS`/`FAIL` (the failing output as `detail`) written under the harness identity, checkout removed. The routing dispatches it, not the operator: `ticket new --type retro|revert` runs it on the branch head (B), and `factory merge` on a retro/revert ticket whose current head has no ci row runs it before judging (G); the explicit command remains for a re-run.
 
 ### M. Audit sample and retro entry
 
diff --git a/docs/changelog.md b/docs/changelog.md
index 83aba0a..5cb18bd 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -48,5 +48,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 44. After issue #20 (2026-10-03), because nothing stopped a coding agent from building more than its ticket needs: a coding standard, `docs/coding.md`, the twin of the writing standard. It opens with a precedence rule (a target repository's own instructions win where they disagree with it) and holds five rules an agent can check in its own output, each with a `Check:` line, the code-design principle it applies and a before-and-after example: reuse before writing, taking the first rung of a check order that holds; grep every caller and fix a shared function once; mark each deliberate shortcut with a `factory:` comment naming its limit and upgrade trigger; tag each over-building review finding; and one name per concept from spec to code. The review tags are `reuse:` (BLOCKING) and `stdlib:`, `native:`, `yagni:` and `delete:` (SHOULD-FIX), and a review pass ends with `net: -N lines possible` or `Lean already.` The implementer's step 4 gains a line pointing to the standard at `{coding standard}`, and the code reviewer's check 7 is replaced by one: its old "Maintainability, only where it will cause real problems" text is gone. The harness fills `{coding standard}` when a run starts, with the path of `docs/coding.md` in the harness checkout that runs it, through the same helper that fills `{writing standard}`, now applied to the role prompt as well as the preamble. The spec writer gains a rule to cut any part the ticket's intent does not need, naming it under Out of scope, and critic rubric 3 makes such a part a finding. The retro's input names the marker ledger, one row per `factory:` comment in the code on the integration branch; this is design only, and the harness code that builds the ledger waits for the ticket that builds the retro. The check order and the tag vocabulary are adapted from ponytail (DietrichGebert/ponytail, MIT).
 45. After issue #31 (2026-10-03), from the T-0013 to T-0015 build timings, where a parent-close run took 13 to 23% of each build and only two of about six test-suite runs per build could change a verdict: a REGRESSION acceptance check runs once, after the change. The implementer runs only the NEW checks before editing, and runs a REGRESSION check on its base only when it fails after the change; the verifier runs a REGRESSION check on base only when it fails on the PR. One gate run per commit: an acceptance check that already ran a gate command exactly as written on the same commit is that gate's run, for the implementer and the verifier. A parent with one sub-ticket closes on that sub-ticket's VERIFIED run when `main` has not moved since it merged, the run checked the merged head against the parent's recorded base, and the sub-ticket's text names every scenario of the parent's pinned spec; the run stands for the parent-close run, `ticket parent-check` reports it as `reuse`, and the close records it as `verified_by`. Every other parent still gets its own parent-close run, and every refusal is kept: a NEW check that does not fail first is a SPEC-DEFECT, a failing REGRESSION check fails the branch, and a gate failure is FAILED. The requested path-scoped gate skip was cut: a correct path list for this repository covers `docs/**`, which would have skipped no suite run in those builds.
 46. After the Nanobot target's T-0003 (2026-10-04), a ticket that existed only to get a decision: the human answered its question about where the port's code lives and closed it, archive never ran, and the decision stayed in that ticket's request, so the operator copied it by hand into the two later requests that depend on it. `decisions.md` gains writers besides archive: `factory decision add <ticket id> "<line>"`, at any ticket state, closed included, and `--decision "<line>"` on `resolve --answer` or `resolve --close`, refused with any other `resolve` mode. Each appends the line in archive's format, `<YYYY-MM-DD> <ticket id> <line>`, creates the file when absent, and logs `decision.recorded`. The spec writer and the critic receive a non-empty `decisions.md` after current truth, and the planner after the approved spec; triage and the build roles do not. Triage's NEEDS-HUMAN question and the spec writer's open questions now ask whether the answer is a standing decision that later tickets must follow. Archive's own output is unchanged.
+47. After issue #33 (2026-10-04), where six approved tickets on the Nanobot target stalled with no record of why: intake ends at the spec gate, and the build owns planning. A build that finds a planned parent with no sub-tickets creates them from the planner run named by the parent's latest `plan.added` event (`subticket add PARENT` with no `--run`), or parks the parent with a reason containing `no sub-tickets`. No stop is silent any more: an `agent()` call that throws finishes its run KILLED and parks the ticket with `agent call failed: <role>: <error>`, and a refused `parent-check` parks the parent with its refusal. The verifier writes `Gate suite:` as a plain line, never a heading or bold, and the harness also reads that line in heading or bold form, so a verifier's PASS written as `## Gate suite: PASS` is no longer recorded as a missing gate line.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 76ad2f6..5b22403 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -641,7 +641,8 @@ RULES
 OUTPUT
 Commit: <head SHA you verified>
 Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL (base: not run, for a REGRESSION that passed on the PR)
-Gate suite: PASS/FAIL, with failing output
+Gate suite: PASS/FAIL, with failing output on the lines below it
+  (a plain line starting "Gate suite:", never a heading or bold)
 Probes: input → result → OK / CONCERN
 STATUS: VERIFIED | FAILED | SPEC-DEFECT (precedence: SPEC-DEFECT > FAILED)
 CONFIDENCE / ESCALATIONS
diff --git a/docs/prompts/07-verifier.md b/docs/prompts/07-verifier.md
index 4ef112c..1f95b6e 100644
--- a/docs/prompts/07-verifier.md
+++ b/docs/prompts/07-verifier.md
@@ -34,7 +34,8 @@ RULES
 OUTPUT
 Commit: <head SHA you verified>
 Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL (base: not run, for a REGRESSION that passed on the PR)
-Gate suite: PASS/FAIL, with failing output
+Gate suite: PASS/FAIL, with failing output on the lines below it
+  (a plain line starting "Gate suite:", never a heading or bold)
 Probes: input → result → OK / CONCERN
 STATUS: VERIFIED | FAILED | SPEC-DEFECT (precedence: SPEC-DEFECT > FAILED)
 CONFIDENCE / ESCALATIONS
diff --git a/factory/cli.py b/factory/cli.py
index 9807d32..8a96fc4 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -363,10 +363,26 @@ def plan_add(a, root, cfg):
 
 # ----- build half: sub-tickets, results, merge (parts B, D, G; local stand-in) -------------------
 
+def _recorded_plan_run(root: Path, tid: str) -> str:
+    """The run named by the ticket's latest `plan.added` event, when that is a run of this store."""
+    source = None
+    for p in sorted((root / "log").glob("*.jsonl")):
+        for ln in p.read_text(encoding="utf-8").splitlines():
+            e = json.loads(ln)
+            if e.get("event") == "plan.added" and e.get("ticket") == tid:
+                source = e.get("source")
+    if not source or "/" in source or not (root / "runs" / source / "meta.yaml").exists():
+        raise Refused(f"no recorded planner run found for {tid} (latest plan.added source: {source or 'none'}); "
+                      "pass --run RUN or --file F")
+    return source
+
+
 def subticket_add(a, root, cfg):
     parent = store.load_ticket(root, a.id)
     if parent["spec"]["approved_version"] is None:
         raise Refused(f"{parent['id']} has no approved spec")
+    if not a.run and not a.file:
+        a.run = _recorded_plan_run(root, parent["id"])
     if a.run:
         d = _run_dir(root, a.run)
         meta = store.read_yaml(d / "meta.yaml")
@@ -417,7 +433,7 @@ def ticket_ready_implementers(a, root, cfg):
             s["history"].append({"ts": store.now(), "from": "waiting-dependencies", "to": "ready-for-implementer", "by": "ready-implementers"})
             store.save_ticket(root, s)
             store.log_event(root, "ticket.transition", ticket=s["id"], **{"from": "waiting-dependencies", "to": "ready-for-implementer", "by": "ready-implementers"})
-    out({"ok": True, "parent": a.id, "ready": ready,
+    out({"ok": True, "parent": a.id, "ready": ready, "subtickets": [s["id"] for s in subs],
          "remaining": [s["id"] for s in subs if s["status"] not in ("merged", "parked", "closed")],
          "in_flight": [s["id"] for s in subs if s["in_flight"] or s["status"] in subtickets.IN_FLIGHT_STATES],
          "parked": [s["id"] for s in subs if s["status"] == "parked"],
@@ -477,8 +493,10 @@ def results_record(a, root, cfg):
     stale = t.get("head") is not None and a.head != t.get("head")
     rows = [store.record_result(root, t["id"], a.head, a.role, st, a.run)]
     if a.role == "verifier" and not a.killed:
-        m = re.search(r"^Gate suite:\s*(PASS|FAIL)\b(.*)$", text, re.M)
-        ci = (m.group(1), m.group(2).strip() or None) if m else ("FAIL", "missing Gate suite line")
+        # Heading and emphasis marks may wrap the line (`## Gate suite: PASS`, `**Gate suite:** PASS`);
+        # other text before `Gate suite:` is prose, not a verdict.
+        m = re.search(r"^[ \t#*]*Gate suite:[ \t*]*(PASS|FAIL)\b(.*)$", text, re.M)
+        ci = (m.group(1), m.group(2).strip(" \t\r*") or None) if m else ("FAIL", "missing Gate suite line")
         rows.append(store.record_result(root, t["id"], a.head, "ci", ci[0], a.run, ci[1]))
     ev = "result.stale-discarded" if stale else "result.recorded"
     for r in rows:
@@ -1054,7 +1072,8 @@ def build_parser() -> argparse.ArgumentParser:
     p.add_argument("--run", required=True)
     p.set_defaults(fn=spec_tasks)
     sb = sp.add_parser("subticket").add_subparsers(dest="sub", required=True)
-    p = sb.add_parser("add")
+    p = sb.add_parser("add", help="create the parent's sub-tickets from a plan; with neither --run nor --file, "
+                                  "from the planner run named by its latest plan.added event")
     p.add_argument("id")
     p.add_argument("--run")
     p.add_argument("--file")
diff --git a/factory/prompts/verifier.md b/factory/prompts/verifier.md
index 305f813..b9f7855 100644
--- a/factory/prompts/verifier.md
+++ b/factory/prompts/verifier.md
@@ -35,7 +35,8 @@ RULES
 OUTPUT
 Commit: <head SHA you verified>
 Per criterion: NEW/REGRESSION | command | base | PR | PASS/FAIL (base: not run, for a REGRESSION that passed on the PR)
-Gate suite: PASS/FAIL, with failing output
+Gate suite: PASS/FAIL, with failing output on the lines below it
+  (a plain line starting "Gate suite:", never a heading or bold)
 Probes: input → result → OK / CONCERN
 STATUS: VERIFIED | FAILED | SPEC-DEFECT (precedence: SPEC-DEFECT > FAILED)
 CONFIDENCE / ESCALATIONS
diff --git a/factory/workflows/build.js b/factory/workflows/build.js
index e5a1529..4ece3ff 100644
--- a/factory/workflows/build.js
+++ b/factory/workflows/build.js
@@ -69,26 +69,35 @@ async function runRole(role, ticket, phase) {
   if (!comp.ok) { await park(ticket, `harness-bug: run compose ${role}: ${comp.stderr || ''}`, [runId], phase); return null }
   const outputPath = `${STATE}/runs/${runId}/output.md`
   let out
-  if (args.stubs) {
-    stubCount[role] = (stubCount[role] || 0) + 1
-    out = await agent(
-      `Stub file: ${args.stubs}/${role}-${stubCount[role]}.md\nOutput file: ${outputPath}\n` +
-      `If the stub file exists, write its content verbatim to the output file and return that content. ` +
-      `If it does not exist, write nothing and return an empty message.` +
-      (INLINE ? ' You are a test stub: do exactly this and nothing else; run no other command.' : ''),
-      { agentType: INLINE ? 'general-purpose' : `${PREFIX}stub`, model: 'haiku', effort: 'low', phase, label: `${role} (stub) ${ticket}` })
-    // Stub seam for the build half: `<role>-<n>.sh` beside the stub, run in the run's worktree, lets a stub
-    // implementer make its commit (or merge the integration branch on a conflict run).
-    if (role === 'implementer' && start.worktree) {
-      const sh = `${args.stubs}/${role}-${stubCount[role]}.sh`
-      await clerk(`if [ -f ${sh} ]; then (cd ${start.worktree} && sh ${sh}) >/dev/null 2>&1; fi; echo '{"ok": true}'`, phase, `stub script ${role}-${stubCount[role]}`)
+  try {
+    if (args.stubs) {
+      stubCount[role] = (stubCount[role] || 0) + 1
+      out = await agent(
+        `Stub file: ${args.stubs}/${role}-${stubCount[role]}.md\nOutput file: ${outputPath}\n` +
+        `If the stub file exists, write its content verbatim to the output file and return that content. ` +
+        `If it does not exist, write nothing and return an empty message.` +
+        (INLINE ? ' You are a test stub: do exactly this and nothing else; run no other command.' : ''),
+        { agentType: INLINE ? 'general-purpose' : `${PREFIX}stub`, model: 'haiku', effort: 'low', phase, label: `${role} (stub) ${ticket}` })
+    } else {
+      out = await agent(
+        (INLINE ? `First read ${STATE}/runs/${runId}/system-prompt.txt: it is your role and your rules for this run; follow it exactly, including the preamble at its top. ` : '') +
+        `Your entire input is the file ${STATE}/runs/${runId}/input.md; read it first and follow it. ` +
+        `Write your complete output to ${outputPath} and return the same text.`,
+        { agentType: INLINE ? 'general-purpose' : `${PREFIX}${AGENT_NAME[role]}`, model: MODELS[role], phase, label: `${role} ${ticket}` })
     }
-  } else {
-    out = await agent(
-      (INLINE ? `First read ${STATE}/runs/${runId}/system-prompt.txt: it is your role and your rules for this run; follow it exactly, including the preamble at its top. ` : '') +
-      `Your entire input is the file ${STATE}/runs/${runId}/input.md; read it first and follow it. ` +
-      `Write your complete output to ${outputPath} and return the same text.`,
-      { agentType: INLINE ? 'general-purpose' : `${PREFIX}${AGENT_NAME[role]}`, model: MODELS[role], phase, label: `${role} ${ticket}` })
+  } catch (e) {
+    // A thrown call (e.g. an agent type that is not installed) gives no result: record the run as
+    // killed and park with the error, so no run is left in flight. parallel() would otherwise absorb it.
+    await clerk(`${BIN} run finish ${runId} --status-override KILLED`, phase, `run finish ${role} (agent call failed)`)
+    if (role === 'reviewer' || role === 'verifier') await clerk(`${BIN} run cleanup ${runId}`, phase, `run cleanup ${role}`)
+    await park(ticket, `agent call failed: ${role}: ${e && e.message ? e.message : e}`, [runId], phase)
+    return null
+  }
+  // Stub seam for the build half: `<role>-<n>.sh` beside the stub, run in the run's worktree, lets a stub
+  // implementer make its commit (or merge the integration branch on a conflict run).
+  if (args.stubs && role === 'implementer' && start.worktree) {
+    const sh = `${args.stubs}/${role}-${stubCount[role]}.sh`
+    await clerk(`if [ -f ${sh} ]; then (cd ${start.worktree} && sh ${sh}) >/dev/null 2>&1; fi; echo '{"ok": true}'`, phase, `stub script ${role}-${stubCount[role]}`)
   }
   const killed = out === null || (typeof out === 'string' && out.trim() === '')
   const fin = killed
@@ -196,9 +205,20 @@ if (state === 'ready-for-planner') {
 // --- phase 2: Build (while any sub-ticket is not merged|parked|closed)
 if (state === 'planned') {
   phase('Build')
+  let first = true
   while (true) {
     const ready = await clerk(`${BIN} ticket ready-implementers ${TICKET}`, 'Build', 'ready-implementers')
     if (!ready.ok) { await park(TICKET, `harness-bug: ready-implementers: ${ready.stderr || ''}`, [], 'Build'); return { ticket: TICKET, state: 'parked' } }
+    // A parent planned with no sub-tickets (e.g. by an older intake): create them once from the planner
+    // run its recorded plan names, or park the parent saying why.
+    if (first && ready.subtickets && ready.subtickets.length === 0) {
+      first = false
+      const made = await clerk(`${BIN} subticket add ${TICKET}`, 'Build', 'subticket add (recorded plan)')
+      if (!made.ok) { await park(TICKET, `no sub-tickets, and none could be created from the recorded plan: ${made.stderr || ''}`, [], 'Build'); return { ticket: TICKET, state: 'parked' } }
+      log(`${TICKET}: created ${(made.subtickets || []).length} sub-ticket(s) from the recorded plan`)
+      continue
+    }
+    first = false
     // A sub-ticket the human closed parks the parent: amend the spec and re-plan, or close (doc §Routing rules).
     if (ready.closed && ready.closed.length) { await park(TICKET, `sub-ticket closed by a human: ${ready.closed.join(', ')}`, [], 'Build'); return { ticket: TICKET, state: 'parked' } }
     const todo = ready.ready.concat(ready.resumable || [])
@@ -210,7 +230,8 @@ if (state === 'planned') {
     await parallel(todo.map(st => () => buildOne(st)))
   }
   const pc = await clerk(`${BIN} ticket parent-check ${TICKET}`, 'Build', 'parent-check')
-  if (!pc.ok || pc.state !== 'ready-for-parent-verify') return { ticket: TICKET, state: pc.state || 'planned' }
+  if (!pc.ok) { await park(TICKET, `parent-check refused: ${pc.stderr || ''}`, [], 'Build'); return { ticket: TICKET, state: 'parked' } }
+  if (pc.state !== 'ready-for-parent-verify') return { ticket: TICKET, state: pc.state || 'planned' }
   state = 'ready-for-parent-verify'
 }
 
diff --git a/factory/workflows/intake.js b/factory/workflows/intake.js
index dfa015a..b145f46 100644
--- a/factory/workflows/intake.js
+++ b/factory/workflows/intake.js
@@ -1,10 +1,9 @@
 export const meta = {
   name: 'factory-intake',
-  description: 'Spec factory intake: Triage -> Spec writer <-> Spec critic (max 2 rounds) -> human gate -> Planner, for one ticket',
+  description: 'Spec factory intake: Triage -> Spec writer <-> Spec critic (max 2 rounds) -> human gate, for one ticket',
   phases: [
     { title: 'Triage', detail: 'classify the request; ACCEPT routes to the spec writer' },
     { title: 'Spec', detail: 'writer and critic alternate, fresh context each, until APPROVE or the round cutoff' },
-    { title: 'Plan', detail: 'after the human gate: planner decomposes the approved spec' },
   ],
 }
 // args: { ticket, repo, instance?, state?, stubs?, agentPrefix? }
@@ -32,7 +31,7 @@ const PREFIX = args.agentPrefix || 'factory-'
 // role prompt from runs/<id>/system-prompt.txt. Model per role is unchanged; tool fences are not.
 const INLINE = !!args.inlineRoles
 const CLERK_RULES = 'You are the store clerk of the spec factory: run the one command you are given, once, unchanged, from the repository root; run nothing else, edit nothing, interpret nothing. '
-const AGENT_NAME = { triage: 'triage', spec_writer: 'spec-writer', critic: 'spec-critic', planner: 'planner' }
+const AGENT_NAME = { triage: 'triage', spec_writer: 'spec-writer', critic: 'spec-critic' }
 
 const CLERK_SCHEMA = {
   type: 'object',
@@ -79,20 +78,28 @@ async function runRole(role, phase) {
   if (!comp.ok) { await park(`harness-bug: run compose ${role}: ${comp.stderr || ''}`, [runId], phase); return null }
   const outputPath = `${STATE}/runs/${runId}/output.md`
   let out
-  if (args.stubs) {
-    stubCount[role] = (stubCount[role] || 0) + 1
-    out = await agent(
-      `Stub file: ${args.stubs}/${role}-${stubCount[role]}.md\nOutput file: ${outputPath}\n` +
-      `If the stub file exists, write its content verbatim to the output file and return that content. ` +
-      `If it does not exist, write nothing and return an empty message.` +
-      (INLINE ? ' You are a test stub: do exactly this and nothing else; run no other command.' : ''),
-      { agentType: INLINE ? 'general-purpose' : `${PREFIX}stub`, model: 'haiku', effort: 'low', phase, label: `${role} (stub) ${TICKET}` })
-  } else {
-    out = await agent(
-      (INLINE ? `First read ${STATE}/runs/${runId}/system-prompt.txt: it is your role and your rules for this run; follow it exactly, including the preamble at its top. ` : '') +
-      `Your entire input is the file ${STATE}/runs/${runId}/input.md; read it first and follow it. ` +
-      `Write your complete output to ${outputPath} and return the same text.`,
-      { agentType: INLINE ? 'general-purpose' : `${PREFIX}${AGENT_NAME[role]}`, model: MODELS[role], phase, label: `${role} ${TICKET}` })
+  try {
+    if (args.stubs) {
+      stubCount[role] = (stubCount[role] || 0) + 1
+      out = await agent(
+        `Stub file: ${args.stubs}/${role}-${stubCount[role]}.md\nOutput file: ${outputPath}\n` +
+        `If the stub file exists, write its content verbatim to the output file and return that content. ` +
+        `If it does not exist, write nothing and return an empty message.` +
+        (INLINE ? ' You are a test stub: do exactly this and nothing else; run no other command.' : ''),
+        { agentType: INLINE ? 'general-purpose' : `${PREFIX}stub`, model: 'haiku', effort: 'low', phase, label: `${role} (stub) ${TICKET}` })
+    } else {
+      out = await agent(
+        (INLINE ? `First read ${STATE}/runs/${runId}/system-prompt.txt: it is your role and your rules for this run; follow it exactly, including the preamble at its top. ` : '') +
+        `Your entire input is the file ${STATE}/runs/${runId}/input.md; read it first and follow it. ` +
+        `Write your complete output to ${outputPath} and return the same text.`,
+        { agentType: INLINE ? 'general-purpose' : `${PREFIX}${AGENT_NAME[role]}`, model: MODELS[role], phase, label: `${role} ${TICKET}` })
+    }
+  } catch (e) {
+    // A thrown call (e.g. an agent type that is not installed) gives no result: record the run as
+    // killed and park with the error, so no run is left in flight.
+    await clerk(`${BIN} run finish ${runId} --status-override KILLED`, phase, `run finish ${role} (agent call failed)`)
+    await park(`agent call failed: ${role}: ${e && e.message ? e.message : e}`, [runId], phase)
+    return null
   }
   const killed = out === null || (typeof out === 'string' && out.trim() === '')
   const fin = killed
@@ -169,23 +176,4 @@ if (state === 'ready-for-spec-writer' || state === 'ready-for-critic') {
   }
 }
 
-// --- phase 3: Plan (only after the human gate moved the ticket to ready-for-planner)
-if (state === 'ready-for-planner') {
-  phase('Plan')
-  const p = await runRole('planner', 'Plan')
-  if (!p) return { ticket: TICKET, state: 'parked' }
-  if (p.status === 'PLANNED') {
-    // Spec store (build spec H, K): the plan is the change's tasks.md; a store without `factory init` reports skipped.
-    const tasks = await clerk(`${BIN} spec tasks ${TICKET} --run ${p.runId}`, 'Plan', 'spec tasks')
-    if (!tasks.ok) { await park(`harness-bug: spec tasks: ${tasks.stderr || ''}`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
-    const added = await clerk(`${BIN} plan add ${TICKET} --from-run ${p.runId}`, 'Plan', 'plan add')
-    if (!added.ok) { await park(`harness-bug: plan add: ${added.stderr || ''}`, [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
-    await transition('planned', null, 'Plan')
-    return { ticket: TICKET, state: 'planned' }
-  }
-  if (p.status === 'ESCALATE') { await park('ESCALATE from planner', [p.runId], 'Plan'); return { ticket: TICKET, state: 'parked' } }
-  await park(`harness-bug: unknown STATUS ${p.status} from planner`, [p.runId], 'Plan')
-  return { ticket: TICKET, state: 'parked' }
-}
-
 return { ticket: TICKET, state, note: 'nothing to dispatch from this state' }
diff --git a/tests/factory/test_build_startup.py b/tests/factory/test_build_startup.py
new file mode 100644
index 0000000..97f4d3a
--- /dev/null
+++ b/tests/factory/test_build_startup.py
@@ -0,0 +1,117 @@
+"""What the build needs at its start (issue #33): `subticket add` with no source takes the planner run
+the parent's recorded plan names, `ready-implementers` lists every sub-ticket so the build can see a
+parent with none, and the verifier's `Gate suite:` line is read under heading and emphasis marks."""
+from __future__ import annotations
+
+from pathlib import Path
+
+import pytest
+import yaml
+
+from .test_subtickets import PLAN_LETTERS, js, run, ticket
+
+
+def approved_parent(store: Path, tmp_path: Path) -> str:
+    """A parent past the spec gate (old-format spec; no spec store), with no plan yet."""
+    req = tmp_path / "r.md"
+    req.write_text("# Fixture\n\nThe bot should do the thing.\n")
+    tid = js(run(store, "ticket", "new", "--file", str(req)))["id"]
+    spec = tmp_path / "s.md"
+    spec.write_text("## Problem\nx\n")
+    js(run(store, "ticket", "transition", tid, "--to", "ready-for-spec-writer", "--by", "t"))
+    js(run(store, "spec", "add", tid, "--file", str(spec)))
+    js(run(store, "ticket", "transition", tid, "--to", "ready-for-critic", "--by", "t", "--round", "spec:init"))
+    js(run(store, "ticket", "transition", tid, "--to", "awaiting-spec-gate", "--by", "t"))
+    js(run(store, "approve-spec", tid))
+    return tid
+
+
+def planner_run(store: Path, tid: str, plan: str) -> str:
+    rid = js(run(store, "run", "start", "--role", "planner", "--ticket", tid))["run_id"]
+    js(run(store, "run", "compose", rid))
+    (store / "runs" / rid / "output.md").write_text(plan)
+    js(run(store, "run", "finish", rid))
+    return rid
+
+
+def ticket_files(store: Path) -> list[str]:
+    return sorted(p.name for p in (store / "tickets").iterdir())
+
+
+def test_subticket_add_without_a_source_uses_the_recorded_planner_run(tmp_path):
+    store = tmp_path / "state"
+    tid = approved_parent(store, tmp_path)
+    rid = planner_run(store, tid, PLAN_LETTERS)
+    js(run(store, "plan", "add", tid, "--from-run", rid))
+    out = js(run(store, "subticket", "add", tid))
+    assert out["ok"] is True and [s["id"] for s in out["subtickets"]] == ["T-0001.1", "T-0001.2", "T-0001.3"]
+    assert ticket(store, "T-0001.1")["source"] == f"plan:{rid}"
+
+
+def test_subticket_add_without_a_source_takes_the_latest_plan(tmp_path):
+    store = tmp_path / "state"
+    tid = approved_parent(store, tmp_path)
+    first = planner_run(store, tid, PLAN_LETTERS)
+    js(run(store, "plan", "add", tid, "--from-run", first))
+    second = planner_run(store, tid, PLAN_LETTERS)
+    js(run(store, "plan", "add", tid, "--from-run", second))
+    js(run(store, "subticket", "add", tid))
+    assert ticket(store, "T-0001.1")["source"] == f"plan:{second}"
+
+
+@pytest.mark.parametrize("plan_from", ["none", "file"])
+def test_subticket_add_without_a_source_refuses_with_no_recorded_planner_run(tmp_path, plan_from):
+    store = tmp_path / "state"
+    tid = approved_parent(store, tmp_path)
+    if plan_from == "file":
+        plan = tmp_path / "plan.md"
+        plan.write_text(PLAN_LETTERS)
+        js(run(store, "plan", "add", tid, "--file", str(plan)))
+    log_before = sorted((p.name, p.read_text()) for p in (store / "log").glob("*.jsonl"))
+    cp = run(store, "subticket", "add", tid)
+    assert cp.returncode == 2, cp.stderr
+    assert "no recorded planner run found for T-0001" in cp.stderr and "TypeError" not in cp.stderr
+    assert ticket_files(store) == ["T-0001.yaml"]
+    assert sorted((p.name, p.read_text()) for p in (store / "log").glob("*.jsonl")) == log_before
+
+
+def test_ready_implementers_lists_every_sub_ticket_in_id_order(tmp_path):
+    store = tmp_path / "state"
+    tid = approved_parent(store, tmp_path)
+    rid = planner_run(store, tid, PLAN_LETTERS)
+    js(run(store, "plan", "add", tid, "--from-run", rid))
+    js(run(store, "ticket", "transition", tid, "--to", "planned", "--by", "t"))
+    assert js(run(store, "ticket", "ready-implementers", tid))["subtickets"] == []
+    js(run(store, "subticket", "add", tid))
+    t = ticket(store, "T-0001.1")
+    t["status"] = "merged"  # a finished sub-ticket is still listed
+    (store / "tickets" / "T-0001.1.yaml").write_text(yaml.safe_dump(t, sort_keys=False))
+    r = js(run(store, "ticket", "ready-implementers", tid))
+    assert r["subtickets"] == ["T-0001.1", "T-0001.2", "T-0001.3"]
+    assert r["remaining"] == ["T-0001.2", "T-0001.3"]
+
+
+HEAD = "a" * 40
+
+
+@pytest.mark.parametrize("line, status, detail", [
+    ("## Gate suite: PASS", "PASS", None),
+    ("**Gate suite:** PASS", "PASS", None),
+    ("### **Gate suite: PASS**", "PASS", None),
+    ("**Gate suite: FAIL** 2 failed", "FAIL", "2 failed"),
+    ("  Gate suite: PASS", "PASS", None),
+    ("Gate suite: PASS", "PASS", None),
+    ("Gate suite: FAIL 1 failed", "FAIL", "1 failed"),
+    ("The Gate suite: PASS line was missing", "FAIL", "missing Gate suite line"),
+    ("- Gate suite: PASS", "FAIL", "missing Gate suite line"),
+])
+def test_the_gate_line_is_read_under_heading_and_emphasis_marks_only(tmp_path, line, status, detail):
+    store = tmp_path / "state"
+    req = tmp_path / "r.md"
+    req.write_text("# Fixture\n\nThe bot should do the thing.\n")
+    tid = js(run(store, "ticket", "new", "--file", str(req)))["id"]
+    out = tmp_path / "v.md"
+    out.write_text(f"Commit: {HEAD}\n{line}\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n")
+    js(run(store, "results", "record", tid, "--head", HEAD, "--role", "verifier", "--output", str(out)))
+    ci = yaml.safe_load((store / "results" / HEAD / "ci.yaml").read_text())
+    assert (ci["status"], ci.get("detail")) == (status, detail)
