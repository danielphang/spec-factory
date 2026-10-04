# merge-gate

## Requirements

### Requirement: A store commit does not hold back a merge
On an instance whose store is the checkout of `factory-store`, a store commit made after a sub-ticket's checks SHALL NOT stop `factory merge` from merging that sub-ticket.

#### Scenario: A sub-ticket merges after a store commit
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: rows recorded"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=0 refused=0`

### Requirement: A commit to the integration branch still holds back a merge
`factory merge` MUST still refuse, with `head does not contain main`, a sub-ticket whose head does not contain a commit made to the integration branch after its checks.

#### Scenario: A sub-ticket is refused after a code commit to main
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-gate.sh && echo y > y.txt && git add y.txt && git commit -q -m "code on main"; $B merge T-0001 >/dev/null 2>$T25/err; echo "exit=$? refused=$(grep -c 'head does not contain main' $T25/err)")`
- THEN it prints `exit=2 refused=1`
