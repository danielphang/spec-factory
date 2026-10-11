T-0041.1 / Spec drift check parks a sub-ticket for its own sibling's merge; no resolve route back from a harness-bug park before the first implementer run
Depends on: none
Parallel-safe: yes

Parent: T-0041, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges
- A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start
- A merged sibling's merge is not drift, and a later commit or merge from elsewhere still is
- A ruling on a harness-bug park from an implementer's run start returns the sub-ticket, and its implementer then starts
- A ruling on a checker's or a compose step's harness-bug park is still refused
- The design doc, build spec, README and changelog record both changes, and no prompt copy changes
- The sibling-merge change adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
