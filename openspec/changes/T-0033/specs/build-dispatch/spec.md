## ADDED Requirements

### Requirement: The build parks a merge the gate blocked, with the gate's reason
When `factory merge` is refused with an error that starts `BLOCKED `, `factory/workflows/build.js` MUST park the sub-ticket with that error, verbatim, as the reason, and SHALL NOT record it as a harness bug.

#### Scenario: The build parks a merge refused for protected paths with the gate's reason
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "ticket join": {"out": {"ok": true, "decision": "merge", "reason": "ci PASS + APPROVE + VERIFIED on the current head"}}, "merge": {"out": {"ok": false, "error": "BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py"}, "exit": 2}}')`
- THEN it prints exactly `park: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py`

