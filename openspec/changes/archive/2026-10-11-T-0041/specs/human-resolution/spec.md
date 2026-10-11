## ADDED Requirements

### Requirement: A ruling returns a sub-ticket whose implementer run failed to start
`factory resolve <id> --ruling F` on a park whose reason starts `harness-bug: run start implementer:` and that was parked from `ready-for-implementer` MUST write F as the ticket's next ruling and return it to `ready-for-implementer` at the same round; on a harness-bug park of any other kind it MUST still refuse with exit 2, writing nothing.

#### Scenario: A ruling on a harness-bug park from an implementer's run start returns the sub-ticket, and its implementer then starts
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" (current truth, spec-amendment) run once. The park reason is the spec drift refusal wrapped as the Workflow script's clerk wrapped it for the sub-ticket that showed this problem.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n' && land src/greet.py tests/test_greet.py && E=$(bin/factory run start --role implementer --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"error": "\([^"]*\)".*/\1/p') && bin/factory ticket park T-0001.1 --reason "harness-bug: run start implementer: $E" >/dev/null && printf 'Ruling: the new test may change.\n' > $T27/r.md; bin/factory resolve T-0001.1 --ruling $T27/r.md >/dev/null 2>&1; echo "ruling=$? $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') kept=$(cmp -s $T27/r.md $FACTORY_STATE/approvals/T-0001.1/ruling-1.md && echo yes || echo no) drift=$(echo "$E" | grep -c '^BLOCKED from harness: spec drift: ')"; bin/factory run start --role implementer --ticket T-0001.1 >/dev/null 2>&1; echo "start=$? runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c implementer)")`
- THEN it prints exactly `ruling=0 ready-for-implementer kept=yes drift=1`, then `start=0 runs=1`

#### Scenario: A ruling on a checker's or a compose step's harness-bug park is still refused
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) run once.
- WHEN `(for r in 'harness-bug: run start reviewer: x' 'harness-bug: run compose implementer: x'; do (. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && { case "$r" in *reviewer*) bin/factory ticket set T-0001.1 status=checks-in-flight >/dev/null;; esac; } && bin/factory ticket park T-0001.1 --reason "$r" >/dev/null && printf 'Ruling: x\n' > $T23/r.md; bin/factory resolve T-0001.1 --ruling $T23/r.md >/dev/null 2>$T23/err; echo "exit=$? refused=$(grep -c -- '--ruling applies to' $T23/err) $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') rulings=$(ls $FACTORY_STATE/approvals/T-0001.1 2>/dev/null | grep -c ruling)"); done)`
- THEN it prints two lines, each exactly `exit=2 refused=1 parked rulings=0`

