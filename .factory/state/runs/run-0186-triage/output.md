Type: feature (prompt change to the planner and spec writer; harness label)

Title: Planner and spec writer: label checks per sub-ticket, and list the tests a sibling or a decision overturns

Summary:
Sub-tickets park for reasons the planner or spec writer could have foreseen. A park is the harness stopping a ticket until a human relabels it or rules on it, and each one costs a full role run. The requester wants three prompt changes so that each sub-ticket's acceptance labels and test permissions are right the first time:
- A. The planner labels each check NEW (must fail before the change) or REGRESSION (must pass before and after) against that sub-ticket's own base, not by copying the parent's label.
- B. The planner lists, under a sub-ticket's "Tests to change", the tests an earlier sibling sub-ticket adds that this sub-ticket will break. The earlier sibling's text marks those tests as interim.
- C. The spec writer lists the existing tests that each behaviour-changing Decision overturns, and the critic checks for omissions.
The requester rules out letting the implementer edit a test on its own judgement.

Evidence:
I checked each claim against the prompts and the run records.

| Claim | What I found |
|---|---|
| Planner copies the parent's label | `docs/design.md:495`, `docs/prompts/04-planner.md:33`, `factory/prompts/planner.md:33` and the runtime copy all say intermediate checks are "labelled NEW or REGRESSION the same way". No text mentions the sub-ticket's own base. |
| Planner may only take a subset of the parent's tests | Same three files, line 34 (design.md:496): "Tests to change: none \| the subset of the parent's list this one touches". |
| Spec writer has no rule for tests a Decision overturns | `docs/design.md:362` says only "existing tests the intended change breaks, and why". Critic rubric 3 (`docs/design.md:399`) checks that listed tests are really broken. It does not check for missing ones. |
| T-0012.2, .5 and .6 parked as SPEC-DEFECT; T-0012.4 BLOCKED | `.factory/state/tickets/T-0012.{2,5,6}.yaml` each have `reason: SPEC-DEFECT from verifier`. `T-0012.4.yaml:26` has `reason: BLOCKED from implementer`. |
| Nanobot T-0002.5 blocked on T-0002.4's interim tests | `~/dev/nanobot-upstream/.factory/state/runs/run-0147-implementer/output.md:87`: "The 8 failures are the T-0002.4 tests that pin the old "not yet available" behaviour, and they passed on the base." |
| Nanobot T-0002.2 blocked on a test that D22 overturns | `run-0129-implementer/output.md:102`. Line 136 of `test_interactive_agent_routes_a_complete_user_turn` asserts that the CLI's metadata is exactly `{"_wants_stream": True}`. D22 (the CLI marker) adds `_local_cli: True`, "so no correct implementation of D22 passes this assertion unchanged." |

The request names no Nanobot-side commit, and Nanobot carries only `.factory/`. So no as-built fix exists to check. I did not verify the T-0014 and T-0015 relabels or T-0012.4's "four vacuous NEW checks".

No duplicate exists. This is issue #40 (`dev/issues.md:49`, "not in intake"), filed as T-0022. #36/T-0019 part D changed the planner's field-line format, which does not overlap. No other request or spec mentions per-sub-ticket labels or interim tests.

Assumptions:
- (Assumption) Parts A and C change no authority. Under A the planner labels its own checks, as it does now. Under C the human still approves the "Tests to change" list at the spec gate. The queue policy (`.factory/answers/queue-preapproval-policy.md`) pre-approves "per-sub-ticket NEW/REGRESSION labels" by name. It does not name B or C.
- (Assumption) "The integration branch with its dependencies merged" means the base the harness gives the sub-ticket's worktree.
- (Assumption) The requester's acceptance, a re-plan and re-spec of Nanobot T-0002 that the operator reviews side by side, is an Operator step, not a runnable Acceptance item. The spec writer will need runnable criteria as well, such as greps of the new prompt text across `docs/design.md`, `docs/prompts/` and `factory/prompts/`. Running the planner against Nanobot's store would need a throwaway copy, because `~/dev/nanobot-upstream/**` is a protected path.
- Suggested priority (a suggestion only): p1. Each avoided park saves a full role run, and T-0002 is the v3.5 port's live ticket.

Question for human:
Part B changes who may authorize a test edit. Today the human-approved spec's "Tests to change" is "the only authorization to alter an existing test" (`docs/design.md:142`). The planner may only take a subset of that list. No human sees the plan before sub-tickets dispatch. The implementer and reviewer for a sub-ticket read both its plan text and the pinned parent spec (`factory/compose.py:175-176`, `192-193`). As far as I can tell, no harness code enforces "Tests to change" (a grep for it under `factory/`, outside `prompts/`, returns nothing). The rule is held only by those roles' prompts. Under B, a planner-written list would authorize changing tests that a human never approved. The request itself treats letting an agent edit a test on its own judgement as loosening a guardrail. Which rule should B follow?

1. **The planner's list is enough, for sibling tests only.** A sub-ticket's "Tests to change" may also name tests that an earlier sibling of the same parent added, and only those. Line 142 is amended to say so. This is the cheapest option, but an agent authorizes the edit and no human sees it. That arguably falls outside the queue policy's "no loosened check".
2. **The planner lists them and a human still approves them.** Any test the plan adds beyond the parent's list goes to the operator once, before dispatch: one approval for the plan, not one park per sub-ticket. Authority stays with the human. This adds a gate step that does not exist today.
3. **No interim tests in committed files.** The planner checks a sibling's interim behaviour only with that sub-ticket's acceptance commands. It never plans a committed test that a later sibling must break. Authority does not change. This narrows how the planner may plan, and may not fit every split.

Is the answer a standing decision that later tickets must follow? It sets who may authorize a test edit after the spec gate, so I expect yes.

STATUS: NEEDS-HUMAN
CONFIDENCE: high. Every prompt line and park cited above was read in the files. The only open point is the authority question in B, which the queue policy does not cover.
ESCALATIONS: Part B would move authority over existing-test edits from the spec gate to the planner, which runs after the gate. The queue policy pre-approves part A only. B needs the operator's ruling (question above) before it is specced as pre-approved.
