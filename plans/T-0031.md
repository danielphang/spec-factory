T-0031.1 / Role commands drop an inherited VIRTUAL_ENV, and build checkouts start with a synced environment
Depends on: none
Parallel-safe: yes

Parent: T-0031, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A role's wrapper and its wrapped gate command drop an inherited virtual environment
- An implementer's worktree is synced through the wrapper at every dispatch, and its input says so
- A checker's checkout is synced before the checker starts, and its input says so
- A failed sync refuses the run start, names the sync, and leaves no run or checker checkout
- Without environment_sync, run start and the input are as before
- The design doc, build spec, template and README name the sync and the dropped virtual environment, and no prompt copy changes
- The changelog records the environment sync as its last entry
- The environment-sync change adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
