## ADDED Requirements

### Requirement: docs/benchmark.md holds the upstream benchmark's method
`docs/benchmark.md` MUST give the upstream benchmark's method under its eight sections: how tasks are chosen, how the arms are kept blind, how each arm is run, how a task is scored, what each measure is and where it comes from, how a result goes into a review, and the spend, and SHALL say that operator time measures interactions, not attention, undercounts reading and review time, and is counted in sittings.

#### Scenario: The benchmark page has its eight sections in order
- WHEN `(grep '^## ' docs/benchmark.md 2>/dev/null; echo "exit=$?")`
- THEN it prints exactly these nine lines, one per line: `## What the benchmark compares`, `## Choosing the tasks`, `## Keeping the arms blind`, `## Running a task`, `## Scoring a task`, `## The measures`, `## Putting a result in a review`, `## Spend`, `exit=0`

#### Scenario: The benchmark page states its selection, blinding, setup, measures, review and spend rules
- WHEN `(h() { for p in "$@"; do grep -qF -- "$p" docs/benchmark.md 2>/dev/null || { echo no; return; }; done; echo yes; }; echo "caveat=$(h 'measures interactions, not attention' 'undercounts reading and review time') selection=$(h 'first parent' '10 most recently merged') blind=$(h 'git fetch --depth 1' 'nanobot-upstream' 'leaked') arms=$(h 'FACTORY_STATE' 'FACTORY_INSTANCE' 'gives the implementer') measures=$(h 'python -m factory.benchmark' 'factory stats --scorecard' 'more than 15 minutes' 'first interaction') review=$(h 'docs/reviews/' 'not yet computed') spend=$(h '10 factory intakes and builds' '10 plain sessions')")`
- THEN it prints exactly `caveat=yes selection=yes blind=yes arms=yes measures=yes review=yes spend=yes`

#### Scenario: No relative link in the benchmark page is broken
- WHEN `(f=docs/benchmark.md; [ -f $f ] || { echo "$f missing"; exit 0; }; n=0; bad=0; for l in $(grep -oE '\]\([^)#]+\)' $f | sed -E 's/^\]\(//; s/\)$//' | grep -v '^[a-z]*:'); do n=$((n+1)); [ -e "docs/$l" ] || bad=$((bad+1)); done; echo "relative=$([ $n -gt 0 ] && echo some || echo none) broken=$bad")`
- THEN it prints exactly `relative=some broken=0`

### Requirement: README points to the benchmark's method and its report
README's "Where things live" MUST have one row for `docs/benchmark.md`, and "What depends on Claude Code" SHALL name `factory/benchmark.py` in the row it shares with `factory/cost.py`.

#### Scenario: README names the benchmark page and puts its report in the cost row
- WHEN `(W=$(sed -n '/^## Where things live$/,/^## Related work and history$/p' README.md | grep '^| '); D=$(sed -n '/^### What depends on Claude Code$/,/^## Terms used on this page$/p' README.md | grep '^| '); echo "where=$(printf '%s\n' "$W" | grep -c 'docs/benchmark.md') depends=$(printf '%s\n' "$D" | grep -c 'factory/benchmark.py') shared=$(printf '%s\n' "$D" | grep 'factory/benchmark.py' | grep -c 'factory/cost.py')")`
- THEN it prints exactly `where=1 depends=1 shared=1`

