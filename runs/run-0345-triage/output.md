Type: bug

Title: After a re-spec and re-plan, a sub-ticket from the old plan keeps parking the parent: sub-tickets should record which plan they belong to, and only the current plan's sub-tickets should count

Summary:
A sub-ticket is one piece of a ticket's work, built and merged on its own; the planner is the agent that splits an approved spec into sub-tickets. When an approved and planned ticket is sent back, re-specced and approved again, its old sub-tickets stay attached to it. The re-plan's new sub-tickets take the next free ids. The build then still counts the old ones. A sub-ticket from the old plan that a human closed parks the parent with "sub-ticket closed by a human" (to park is to stop the ticket and hand it to a human), and there is no route that resumes the build. The design already says this case should work: `docs/design.md:109` says a sub-ticket closed by the human parks the parent, and "the human amends the spec and re-plans (new sub-tickets under the same parent)". The requester needs each sub-ticket to record the plan it belongs to, so that sub-tickets from a superseded plan never block the new one. Merged work from the old plan must stay merged.

Evidence:
- The request's report: on Nanobot v3.5, T-0024 (SPEC-11), 2026-10-08, reported by the Driver. The ticket was planned once and got T-0024.1. It was sent back, the build stopped, and T-0024.1 was closed by hand with no commits. It was re-specced and approved at v4, and the new planner created T-0024.2. The build parked the parent: "sub-ticket closed by a human: T-0024.1".
- I read the Nanobot store read-only (`~/dev/nanobot-upstream/.factory/store`) and it matches. Log lines 1732-1753 show the re-approval, `run-0332-planner` PLANNED, then `ticket.parked ... "reason": "sub-ticket closed by a human: T-0024.1"`. `tickets/superseded/T-0024.1.yaml` has `status: closed` with `spec.version: 2`. `tickets/T-0024.2.yaml` has `spec.version: 4`. Decision line 254 of `decisions.md` and log line 1781 record the hand stand-in from the request's comment: the file was moved and T-0024 set back to `planned`. No harness fix exists on the Nanobot side; only that stand-in was applied.
- The stand-in works only because the lookup ignores subdirectories. `factory/store.py:228-235` (`subtickets_of`) globs `tickets/<parent>.*.yaml` and returns every match.
- `factory/cli.py:570` (`ticket ready-implementers`) reports every closed sub-ticket in `closed`. `factory/workflows/build.js:264` parks the parent whenever `closed` is non-empty.
- No route resumes the parent. In `.factory/instance.yaml:61` the `parked` row has no `planned` edge. `resolve --replan` (`factory/cli.py:908-921`) refuses unless every sub-ticket is merged, so a closed old sub-ticket blocks that route as well.
- Other callers of `subtickets_of` would also count old sub-tickets: `ticket parent-check` (`factory/cli.py:738-745`) needs all of them merged; the merge sibling-test check (`factory/cli.py:255`); the parent-close guard in `archive_cmd` (`factory/cli.py:1365`); and the planner's input listing (`factory/compose.py:318-322`).
- The request's comment: `ticket set` refuses unknown keys, so a stand-in cannot be annotated on the ticket. The Driver asks for supersession to be a real field.
- Duplicate search: there is no duplicate. T-0027 (#44, "Amend a pinned spec after planning", approved v2, ready-for-planner) adds `factory spec amend`. It does not mark old-plan sub-tickets superseded. #50 is not in intake. Index row: `dev/issues.md:82`. Issue: https://github.com/danielphang/spec-factory/issues/77

Assumptions:
- (Inference) The requirement is the behaviour in the Summary. Proposed changes A-E (a `planned_from` field, a separate `superseded` list, marking at re-plan time, the legacy default, the tests) are the requester's suggestions for the spec writer to weigh, not fixed requirements.
- (Inference) Sub-tickets already carry the parent's spec version from when they were created (`factory/cli.py:478`, `st["spec"] = {"version": parent["spec"]["version"], ...}`). On T-0024 this already tells the two plans apart (v2 and v4). But approved T-0027 (#44) moves every unmerged, unclosed sub-ticket's `spec` record to the amended version (its spec v2, Decisions line 66). After #44 that field would no longer show which plan a sub-ticket came from. So the spec writer must either add a field that never moves, as the request proposes, or settle how this interacts with #44. A NEW acceptance check for this must fail on today's checkout. A check that only reads the existing `spec.version` could already pass and would prove nothing.
- (Inference) "Superseded" applies to unmerged sub-tickets from an earlier approved version, whether closed, parked or never started. Merged ones stay merged and count as done work (point D).
- Suggested priority (a suggestion; priority is a human call): high, and sequenced with #44 as the request asks ("Build together with #44, or before it"). Any ticket re-specced after planning hits this, and T-0024 is running on a hand stand-in.

Question for human / Missing info / Reason: none. The intent is clear and the design doc already states the intended behaviour (`docs/design.md:109`). How to sequence this with #44 (T-0027) is a planning call for the operator, flagged above.

STATUS: ACCEPT
CONFIDENCE: high. The failure is reproduced in the Nanobot store's log and records, and every code path the request names was read on this checkout.
ESCALATIONS: none
