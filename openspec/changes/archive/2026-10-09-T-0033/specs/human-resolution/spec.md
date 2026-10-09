## ADDED Requirements

### Requirement: Accepting the refused paths returns the sub-ticket to its checks, which then merge
`factory resolve <id> --accept-paths F`, on a park whose reason starts `BLOCKED from merge gate:`, MUST write F as the ticket's next ruling, add the head's undeclared protected paths to the ticket's `accepted_paths`, keep every result row, and return the ticket to `checks-in-flight`; `factory merge` SHALL then merge it. On any other park it MUST refuse with exit 2, writing nothing, with an error containing `--accept-paths applies to`.

#### Scenario: Accepting the refused paths returns the sub-ticket to its checks, and the merge then goes through
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once. The scenario parks the sub-ticket with the gate's own error, as the build does.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: ^core/a.py^' 'core/a.py core/b.py' && E=$($B merge T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p'); $B ticket park T-0001.1 --reason "$E" >/dev/null 2>&1; printf 'Ruling: core/b.py is part of the approved design.\n' > $T/ru.md; $B resolve T-0001.1 --accept-paths $T/ru.md >/dev/null 2>&1; echo "accept=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') rows=$(ls $FACTORY_STATE/results/$H | grep -c yaml) ruling=$(cmp -s $T/ru.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo kept || echo missing)"; $B merge T-0001.1 >/dev/null 2>&1; echo "merge=$? on_main=$(git -C $T/t diff --name-only $M main | grep -c 'core/b\.py')")`
- THEN it prints exactly `accept=0 checks-in-flight rows=3 ruling=kept`, then `merge=0 on_main=1`

#### Scenario: Accepting paths is refused on any other park and writes nothing
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'core/b.py' && $B ticket park T-0001.1 --reason "ESCALATE from reviewer" >/dev/null && printf 'Ruling: x\n' > $T/ru.md; $B resolve T-0001.1 --accept-paths $T/ru.md >/dev/null 2>$T/err; echo "accept=$? refused=$(grep -c 'accept-paths applies to' $T/err) $($B ticket show T-0001.1 | sed -n 's/^status: //p') rulings=$(ls $FACTORY_STATE/approvals/T-0001.1 2>/dev/null | grep -c ruling)")`
- THEN it prints exactly `accept=2 refused=1 parked rulings=0`

### Requirement: A ruling on a merge gate's refusal sends the sub-ticket back to its implementer
`factory resolve <id> --ruling F` on a park whose reason starts `BLOCKED from merge gate:` SHALL return the sub-ticket to `ready-for-implementer` at the same round, and the next implementer input SHALL contain F.

#### Scenario: A ruling on a merge-gate refusal sends the sub-ticket back to its implementer with the ruling
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'core/b.py' && E=$($B merge T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p'); $B ticket park T-0001.1 --reason "$E" >/dev/null 2>&1; printf 'Ruling: take core/b.py out of this change.\n' > $T/ru.md; $B resolve T-0001.1 --ruling $T/ru.md >/dev/null 2>&1; echo "ruling=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') reason=$(echo "$E" | grep -c '^BLOCKED from merge gate: ')"; R=$($B run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && $B run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: take core/b.py out of this change.')")`
- THEN it prints exactly `ruling=0 ready-for-implementer reason=1`, then `in_input=1`

### Requirement: A ruling on a reviewer's escalation returns the sub-ticket to its checks
`factory resolve <id> --ruling F` on a park whose reason starts `ESCALATE from reviewer` MUST write F as the ticket's next ruling and return the ticket to `checks-in-flight` at the same round. It MUST set aside the head's rows that did not pass, by the rule `--redispatch` uses, and the next reviewer input SHALL contain F.

#### Scenario: A ruling on a reviewer escalation returns the sub-ticket to its checks with the ruling
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: none' 'docs/d.md' && printf "Commit: $H\nSTATUS: ESCALATE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/e.md && $B results record T-0001.1 --head $H --role reviewer --output $T/e.md --run run-0003-reviewer >/dev/null && $B ticket park T-0001.1 --reason "ESCALATE from reviewer" >/dev/null && printf 'Ruling: the escalation is settled.\n' > $T/ru.md; $B resolve T-0001.1 --ruling $T/ru.md >/dev/null 2>&1; echo "exit=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p') kept: $(ls $FACTORY_STATE/results/$H | grep yaml | tr '\n' ' ')"; R=$($B run start --role reviewer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); [ -n "$R" ] && $B run compose $R >/dev/null; echo "in_input=$(cat $FACTORY_STATE/runs/${R:-none}/input.md 2>/dev/null | grep -c 'Ruling: the escalation is settled.')")`
- THEN it prints exactly `exit=0 checks-in-flight kept: ci.yaml verifier.yaml ` (the reviewer's ESCALATE row set aside, the passing verifier and gate rows kept), then `in_input=1`

