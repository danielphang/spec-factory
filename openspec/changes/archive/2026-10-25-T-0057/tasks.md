T-0057.1 / Check a spec's format when the spec is added, and send a format error back to the spec writer instead of to the human gate
Depends on: none
Parallel-safe: yes

Parent: T-0057, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one
- approve-spec still refuses a malformed spec
- A store without current truth stores a malformed spec as before
- A spec writer's NEEDS-HUMAN draft is stored even when malformed
- A refused draft goes back to the spec writer and the next well-formed one reaches the critic, in the driver and the script
- A refusal in the last round parks with the refusal, quoted safely, in the driver and the script
- The spec writer's next run receives the refusal and its refused output
- README, the design doc and the changelog describe the refusal route
- The suite passes, only the two listed test files change, and every added test file fails on the base
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
