## ADDED Requirements

### Requirement: The documents record the scorecard, escape and intervention records, and workflow token records
README SHALL describe `factory stats --scorecard` and `target_is_factory` in "Counting what each role catches and costs", with the run token record that `run finish --transcripts` writes in place of the claim that only driver runs carry a cost record; SHALL give `factory escape add` and `factory intervention add` their rows in "Where a human decides", the **Escape** row saying the store keeps only the link's SHA-256 hash; SHALL list the transcript record among the six pieces in "What depends on Claude Code"; and SHALL give the three a short Built entry that points to that subsection and says they have not yet run on a real store; `factory/instance.template.yaml` SHALL document `target_is_factory`.

#### Scenario: README and the instance template describe the scorecard, the two records and the token record
- WHEN `(r=README.md; y() { [ "$1" -gt 0 ] && echo yes || echo no; }; C=$(sed -n '/^### Counting what each role catches and costs/,/^## /p' $r); H=$(sed -n '/^## Where a human decides/,/^### What you read at each stop/p' $r); D=$(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r); echo "scorecard=$(y $(printf '%s\n' "$C" | grep -c -- '--scorecard')) setting=$(y $(printf '%s\n' "$C" | grep -c 'target_is_factory')) escape=$(y $(printf '%s\n' "$H" | grep '^| \*\*Escape\*\* |' | grep -c 'factory escape add')) hash=$(y $(printf '%s\n' "$H" | grep '^| \*\*Escape\*\* |' | grep -c 'SHA-256')) intervene=$(y $(printf '%s\n' "$H" | grep '^| \*\*Intervene\*\* |' | grep -c 'factory intervention add')) record=$(y $(printf '%s\n' "$C" | tr '\n' ' ' | grep -c 'run finish --transcripts')) old=$(y $(grep -c 'Any other run has its tokens only in the transcript' $r)) depends=$(y $(printf '%s\n' "$D" | grep '^| ' | grep -c 'run finish --transcripts')) pieces=$(y $(printf '%s\n' "$D" | grep -c 'Six pieces assume Claude Code')) template=$(y $(grep -c 'target_is_factory' factory/instance.template.yaml))"; awk -v h='- **The scorecard, escapes and workflow token records.**' 'index($0,h)==1{f=1;print;next} f&&/^(- \*\*|$|#)/{f=0} f' $r | awk '{t=t" "$0} END{gsub(/ +/," ",t); print ((NR>0 && NR<=3 && index(t,"Counting what each role catches") && index(t,"Not yet run on a real store")) ? "built=pointer" : "built=long")}')`
- THEN it prints exactly `scorecard=yes setting=yes escape=yes hash=yes intervene=yes record=yes old=no depends=yes pieces=yes template=yes`, then `built=pointer`

## MODIFIED Requirements

### Requirement: README stays within its line budget
`README.md` SHALL be at most 1,225 lines long; a later change that needs more room raises this bound in its own spec, where the operator approves it at the gate.

#### Scenario: README is at most 1,225 lines
- WHEN `(echo "readme=$(wc -l < README.md | awk '{print ($1 <= 1225 ? "within" : "over")}')")`
- THEN it prints exactly `readme=within`

### Requirement: The documents record the template fix and init's report of a differing agent copy
`README.md`'s `.claude/agents/factory-*.md` row SHALL say that init reports a copy that differs from its template, and step 1 of "Adopting the factory in a repo" SHALL name `stale_agents`. `docs/changelog.md` SHALL hold one entry for issue #108, numbered without a gap, that names `frontmatter`, `stale_agents` and `Nanobot`. README MUST stay within its 1,225-line budget, and both documents MUST carry no whitespace error.

#### Scenario: README describes init's report of a differing agent copy
- WHEN `(echo "row=$(grep '^| .\.claude/agents/factory-\*\.md. |' README.md | grep -c 'differs from its template') step=$(sed -n '/^### Adopting the factory in a repo/,/^2\. /p' README.md | tr '\n' ' ' | grep -c 'stale_agents') missing=$(grep '^| .\.claude/agents/factory-\*\.md. |' README.md | grep -c 'when they are missing')")`
- THEN it prints exactly `row=1 step=1 missing=1`

#### Scenario: The changelog records issue 108 in one entry without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #108 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e frontmatter -e stale_agents -e Nanobot | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `3`

#### Scenario: README stays within its line budget and both documents pass the whitespace check
- WHEN `(E=$(git hash-object -t tree /dev/null); echo "readme=$(wc -l < README.md | awk '{print ($1 <= 1225 ? "within" : "over")}')"; git diff --check $E HEAD -- README.md docs/changelog.md >/dev/null; echo "check=$?")`
- THEN it prints exactly `readme=within`, then `check=0`

### Requirement: The documents record the launch copy and the route back to checks
`README.md`'s "Starting a run" SHALL tell the operator to launch the copy `factory launch-script` writes. Its "Where a human decides" SHALL list `launch-script` among the commands that are not writes, and its **Unstick** row SHALL name `resolve --to checks`. `docs/design.md` SHALL list `launch-script` in the live-store fence's read-only list and describe the `--to checks` route. `docs/changelog.md` SHALL hold one entry opening `After issue #109`, naming #112, `launch-script` and `--to checks`, numbered without a gap. README SHALL stay within its 1,225-line budget, and the maintained documents SHALL carry no whitespace error.

#### Scenario: The README, the design doc and the changelog describe the launch copy and the route back to checks
Run from the repository root of the checkout under test.
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "start=$(y $(sed -n '/^## Starting a run/,/^### Driving a ticket/p' README.md | grep -c 'factory launch-script')) unstick=$(y $(grep '^| \*\*Unstick\*\*' README.md | grep -c -- '--to checks')) writes=$(y $(printf '%s' "$R" | grep -o 'A write is any command except [^;]*;' | grep -c 'launch-script')) list=$(printf '%s' "$R" | grep -o 'A write is any command except [^;]*;' | grep -c .) fence=$(y $(grep '^\*\*Only the dispatcher writes a live store' docs/design.md | grep -c 'launch-script')) route=$(y $(grep -c -- '--to checks' docs/design.md)) readme=$(wc -l < README.md | awk '{print ($1 <= 1225 ? "within" : "over")}')"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #109 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e '#112' -e 'launch-script' -e '--to checks' | sort -u | grep -c .)"; E0=$(git hash-object -t tree /dev/null); git diff --check $E0 HEAD -- README.md docs dev .factory/context.md; echo "exit=$?")`
- THEN it prints exactly `start=yes unstick=yes writes=yes list=1 fence=yes route=yes readme=within`, `CONTIGUOUS`, `entries=1 terms=3`, `exit=0`, one per line

### Requirement: README shows the north star on its first screen
`README.md` SHALL hold one paragraph opening `**North star.**`, placed before "What problem it solves", that states the primary metric per hour of operator attention and names `docs/north-star.md`, `STATUS.md` and `docs/reviews/`. README MUST stay within its 1,225-line budget.

#### Scenario: README opens with the north-star paragraph and stays within its budget
- WHEN `(H=$(grep -n '^## What problem it solves$' README.md | cut -d: -f1); B=$(awk -v h="$H" 'NR>=h{exit} /^\*\*North star\.\*\*/{f=1} f&&/^$/{f=0} f' README.md | tr '\n' ' ' | tr -s ' '); echo "block=$(grep -c '^\*\*North star\.\*\*' README.md) top=$(printf '%s' "$B" | grep -c '^\*\*North star\.\*\*') metric=$(printf '%s' "$B" | grep -c 'per hour of operator attention') links=$(printf '%s' "$B" | grep -oF -e 'docs/north-star.md' -e 'STATUS.md' -e 'docs/reviews/' | sort -u | grep -c .) readme=$(wc -l < README.md | awk '{print ($1 <= 1225 ? "within" : "over")}')")`
- THEN it prints exactly `block=1 top=1 metric=1 links=3 readme=within`

