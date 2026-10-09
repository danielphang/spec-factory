T-0037.1 / Send the whole decision log to the spec writer, critic and planner again, removing #75's decision filter (#75 follow-up)
Depends on: none
Parallel-safe: yes

Parent: T-0037, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- With a Capabilities line every decision line reaches the writer, critic and planner, and no decision index does
- The capabilities each role receives and triage's input are unchanged by the whole log
- The harness suite passes with the whole decision log
- The design, README and changelog describe the whole decision log and no decision index
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
