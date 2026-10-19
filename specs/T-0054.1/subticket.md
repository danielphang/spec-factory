T-0054.1 / Workflow builds stop parking on the clerk's relays: the harness writes each role's model into a launch copy of the script, the scripts parse a reformatted reply, and `resolve` has a route back from a park after a finished implementer (#109, #112)
Depends on: none
Parallel-safe: yes

Parent: T-0054, approved spec v3. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A build launched from its launch copy runs the verifier on the instance's model while the clerk retypes it, and the script itself still parks
- An intake launched from its launch copy runs triage on the instance's model while the clerk retypes it
- Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance
- launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy
- launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy
- A launch copy launched for another instance returns an error naming its own and runs nothing
- A build and an intake whose every store reply is relayed pretty-printed reach the ends they reach with one-line replies
- A sub-ticket parked when its implementer's finish did not parse returns to its checks at the branch tip, and the build then merges it
- The route back to checks is refused after a BLOCKED run, after a revise, from the checks, on a tripwire park and on a ticket that is not parked
- Unmarked writes from inside the target are refused while a run is in flight, init included
- The refusal names the throwaway store and not the marker
- A harness acceptance is refused while a run is in flight
- A launch copy is written unmarked while a run is in flight, and the target is unchanged
- The README, the design doc and the changelog describe the launch copy and the route back to checks
- The suite passes, no existing test changes, and every test file this change adds fails on the base
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
