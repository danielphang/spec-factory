# Critic review of T-0056 spec v3 (round 2 of this ticket's critic review)

Per the convergence rule I reviewed only whether my round-1 findings were resolved and the text the v2-to-v3 diff changed. `main` is still `3e4705a`, as the spec says, so the code citations I checked in round 1 stand.

What I checked from `~/dev/spec-factory`, through the briefing's wrapper with a throwaway HOME:
- The seam routing. `factory/cli.py:496` defines `SEAM_HEADING_RE` as `^#{2,3}\s`; `_planner_needed` (`:499-516`) returns a planner reason when the last spec writer run's status is `NEEDS-SPLIT` (`:509-510`) or when a `##`/`###` line outside a fence contains "seam" (`:511-514`), as the spec's Responses describe. `factory/drive.py:291` and `factory/workflows/intake.js:187` both accept `NEEDS-SPLIT` beside `READY-FOR-CRITIC` from the spec writer. The writer's run-0570 output ends `STATUS: NEEDS-SPLIT`.
- The stored spec. `.factory/store/specs/T-0056/v3.md:232` is `### Size and seams (NEEDS-SPLIT, two sub-tickets)`, with 14 fence markers before it, so it sits outside a fence. I ran the harness's own check over v3 (`specstore.lines_outside_fences` with `_planner_needed`'s heading test) and it reports that one seam heading. v2 had none.
- The diff. Beyond the heading and the Responses section, v3 changes only glosses in Evidence (first paragraph, a new "store's event log" bullet, the amendment bullet), Out of scope (the live-store fence), Decisions (first and last bullets) and Risk (the heading's name). No scenario, figure, requirement or seam content changed, as the writer says.
- The human-facing sections, read as the gate operator. Problem's first paragraph says what is wrong (the five north-star numbers cannot be read from the store) and for whom (the operator at the fortnightly review). Evidence's first paragraph now glosses the wrapper, briefing, round, critic and capability; Decisions' first bullet glosses the runner session, the event log and "standing".
- Approved changes not yet archived: none, so rubric 5 raises nothing.
- Not run this round: any acceptance command. Round 1 ran six of the WHENs as written and each matched its "today" line; none of them changed.

## Findings

[SHOULD-FIX] 6 Operator steps, step 1; Decisions, first bullet
Problem: Two terms specific to this system remain unglossed in a first paragraph: "(protected)" after `.factory/instance.yaml` in step 1, and "Answer 2, question 1, option (a)" in Decisions' first bullet.
Evidence: No human-facing section says what a protected path is (a path the harness refuses to let a role change, which only the operator edits) or that an Answer is the operator's written reply to a round's open questions, stored with the ticket. Both are unchanged from v2 and I missed them in round 1. I do not block on them: the operator reading this gate is the person who wrote Answer 2 and configured the protected paths, and the parenthetical "(protected)" can be dropped without changing the step, so the failure does not matter for this spec's reader.
Suggested fix: Write "(a protected path: one the harness refuses to let a role change, so you edit it yourself)" in step 1, and "(Answer 2, your written reply to the last round's open questions, question 1, option (a); …)" in the first Decisions bullet, or drop "(protected)".

## Prior findings
- [BLOCKING] 3, 5 seam marker: RESOLVED. The marker is a `###` heading outside a fence that the harness's seam check finds, and the writer's run ended NEEDS-SPLIT; either alone sends the approved spec to the planner.
- [BLOCKING] 6 unglossed terms in Evidence and Decisions: RESOLVED. Every term I named is glossed at its first use, in the section where it first appears, and the glosses are accurate against the code and store I read in round 1.

STATUS: APPROVE
CONFIDENCE: high, both fixes rest on code I read and on the harness's own seam check run over the stored v3; the rest of the spec is unchanged from the version I verified in round 1
ESCALATIONS: none
