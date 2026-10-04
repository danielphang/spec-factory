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
