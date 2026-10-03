## ADDED Requirements

### Requirement: killed-checker-parks-as-budget-kill
When a reviewer or verifier run is killed and the build loop records it the way it does today (passing `--output` with the run's output path, which a killed run never wrote, and `--killed`), `factory results record` SHALL record a KILLED row and exit 0, so that `factory ticket join` decides `park` with reason `budget kill: <role>`.

#### Scenario: killed-verifier-without-output-file-parks-as-budget-kill
- GIVEN a throwaway store whose ticket's head is set directly in its ticket file (a stand-in for `ticket head`, which needs a git branch), and a reviewer APPROVE already recorded for that head
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; sed "s/^head: null\$/head: '$H'/" $S/tickets/T-0001.yaml > $S/t.yaml && mv $S/t.yaml $S/tickets/T-0001.yaml; printf "Commit: $H\nFindings: none\nSTATUS: APPROVE\nCONFIDENCE: high\nESCALATIONS: none\n" > $S/rev.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/rev.md --run R1 >/dev/null 2>&1; a=$?; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --output $S/runs/R2/output.md --run R2 --killed >/dev/null 2>&1; b=$?; echo "reviewer=$a verifier=$b $(FACTORY_STATE=$S bin/factory ticket join T-0001 2>/dev/null | sed -n 's/.*"decision": "\([^"]*\)", "reason": "\([^"]*\)".*/decision=\1 reason=\2/p')"` (run from the repo root)
- THEN it prints `reviewer=0 verifier=0 decision=park reason=budget kill: verifier`

#### Scenario: killed-reviewer-without-output-file-parks-as-budget-kill
- GIVEN the same throwaway store, with a verifier VERIFIED (`Gate suite: PASS`) already recorded for the head
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; sed "s/^head: null\$/head: '$H'/" $S/tickets/T-0001.yaml > $S/t.yaml && mv $S/t.yaml $S/tickets/T-0001.yaml; printf "Commit: $H\nPer criterion: all pass\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high\nESCALATIONS: none\n" > $S/ver.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --output $S/ver.md --run R1 >/dev/null 2>&1; a=$?; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/runs/R2/output.md --run R2 --killed >/dev/null 2>&1; b=$?; echo "verifier=$a reviewer=$b $(FACTORY_STATE=$S bin/factory ticket join T-0001 2>/dev/null | sed -n 's/.*"decision": "\([^"]*\)", "reason": "\([^"]*\)".*/decision=\1 reason=\2/p')"` (run from the repo root)
- THEN it prints `verifier=0 reviewer=0 decision=park reason=budget kill: reviewer`

#### Scenario: killed-record-without-output-flag-still-records-killed
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --run R1 --killed >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] status=$(sed -n 's/^status: //p' $S/results/$H/verifier.yaml 2>/dev/null)"` (run from the repo root)
- THEN it prints `exit=0 rows=[verifier.yaml ] status=KILLED`

### Requirement: killed-run-output-is-not-read
With `--killed`, `factory results record` MUST record KILLED without reading or checking the `--output` file, whatever that file holds. Without `--killed`, the output file MUST still be read and checked as before.

#### Scenario: killed-output-naming-another-commit-records-killed
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; printf 'Commit: deadbeef00\nPer criterion: (cut off)\n' > $S/o.md; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role verifier --output $S/o.md --run R1 --killed >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] status=$(sed -n 's/^status: //p' $S/results/$H/verifier.yaml 2>/dev/null)"` (run from the repo root)
- THEN it prints `exit=0 rows=[verifier.yaml ] status=KILLED`

#### Scenario: unkilled-record-with-missing-output-file-still-fails
- WHEN `S=$(mktemp -d); H=$(printf '%040d' 0); printf '# x\n\nthe thing\n' > $S/r.md; FACTORY_STATE=$S bin/factory ticket new --file $S/r.md >/dev/null; FACTORY_STATE=$S bin/factory results record T-0001 --head $H --role reviewer --output $S/missing.md --run R1 >/dev/null 2>&1; echo "exit=$? rows=[$(ls $S/results/$H 2>/dev/null | tr '\n' ' ')] events=$(cat $S/log/*.jsonl | grep -c '"event": "result\.')"` (run from the repo root)
- THEN it prints `exit=1 rows=[] events=0`

#### Scenario: factory-suite-passes-with-killed-checker-change
- WHEN `PYTHONDONTWRITEBYTECODE=1 COLUMNS=200 TERM=dumb NO_COLOR=1 uv run pytest -q -p no:cacheprovider tests/factory` (run from the repo root)
- THEN it exits 0 and reports no failed tests

