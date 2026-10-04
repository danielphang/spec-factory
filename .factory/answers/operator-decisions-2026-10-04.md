# Operator decisions, 2026-10-04 (on the efficiency ledger and the decisions page)

"approve everything - file the missed ideas too, pre-approved. slashing clearly redundant work is always going to be OK, if we trust our process"

Taken as the Green session's recommendations:
- #40: option 1 (planner may approve sibling-added tests, harness-checked). Logged in decisions.md; T-0022 resumed.
- #44: approve parts A (spec amend, human-only, logged) and B (critic cross-ticket check) as one ticket, pre-approved.
- #24 A + C: schedule after the current small fixes (#46, #47, #41, #28, #27, #29); the clerk (B) stays deferred.
- #37: start the sandbox investigation after #45 and #46 are live.
- Missed ideas filed, pre-approved: #48 (small-change lane), #49 (duplicate protected-path notices).
- Retro proposal "take recommended defaults instead of parking": no; keep the stops.
- #22: keep parked; fold into #24 A.
- Standing decision (decisions.md): removing clearly redundant work is pre-approved provided every refusal the pipeline gives today still fires.

## Operator's pasted choices (decisions page), later the same day
- #40: option 1 (confirmed).
- #44: A and B as one ticket (confirmed). Operator question: should we judge whether to interrupt and restart rather than amend (an expensive build), and what triggers a change request? Green session's answer: add an intent classification to `spec amend`. An intent-unchanged amendment (setup, precondition, wording) is amended in place. An intent change is refused and goes to re-plan or re-file, with a note of what is merged and what a restart discards. Proposed as a follow-up issue, pending the operator.
- #24 A + C: schedule after the current small fixes (#41, #28, #27, #29). This supersedes the Green session's earlier move of #24 ahead of them.
- #37: not yet. Operator's framing: the simplest fix is separating the deployment environment from development (a separate macOS user or a separate machine); the leaks happen because the live bot and development share a machine.
- Missed ideas: file both (done: #48, #49).
- Retro proposal: no, keep the stops (confirmed).
- #22: keep parked; fold into #24 A (confirmed).
