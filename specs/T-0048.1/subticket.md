T-0048.1 / Shrink the maintained documents: freeze the three `dev/` build documents as history, fix README's stale "not yet run" claims, describe each mechanism once in README, move history to the changelog, and update the `harness-docs` current truth to match
Depends on: none
Parallel-safe: yes

Parent: T-0048, approved spec v1. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- The changelog records the change in order
- The README describes the new resolve verbs
- The README says relative paths resolve from the caller's directory
- The changelog records the guard in one entry
- The design doc names the marker and the run-directory rule
- README tells the operator how to write during a run, first thing under Where a human decides
- README says the final verifier run is listed as in flight
- README no longer says the factory's capabilities never entered the spec store
- The design doc names the store branch and the path rule
- The changelog records the store branch in one contiguous entry
- The README describes the store branch and the move
- The design doc describes the check
- The changelog records issue 40's change without a numbering gap
- README describes the sibling tests check and its ruling
- The design blocks and their copies carry the rule and stay in step
- The changelog records the declared-path rule in a contiguous entry
- The changelog records the small-change lane in one entry
- The design doc and README describe both skips
- Every reviewer copy carries the rule and the copies stay in step
- The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do
- The design doc states the EMPTY-OUTPUT rule, its rows and its park
- README drops the budget park and describes the empty-output retry
- The changelog records issue 41 without a numbering gap
- Principle 2 names the critic's no-suite rule and no longer its build ban
- The changelog records the revert in one entry
- The Spiking section allows a small scratch check and records the replay
- The prompt copies, design, README and changelog name the capability index
- The design, README and changelog describe the whole decision log and no decision index
- The design doc, README and changelog record superseded plans
- The design doc drops the per-PR approval for protected paths
- The changelog records issue 57's change without a numbering gap
- README describes the protected-path check and the new resolve verb
- The changelog records the reading rules for the five roles in one entry
- The changelog records the change in one contiguous entry
- The design doc names the amend command, its intent flag, spec drift and the critic's new input
- README lists the amend command and the drift check
- The design doc, template and README name the sync and the dropped virtual environment
- The changelog records the environment sync in one entry
- The documents describe the driver
- The design doc, README and changelog record both changes
- The documents describe the driver's exemption and its same-ticket guard
- The documents record factory stats
- The README describes the model check
- The design doc names the waiting park reason
- The README names pytest-xdist and the waiting reason
- The changelog records issue 106 as entry 71, without a numbering gap
- The maintained documents pass git's whitespace check in full
- Each build document carries the header and is otherwise unchanged
- The briefing no longer asks a change to keep the build spec in step
- README no longer calls run features untried, and keeps the claims that are still true
- The Built rule asks for run status, and the design doc's date line points to the changelog
- Each Built entry is a short pointer, and each mechanism's detail has one home
- The glossary points to Where it runs and defines protected path once
- README keeps its issue references and drops the moved history, and the changelog records the move
- README is at most 1,110 lines
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
