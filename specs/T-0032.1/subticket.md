T-0032.1 / A role that ends its turn while its own background commands are still running returns no output, and the harness records it as a budget kill and parks the ticket
Depends on: none
Parallel-safe: yes

Parent: T-0032, approved spec v1. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows
- One empty reviewer run followed by a real one routes on the real one
- An implementer that returns nothing twice parks as EMPTY-OUTPUT
- An intake role's second empty output in a row parks as EMPTY-OUTPUT
- A reviewer that writes its output runs once
- Every preamble copy carries the wait rule and the copies stay identical
- Implementer, reviewer and verifier run prompts carry the wait rule, and only the reviewer's carries the judge-the-diff rule
- Every reviewer copy carries the rule, keeps every existing line, and the verifier prompt is unchanged
- The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do
- The design doc states the EMPTY-OUTPUT rule, its rows and its park
- The build spec describes EMPTY-OUTPUT and no longer a KILLED condition
- README drops the budget park and describes the empty-output retry
- The changelog records issue 41 without a numbering gap
- The empty-output change adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
