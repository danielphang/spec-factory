Type: feature (prompt changes to the planner, spec writer and critic, plus one new harness check; harness label)

Title: Planner and spec writer: label checks per sub-ticket, and list the tests a sibling or a decision overturns, with a harness check on sibling tests

Summary:
Sub-tickets park for reasons the planner or spec writer could have foreseen. A park is the harness stopping a ticket until a human relabels it or rules on it, and each one costs a full role run. A sub-ticket is one piece of a parent ticket that the planner splits out; siblings are the other pieces of the same parent. The requester wants each sub-ticket's acceptance labels and test permissions right the first time:
- A. The planner labels each check NEW (must fail before the change) or REGRESSION (must pass before and after) against that sub-ticket's own base, not by copying the parent's label. A check that an earlier sibling already made true is REGRESSION.
- B. The planner lists, under a sub-ticket's "Tests to change", the tests an earlier sibling of the same parent added that this sub-ticket will break, with the reason. The earlier sibling's text marks those tests as interim. Per the operator's answer, this list may name sibling-added tests only. The harness checks each one: it must first appear in a sibling's merge into the integration branch since the parent's base. If it does not, the sub-ticket parks for the operator, as today. Tests that existed before the parent's approved spec still need that spec's "Tests to change".
- C. The spec writer lists the existing tests that each behaviour-changing Decision overturns, naming the decision. The critic checks for omissions, grounded.
The requester rules out letting the implementer edit a test on its own judgement.

Evidence:
The previous triage output checked each claim in the files. I re-read the cited prompt lines on today's `main` (`0b1abad`). The lines have moved since that output, but the text has not changed:

| Claim | What I found |
|---|---|
| The planner copies the parent's label | `docs/design.md:509`, `docs/prompts/04-planner.md:33` and `factory/prompts/planner.md:33` say "labelled NEW or REGRESSION the same way". |
| The planner may only take a subset of the parent's tests | `docs/design.md:510` and line 34 of both prompt copies say "Tests to change: none \| the subset of the parent's list this one touches". |
| Only the spec gate authorizes a test edit | `docs/design.md:146`: the approved "Tests to change" list "is the only authorization to alter an existing test". `docs/design.md:46` (piece 8, the merge gate's guardrail rule) says the same for the merge gate. |
| The spec writer has no rule for tests a Decision overturns | `docs/design.md:376`: "existing tests the intended change breaks, and why". `docs/design.md:413`, the critic rubric: listed tests must be "genuinely" broken. Nothing checks for missing ones. |
| No harness code enforces "Tests to change" today | `grep -rn "Tests to change\|tests_to_change\|diff-filter" factory bin`, with `factory/prompts/` filtered out, printed nothing. So B's harness check is new code, not a change to an existing check. |
| The data B's check needs is already recorded | A parent ticket records `parent_base` (`T-0024.yaml:118`). Each merged sub-ticket records `merge.base_before` and `merge.main_after` (`T-0024.1.yaml:43-44`). So the check can tell which sibling's merge added a given test. |
| T-0012.2, .5 and .6 parked as SPEC-DEFECT; T-0012.4 BLOCKED; Nanobot T-0002.5 and T-0002.2 BLOCKED | Verified in the previous output, from the ticket files and the Nanobot run records `run-0147-implementer/output.md:87` and `run-0129-implementer/output.md:102`. |

The operator's answer: `.factory/answers/operator-decisions-2026-10-04.md:6` ("#40: option 1 … harness-checked"). It is logged as a standing decision at `.factory/state/decisions.md:31`. The spec gate is pre-approved (request footer; `.factory/answers/queue-preapproval-policy.md`).

No duplicate. This is issue #40 (`dev/issues.md:47`), ticket T-0022. T-0027 (issue #44) is related but distinct. Its part B is a critic check for scenarios that depend on another ticket's unmerged decision. It calls itself "the same class as #40" applied across tickets. Part C here covers existing tests within one ticket's own decisions.

The request names no Nanobot-side commit. Nanobot carries only `.factory/`, so there is no as-built fix to check. I did not verify the T-0014 and T-0015 relabels or T-0012.4's "four vacuous NEW checks".

Assumptions:
- (Assumption) "Sibling" means a sub-ticket of the same parent that merged before this one. The check uses the parent's `parent_base` and the siblings' recorded merge ranges, as the operator's answer describes. The spec writer decides where the check runs: at dispatch, at the merge gate, or both. The answer says only that a failure parks the sub-ticket.
- (Assumption) Part B amends `docs/design.md:146` and the piece-8 row at line 46. Those lines say the spec gate is the only authority for a test edit, and they would be wrong after B. The README's current-state page changes too if a new stop or park reason appears.
- (Assumption) The change touches protected harness paths: `factory/**` for the check and `factory/prompts/`, and `docs/prompts/**` (generated). The spec's Risk section must declare them.
- (Assumption) The requester's acceptance is an Operator step, not a runnable Acceptance item. It asks for a re-plan and re-spec of Nanobot T-0002 that the operator reviews side by side before the runtime moves. Running the planner against Nanobot's store needs a throwaway copy, because `~/dev/nanobot-upstream/**` is protected. Runnable criteria will also be needed: greps of the new prompt text across the three copies, and harness tests showing that the new check accepts a sibling-added test and parks on a pre-existing one.
- Suggested priority (a suggestion only): p1. Each avoided park saves a full role run, and T-0002 is the v3.5 port's live ticket.

Reason: the operator answered the one open question, which was who may authorize a sibling-test edit. They chose option 1: the planner may list sibling-added tests, the harness checks them, and pre-existing tests still need the approved spec. The intent is now clear and no other product decision is open.

Out-of-scope observations:
- Line numbers in the previous triage output (design.md 142, 362, 399, 495-496) are stale on today's `main`. The table above gives the current ones.

STATUS: ACCEPT
CONFIDENCE: high. Every prompt line, the operator's answer and the logged decision were read in the files today. The only inference is where the new harness check runs, which is left to the spec writer.
ESCALATIONS: none
