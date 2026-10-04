# Spec-gate pre-approval for the harness-fix queue (operator, 2026-10-04)

Operator, in the Green session: "pre-approve if you tell me the blast radius pretty small"; then, for #33: "just do it, tell Driver, if there are issues then we pause and try to fix it, unless there is a hard decision to make."

Policy:
- Small blast radius = no routing, gate or merge-rule change, no loosened check, a handful of files, reversible by moving the runtime back. The Green session approves these at the spec gate on the critic's APPROVE and reports a one-line blast radius.
- Pre-approved now: #32 (decisions log), #33 (intake Plan phase removal, build start-up repair, park on parent-check refusal), the planner fixes (per-sub-ticket NEW/REGRESSION labels, ID line format), the small items of the hygiene batch.
- Waits for the operator: #24 part A (typed agents for every role), and the hygiene batch's "store commits move main" design change.
- On trouble: pause and fix it; stop for the operator only on a hard decision.
- Unchanged: the runtime moves only between the Driver's builds; a standards or prompt change still gets the operator's acceptance test before the runtime moves.
