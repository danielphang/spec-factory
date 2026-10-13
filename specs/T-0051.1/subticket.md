T-0051.1 / Get one harness-suite run well under the 10-minute tool-call cap, and name a background wait in the EMPTY-OUTPUT park reason (spec-factory #106)
Depends on: none
Parallel-safe: yes

Parent: T-0051, approved spec v3. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- One suite run passes in under three minutes
- Two suite runs at once each pass in under five minutes
- Four stand-ins of one role started together all reply, 200 times over
- No test is removed and only the two listed assertions change
- The gate's suite command, as the instance lists it, passes in under three minutes
- A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows
- One empty reviewer run followed by a real one routes on the real one
- An implementer that returns nothing twice parks as EMPTY-OUTPUT
- An intake role's second empty output in a row parks as EMPTY-OUTPUT
- An intake role that ends waiting twice parks with the waiting reason, in the driver and the script
- A build checker that ends waiting twice parks with the waiting reason, in the driver and the script
- A role whose last message is not about waiting parks with the plain reason
- The design doc and build spec name the waiting park reason, and no prompt copy changes
- The README names pytest-xdist and the waiting reason
- The changelog records issue 106 as its last entry, without a numbering gap
- The parallel-suite change adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
