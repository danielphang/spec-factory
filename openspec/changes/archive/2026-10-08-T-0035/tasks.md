T-0035.1 / Revert #73's critic limits: drop the per-claim cap and the no-build rule; keep the no-suite line and the reading rules
Depends on: none
Parallel-safe: yes

Parent: T-0035, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- Every critic copy drops the cap and the no-build rule and keeps the rest; every writer copy keeps its rules
- A critic run's prompt has the no-suite rule and the scratch allowance, and no cap or build ban
- The writer prompt is as #73 left it, and only the critic's PROCESS changes
- Principle 2 names the critic's no-suite rule and no longer its build ban
- The changelog records the revert as its last entry
- The Spiking section allows a small scratch check and records the replay
- The critic revert adds no whitespace errors
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
