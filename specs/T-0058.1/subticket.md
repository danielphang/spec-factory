T-0058.1 / Four small harness defects: the escalation parser counts Claude Code's attribution footer as escalations, a build-dispatch scenario fails under macOS /bin/sh, `factory init` exits 1 on an unreadable agent copy, and `--accept-harness` is silently ignored by `init`, `paths` and `stats` (#88, #113, #114, #115)
Depends on: none
Parallel-safe: yes

Parent: T-0058, approved spec v3. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- A none trailer followed by the attribution footer finishes with no escalation and queues nothing
- A real item above the attribution footer stays, and the footer is dropped
- Real item lines, and a line that only mentions Claude Code, are still read by rule (b)
- Each launch copy is a one-line change to its script, in a read-only file in a directory of its own, naming the harness revision and the instance
- launch-script is refused with config's error where the instance has not accepted the running harness, and writes no copy
- launch-script removes a launch copy over an hour old and keeps a recent one and a directory that holds no launch copy
- init reports an edited agent copy and leaves it as it is
- init still creates a missing agent copy and lists no matching copy
- init lists an agent copy it cannot read, says so, exits 0 and leaves it as it is
- The flag with init, paths or stats is refused, names config, and writes nothing, even where init would create an instance
- Without the flag paths and stats still run under another lock, and config still accepts a revision
- README says which commands refuse the flag, how to accept a revision, and that init reports an unreadable copy
- The design doc states the footer rule and the refusal in the lock clause
- The changelog records the four issues in one entry without a numbering gap
- The harness suite passes
- The only existing test file changed is the stats test
Tests to change: the parent's list.
Protected paths: the parent's Risk list.
