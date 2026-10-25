## ADDED Requirements

### Requirement: The spec writer's run after a refused draft receives the refusal and that draft
When the ticket's previous finished spec writer run ended READY-FOR-CRITIC or NEEDS-SPLIT, no spec version came from it, and its output fails the format check, the next spec writer run's input SHALL hold a section titled "Your previous output, which the harness refused to store as a spec version" that opens with the refusal and holds that run's output, and that run's `output.md` MUST be among the input's sources; a first spec writer run gets no such section.

#### Scenario: The spec writer's next run receives the refusal and its refused output
Needs the GIVEN block of "spec add refuses a spec whose label wraps or is followed by a word, and stores a well-formed one" run once.
- WHEN `(SIDE=drive; P='{"spec_writer": ["wrapped:READY-FOR-CRITIC", "good:READY-FOR-CRITIC"], "critic": ["APPROVE"]}'; . ${TMPDIR:-/tmp}/t0057-intake.sh >/dev/null; I=$S/runs/run-0002-spec_writer/input.md; echo "first=$(grep -c '^## Your previous output, which the harness refused' $S/runs/run-0001-spec_writer/input.md) heading=$(grep -c '^## Your previous output, which the harness refused' $I 2>/dev/null) message=$(grep -c "spec not added: scenario 'the thing works' has no NEW/REGRESSION label in verification.md" $I 2>/dev/null) output=$(grep -cx '  → NEW; fails today' $I 2>/dev/null) source=$(grep -c 'runs/run-0001-spec_writer/output.md' $S/runs/run-0002-spec_writer/meta.yaml 2>/dev/null)")`
- THEN it prints exactly `first=0 heading=1 message=1 output=1 source=1`

