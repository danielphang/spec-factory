## ADDED Requirements

### Requirement: The documents record the parallel suite and the waiting park reason
`docs/design.md`'s EMPTY-OUTPUT rule and `dev/build-harness.spec.md` SHALL name the waiting park reason, and the build spec's `run last-message` entry SHALL name its `waiting` field. `README.md` SHALL name pytest-xdist, and its Empty output entry SHALL give the waiting reason and no longer say it has not fired on a real ticket. `docs/changelog.md` SHALL gain entry 71 for issue #106, numbered without a gap. No `docs/prompts/` file SHALL change, and the change MUST add no whitespace errors.

#### Scenario: The design doc and build spec name the waiting park reason, and no prompt copy changes
- WHEN `(echo "design=$(grep '^- A role run that ends without writing its output is EMPTY-OUTPUT' docs/design.md | grep -c 'ended its turn waiting on a background command') spec=$(grep -c 'ended its turn waiting on a background command' dev/build-harness.spec.md | awk '{print ($1 > 0)}') cli=$(grep '^- .factory run last-message' dev/build-harness.spec.md | grep -c 'waiting') prompts=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts | grep -c .)")`
- THEN it prints exactly `design=1 spec=1 cli=1 prompts=0`

#### Scenario: The README names pytest-xdist and the waiting reason
- WHEN `(B=$(awk '/^- \*\*Empty output\.\*\*/{f=1; print; next} f && /^(- \*\*|$|#)/{f=0} f' README.md | tr '\n' ' ' | tr -s ' '); echo "bullet=$(grep -c '^- \*\*Empty output\.\*\*' README.md) waiting=$(echo "$B" | grep -c 'ended its turn waiting on a background command') unfired=$(echo "$B" | grep -c 'has not yet fired') xdist=$(grep -c 'pytest-xdist' README.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `bullet=1 waiting=1 unfired=0 xdist=1`

#### Scenario: The changelog records issue 106 as its last entry, without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; L=$(grep '^[0-9]*\. ' docs/changelog.md | tail -1); echo "$L" | grep -c '^71\. After issue #106 '; echo "$L" | grep -oF -e 'pytest-xdist' -e 'ended its turn waiting on a background command' -e 'EMPTY-OUTPUT' -e 'stand-in' -e 'in-process' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `5`

#### Scenario: The parallel-suite change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints exactly `exit=0`

