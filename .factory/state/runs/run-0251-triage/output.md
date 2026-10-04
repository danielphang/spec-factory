Type: feature

Title: Small-change lane: skip a gate command when the diff touches none of its declared paths, and skip the planner for a spec that fits one sub-ticket

Summary:
Every ticket goes through the whole pipeline, however small it is. The operator wants work that cannot change a verdict removed. This was pre-approved on 2026-10-04, provided every refusal the pipeline gives today still fires. The requester asks for two changes. (A) A gate command is one of the repository's own checks that the verifier runs on every branch, such as the test suite. Each gate command may declare the paths it covers. When a sub-ticket's diff touches none of them, the command is recorded as SKIPPED with the reason, and the merge still needs every command that did run to PASS. A command with no declared paths always runs. (B) The planner is the agent that splits an approved spec into sub-tickets. When a spec needs only one sub-ticket, the build creates that sub-ticket directly from the spec, records that the planner was skipped, and moves on. Part C (a parent with one sub-ticket closes on that sub-ticket's verified run) already shipped and needs no work.

Evidence:
- Request: T-0014 added about 140 lines of prose to `docs/writing.md` and still ran the full suite at every stage. T-0013 and T-0015 each paid a planner run that produced one sub-ticket.
- Planner cost, from the run log `.factory/state/log/2026-10.jsonl` (`run.finished` events, `wall_s`). All nine recent parents that got one sub-ticket paid a planner run: T-0013 118 s, T-0014 72 s, T-0015 139 s, T-0016 162 s, T-0017 185 s, T-0018 302 s, T-0020 183 s, T-0021 138 s, T-0024 95 s. This matches the request's "about 2 to 5 min", with 72 s at the low end.
- Part C is already live. `factory/workflows/build.js` phase 3 skips the parent-close verifier when `ticket parent-check` returns `reuse`. The tests are in `tests/factory/test_parent_close_reuse.py`. Both came from T-0016 (issue #31).
- Today the gate commands are a flat list with no path field. `.factory/instance.yaml:22-24` lists `git diff --check main...HEAD` and the pytest suite. `factory/compose.py:44-51` reads them as strings.
- Operator decision: `.factory/answers/operator-decisions-2026-10-04.md` files this request as #48, "pre-approved". The standing decision is recorded in `.factory/state/decisions.md:30`.

Assumptions (my inferences, not stated by the requester):
1. Part A overturns an earlier decision, and the spec should say so. T-0016's spec cut this exact skip in its Decisions (`.factory/state/specs/T-0016.md:70`). The reason given: a path list that misses one file the suite reads drops a refusal without warning. The requester knows this ("as #31's analysis found"), and the operator has pre-approved the work. I take that as deliberately reversing the cut, not as a duplicate. The spec writer should record it as an overturned decision.
2. The requester's path list for this repository is a suggestion, not a requirement. The requirement is that every refusal still fires. The suggested list (`factory/**`, `bin/factory`, `tests/**`, `agents/**`, `docs/**`, `pyproject.toml`, `uv.lock`) leaves out at least one file that a test outcome depends on: `.gitignore`. The suite clones the whole checkout (`tests/factory/test_harness_lock.py:108-114`). One test then relies on that clone ignoring `__pycache__/` (`tests/factory/test_harness_lock.py:260-268`). So a diff that only removed `__pycache__/` from `.gitignore` would skip the suite under the suggested list, even though the suite would fail on it. The spec writer should build the list from what the suite actually reads.
3. The trigger for part B is a suggestion, and as worded it misses most of the cases the request cites. "Exactly one lettered part" held for only one of the nine one-sub-ticket parents above: T-0015. T-0013 had six lettered parts, A to F, so the request is wrong to call it a one-part spec. The others had two to six. The cause is the spec-writer prompt, which asks for every Proposed change as lettered parts (`factory/prompts/spec_writer.md:81`). Records and tests therefore get letters of their own. With the trigger as written, part B would have skipped about 2 minutes in one build out of nine. I assume the requester wants the saving the evidence describes. The spec writer should choose a trigger that matches the one-sub-ticket cases, state it in Decisions, and give the saving it would have made on those nine builds. The operator then confirms the choice at the spec gate. If the spec writer keeps the literal trigger, the spec should say how small the saving is.
4. Skipping the planner must not lose a refusal the planner gives today. The planner has returned ESCALATE three times: `run-0030`, `run-0031` and `run-0032`. Each time the approved spec was already applied on `main`, or its acceptance criteria contradicted `main`. It also checks the plan's format through the `spec tasks`, `plan add` and `subticket add` steps (`factory/workflows/build.js:205-216`). The spec must show where each of these refusals still fires when the planner is skipped. One candidate is the verifier's base run of NEW checks, which catches a spec that is already applied. If one of them would no longer fire, the standing decision does not cover that part.

Acceptance (from the request, restated as behaviour):
- Given a gate command that declares its paths, when the verifier checks a sub-ticket whose diff touches none of those paths, then the command is recorded as SKIPPED with its reason, and the merge still needs PASS from every command that ran.
- Given a gate command that declares no paths, when any sub-ticket is checked, then the command runs, as it does today.
- Given an approved spec that needs one sub-ticket, when it is built, then an implementer starts without a planner run, and the store records that the planner was skipped.
- Given an approved spec with two or more parts that need separate sub-tickets, when it is built, then the planner runs, as it does today.
- Every refusal listed under "Kept" in the request still fires. The checks labelled NEW still run on the base commit and on the head. REGRESSION checks and gate commands that are not skipped still run on the head. Both checkers still run. The merge still needs CI PASS, APPROVE and VERIFIED on the current head. Approvals for protected paths still apply.
- Timing: the next build that qualifies is compared against T-0014's and T-0015's numbers.

Priority (suggestion only): high. The operator's note says efficiency work goes first, and this is the efficiency ticket that is ready to go.

Question for human / Missing info / Reason: none needed to proceed. Assumptions 2 to 4 are for the spec writer to resolve in the spec, and the operator sees them at the spec gate.

Out-of-scope observations:
- T-0022 (issue #40: per-sub-ticket check labels and a harness check on tests added by a sibling sub-ticket) changes the planner's output and the harness checks on that output. T-0027 (issue #44: amending a spec after it is planned) adds a re-plan path. Part B goes around the planner, so the spec writer should check both of them for overlap in `factory/workflows/build.js` and the `plan`/`subticket` commands, and order the tickets if needed.
- Every time a ticket is created, the request-source path in the ticket records points into a session scratchpad (`source:` in `.factory/state/tickets/T-0028.yaml`). That directory is temporary.

STATUS: ACCEPT
CONFIDENCE: medium. The intent and the operator's pre-approval are clear. But the requester's suggested path list and part B trigger do not fully deliver the stated goal, so the spec must resolve both.
ESCALATIONS: none
