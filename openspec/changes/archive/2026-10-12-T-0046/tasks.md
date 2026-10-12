T-0046.1 / De-bloat C: give each operation the harness writes out several times one shared helper, with no change in behaviour
Depends on: none
Parallel-safe: yes

Parent: T-0046, approved spec v3. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- Only the store module lists a ticket's runs
- The CLI and the stats report read the event log through a shared reader
- One function records a status transition outside spec approval
- Neither spec amend nor the dispatcher builds the in-flight list itself
- One function reads the integration-branch tip
- Record copies, row set-asides, planner-run checks and spec apply checks each have one definition
- One line formats a failed-command park and one call cleans up a checker
- Status transitions write the same events and history entries
- Spec pinning and planner-run refusals keep their text
- The dispatcher parks a refused store command with the same reason
- The spec parser gives the same result as the base on every spec in the store
- The refactored harness has no unused imports or variables
- The harness suite passes and no existing test file changes
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
