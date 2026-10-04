## ADDED Requirements
### Requirement: A role whose agent type is not registered parks its ticket with no run in flight
When a role's agent call fails because the session has not registered its agent type, the workflow MUST record that run killed and park the ticket with `agent call failed: <role>: <error>`; when no factory agent is registered at all, the workflow SHALL stop at its first store command, having written nothing.

#### Scenario: A build run before the build-role agents register parks the sub-ticket
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0030-throw.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}}')`
- THEN it prints exactly `run finish run-0009-x --status-override KILLED`, then `ticket park T-0001.1 --reason "agent call failed: implementer: agent type 'factory-implementer' not found" --outputs run-0009-x`

#### Scenario: A workflow in a session with no factory agents stops at its first store command
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(for w in intake build; do node ${TMPDIR:-/tmp}/t0030-throw.mjs factory/workflows/$w.js '{}' all; done)`
- THEN it prints exactly `stopped: agent type 'factory-clerk' not found after 1 agent call(s)` twice, one per line

