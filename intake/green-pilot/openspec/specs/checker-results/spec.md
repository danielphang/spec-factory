# checker-results

## Requirements

### Requirement: checker-output-must-name-the-head
`factory results record` without `--killed` SHALL refuse with exit 2, and write no results row and no `result.*` log event, unless the output has at least one line starting with `Commit:` and every such line's value is a 7-40 character hex commit id (optionally in backticks) that is a prefix of the `--head` being recorded.

#### Scenario: no-commit-line-is-refused
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf 'Findings: none\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n' > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=2 rows=[] events=0`

#### Scenario: non-hex-commit-value-is-refused
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf 'Commit: HEAD\nFindings: none\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n' > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=2 rows=[] events=0`

#### Scenario: later-commit-line-naming-another-commit-is-refused
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf "Commit: $H\nFindings: none\nCommit: deadbeef00\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n" > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=2 rows=[] events=0`

#### Scenario: verifier-without-commit-line-writes-no-ci-row
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf 'Per criterion: none\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n' > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=2 rows=[] events=0`

#### Scenario: earlier-commit-line-naming-another-commit-is-refused
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf "Commit: deadbeef00\nFindings: none\nCommit: $H\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n" > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=2 rows=[] events=0`

#### Scenario: full-head-sha-is-recorded
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf "Commit: $H\nFindings: none\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n" > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=0 rows=[reviewer.yaml ] events=1`

#### Scenario: abbreviated-sha-in-backticks-is-recorded
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf 'Commit: \1400000000\140\nPer criterion: none\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n' > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --output $S/o.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root; `\140` is a backtick, so the line reads ``Commit: `0000000` ``)
- THEN it prints `exit=0 rows=[ci.yaml verifier.yaml ] events=2`

### Requirement: killed-run-recording-is-unchanged
`factory results record --killed` MUST record a KILLED row as it does today, both with no `--output` and with an `--output` that has no `Commit:` line.

#### Scenario: killed-without-output-records-killed
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --run R1 --killed >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] status=$(sed -n 's/^status: //p' $S/results/$H/verifier.yaml 2>/dev/null)"` (run from the repo root)
- THEN it prints `exit=0 rows=[verifier.yaml ] status=KILLED`

#### Scenario: killed-with-cut-off-output-records-killed
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf 'Per criterion: (cut off)\n' > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --output $S/o.md --run R1 --killed >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] status=$(sed -n 's/^status: //p' $S/results/$H/verifier.yaml 2>/dev/null)"` (run from the repo root)
- THEN it prints `exit=0 rows=[verifier.yaml ] status=KILLED`

#### Scenario: factory-suite-still-passes
- WHEN `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory` (run from the repo root)
- THEN it exits 0 and reports no failed tests (today: `55 passed`)
