T-0044.1 / De-bloat A: delete dead code, redundant lines and stale docstrings in the harness
Depends on: none
Parallel-safe: yes

Parent: T-0044, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- The four dead definitions are gone and nothing names them
- No harness or test file names the force-push setting
- Run start carries one intake-and-implementer in-flight refusal, no rename and one store-ignore write
- No harness module has three blank lines in a row
- The three stale texts are gone
- The repo-root helper takes no argument and every caller passes none
- The harness has no unused imports or variables
- The harness suite passes, and only the force-push test lines change under tests
- A second intake run on a ticket is refused with the same text
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
