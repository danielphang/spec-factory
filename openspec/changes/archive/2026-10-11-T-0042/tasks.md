T-0042.1 / factory drive: let a drive on one ticket start while another ticket has a run in flight, and refuse a second drive on the same ticket
Depends on: none
Parallel-safe: yes

Parent: T-0042, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- Unmarked writes from inside the target are refused while a run is in flight, init included
- The refusal names the throwaway store and not the marker
- A harness acceptance is refused while a run is in flight
- An unmarked drive starts beside another ticket's run, is refused from a run's directory, and marks only its own store calls
- A drive of a ticket with its own run in flight is refused, marked or not, and writes nothing
- A drive of a parent whose sub-ticket has a run in flight is refused and writes nothing
- A recorded live driver blocks a second drive, and an ended or dead one does not
- The documents describe the driver's exemption and its same-ticket guard
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
