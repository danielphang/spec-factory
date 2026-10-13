## ADDED Requirements

### Requirement: The gate's suite command finishes in under three minutes
The harness-suite command in this repository's `gate_commands` SHALL, run as written, pass every test and finish in under 180 seconds on the operator's machine.

#### Scenario: The gate's suite command, as the instance lists it, passes in under three minutes
Needs the GIVEN block of "One suite run passes in under three minutes" (this change, harness-suite) run once.
- WHEN `(C=$(sed -n 's/^  - "\(uv run .*tests\/factory\)"$/\1/p' .factory/instance.yaml); echo "gate: $C"; .venv/bin/python ${TMPDIR:-/tmp}/t0051-time.py 1 180 "$C")`
- THEN it prints exactly `gate: uv run --frozen pytest -q -p no:cacheprovider tests/factory`, then one line that reports a number of passed tests, contains no `failed` or `error`, and ends with `| under 180 s`

