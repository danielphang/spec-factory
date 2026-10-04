## Findings

No blocking issues. No new findings on changed text.

## Prior findings (round 1)

- [BLOCKING] 6 Operator steps gloss: RESOLVED. Operator steps now opens with a paragraph that defines the runtime (the pinned checkout that runs tickets, moved only by the operator), `--accept-harness <revision>` (each instance refuses to run until it accepts), the head (a sub-ticket's latest commit) and the ci row (the test-suite verdict read from the `Gate suite:` line). Risk glosses the runtime at its first use, and the Evidence gate-line bullet glosses result rows and the ci row before quoting `role: ci, status: FAIL`. Read all five human-facing sections again as the rubric's reader: every system-specific term is now glossed before or at first use.
- [SHOULD-FIX] 6 Problem paragraph 1: RESOLVED. "the store, the directory of files where the factory keeps every ticket, run and result" and "On the factory's other instance, the Nanobot repository, ..." are in place; the Evidence bullet says "that instance's builds".
- [SHOULD-FIX] 2 README scenario: RESOLVED. Design part E pins the exact replacement sentence and the line-276 replacement. The renamed scenario checks the pinned sentence count and `intake script also contains`. Ran it on `429d218`: `grep -cF 'The intake script stops at the spec gate; the build script runs the planner.' README.md` → `0`; `grep -c 'intake script also contains' README.md` → `1`. The scenario is NEW for the reason verification.md states, and an implementer who keeps describing intake planning in other words now fails the first grep, not the second.
- [NIT] 4 Risk pre-approval sentence: RESOLVED. The new sentence matches `.factory/answers/queue-preapproval-policy.md`: the "Pre-approved now" line names #33 as "intake Plan phase removal, build start-up repair, park on parent-check refusal" (parts A, B, C1), and the first "Policy:" bullet gives the small-blast-radius rule in the words the spec quotes. The policy's last bullet ("a standards or prompt change still gets the operator's acceptance test before the runtime moves") matches Operator step 1.

## Checks run this round

- Changed text only: Problem paragraph 1, Evidence gate-line bullet and the "that instance's builds" bullet, Risk (runtime gloss, pre-approval sentence), Operator steps opening paragraph, design.md part E, harness-docs README scenario, verification.md README line. Everything else is byte-identical to v1 and was reviewed in round 1.
- `README.md` lines 83-85 still read "The intake script also contains a planning step, but it only runs when a ticket is already past the gate at launch; in practice the build script runs the planner." and line 276 "Start the build script after the spec gate, never the intake script (#33)." — the two sentences part E replaces, quoted correctly. README line 9 status header reads `2026-10-04`, as part E says. README "Maintaining this page" asks for the date bump and for issue numbers to sit in "Related work and history", not the body; part E's line-276 replacement follows both.
- HEAD is `429d218`, as the Evidence states; the working tree's only changes are under `.factory/state/`.

STATUS: APPROVE
CONFIDENCE: high, all four round-1 findings are fixed as described, each checked against the file or command it concerns; the unchanged parts were verified by hand in round 1 on the same commit.
ESCALATIONS: none
