T-0034.1 / Cut the spec writer's and critic's turn count: batch reads, read line ranges, keep long output in scratch; the critic runs no test suites and builds no prototypes
Depends on: none
Parallel-safe: yes

Parent: T-0034, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- Every spec writer and critic copy carries the turn-economy rules and the critic's no-build rule
- Spec writer and critic run prompts carry the new rules
- Rubric, round limit, format and every other prompt are unchanged
- The changelog and the principles page record the change
- The turn-economy change adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
