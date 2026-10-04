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
`/Users/dphang/dev/spec-factory/.factory/state/runs/run-0156-spec_writer/output.md`

## Ticket (Triage output)

Type: bug

Title: Planning without sub-tickets, silent build exits, and a misread gate line stall tickets with no record of why

Summary:
The requester runs the factory on the Nanobot v3.5 port. The factory's two workflow scripts can stall a ticket without saying so. In the factory, a parent ticket is an approved spec. Its sub-tickets are the pieces the planner splits it into, each built and merged separately. To park a ticket is to stop it and put the reason in the human queue.
1. The intake workflow's Plan phase plans a parent but never creates its sub-tickets. The build workflow then finds nothing to build and exits after about 30 s. The parent stays `planned`, nothing is parked and no error is logged.
2. When a role's agent call fails, the build workflow returns without parking. The run is left recorded as in flight on the ticket.
3. When the verifier writes its gate result as a heading (`## Gate suite: PASS`), the harness misses it. It records the CI result as FAIL with "missing Gate suite line", and each occurrence has cost a full revision round.
The requester wants intake to stop at the spec gate, with planning done only by the build workflow. A build that starts on a `planned` parent with no sub-tickets should create them from the planner run already recorded for that parent. A refusal from the parent check, or any failed role call, should park the ticket with the reason, and a failed call should also record its run as KILLED. The gate-line reader should accept the heading and emphasis forms. The verifier prompt should state the exact line format.

Evidence:
- Request (issue #33, filed by the Nanobot v3.5 Driver, the session that runs the port's builds): six parents were planned at once in the Nanobot v3.5 store on 2026-10-04 with no sub-tickets: T-0001, T-0004, T-0007, T-0008, T-0011 and T-0012. The Driver created the sub-tickets by hand with `subticket add <parent> --run <planner run>`, taking the run ids from the `plan.added` log events.
- Confirmed on this checkout, `factory/workflows/intake.js` lines 172-184. The Plan phase runs the planner, `spec tasks` and `plan add`, then moves the parent to `planned`. It has no `subticket add`. The build workflow does run it, at `factory/workflows/build.js` line 190.
- Confirmed, `build.js` lines 197-213. On a `planned` parent, the empty-sub-ticket case breaks out of the build loop at line 207. `parent-check` is then called at line 212. When it refuses, line 213 returns `{ticket, state: 'planned'}` with no park and no log line. The refusal text is in `factory/cli.py` line 594: `"{id} has no sub-tickets"`.
- Confirmed in the Nanobot store, read only: `.factory/state/log/2026-10.jsonl` has six `plan.added` events between 05:54:51 and 05:56:18. One of them is T-0012 from run-0043-planner. T-0012 moved `ready-for-planner → planned` at 05:54:59. All sub-tickets for the six parents carry the same `ticket.created` timestamp, 05:56:56 (log lines 276-282), which fits the hand-run batch.
- Confirmed, `README.md` lines 83-85 say the intake script's planning step "only runs when a ticket is already past the gate at launch; in practice the build script runs the planner". Line 276 already warns to start the build script after the gate, "never the intake script (#33)". Issue #21 part D lists intake's Plan phase as known dead code.
- `dev/build-harness.spec.md` lines 277-281 describe `intake.js` as Triage and Spec phases only. Its re-run states stop at `ready-for-critic`, and it has no Plan phase. Removing the phase brings the code back in line with the build spec.
- Part D, comment on #33: in spec-factory run-0073-verifier (T-0012.5), `output.md` line 21 reads `## Gate suite: PASS`. The CI results rows `results/302f70bb…/ci.yaml` and `results/7090d9d2…/superseded-2/ci.yaml` both record `detail: missing Gate suite line`. The parser is `factory/cli.py` line 480: `re.search(r"^Gate suite:\s*(PASS|FAIL)\b(.*)$", text, re.M)`. It is anchored at line start, so a leading `## ` or `**` does not match. The second occurrence is Nanobot v3.5 T-0012.1 (run-0052). I did not open that run.
- Operator, appended to the request: the orphaned in-flight run from the comment on #24 (2026-10-04) belongs with part C: "any role call that fails records the run KILLED and parks with the error". The #24 comment, read with `gh issue view 24 --comments`, reports that "the build workflow left the sub-ticket holding an orphan in-flight run and returned without parking" after an agent call failed with "agent type 'factory-implementer' not found".
- Operator: spec gate pre-approved under `.factory/answers/queue-preapproval-policy.md`. That file lists "#33 (intake Plan phase removal, build start-up repair, park on parent-check refusal)" as pre-approved. The spec gate is the point where a human signs off a spec before code is written.

Assumptions (inferences, not stated by the requester):
- In both scripts, `runRole` already marks a run KILLED when `agent()` returns null or an empty string (`build.js` lines 93-96, `intake.js` lines 97-100). It does not catch an exception from `agent()`. My inference is that the "agent type not found" failure was a thrown error, so the run was never finished and stayed in flight. I have not checked how the Workflow tool's `agent()` reports a failure. The spec writer should confirm that before choosing the fix.
- "Any role call that fails" applies to both `intake.js` and `build.js`, because both share the same `runRole` shape. The #24 comment saw it only in `build.js`.
- Part B mainly helps parents already planned by an older runtime, or planned by hand, because part A removes the path that caused the bug. The requester asked for it, and the operator's pre-approval names "build start-up repair", so it stays in scope.
- Part D(b) changes the verifier's prompt block in `docs/design.md`. Under this repo's conventions, that means a `docs/changelog.md` entry and a re-copy of `docs/prompts/07-verifier.md`, which is a protected generated path. `factory/prompts/verifier.md` line 38 changes too. The spec's Risk section must declare both. The pre-approval policy also says "a standards or prompt change still gets the operator's acceptance test before the runtime moves". That holds for part D(b).
- Removing intake's Plan phase changes `README.md` lines 83-85 and 276, and the README's "Maintaining this page" rule requires the update in the same ticket.
- Suggested priority, a suggestion only: high. This bug stalls v3.5 builds with no record of why, and the operator has pre-approved the fix.

Reason: ACCEPT. The intent is clear and every claim I checked holds on this checkout or in the Nanobot store. The operator has pre-approved the spec gate for this issue and placed part D and the orphaned-run fix in scope. No product decision is left open.

Out-of-scope observations:
- Issue #21 part D says dead code is "listed, not fixed" and names intake's Plan phase as its known example. Once this ticket lands, #21's list should drop that item, not record it as still present.
- The planner's output format stays out of scope, as the request says (#13).

STATUS: ACCEPT
CONFIDENCE: high. All four symptoms are confirmed in code or store records, and the scope and gate approval come from the operator. The one open fact is how `agent()` reports a failure, and that only shapes how the fix is built.
ESCALATIONS:
- Protected paths: part D(b) changes a prompt. That touches the design doc's verifier block and the generated copy `docs/prompts/07-verifier.md`, plus the guardrail path `factory/prompts/verifier.md`. The spec's Risk section must declare these paths. Under the pre-approval policy, the operator's acceptance test of the prompt change is still needed before the runtime moves.

## Request (raw)

---
title: "Intake's Plan phase plans without sub-tickets; the build then exits silently"
labels: "harness"
---
**Where:** `factory/workflows/intake.js` Plan phase (runs when the ticket is `ready-for-planner` at launch); `factory/workflows/build.js` start-up on a `planned` parent, and its handling of a `parent-check` refusal.

**Problem:** starting intake on an approved ticket plans it without its sub-tickets, and the build then does nothing, silently. Intake's Plan phase runs the planner, `spec tasks` and `plan add`, then moves the parent to `planned`. It never runs `subticket add`. The build workflow skips its own Plan phase on a parent that is already `planned`. `ready-implementers` then returns nothing, `parent-check` refuses ("<ID> has no sub-tickets"), and the build exits after about 30 s with the parent still `planned`. Nothing is parked and no error is logged.

**Evidence:** Nanobot v3.5 store, 2026-10-04: six parents at once (T-0001, T-0004, T-0007, T-0008, T-0011, T-0012). The Driver ran `subticket add <parent> --run <planner run>` by hand for each, with run ids taken from the `plan.added` log events. The README already calls intake's Plan phase unused ("in practice the build script runs the planner"), and #21 part D lists it as dead code.

**Proposed change:**
- A. Remove intake's Plan phase. Intake ends at the spec gate; the build workflow owns planning. One planner path, no duplicate.
- B. When the build workflow starts on a `planned` parent with no sub-tickets, it runs `subticket add` from the parent's recorded planner run (the `plan.added` event) instead of exiting.
- C. When `parent-check` refuses, the build workflow parks the parent with the refusal as the reason, instead of exiting quietly.

**Out of scope:** the planner's output format (#13).

Reported by the Nanobot v3.5 Driver.


---

**Comment on the issue:**

Part D, added 2026-10-04: the verifier's gate result is misread when written as a heading. This is the second occurrence, and each one cost a full round:
- spec-factory T-0012.5 (run-0073, `## Gate suite: PASS` → ci FAIL "missing Gate suite line");
- Nanobot v3.5 T-0012.1 (run-0052; round 1 → 2 at 06:15:11, and the round-2 implementer and reviewer both escalated it).

Fix:
- (a) the gate-line parser accepts optional leading `#` characters, `*` emphasis and whitespace before `Gate suite:`;
- (b) the verifier prompt pins the exact line format.

Both are kept: the parser stays tolerant to drift, and the prompt states the contract.

---

Operator: spec gate pre-approved ("#33 just do it"; `.factory/answers/queue-preapproval-policy.md`). Part D (gate line read as a heading) is in scope. The orphaned in-flight run on an agent-call failure (comment on #24, 2026-10-04) belongs with part C: any role call that fails records the run KILLED and parks with the error.

## Critic findings on your previous version

## Findings

[BLOCKING] 6 Operator steps, step 1 and step 2
Problem: The operator steps use "runtime", "ci row", "head" and `--accept-harness` with no gloss anywhere in the human-facing sections, so an operator new to this system cannot tell when step 1 is due ("before the runtime moves") or what to compare in it ("the ci row recorded for that head").
Evidence: Read Problem, Evidence, Decisions and Operator steps as the rubric's reader. "Runtime" first appears in Risk ("after the runtime moves to this change"), which is not a human-facing section, and is never defined. "ci row" and "head" appear only in Operator steps step 1 and in Evidence's gate-line bullet (`role: ci, status: FAIL`), neither of which says what a results row or a head is. `--accept-harness` appears once, in step 2, undefined. The writing standard's own rule 2 example is this exact term.
Suggested fix: Open Operator steps with two sentences: "The runtime is the pinned checkout of the harness that runs tickets; a merge into `main` reaches it only when the operator moves it, after which each instance accepts the new revision with `--accept-harness <revision>`. The store keeps one result row per checker for a sub-ticket's latest commit, its head; the ci row is the test-suite verdict read from the verifier's `Gate suite:` line." Then keep the steps as written.

[SHOULD-FIX] 6 Problem, first paragraph
Problem: "store files" and "the Nanobot port" are used before either is introduced; the first is this system's name for its state directory and the second is a project-internal reference (writing standard rule 6).
Evidence: Paragraph 1: "has to dig through store files" and "On the Nanobot port on 2026-10-04 this stalled six approved tickets at once." Paragraph 2 glosses role, run, planner, parent, park and queue, but not store or the port. Not raised as BLOCKING on its own: a technical reader can take "store files" as plain English, and the port is named only as the place the count came from.
Suggested fix: "has to dig through the store, the directory of files where the factory keeps every ticket, run and result" and "On the factory's other instance, the Nanobot repository, this stalled six approved tickets at once on 2026-10-04."

[SHOULD-FIX] 2 specs/harness-docs/spec.md, "The README no longer describes a planning step in intake"
Problem: `grep -c "planning step" README.md` → `0` tests the phrase, not the behaviour; an implementer who rewords lines 83-85 while still describing intake planning passes it, and one who writes the required sentence with the words "planning step" fails it.
Evidence: README line 83 reads "The intake script also contains a planning step, but it only runs when ..."; `grep -c "planning step" README.md` printed `1` today. Design part E asks for "one sentence saying the intake script stops at the spec gate" without naming words the test could check.
Suggested fix: Pin the replacement wording in part E (for example "The intake script stops at the spec gate") and make the scenario check both that sentence's count is `1` and that `intake script also contains` is `0`.

[NIT] 4 Risk, pre-approval paragraph
Problem: The paragraph says the gate is pre-approved under the policy "which names #33", but the policy's #33 entry names only intake Plan removal, build start-up repair and the parent-check park (parts A, B, C1); parts C2 and D ride on the policy's general small-blast-radius rule, not on the #33 line.
Evidence: `.factory/answers/queue-preapproval-policy.md` line 7: "#33 (intake Plan phase removal, build start-up repair, park on parent-check refusal)"; line 6 gives the general rule ("no loosened check, a handful of files, reversible by moving the runtime back"). The request `T-0018.md` does bundle the gate-line part (its lines 26-30), so the scope is the ticket's; only the sentence overstates what the policy names.
Suggested fix: "The policy names #33's parts A, B and C1; C2 and D fall under its small-blast-radius rule (no loosened check, a handful of files, reversible by moving the runtime back)."

## Checks run

- Cited paths and lines: `factory/workflows/intake.js` lines 7, 35, 74-104, 172-189, 191; `factory/workflows/build.js` lines 64-101, 190, 205-213; `factory/cli.py` lines 366-403 (`Path(a.file)` at 381), 480 (the anchored regex), 594 (`has no sub-tickets`), 406-427 (`ready-implementers` keys); `docs/design.md` line 644, `docs/prompts/07-verifier.md` line 37, `factory/prompts/verifier.md` line 38 (step 4 differs from the design block as the spec says; the rest is identical); `README.md` lines 83-85 and 276; `dev/build-harness.spec.md` lines 275, 285, 320; `docs/changelog.md` entry 46 then "Declined:"; `.factory/answers/queue-preapproval-policy.md`. All as cited. HEAD is `429d218`.
- Ran the two gate-line scenarios on today's tree: the four marked forms all gave `FAIL|missing Gate suite line`; the three plain forms gave exactly the three expected lines. The awk block-copy check printed `SAME`. The prompt grep printed `0 0 1` for each of the three files. `grep -c "planning step" README.md` → `1`; `grep -c "heading or emphasis marks" dev/build-harness.spec.md` → `0`.
- Ran three driver scenarios with node v24: "Intake leaves an approved ticket" printed `returned planned`, `ticket T-0001 planned in_flight=0 reason=-`, `run run-0004-planner PLANNED`; "Build creates the missing sub-tickets" printed `returned planned`, no `T-0001.1` line, and grep's "No such file" for `T-0001.1.yaml`; "A failed agent call in intake" printed `threw agent type 'factory-triage' not found`, `ticket T-0001 ready-for-triage in_flight=1 reason=-`, `run run-0001-triage running`. Each NEW item fails today for the reason verification.md states.
- Tests to change: no test under `tests/factory/` reads intake's `meta.phases`, `AGENT_NAME` or the Plan phase; `ready-implementers` tests read `ready` and `resumable` only; `test_coding_standard.py` pins the spec writer, implementer and retro prompts as verbatim copies, not the verifier; existing gate-line fixtures use plain `Gate suite:` lines (`test_shepherd.py` lines 266, 411, 492, 578; `test_results_commit.py` line 22) and still match the proposed regex. "none" holds.
- Decision on `subtickets` key: the existing `ready-implementers` keys cannot distinguish a parent with no sub-tickets from one whose sub-tickets are all merged (merged ids appear in no list), so the new key is needed, not a convenience.
- Scope: four fixes, about 170 lines, one PR; the request bundles all four and the rubric's "lettered part the intent does not need" does not apply.

STATUS: REVISE
CONFIDENCE: high, every cited path and three NEW scenarios were checked by hand on the stated commit; the one BLOCKING is a gloss the operator steps need, not a design defect.
ESCALATIONS: none

## Your previous spec (v1)

=== proposal.md
## Problem

The spec factory runs each ticket (a requested change) through AI agents, driven by two workflow scripts: the intake script (triage, then writing and critiquing a spec) and the build script (planning, building, checking and merging). A human signs off each spec at the spec gate before any code is written. Today both scripts can stop a ticket and leave no record of why. The operator then finds a ticket that has not moved and has to dig through store files to learn what happened. On the Nanobot port on 2026-10-04 this stalled six approved tickets at once.

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
- **The Nanobot store shows the same thing at scale** (from triage, read only): six parents planned on 2026-10-04 with no sub-tickets (T-0001, T-0004, T-0007, T-0008, T-0011, T-0012). The Nanobot Driver session, which runs that port's builds, created them by hand with `subticket add <parent> --run <planner run>`, taking each run id from the parent's `plan.added` log event. `plan.added` is the event the store writes when a plan is recorded, and its `source` field names the planner run.
- **There is no way to create sub-tickets without naming the run.** `bin/factory subticket add T-0001` with neither `--run` nor `--file` printed `factory: TypeError: argument should be a str or an os.PathLike object ... not 'NoneType'` and exited 1. So the command crashes instead of using the plan the store already recorded.
- **A failed agent call orphans its run (intake).** The driver made the triage role's `agent()` call throw `agent type 'factory-triage' not found`. It printed `threw agent type 'factory-triage' not found`, `ticket T-0001 ready-for-triage in_flight=1` and `run run-0001-triage running`. So the script died, the run stayed in flight, and the ticket was not parked.
- **The same happens in the build.** With the implementer's call throwing, the driver printed `ticket T-0001.1 ready-for-implementer in_flight=1 reason=-` and `run run-0005-implementer running`. The build returned `planned` and logged "1 sub-ticket(s) parked or waiting on a human", which was false. This matches the issue #24 comment from 2026-10-04: "left the sub-ticket holding an orphan in-flight run and returned without parking", after "agent type 'factory-implementer' not found".
- **How `agent()` fails.** The Workflow reference says `agent()` returns null when the user skips it or after a terminal API error, and that a thunk which throws inside `parallel()` resolves to null. If the #24 call had returned null, `runRole` would have finished the run as KILLED (`build.js` lines 93-96). The run stayed `running`, so the call threw. `build.js` calls `buildOne` inside `parallel()` (line 210), so the throw was absorbed there and the build carried on. The reference does not say in so many words that an unknown agent type throws. That part is inferred from the #24 symptoms, which the reproduction above matches exactly.
- **Gate line read as a heading.** spec-factory `run-0073-verifier` (T-0012.5), `output.md` line 21, reads `## Gate suite: PASS`. The store logged `result.recorded ... role: ci, status: FAIL` for that run (log line 378), and `results/302f70bb…/ci.yaml` and `results/7090d9d2…/superseded-2/ci.yaml` both hold `detail: missing Gate suite line`. On a scratch store, `results record` gave ci `FAIL|missing Gate suite line` for each of `## Gate suite: PASS`, `**Gate suite:** PASS`, `### **Gate suite: PASS**` and `**Gate suite: FAIL** 2 failed`. Plain `Gate suite: PASS` gave `PASS|`. So any leading mark hides the verdict. The parser is `factory/cli.py` line 480, `re.search(r"^Gate suite:\s*(PASS|FAIL)\b(.*)$", text, re.M)`, which is anchored at the start of the line. The second occurrence was Nanobot v3.5 T-0012.1 (run-0052), as reported in the issue; I did not open that run.
- **The documents already expect this.** `README.md` lines 83-85 say intake's planning step "only runs when a ticket is already past the gate at launch; in practice the build script runs the planner". Line 276 says to start the build script after the gate, "never the intake script (#33)". `dev/build-harness.spec.md` lines 277-281 describe `intake.js` as triage and spec phases only. Removing the phase brings the code in line with the build spec.
- **Baseline gates.** `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `157 passed in 97.42s`. `git diff --check` printed nothing.

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

Blast radius: every intake and build run on both instances after the runtime moves to this change. All changes can be undone by moving the runtime back. Behaviour changes, in brief:
- Intake on a `ready-for-planner` ticket now does nothing.
- A build on a planned parent with no sub-tickets now creates them or parks the parent.
- A thrown agent call now parks instead of orphaning its run.
- More verifier outputs now yield a ci row of PASS. The verdict is unchanged: PASS and FAIL are read from the same word, so no check is loosened. Only lines that start with `#`, `*` or whitespace before `Gate suite:` are newly read.

Protected paths touched, all declared:
- harness `factory/**`: `factory/workflows/intake.js`, `factory/workflows/build.js`, `factory/cli.py`, `factory/prompts/verifier.md`. The last is also a guardrail path, an agent prompt, and the ticket asks for this change to it.
- generated `docs/prompts/**`: `docs/prompts/07-verifier.md`, re-copied verbatim from the design doc's verifier block.

No `.factory/**`, `agents/**`, `bin/factory`, `pyproject.toml`, `uv.lock`, `~/dev/nanobot-upstream/**` or `~/.nanobot/**` path is touched. Existing tests are unchanged. New tests go in a new file.

The spec gate is pre-approved under `.factory/answers/queue-preapproval-policy.md`, which names #33. The same policy says a prompt change still gets the operator's acceptance test before the runtime moves. See Operator steps.

## Operator steps

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
- `README.md` lines 83-85: replace "The intake script also contains a planning step, … the build script runs the planner." with one sentence saying the intake script stops at the spec gate.
- `README.md` line 276: replace "never the intake script (#33)" with a reason that holds after this change, for example "the intake script stops at the gate". Bump the status-header date as "Maintaining this page" requires.
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
The README SHALL no longer describe a planning step in the intake script, the changelog SHALL record the change as entry 47, and the build spec SHALL name the accepted gate line forms.

#### Scenario: The README no longer describes a planning step in intake
- WHEN `grep -c "planning step" README.md`
- THEN it prints `0`

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
- The README no longer describes a planning step in intake → NEW. Today it prints `1` (README line 83).
- The changelog records the change → NEW. Today it prints `0` then `0`: there is no entry 47.
- The build spec names the accepted gate line forms → NEW. Today it prints `0`.
