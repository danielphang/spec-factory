T-0053.1 / Add `docs/standards.md`, the operator's writing and design standards in one self-contained file, point to it from README, and stop `docs/north-star.md` naming the private port (spec-factory #110)
Depends on: none
Parallel-safe: yes

Parent: T-0053, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- The standards file holds the approved text
- Where things live names the standards file
- Nothing a role reads names the standards file
- The north-star sentence names a port of the Nanobot chat bot
- The changelog records issue 110 in one entry without a numbering gap
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
