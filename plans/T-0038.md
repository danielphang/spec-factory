T-0038.1 / After a re-spec and re-plan, a sub-ticket from the old plan keeps parking the parent: sub-tickets should record which plan they belong to, and only the current plan's sub-tickets should count
Depends on: none
Parallel-safe: yes

Parent: T-0038, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept
- The plan a sub-ticket belongs to does not move with its spec record, and a record without it falls back to its creation version
- A second plan at the same approved version supersedes nothing
- A plan that depends on an old unmerged sub-ticket is refused and writes nothing
- A re-specced parent's planner input names the sub-tickets its plan supersedes
- The build of a re-planned parent dispatches the new sub-ticket instead of parking on the old one
- A sub-ticket of the current plan that a human closed still parks the parent
- With the new plan merged, the re-planned parent reaches its final check and closes
- A re-plan sends a parent whose sub-tickets all merged back to its planner with the note and the sub-ticket list
- A re-plan is refused while a sub-ticket is not merged
- A re-planned parent whose final check failed can be re-planned again past its superseded sub-tickets
- The design doc, build spec, README and changelog record superseded plans
- The superseded-plan change leaves prompts, workflows and agents alone and adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
