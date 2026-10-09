## MODIFIED Requirements

### Requirement: Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
The system prompts of implementer, code reviewer and verifier runs MUST still carry the preamble's rule to escalate a protected path that the approved spec's Risk section does not declare. The code reviewer's prompt MUST still carry check 6's rule to ESCALATE a path the sub-ticket does not declare and to list a declared one under ESCALATIONS. Check 6 SHALL say that the merge gate merges a path the approved spec's Risk section declares with no further approval, and SHALL NOT promise a human approval at merge.

#### Scenario: All three run prompts keep the undeclared-path rule and the reviewer keeps check 6
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" (current truth, role-escalations) run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && u="a protected path the approved spec's Risk section does not declare"; for r in implementer reviewer verifier; do echo "$r undeclared=$(prompt $r | grep -cF "$u")"; done; echo "check6=$(prompt reviewer | grep -cF '6. Protected paths touched? If the sub-ticket does not declare them, ESCALATE. If it does, list them under ESCALATIONS')")`
- THEN it prints exactly `implementer undeclared=1`, `reviewer undeclared=1`, `verifier undeclared=1`, `check6=1`, one per line

#### Scenario: The reviewer run prompt says what the merge gate checks
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" (current truth, role-escalations) run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && P=$(prompt reviewer); echo "gate=$(echo "$P" | grep -c "The merge gate merges a path the approved spec's Risk section declares with no further approval") promise=$(echo "$P" | grep -c 'will require a human approval')")`
- THEN it prints exactly `gate=1 promise=0`

