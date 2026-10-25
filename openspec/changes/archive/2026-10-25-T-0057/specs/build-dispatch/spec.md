## ADDED Requirements

### Requirement: A spec that spec add refuses as malformed goes back to the spec writer as a new round
When `spec add` refuses a spec writer's READY-FOR-CRITIC or NEEDS-SPLIT output with an error starting `spec not added: `, the driver and the intake Workflow script SHALL send the ticket back to the spec writer, counting the refused draft as one round, while a round is left; the next stored version then goes to the critic as usual, and both runners MUST leave the same records.

#### Scenario: A refused draft goes back to the spec writer and the next well-formed one reaches the critic, in the driver and the script
Needs the GIVEN block of "spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one" run once.
- WHEN `(for SIDE in script drive; do P='{"spec_writer": ["wrapped:READY-FOR-CRITIC", "good:READY-FOR-CRITIC"], "critic": ["APPROVE"]}'; . ${TMPDIR:-/tmp}/t0057-intake.sh; done)`
- THEN it prints exactly `awaiting-spec-gate spec=2 versions=1 writer=2 critic=1 reason=` twice, one per line

### Requirement: A spec refused in the last round parks the ticket with the refusal
When no round is left, the driver and the intake Workflow script SHALL park the ticket with the reason `max rounds: ` followed by the refusal's first line, in which each backtick, `$` and `\` is replaced by `'`, so that no part of it runs as a shell command; both runners MUST record the same reason.

#### Scenario: A refusal in the last round parks with the refusal, quoted safely, in the driver and the script
Needs the GIVEN block of "spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one" run once. The first plays refuse both drafts. The second has the critic send a stored version back and then refuses the second draft.
- WHEN `(for P in '{"spec_writer": ["ticked:READY-FOR-CRITIC"]}' '{"spec_writer": ["good:READY-FOR-CRITIC", "worded:NEEDS-SPLIT"], "critic": ["REVISE"]}'; do for SIDE in script drive; do . ${TMPDIR:-/tmp}/t0057-intake.sh; done; done)`
- THEN it prints exactly `parked spec=2 versions=0 writer=2 critic=0 reason=max rounds: spec not added: scenario 'the 'echo hi' thing works' has no NEW/REGRESSION label in verification.md` twice, then `parked spec=2 versions=1 writer=2 critic=1 reason=max rounds: spec not added: scenario 'the thing works' has no NEW/REGRESSION label in verification.md` twice, one per line

