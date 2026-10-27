T-0060.1 / Benchmark the factory against one plain Claude Code session on about 10 upstream Nanobot fix PRs, each scored by that PR's own tests
Depends on: none
Parallel-safe: yes

Parent: T-0060, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A plain session's transcript gives its operator messages, operator time, elapsed time and tokens
- A factory arm's store events and runner session give one operator time
- The benchmark report refuses no input, a missing transcript and a store with no log, and writes nothing
- The suite passes and no existing test file is modified or deleted
- The benchmark page has its eight sections in order
- The benchmark page states its selection, blinding, setup, measures, review and spend rules
- No relative link in the benchmark page is broken
- README names the benchmark page and puts its report in the cost row
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
