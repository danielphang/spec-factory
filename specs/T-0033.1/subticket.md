T-0033.1 / Merge gate merges protected-path changes the approved spec never declared, and the reviewer prompt promises a check the gate does not run
Depends on: none
Parallel-safe: yes

Parent: T-0033, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- An undeclared protected path is refused at merge, by name, and nothing merges
- Another ticket's declaration, a protected file moved away, or a Risk line in another form authorizes nothing
- A declared protected path, or an unprotected one, merges with no further approval
- The build parks a merge refused for protected paths with the gate's reason
- Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through
- Accepting paths is refused on any other park and writes nothing
- A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling
- A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling
- All three run prompts keep the undeclared-path rule and the reviewer keeps check 6
- The reviewer run prompt says what the merge gate checks
- Every reviewer prompt copy states what the merge gate checks
- Every spec writer prompt copy gives the declaration line
- The design doc and build spec drop the per-PR approval for protected paths
- The changelog records issue 57's change without a numbering gap
- README describes the protected-path check and the new resolve verb
- The protected-path change adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
