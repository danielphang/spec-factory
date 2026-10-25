# harness-docs

## Requirements

### Requirement: The documents record the change
`docs/changelog.md` SHALL hold entry 51 covering every part and stay numbered without a gap, and `README.md` SHALL describe the new `resolve` behaviour and relative environment paths.

#### Scenario: The changelog records the change in order
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; sed -n '/^51\. /p' docs/changelog.md | grep -oF -e BLOCKED -e '--replan' -e 'next free' -e 'error text' -e redispatch -e '-whitespace' -e context.md -e relative -e uncommitted | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `9`

#### Scenario: The README describes the new resolve verbs
- WHEN `(echo "replan=$(grep -c -- '--replan' README.md | awk '{print ($1 > 0)}') gap=$(grep -c 'has no .resolve. verb' README.md)")`
- THEN it prints `replan=1 gap=0`

#### Scenario: The README says relative paths resolve from the caller's directory
- WHEN `(grep -c 'relative .FACTORY_' README.md | awk '{print ($1 > 0)}')`
- THEN it prints `1`

### Requirement: The documents record the live-store guard
`docs/changelog.md` SHALL hold one entry for issue #45 recording the guard, numbered without a gap; `docs/design.md` SHALL describe the dispatcher marker and the run-directory rule; README's "Where a human decides" SHALL open with the marker's exact command form and say that the refusal deliberately does not name it; README SHALL say the final verifier run is listed as in flight and SHALL no longer say the factory's capabilities never entered the spec store.

#### Scenario: The changelog records the guard in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #45 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e FACTORY_DISPATCH -e 'in flight' -e throwaway -e 'exit 2' -e 'worktrees/' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `5`

#### Scenario: The design doc names the marker and the run-directory rule
- WHEN `(echo "design=$(grep -c FACTORY_DISPATCH docs/design.md | awk '{print ($1 > 0)}') dirs=$(grep FACTORY_DISPATCH docs/design.md | grep -c 'worktrees/' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `design=1 dirs=1`

#### Scenario: README tells the operator how to write during a run, first thing under Where a human decides
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^## What is built/p' README.md); J=$(echo "$H" | tr '\n' ' ' | tr -s ' '); echo "first=$(echo "$H" | sed -n '3p' | grep -c 'FACTORY_DISPATCH=1') command=$(echo "$J" | grep -c 'FACTORY_DISPATCH=1 [^ ]*bin/factory ') unnamed=$(echo "$J" | grep -c 'deliberately does not name the marker') export=$(echo "$J" | grep -ci 'never export') rundirs=$(echo "$J" | grep -c 'worktrees/')")`
- THEN it prints exactly `first=1 command=1 unnamed=1 export=1 rundirs=1`

#### Scenario: README says the final verifier run is listed as in flight
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(echo "$R" | grep -o 'does not list it as in flight' | grep -c .) listed=$(echo "$R" | grep -o 'lists it as in flight' | grep -c .)")`
- THEN it prints exactly `stale=0 listed=1`

#### Scenario: README no longer says the factory's capabilities never entered the spec store
- WHEN `(echo "bullet=$(grep -c 'Current truth for the factory itself' README.md) stale=$(grep -c 'never entered it' README.md)")`
- THEN it prints exactly `bullet=1 stale=0`

### Requirement: The documents describe the store branch
The design doc SHALL name the store branch `factory-store` and the never-tracked path rule. `docs/changelog.md` SHALL hold one contiguously numbered entry recording the change. `README.md` SHALL describe committing the store on its branch, `factory store migrate`, the `git clean -ffdx` hazard and a checkout from before the move, and SHALL no longer say that a store commit moves the integration branch or give `.factory/state/` as the live store's location.

#### Scenario: The design doc names the store branch and the path rule
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' docs/design.md | awk '{print ($1 > 0)}') tickets_branch=$(grep -c "${Q}tickets${Q} branch" docs/design.md) never_tracked=$(grep -c 'never tracked' docs/design.md | awk '{print ($1 > 0)}')")`
- THEN it prints `store_branch=1 tickets_branch=0 never_tracked=1`

#### Scenario: The changelog records the store branch in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep 'factory-store' | grep -c 'never tracked')`
- THEN it prints `CONTIGUOUS`, then `1`

#### Scenario: The README describes the store branch and the move
`old_cost` joins the page into one line first, because the retired clause is wrapped across two lines. `old_refs` counts only the places that give the live store's location, so a how-to may still name the path a store moves from.
- WHEN `(Q=$(printf '\140'); echo "store_branch=$(grep -c 'factory-store' README.md | awk '{print ($1 > 0)}') migrate=$(grep -c 'factory store migrate' README.md | awk '{print ($1 > 0)}') ffdx=$(grep -c -- '-ffdx' README.md | awk '{print ($1 > 0)}') premove=$(grep -c 'from before the move' README.md | awk '{print ($1 > 0)}') old_cost=$(tr '\n' ' ' < README.md | grep -c 'committing the store to the same branch') old_refs=$(grep -c "\.factory/state/\(log\|tickets\)\|(${Q}\.factory/state/${Q})\|at ${Q}\.factory/state/${Q}" README.md)")`
- THEN it prints `store_branch=1 migrate=1 ffdx=1 premove=1 old_cost=0 old_refs=0`

### Requirement: The planner labels checks per sub-ticket and may list tests an earlier sibling added
Every copy of the planner prompt (the `docs/design.md` §4 block, `docs/prompts/04-planner.md`, `factory/prompts/planner.md`) SHALL tell the planner to label each check against the sub-ticket's own base, to name interim tests, and to list a sibling-added test as `` `<file>[::<test>]` (added by <sibling ID>): <reason> ``; it MUST no longer say to label checks "the same way", and the design block and its `docs/prompts/` copy SHALL stay byte-identical.

#### Scenario: Every planner copy labels per sub-ticket and lists sibling tests
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0022-planner.txt; sed -n '/^## 4\. Planner/,/^## 5\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/04-planner.md factory/prompts/planner.md; do echo "own=$(grep -c "against this sub-ticket's own base" $f) sibling=$(grep -cF '(added by <sibling ID>)' $f) interim=$(grep -c '^  Interim tests: ' $f) copied=$(grep -c 'labelled NEW or REGRESSION the same way' $f)"; done; cmp -s $X docs/prompts/04-planner.md && echo verbatim || echo differs)`
- THEN it prints three lines, each exactly `own=1 sibling=1 interim=1 copied=0`, then `verbatim`

### Requirement: The spec writer lists the tests a decision overturns, and the critic checks for one left off
Every copy of the spec writer prompt SHALL carry the RULES bullet that starts `- Tests a decision overturns: `, and every copy of the critic prompt SHALL say under rubric 1 that a test pinning the old behaviour and `missing from "Tests to change" is a finding`.

#### Scenario: Every spec writer and critic copy carries the decision-overturns rule
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0022-sw.txt; for h in '2\. Spec writer' '3\. Spec critic'; do sed -n "/^## $h/,/^## [0-9]/p" docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p"; done > $X; echo "design: writer=$(grep -c '^- Tests a decision overturns: ' $X) critic=$(grep -c 'from "Tests to change" is a finding' $X)"; echo "docs/prompts: writer=$(grep -c '^- Tests a decision overturns: ' docs/prompts/02-spec-writer.md) critic=$(grep -c 'from "Tests to change" is a finding' docs/prompts/03-spec-critic.md)"; echo "factory/prompts: writer=$(grep -c '^- Tests a decision overturns: ' factory/prompts/spec_writer.md) critic=$(grep -c 'from "Tests to change" is a finding' factory/prompts/critic.md)")`
- THEN it prints exactly `design: writer=1 critic=1`, then `docs/prompts: writer=1 critic=1`, then `factory/prompts: writer=1 critic=1`

### Requirement: The preamble and the code reviewer accept a checked sibling entry
Every copy of the preamble SHALL allow an existing test listed `in your sub-ticket as added by an earlier sibling`, and every copy of the code reviewer prompt SHALL not block a test `the sub-ticket lists it there as added by an earlier sibling`.

#### Scenario: Every preamble and reviewer copy accepts a sibling entry
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0022-pr.txt; for h in 'Shared preamble' '6\. Code reviewer'; do sed -n "/^## $h/,/^## [0-9A-Z]/p" docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p"; done > $X; echo "design: guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' $X) review=$(grep -c 'or the sub-ticket lists it there as added by an earlier sibling' $X)"; echo "docs/prompts: guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' docs/prompts/00-preamble.md) review=$(grep -c 'or the sub-ticket lists it there as added by an earlier sibling' docs/prompts/06-code-reviewer.md)"; echo "factory/prompts: guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' factory/prompts/preamble.md) review=$(grep -c 'or the sub-ticket lists it there as added by an earlier sibling' factory/prompts/reviewer.md)")`
- THEN it prints exactly `design: guard=1 review=1`, then `docs/prompts: guard=1 review=1`, then `factory/prompts: guard=1 review=1`

### Requirement: Role runs receive the new rules
The system prompt that `run start` writes for a planner, spec writer and critic run SHALL contain that role's new rule and the new preamble sentence.

#### Scenario: Planner, spec writer and critic runs get the new rules in their system prompts
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; for i in 1 2 3; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-planner >/dev/null; bin/factory ticket set T-0002 status=ready-for-spec-writer >/dev/null; bin/factory ticket set T-0003 status=ready-for-critic >/dev/null; for p in planner:T-0001 spec_writer:T-0002 critic:T-0003; do bin/factory run start --role ${p%%:*} --ticket ${p##*:} >/dev/null 2>&1; done; P=$(ls $FACTORY_STATE/runs/*-planner/system-prompt.txt); W=$(ls $FACTORY_STATE/runs/*-spec_writer/system-prompt.txt); C=$(ls $FACTORY_STATE/runs/*-critic/system-prompt.txt); echo "planner own=$(grep -c "against this sub-ticket's own base" $P) sibling=$(grep -cF '(added by <sibling ID>)' $P) guard=$(grep -c '^in your sub-ticket as added by an earlier sibling' $P) writer=$(grep -c '^- Tests a decision overturns: ' $W) critic=$(grep -c 'from "Tests to change" is a finding' $C)")`
- THEN it prints exactly `planner own=1 sibling=1 guard=1 writer=1 critic=1`

### Requirement: The documents record the sibling-tests check
`docs/design.md` SHALL describe the check in a paragraph that starts `**Tests a sibling added.**`, in piece 8 and in the spec approval gate row, and SHALL no longer call the gate's list the only authorization to alter an existing test; `docs/changelog.md` SHALL hold an entry for issue #40 and stay numbered without a gap; and `README.md` SHALL describe the check and the new `--ruling` case.

#### Scenario: The design doc describes the check
- WHEN `(echo "piece8=$(grep '^| 8 |' docs/design.md | grep -c 'added by that sibling') gate=$(grep '^| Spec approval |' docs/design.md | grep -c 'a test an earlier sibling added') stale=$(grep -c 'which is the only authorization to alter an existing test' docs/design.md) check=$(grep -c '^\*\*Tests a sibling added\.\*\*.*BLOCKED from harness:' docs/design.md)")`
- THEN it prints exactly `piece8=1 gate=1 stale=0 check=1`

#### Scenario: The changelog records issue 40's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #40 ' docs/changelog.md | grep -oF -e 'own base' -e 'added by' -e 'BLOCKED from harness' -e 'Decision' -e 'critic rubric 1' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the sibling tests check and its ruling
- WHEN `(echo "built=$(grep -c '^- \*\*Sibling tests check\.\*\*' README.md) ruling=$(grep '^| \*\*Unstick\*\*' README.md | grep -c 'a test no merged sibling added')")`
- THEN it prints exactly `built=1 ruling=1`

### Requirement: The documents record the declared-path rule
The "## 5. Implementer" and "## 7. Verifier" blocks of `docs/design.md` SHALL carry the declared-path rule and stay verbatim copies of `docs/prompts/05-implementer.md` and `docs/prompts/07-verifier.md`. The run copies under `factory/prompts/` SHALL differ from those files only by the fills they had on `main`. `docs/changelog.md` SHALL hold one entry for issue #49, numbered without a gap.

#### Scenario: The design blocks and their copies carry the rule and stay in step
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); for r in "5. Implementer|05-implementer.md|implementer" "7. Verifier|07-verifier.md|verifier"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) rule=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -c 'A protected path the sub-ticket declares is not an escalation') fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly `implementer copy=SAME rule=1 fill=unchanged`, then `verifier copy=SAME rule=1 fill=unchanged`. `copy=SAME`: the design block equals its `docs/prompts/` file. `rule=1`: that file carries the rule. `fill=unchanged`: the run copy under `factory/prompts/` differs from the documented copy only where it did on `main`.

#### Scenario: The changelog records the declared-path rule in a contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep -E '^[0-9]+\. ' docs/changelog.md | grep -F '#49' | grep -c 'ESCALATIONS')`
- THEN it prints `CONTIGUOUS`, then `1`

### Requirement: The documents record the small-change lane
`docs/changelog.md` SHALL hold one entry for issue #48 recording the lane, numbered without a gap. `docs/design.md` and `README.md` SHALL describe the whole-spec sub-ticket and gate-command paths.

#### Scenario: The changelog records the small-change lane in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #48 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e 'paths' -e SKIPPED -e 'plan whole-spec' -e NEEDS-SPLIT -e seams | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `5`

#### Scenario: The design doc and README describe both skips
- WHEN `(echo "design=$(grep -c 'whole-spec' docs/design.md | awk '{print ($1 > 0)}') gate=$(grep '^| 11 | Gate runner' docs/design.md | grep -c 'SKIPPED') readme=$(grep -c 'plan whole-spec' README.md | awk '{print ($1 > 0)}') skipped=$(grep -c 'SKIPPED' README.md | awk '{print ($1 > 0)}') stale=$(grep -c 'The build workflow runs the planner, which' README.md)")`
- THEN it prints exactly `design=1 gate=1 readme=1 skipped=1 stale=0`

### Requirement: Every role is told to wait for its own commands
Every copy of the shared preamble SHALL carry the bullet that starts `- Run every command in the foreground and wait for it to finish.` and says `Never end your turn while a command you started is still running`. The design block and both files MUST stay byte-identical, and every role run's system prompt SHALL carry the bullet.

#### Scenario: Every preamble copy carries the wait rule and the copies stay identical
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0032-pre.txt; sed -n '/^## Shared preamble/,/^## [0-9]/p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/00-preamble.md factory/prompts/preamble.md; do echo "fg=$(grep -c '^- Run every command in the foreground and wait for it to finish\.$' $f) end=$(tr '\n' ' ' < $f | tr -s ' ' | grep -c 'Never end your turn while a command you started is still running')"; done; cmp -s $X docs/prompts/00-preamble.md && cmp -s docs/prompts/00-preamble.md factory/prompts/preamble.md && echo verbatim || echo differs)`
- THEN it prints three lines, each exactly `fg=1 end=1`, then `verbatim`

#### Scenario: Implementer, reviewer and verifier run prompts carry the wait rule, and only the reviewer's carries the judge-the-diff rule
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && for r in implementer reviewer verifier; do P=$(prompt $r); echo "$r fg=$(echo "$P" | grep -c 'Never end your turn while a command you started is still running') judge=$(echo "$P" | grep -c 'Do not run the test suite or the gate commands')"; done)`
- THEN it prints exactly `implementer fg=1 judge=0`, `reviewer fg=1 judge=1`, `verifier fg=1 judge=0`, one per line

### Requirement: The code reviewer judges the diff and leaves the suite and the gate to the verifier
Every copy of the code reviewer prompt SHALL say `Do not run the test suite or the gate commands: the verifier runs them on the same head`, and SHALL allow a narrow command that confirms a specific finding. The design block SHALL stay a verbatim copy of `docs/prompts/06-code-reviewer.md`, and the run copy SHALL differ from it only by the fills it had on `main`. The reviewer's composed input MUST NOT list the gate commands, while the implementer's and the verifier's inputs still SHALL.

#### Scenario: Every reviewer copy carries the rule and the copies stay in step
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0032-rev.txt; T=$(mktemp -d); sed -n '/^## 6\. Code reviewer/,/^## 7\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; do J=$(tr '\n' ' ' < $f | tr -s ' '); echo "judge=$(echo "$J" | grep -c 'Do not run the test suite or the gate commands: the verifier runs them on the same head') narrow=$(echo "$J" | grep -c 'You may run a narrow command to confirm a specific finding')"; done; git show main:factory/prompts/reviewer.md > $T/a; git show main:docs/prompts/06-code-reviewer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/06-code-reviewer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/reviewer.md docs/prompts/06-code-reviewer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `judge=1 narrow=1`, then `copy=SAME fill=unchanged`

#### Scenario: The reviewer's input no longer hands it the gate commands, and the implementer's and verifier's still do
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && for r in reviewer verifier implementer; do [ $r = implementer ] && bin/factory ticket set T-0001.1 status=ready-for-implementer 'in_flight=[]' >/dev/null; R=$(bin/factory run start --role $r --ticket T-0001.1 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); bin/factory run compose ${R:-none} >/dev/null 2>&1; I=$FACTORY_STATE/runs/${R:-none}/input.md; echo "$r gates=$(grep -c 'Gate commands (run each from your worktree' $I 2>/dev/null) told=$(grep -c 'The verifier runs the gate commands on this head; you do not run them' $I 2>/dev/null)"; done)`
- THEN it prints exactly `reviewer gates=0 told=1`, `verifier gates=1 told=0`, `implementer gates=1 told=0`, one per line

### Requirement: The documents record the empty-output route
`docs/design.md` SHALL state the EMPTY-OUTPUT rule and its two routing-table rows, and SHALL list a second EMPTY-OUTPUT among the park reasons. `README.md` SHALL no longer say that a run is parked for exceeding a budget, and SHALL describe the empty-output retry. `docs/changelog.md` SHALL hold an entry for issue #41, numbered without a gap.

#### Scenario: The design doc states the EMPTY-OUTPUT rule, its rows and its park
- WHEN `(echo "rule=$(grep -c '^- A role run that ends without writing its output is EMPTY-OUTPUT' docs/design.md) rows=$(grep -c '^| Any role | EMPTY-OUTPUT' docs/design.md) parks=$(grep '^- A non-empty ESCALATIONS line' docs/design.md | grep -c 'a second EMPTY-OUTPUT in a row') kill=$(grep -c 'never recorded as a budget kill' docs/design.md)")`
- THEN it prints exactly `rule=1 rows=2 parks=1 kill=1`

#### Scenario: README drops the budget park and describes the empty-output retry
- WHEN `(echo "budget=$(grep -c 'exceeding its budget\|over budget' README.md) built=$(grep -c '^- \*\*Empty output\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c 'ended without output twice')")`
- THEN it prints exactly `budget=0 built=1 unstick=1`

#### Scenario: The changelog records issue 41 without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #41 ' docs/changelog.md | grep -oF -e EMPTY-OUTPUT -e foreground -e 'last message' -e 're-dispatched once' -e 'gate commands' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

### Requirement: The spec writer and the critic carry the turn-economy rules
Every copy of the spec writer prompt SHALL tell it to batch independent reads and commands, read line ranges once grep has found them, keep long output in a scratch file, and write the spec in as few writes as it can. Every copy of the critic prompt SHALL carry the same reading rules, its minimum spot-check, a rule that it runs no test suite, the rule for picking an acceptance command, a sentence allowing a small experiment in its scratch directory to confirm a finding, and the rule that turns a claim needing a suite run or a build of the change into a finding or a question; it MUST NOT cap a claim at a number of paths and commands or forbid a clone, worktree or prototype. Each design block MUST stay byte-identical to its `docs/prompts/` copy, and each run copy SHALL differ from it only as it did on `main`.

#### Scenario: Every critic copy drops the cap and the no-build rule and keeps the rest; every writer copy keeps its rules
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); printf '%s\n' 'Put independent reads and commands in one turn' 'read that line range, not the whole file' 'to a file in your scratch directory and grep or tail it' > $T/both; { cat $T/both; echo 'Write the spec in as few writes as you can'; } > $T/spec_writer; { cat $T/both; printf '%s\n' 'Spot-check at least 2 cited paths and 1 acceptance command yourself' 'Run no test suite' 'Pick an acceptance command that runs no test suite' 'small experiment in your scratch directory' 'is a finding for the writer, or a question'; } > $T/critic; printf '%s\n' 'Ground any one claim' 'build nothing' 'no clone, worktree or prototype' > $T/gone; for r in "2. Spec writer|02-spec-writer.md|spec_writer" "3. Spec critic|03-spec-critic.md|critic"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) doc=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -oF -f $T/$f | sort -u | grep -c .)/$(grep -c . $T/$f) run=$(tr '\n' ' ' < factory/prompts/$f.md | tr -s ' ' | grep -oF -f $T/$f | sort -u | grep -c .)/$(grep -c . $T/$f) gone=$(for g in docs/prompts/$c factory/prompts/$f.md; do tr '\n' ' ' < $g | tr -s ' ' | grep -oF -f $T/gone; done | grep -c .) fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly `spec_writer copy=SAME doc=4/4 run=4/4 gone=0 fill=unchanged`, then `critic copy=SAME doc=8/8 run=8/8 gone=0 fill=unchanged`. `doc` and `run` count the kept or added phrases found in the documented copy and the run copy, each joined into one line so a phrase may wrap; `gone` counts the removed phrases found in either.

### Requirement: Spec writer and critic runs receive the turn-economy rules
The system prompt that `run start` writes for a spec writer run SHALL contain the writer's turn-economy rule. The one it writes for a critic run SHALL contain the critic's reading rules, its no-suite rule and the sentence allowing a small scratch experiment, and MUST NOT contain the per-claim cap or the no-build rule.

#### Scenario: A critic run's prompt has the no-suite rule and the scratch allowance, and no cap or build ban
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; for i in 1 2; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-spec-writer >/dev/null; bin/factory ticket set T-0002 status=ready-for-critic >/dev/null; bin/factory run start --role spec_writer --ticket T-0001 >/dev/null 2>&1; bin/factory run start --role critic --ticket T-0002 >/dev/null 2>&1; W=$(tr '\n' ' ' < $FACTORY_STATE/runs/run-0001-spec_writer/system-prompt.txt | tr -s ' '); C=$(tr '\n' ' ' < $FACTORY_STATE/runs/run-0002-critic/system-prompt.txt | tr -s ' '); echo "spec_writer batch=$(printf "%s" "$W" | grep -c 'Put independent reads and commands in one turn') writes=$(printf "%s" "$W" | grep -c 'Write the spec in as few writes as you can')"; echo "critic batch=$(printf "%s" "$C" | grep -c 'Put independent reads and commands in one turn') suite=$(printf "%s" "$C" | grep -c 'Run no test suite') scratch=$(printf "%s" "$C" | grep -c 'small experiment in your scratch directory') cap=$(printf "%s" "$C" | grep -c 'Ground any one claim') build=$(printf "%s" "$C" | grep -c 'build nothing')")`
- THEN it prints exactly `spec_writer batch=1 writes=1`, then `critic batch=1 suite=1 scratch=1 cap=0 build=0`

### Requirement: The documents record the turn-economy change
`docs/changelog.md` SHALL hold one entry for issue #73, numbered without a gap. `docs/principles.md` principle 2 SHALL name the critic's no-suite rule among its mechanisms and SHALL no longer say the critic builds nothing.

#### Scenario: Principle 2 names the critic's no-suite rule and no longer its build ban
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; P=$(sed -n '/^### 2\. /,/^### 3\. /p' docs/principles.md | tr '\n' ' ' | tr -s ' '); echo "entries73=$(grep -c '^[0-9]*\. After issue #73 ' docs/changelog.md) implemented=$(printf '%s' "$P" | grep -c 'runs no test suite (#73') builds=$(printf '%s' "$P" | grep -c 'builds nothing')")`
- THEN it prints exactly `CONTIGUOUS`, then `entries73=1 implemented=1 builds=0`

### Requirement: The documents record the critic revert
`docs/changelog.md` SHALL hold one entry for issue #74, numbered without a gap, that records the replay result and the two removed rules. The Spiking section of `docs/principles.md` SHALL no longer bound the critic to two paths and one command or say it does not build, SHALL say the critic may run a small scratch check, SHALL say vetting a whole approach belongs to the spec writer or a spike, and SHALL record the replay.

#### Scenario: The changelog records the revert in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #74 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e '#74' -e replay -e 'per-claim cap' -e 'no-build rule' -e 'no test suite' -e UV_PYTHON_INSTALL_DIR -e brace-list | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `7`

#### Scenario: The Spiking section allows a small scratch check and records the replay
- WHEN `(X=$(sed -n '/^## Spiking/,$p' docs/principles.md | tr '\n' ' ' | tr -s ' '); echo "bound=$(printf '%s' "$X" | grep -c 'two paths, one command') nobuild=$(printf '%s' "$X" | grep -c 'it does not build') scratch=$(printf '%s' "$X" | grep -c 'small scratch check') whole=$(printf '%s' "$X" | grep -c 'vetting a whole approach belongs to the spec writer') replay=$(printf '%s' "$X" | grep -c 'replay')")`
- THEN it prints exactly `bound=0 nobuild=0 scratch=1 whole=1 replay=1`

### Requirement: The documents record the capability index
The triage prompt's design block, its `docs/prompts/` copy and the runtime prompt SHALL each carry the `Capabilities:` output line. `docs/design.md` and the README's Triage, Spec writer and Spec critic rows MUST describe the capability index. `docs/changelog.md` MUST have an entry for issue #75.

#### Scenario: The prompt copies, design, README and changelog name the capability index
- WHEN `(echo "docs-copy=$(grep -c '^Capabilities:' docs/prompts/01-triage.md) runtime=$(grep -c '^Capabilities:' factory/prompts/triage.md) changelog=$(grep -c '^[0-9]*\. After issue #75 ' docs/changelog.md) design=$(grep -q 'capability index' docs/design.md && echo y || echo n) readme=$(grep -E '^\| (Triage|Spec writer|Spec critic) \(' README.md | grep -c 'capability index')")`
- THEN it prints exactly `docs-copy=1 runtime=1 changelog=1 design=y readme=3`

### Requirement: The documents describe the whole decision log for the spec writer, critic and planner
`docs/design.md` and the README's Spec writer, Spec critic and Planner rows MUST say that those roles receive the whole decision log, and neither MUST mention a decision index. `docs/changelog.md` SHALL have an entry for issue #78.

#### Scenario: The design, README and changelog describe the whole decision log and no decision index
- WHEN `(echo "design-index=$(grep -c 'decision index' docs/design.md) design-whole=$(grep -c 'They and the planner receive the whole decision log' docs/design.md) readme-index=$(grep -c 'decision index' README.md) readme-whole=$(grep -E '^\| (Spec writer|Spec critic|Planner) \(' README.md | grep -c 'the whole decision log') changelog=$(grep -c '^[0-9]*\. After issue #78 ' docs/changelog.md)")`
- THEN it prints exactly `design-index=0 design-whole=1 readme-index=0 readme-whole=3 changelog=1`

### Requirement: The documents record superseded plans
`docs/design.md` SHALL say, in its rule for a sub-ticket closed by the human, that a new plan from a later approved version supersedes the earlier plan's unmerged sub-tickets. `README.md` SHALL carry a "Re-plan after a re-spec" bullet. `docs/changelog.md` SHALL hold one entry for issue #77, numbered without a gap.

#### Scenario: The design doc, README and changelog record superseded plans
- WHEN `(echo "design=$(grep 'sub-ticket closed by the human' docs/design.md | grep -c supersede) readme=$(grep -c '^- \*\*Re-plan after a re-spec\.\*\*' README.md) changelog=$(grep '^[0-9]*\. After issue #77 ' docs/changelog.md | grep -oF -e superseded -e planned_from -e 'Depends on' | sort -u | grep -c .) $(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md)")`
- THEN it prints exactly `design=1 readme=1 changelog=3 CONTIGUOUS`

### Requirement: The prompts tell the reviewer what the gate checks and the spec writer how to declare
Every copy of the code reviewer prompt (the `docs/design.md` §6 block, `docs/prompts/06-code-reviewer.md`, `factory/prompts/reviewer.md`) SHALL carry check 6's new last sentence and MUST NOT say `will require a human approval`. Every copy of the spec writer prompt SHALL give the `Protected paths:` line under Risk and the rule of one path or glob per entry with no brace lists. Each design block and its `docs/prompts/` file MUST stay byte-identical, and each `factory/prompts/` copy SHALL differ from its `docs/prompts/` file only where it did on `main`.

#### Scenario: Every reviewer prompt copy states what the merge gate checks
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0033-rev.txt; T=$(mktemp -d); sed -n '/^## 6\. Code reviewer/,/^## 7\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; do J=$(tr '\n' ' ' < $f | tr -s ' '); echo "gate=$(echo "$J" | grep -c "The merge gate merges a path the approved spec's Risk section declares with no further approval, and refuses and parks one it does not declare") promise=$(echo "$J" | grep -c 'will require a human approval')"; done; git show main:factory/prompts/reviewer.md > $T/a; git show main:docs/prompts/06-code-reviewer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/06-code-reviewer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/reviewer.md docs/prompts/06-code-reviewer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `gate=1 promise=0`, then `copy=SAME fill=unchanged`

#### Scenario: Every spec writer prompt copy gives the declaration line
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0033-sw.txt; T=$(mktemp -d); sed -n '/^## 2\. Spec writer/,/^## 3\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md; do echo "reads=$(grep -c 'declared on one line the merge gate reads:$' $f) form=$(grep -c '^ *Protected paths: none | .<path or glob>., .<path or glob>.$' $f) braces=$(grep -c '^ *one path or glob per entry, no brace lists$' $f)"; done; git show main:factory/prompts/spec_writer.md > $T/a; git show main:docs/prompts/02-spec-writer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/02-spec-writer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/spec_writer.md docs/prompts/02-spec-writer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `reads=1 form=1 braces=1`, then `copy=SAME fill=unchanged`

### Requirement: The documents record the protected-path rule at merge
`docs/design.md` SHALL drop the per-PR approval for protected paths, describe the declared-path rule in piece 8 and the Protected paths gate row, and route a reviewer ESCALATE back to its checks; `docs/changelog.md` SHALL hold an entry for issue #57 and stay numbered without a gap; and `README.md` SHALL describe the check and `--accept-paths`.

#### Scenario: The design doc drops the per-PR approval for protected paths
- WHEN `(echo "gates=$(grep -c 'a PR touching a protected path, the daily escalation queue' docs/design.md) either=$(grep -c 'A change to either needs a human approval record before it merges' docs/design.md) onpr=$(grep -c 'any other guardrail or protected path needs a human approval on the PR itself' docs/design.md) piece8=$(grep '^| 8 |' docs/design.md | grep -c 'Protected paths:') piece9=$(grep -c 'review protected PRs' docs/design.md) gaterow=$(grep '^| Protected paths |' docs/design.md | grep -c -- '--accept-paths') stale=$(grep -c 'records the piece-8 approval; the merge gate does not merge without it' docs/design.md) reviewer_rule=$(grep -c '^  - A reviewer ESCALATE returns to its checks' docs/design.md) old_route=$(grep -c 'or a reviewer ESCALATE returns to the implementer' docs/design.md)")`
- THEN it prints exactly `gates=0 either=0 onpr=0 piece8=1 piece9=0 gaterow=1 stale=0 reviewer_rule=1 old_route=0`

#### Scenario: The changelog records issue 57's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #57 ' docs/changelog.md | grep -oF -e 'Risk' -e '--accept-paths' -e 'BLOCKED from merge gate' -e 'checks' -e 'Protected paths:' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the protected-path check and the new resolve verb
- WHEN `(echo "built=$(grep -c '^- \*\*Protected paths at merge\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c -- '--accept-paths') merges=$(sed -n '/^- \*\*Merges, one at a time\.\*\*/,/^- \*\*Setting up the store\.\*\*/p' README.md | grep -c 'Risk section' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `built=1 unstick=1 merges=1`

### Requirement: The implementer, verifier, code reviewer, planner and triage carry the reading rules
Every copy of the implementer, verifier, code reviewer, planner and triage prompts (the `docs/design.md` block, its `docs/prompts/` file and the `factory/prompts/` run copy) SHALL carry the Turn economy paragraph in the critic's words, and MUST NOT carry the spec writer's `as few writes as you can`. Each design block MUST stay byte-identical to its `docs/prompts/` file, and each run copy SHALL differ from it only as it did on `main`.

#### Scenario: The five role prompts carry the critic's reading paragraph in every copy
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); P='Turn economy: every turn re-sends everything read so far, so a wasted turn or a long printout costs again on every later turn. Put independent reads and commands in one turn. Once grep has found the lines you need, read that line range, not the whole file. Send long output to a file in your scratch directory and grep or tail it, rather than printing it in full.'; for r in "1. Triage|01-triage.md|triage" "4. Planner / decomposer|04-planner.md|planner" "5. Implementer|05-implementer.md|implementer" "6. Code reviewer|06-code-reviewer.md|reviewer" "7. Verifier|07-verifier.md|verifier"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) doc=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -oF "$P" | grep -c .) run=$(tr '\n' ' ' < factory/prompts/$f.md | tr -s ' ' | grep -oF "$P" | grep -c .) writes=$(cat docs/prompts/$c factory/prompts/$f.md | tr '\n' ' ' | tr -s ' ' | grep -c 'as few writes as you can') fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly five lines: `triage copy=SAME doc=1 run=1 writes=0 fill=unchanged`, then the same for `planner`, `implementer`, `reviewer` and `verifier`. `copy=SAME`: the design block equals its `docs/prompts/` file. `doc` and `run`: the documented copy and the run copy each carry the whole paragraph once, joined into one line so it may wrap. `writes=0`: neither carries the spec writer's one-write sentence. `fill=unchanged`: the run copy differs from the documented copy only where it did on `main`.

### Requirement: Runs of the five roles receive the reading rules
The system prompt that `run start` writes for an implementer, code reviewer, verifier, triage and planner run SHALL contain the Turn economy paragraph once, and MUST NOT contain `as few writes as you can`.

#### Scenario: Implementer, reviewer and verifier runs receive the reading paragraph
Needs the GIVEN block of "Implementer and verifier run prompts carry the declared-path rule" (current truth, role-escalations) run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0029-prompt.sh && P='Turn economy: every turn re-sends everything read so far, so a wasted turn or a long printout costs again on every later turn. Put independent reads and commands in one turn. Once grep has found the lines you need, read that line range, not the whole file. Send long output to a file in your scratch directory and grep or tail it, rather than printing it in full.'; for r in implementer reviewer verifier; do X=$(prompt $r); echo "$r preamble=$(echo "$X" | grep -c "UNTRUSTED INPUT") economy=$(echo "$X" | grep -cF "$P") writes=$(echo "$X" | grep -c 'as few writes as you can')"; done)`
- THEN it prints exactly `implementer preamble=1 economy=1 writes=0`, `reviewer preamble=1 economy=1 writes=0`, `verifier preamble=1 economy=1 writes=0`, one per line. `preamble=1` shows the run started and its prompt was read.

#### Scenario: Triage and planner runs receive the reading paragraph
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; P='Turn economy: every turn re-sends everything read so far, so a wasted turn or a long printout costs again on every later turn. Put independent reads and commands in one turn. Once grep has found the lines you need, read that line range, not the whole file. Send long output to a file in your scratch directory and grep or tail it, rather than printing it in full.'; for i in 1 2; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-triage >/dev/null; bin/factory ticket set T-0002 status=ready-for-planner >/dev/null; bin/factory run start --role triage --ticket T-0001 >/dev/null 2>&1; bin/factory run start --role planner --ticket T-0002 >/dev/null 2>&1; for r in triage planner; do X=$(tr '\n' ' ' < $(ls $FACTORY_STATE/runs/*-$r/system-prompt.txt) | tr -s ' '); echo "$r preamble=$(printf '%s' "$X" | grep -c 'UNTRUSTED INPUT') economy=$(printf '%s' "$X" | grep -cF "$P") writes=$(printf '%s' "$X" | grep -c 'as few writes as you can')"; done)`
- THEN it prints exactly `triage preamble=1 economy=1 writes=0`, then `planner preamble=1 economy=1 writes=0`

### Requirement: The documents record the reading rules for the five roles
`docs/changelog.md` SHALL hold one entry for issue #76, numbered without a gap, naming the five roles and the operator's replay, and the changelog SHALL end with its closing "Declined:" line.

#### Scenario: The changelog records the reading rules for the five roles in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #76 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oiF -e '#76' -e implementer -e verifier -e 'code reviewer' -e planner -e triage -e replay | tr A-Z a-z | sort -u | grep -c .) footer=$(tail -1 docs/changelog.md | grep -c '^Declined: a dedicated merge agent')")`
- THEN it prints `CONTIGUOUS`, then `entries=1 terms=7 footer=1`

### Requirement: The critic's rubric asks about cross-ticket dependencies
The critic's system prompt MUST tell it to check each scenario against approved changes not yet archived and to require the scenario's setup to hold whichever of the two merges first, and the runtime critic prompt SHALL stay a copy of `docs/prompts/03-spec-critic.md` with its round placeholder filled.

#### Scenario: A critic run's system prompt carries the cross-ticket rule
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/s; printf '# F\n\nDo x.\n' > $T/req.md; bin/factory ticket new --file $T/req.md >/dev/null; bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null; bin/factory ticket transition T-0001 --to ready-for-critic --by t >/dev/null; R=$(bin/factory run start --role critic --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); echo "rule=$(grep -c 'whichever of the two merges first' $FACTORY_STATE/runs/${R:-none}/system-prompt.txt 2>/dev/null)")`
- THEN it prints exactly `rule=1`

#### Scenario: The runtime critic prompt stays a copy of the documented one
- WHEN `(diff <(sed 's/{2}/2/' docs/prompts/03-spec-critic.md) factory/prompts/critic.md >/dev/null && echo copies=same || echo copies=differ)`
- THEN it prints exactly `copies=same`

### Requirement: The documents record spec amendment, spec drift and the cross-ticket check
`docs/changelog.md` SHALL hold one entry, numbered without a gap, covering the amend command with its intent flag, the drift check and the critic's cross-ticket check; `docs/design.md` SHALL name `factory spec amend` and `--intent unchanged`, carry a Spec drift paragraph and give the critic the approved changes not yet archived in its routing row; and README SHALL list the command under "Where a human decides" and the feature under Built.

#### Scenario: The changelog records the change in one contiguous entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. ' docs/changelog.md | grep -F 'factory spec amend'); echo "$E" | grep -c .; echo "$E" | grep -oF -e '--intent' -e 'in flight' -e tasks.md -e 'spec drift' -e 'not yet archived' -e whichever | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `6`

#### Scenario: The design doc names the amend command, its intent flag, spec drift and the critic's new input
- WHEN `(echo "amend=$(grep -c 'factory spec amend' docs/design.md | awk '{print ($1 > 0)}') intent=$(grep -c -- '--intent unchanged' docs/design.md | awk '{print ($1 > 0)}') drift=$(grep -c '^\*\*Spec drift\.\*\*' docs/design.md) row=$(grep '^| Spec writer | READY-FOR-CRITIC' docs/design.md | grep -c 'not yet archived')")`
- THEN it prints exactly `amend=1 intent=1 drift=1 row=1`

#### Scenario: README lists the amend command and the drift check
- WHEN `(H=$(sed -n '/^## Where a human decides/,/^### What you read at each stop/p' README.md); B=$(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' README.md); echo "amend=$(echo "$H" | grep -c 'factory spec amend' | awk '{print ($1 > 0)}') intent=$(echo "$H" | grep -c -- '--intent' | awk '{print ($1 > 0)}') built=$(echo "$B" | grep -c '^- \*\*Spec amendment and drift\.\*\*')")`
- THEN it prints exactly `amend=1 intent=1 built=1`

### Requirement: The documents record the environment sync and the dropped virtual environment
`docs/design.md` SHALL name `environment_sync` and say the wrapper drops `VIRTUAL_ENV`. `factory/instance.template.yaml` SHALL carry an `environment_sync` key. `README.md` SHALL name `environment_sync` and `VIRTUAL_ENV`. `docs/changelog.md` SHALL hold one entry for issue #51 recording the change, numbered without a gap.

#### Scenario: The design doc, template and README name the sync and the dropped virtual environment
- WHEN `(echo "design=$(grep -c environment_sync docs/design.md | awk '{print ($1 > 0)}') design_venv=$(grep -c VIRTUAL_ENV docs/design.md | awk '{print ($1 > 0)}') template=$(grep -c '^environment_sync:' factory/instance.template.yaml) readme=$(grep -c environment_sync README.md | awk '{print ($1 > 0)}') readme_venv=$(grep -c VIRTUAL_ENV README.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `design=1 design_venv=1 template=1 readme=1 readme_venv=1`

#### Scenario: The changelog records the environment sync in one entry
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #51 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e environment_sync -e VIRTUAL_ENV -e PYTHONHOME -e 'already synced' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `4`

### Requirement: The documents describe the driver
`README.md` MUST describe `factory drive` under "Starting a run", its `claude -p` role processes under "What depends on Claude Code", the driver among the built pieces and its status file in the store's file table, and SHALL no longer list per-role effort as not built; `docs/design.md` SHALL name the driver, and `docs/changelog.md` SHALL hold an entry for issue #65.

#### Scenario: The documents describe the driver
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; r=README.md; echo "starting=$(y $(sed -n '/^## Starting a run/,/^### Filing a request/p' $r | grep -c 'factory drive')) depends=$(y $(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r | grep -c 'claude -p')) built=$(y $(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' $r | grep -c 'factory drive')) effort-gap=$(y $(grep -c 'none has an effort level' $r)) drive-row=$(y $(grep -cE '^\| `drive/' $r)) design=$(y $(grep -c 'factory drive' docs/design.md)) changelog=$(y $(grep -cE '^[0-9]+\. After issues? [^(]*#65' docs/changelog.md))")`
- THEN it prints exactly `starting=yes depends=yes built=yes effort-gap=no drive-row=yes design=yes changelog=yes`

### Requirement: The documents record the sibling-merge exception and the start-failure ruling
`docs/design.md`'s Spec drift paragraph SHALL name `main_after` as not drift and its routing rules SHALL name the `harness-bug: run start implementer` ruling; README's Unstick row SHALL name it, and its "Spec amendment and drift" bullet SHALL say a sibling's merge is not drift and SHALL no longer say the check has not yet fired; and `docs/changelog.md` SHALL hold one entry for issue #85, numbered without a gap.

#### Scenario: The design doc, README and changelog record both changes
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; B=$(sed -n '/^- \*\*Spec amendment and drift\.\*\*/,/^- \*\*Re-plan after a re-spec\.\*\*/p' README.md); echo "design-drift=$(y $(grep '^\*\*Spec drift\.\*\*' docs/design.md | grep -c main_after)) design-ruling=$(y $(grep -c 'harness-bug: run start implementer' docs/design.md)) unstick=$(y $(grep '^| \*\*Unstick\*\*' README.md | grep -c 'harness-bug: run start implementer')) bullet-sibling=$(y $(echo "$B" | grep -c 'not drift')) bullet-stale=$(y $(echo "$B" | grep -c 'has not yet fired'))"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #85 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e '#85' -e main_after -e 'harness-bug: run start implementer' | sort -u | grep -c .)`
- THEN it prints exactly `design-drift=yes design-ruling=yes unstick=yes bullet-sibling=yes bullet-stale=no`, then `CONTIGUOUS`, then `1`, then `3`

### Requirement: The documents record the driver's exemption and its same-ticket guard
`docs/changelog.md` SHALL hold one entry for issue #86, numbered without a gap. README's `factory drive` how-to SHALL no longer tell the operator to put the marker in front of the command, and SHALL say that the driver is exempt and what it refuses on the same ticket. The opening of README's "Where a human decides" SHALL say the driver is exempt. `docs/design.md`'s fence paragraph SHALL state the exemption and the same-ticket guard, and SHALL no longer say the driver meets the fence like any write.

#### Scenario: The documents describe the driver's exemption and its same-ticket guard
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; c() { tr '\n' ' ' | tr -s ' ' | grep -ci -- "$1"; }; r=README.md; D=$(sed -n '/^### Driving a ticket from a shell with `factory drive`/,/^Each role process/p' $r); H=$(sed -n '/^## Where a human decides/,/^```/p' $r); G=$(grep '^\*\*Only the dispatcher writes a live store during a run\.\*\*' docs/design.md); echo "changelog=$(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md) entry=$(grep -c '^[0-9]*\. After issue #86 ' docs/changelog.md) step=$(echo "$D" | c 'put `FACTORY_DISPATCH=1` in front of the command') drive=$(y $(echo "$D" | c exempt)),$(y $(echo "$D" | c 'same ticket')) human=$(y $(echo "$H" | c exempt)) design=$(y $(echo "$G" | c exempt)),$(y $(echo "$G" | c 'same ticket')),$(echo "$G" | c 'like any write when it starts')")`
- THEN it prints exactly `changelog=CONTIGUOUS entry=1 step=0 drive=yes,yes human=yes design=yes,yes,0`

### Requirement: The documents record factory stats
README SHALL list `stats` among the commands that are not writes, say under "Accepting a harness revision" that it skips the lock, describe it in a how-to subsection "Counting what each role catches and costs", in "What depends on Claude Code" and under **Built**; `docs/design.md` SHALL list it in the fence paragraph's read-only list, name it in the lock clause, and cite it in the model-per-role paragraph; `docs/principles.md` §4 SHALL name it as implemented and no longer say "1 BLOCKING finding in total"; and `docs/changelog.md` SHALL hold one entry for issues #70 and #61, numbered without a gap.

#### Scenario: The documents record factory stats
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; j() { tr '\n' ' ' | tr -s ' '; }; r=README.md; H=$(sed -n '/^## Where a human decides/,/^```/p' $r | j); L=$(sed -n '/^### Accepting a harness revision/,/^### Upgrading the runtime/p' $r | j); echo "readonly=$(y $(echo "$H" | grep -c '`paths` and `stats`')) howto=$(y $(sed -n '/^### Counting what each role catches and costs/,/^##/p' $r | grep -c 'factory stats')) built=$(y $(sed -n '/^\*\*Built\*\*/,/^\*\*Not built\*\*/p' $r | grep -c 'factory stats')) depends=$(y $(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r | grep -c 'factory stats')) lock=$(y $(echo "$L" | grep -c '`stats`')) design-fence=$(y $(grep '^\*\*Only the dispatcher writes a live store during a run\.\*\*' docs/design.md | grep -c '`paths` and `stats`')) design-lock=$(y $(grep '^\*\*Role-context block\.\*\*' docs/design.md | grep -c '`stats`')) design-model=$(y $(grep '^\*\*Model per role, starting point\.\*\*' docs/design.md | grep -c 'factory stats')) principles=$(y $(sed -n '/^### 4\. Measure catch beside cost\./,/^##/p' docs/principles.md | grep '^Implemented by:' | grep -c '`factory stats`')) principles-old=$(y $(grep -c '1 BLOCKING finding in total' docs/principles.md))"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #70 ' docs/changelog.md); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e '#70' -e '#61' -e 'factory stats' -e 'message id' | sort -u | grep -c .)`
- THEN it prints exactly `readonly=yes howto=yes built=yes depends=yes lock=yes design-fence=yes design-lock=yes design-model=yes principles=yes principles-old=no`, then `CONTIGUOUS`, then `1`, then `4`

### Requirement: The documents name the module that holds each moved gate command
`README.md` and `docs/principles.md` SHALL name `factory/gates.py`, not `factory/cli.py`, for
`ticket_join`, `merge_cmd`, `archive_cmd` and the `merge` guard, and those three functions MUST be
defined in `factory/gates.py`.

#### Scenario: The README and the principles name gates.py for the moved gate commands
- WHEN `echo "$(grep -c 'factory/gates.py. .ticket_join., .merge_cmd., .archive_cmd.' README.md) $(grep -c 'factory/cli.py. .ticket_join.' README.md) $(grep -c 'factory/gates.py. (.merge.)' docs/principles.md) $(grep -c 'guards in .factory/cli.py.:' docs/principles.md) $(grep -cE '^def (ticket_join|merge_cmd|archive_cmd)\(' factory/gates.py 2>/dev/null)"`
- THEN it prints exactly `1 0 1 0 3`

### Requirement: The documents record that run start owns each role's model
`README.md`'s role-call paragraph under "The intake workflow, step by step" SHALL say that `run start` refuses a `--model` the instance does not name.

#### Scenario: The README describes the model check
- WHEN `(echo "readme=$(sed -n '/^### The intake workflow, step by step/,/sequenceDiagram/p' README.md | grep -c -- '--model' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `readme=1`

### Requirement: The documents record the parallel suite and the waiting park reason
`docs/design.md`'s EMPTY-OUTPUT rule SHALL name the waiting park reason. `README.md` SHALL name pytest-xdist, and its Empty output entry SHALL give the waiting reason and no longer say it has not fired on a real ticket. `docs/changelog.md` SHALL hold entry 71 for issue #106, numbered without a gap.

#### Scenario: The design doc names the waiting park reason
- WHEN `(echo "design=$(grep '^- A role run that ends without writing its output is EMPTY-OUTPUT' docs/design.md | grep -c 'ended its turn waiting on a background command')")`
- THEN it prints exactly `design=1`

#### Scenario: The README names pytest-xdist and the waiting reason
- WHEN `(B=$(awk '/^- \*\*Empty output\.\*\*/{f=1; print; next} f && /^(- \*\*|$|#)/{f=0} f' README.md | tr '\n' ' ' | tr -s ' '); echo "bullet=$(grep -c '^- \*\*Empty output\.\*\*' README.md) waiting=$(echo "$B" | grep -c 'ended its turn waiting on a background command') unfired=$(echo "$B" | grep -c 'has not yet fired') xdist=$(grep -c 'pytest-xdist' README.md | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `bullet=1 waiting=1 unfired=0 xdist=1`

#### Scenario: The changelog records issue 106 as entry 71, without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #106 ' docs/changelog.md); printf '%s\n' "$E" | grep -c '^71\. '; printf '%s' "$E" | grep -oF -e 'pytest-xdist' -e 'ended its turn waiting on a background command' -e 'EMPTY-OUTPUT' -e 'stand-in' -e 'in-process' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `5`

### Requirement: The maintained documents carry no whitespace errors
`README.md`, every file under `docs/` and `dev/`, and `.factory/context.md` MUST carry no whitespace error, checked over each file in full rather than over one change's diff.

#### Scenario: The maintained documents pass git's whitespace check in full
- WHEN `(E=$(git hash-object -t tree /dev/null); git diff --check $E HEAD -- README.md docs dev .factory/context.md; echo "exit=$?")`
- THEN it prints only `exit=0`

### Requirement: The build documents under dev/ are frozen as history
`dev/build-harness.spec.md`, `dev/build-harness.plan.md` and `dev/P0-intake-skeleton.md` SHALL each carry, as line 3, a header that starts `> **Frozen as history.**`, followed by a blank line, and SHALL otherwise stay byte for byte as they were at `7231670`. `.factory/context.md` MUST NOT ask a change to keep any of them consistent, and SHALL call them frozen; README's `dev/` row SHALL say they are frozen as history.

#### Scenario: Each build document carries the header and is otherwise unchanged
- WHEN `(for f in dev/build-harness.spec.md dev/build-harness.plan.md dev/P0-intake-skeleton.md; do echo "$f header=$(sed -n 3p $f | grep -c '^> \*\*Frozen as history\.\*\* ') rest=$(sed '3,4d' $f | cmp -s - <(git show 7231670:$f) && echo same || echo changed)"; done)`
- THEN it prints exactly `dev/build-harness.spec.md header=1 rest=same`, then `dev/build-harness.plan.md header=1 rest=same`, then `dev/P0-intake-skeleton.md header=1 rest=same`

#### Scenario: The briefing no longer asks a change to keep the build spec in step
- WHEN `(echo "buildspec=$(grep -c 'build-harness' .factory/context.md) frozen=$(grep -c 'frozen as history' .factory/context.md | awk '{print ($1 > 0)}') readme=$(grep '^| .dev/. |' README.md | grep -c 'frozen as history')")`
- THEN it prints exactly `buildspec=0 frozen=1 readme=1`

### Requirement: README's claims about what has run match the stores
README MUST NOT say that the one-sub-ticket path, the driver, the per-run scratch directory, a gate command's path skip, the re-plan after a re-spec or the protected-path refusal at merge has not yet run, and MUST NOT say that a run with no output is recorded as killed. Its tripwire and sibling-tests entries SHALL still say they have not yet fired, and its per-role effort entry that neither target sets it. Its "Ground truth only above" rule SHALL ask each entry to say whether it has yet run on a real ticket, and line 3 of `docs/design.md` SHALL point to `docs/changelog.md` instead of carrying a date of its own.

#### Scenario: README no longer calls run features untried, and keeps the claims that are still true
- WHEN `(b() { awk -v h="$1" 'index($0,h)==1{f=1;print;next} f&&/^(- \*\*|$|#)/{f=0} f' README.md | tr '\n' ' ' | tr -s ' '; }; R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "stale=$(printf '%s' "$R" | grep -oF -e 'one-sub-ticket path is tested' -e 'has not yet run a real ticket' -e 'remains the tested route' -e 'parked; this is tested' -e 'configuration uses it yet' -e 'recorded as killed' | grep -c .) replan=$(b '- **Re-plan after a re-spec.**' | grep -c 'not yet') paths=$(b '- **Protected paths at merge.**' | grep -c 'not yet') drive=$(b '- **The driver, ' | grep -c 'not yet') tripwire=$(b '- **Tripwire on live files.**' | grep -c 'has not yet fired') sibling=$(b '- **Sibling tests check.**' | grep -c 'has not yet fired') effort=$(b '- **Per-role effort' | grep -c 'Neither target sets it yet')")`
- THEN it prints exactly `stale=0 replan=0 paths=0 drive=0 tripwire=1 sibling=1 effort=1`

#### Scenario: The Built rule asks for run status, and the design doc's date line points to the changelog
- WHEN `(echo "rule=$(sed -n '/^- \*\*Ground truth only above/,/^- \*\*Update with the change/p' README.md | tr '\n' ' ' | tr -s ' ' | grep -c 'its entry says whether it has yet run on a real ticket') date=$(sed -n 3p docs/design.md | grep -c 'docs/changelog.md') old=$(sed -n 3p docs/design.md | grep -c '^2026-09-30 · Daniel$')")`
- THEN it prints exactly `rule=1 date=1 old=0`

### Requirement: README describes each mechanism in one section
README SHALL describe the live-store fence under "Where a human decides", the driver under "Driving a ticket from a shell with `factory drive`", the final check's skip under "The build workflow, step by step", the store branch under "How the factory uses git", and other agent hosts only in `docs/design.md`. Elsewhere it SHALL give each a short entry with a pointer: the Built entries for the fence, the driver, the tripwire, the sibling-tests check, spec drift, empty output, protected paths at merge and `factory stats` SHALL each stay within a line budget and name the section or the `docs/design.md` paragraph that describes it, and "Not built" SHALL list nothing that "Where this can go" lists.

#### Scenario: Each Built entry is a short pointer, and each mechanism's detail has one home
`s` prints `pointer` when a Built entry is at most N lines and names its home, and `long` otherwise.
- WHEN `(b() { awk -v h="$1" 'index($0,h)==1{f=1;print;next} f&&/^(- \*\*|$|#)/{f=0} f' README.md; }; s() { b "$1" | awk -v n="$2" -v p="$3" '{t=t" "$0} END{gsub(/ +/," ",t); print ((NR>0 && NR<=n && index(t,p)) ? "pointer" : "long")}'; }; R=$(tr '\n' ' ' < README.md | tr -s ' '); echo "fence=$(s '- **Live-store fence.**' 3 'Where a human decides') driver=$(s '- **The driver, ' 4 'Driving a ticket from a shell') tripwire=$(s '- **Tripwire on live files.**' 4 'docs/design.md') sibling=$(s '- **Sibling tests check.**' 4 'docs/design.md') drift=$(s '- **Spec amendment and drift.**' 6 'docs/design.md') empty=$(s '- **Empty output.**' 6 'docs/design.md') paths=$(s '- **Protected paths at merge.**' 4 'Where a human decides') stats=$(s '- **Counting catch and cost' 3 'Counting what each role catches') host=$(sed -n '/^### Running on another agent host/,/^## /p' README.md | sed '1d;$d' | awk '{t=t" "$0} /./{n++} /^\|/{tab=1} END{print ((n<=6 && !tab && index(t,"docs/design.md")) ? "pointer" : "long")}') skip=$(printf '%s' "$R" | grep -o 'has not moved since' | grep -c .) store=$(printf '%s' "$R" | grep -o 'never moves the integration branch' | grep -c .) drivefence=$(sed -n '/^### Driving a ticket from a shell/,/^Each role process/p' README.md | tr '\n' ' ' | grep -c 'refused like any write') notbuilt=$(sed -n '/^\*\*Not built\*\*/,/^## Where this can go/p' README.md | grep -c '^- \*\*')")`
- THEN it prints exactly `fence=pointer driver=pointer tripwire=pointer sibling=pointer drift=pointer empty=pointer paths=pointer stats=pointer host=pointer skip=1 store=1 drivefence=0 notbuilt=0`

### Requirement: README defines each term once
README's "Terms used on this page" SHALL point to "Where it runs" for target, instance, runtime and store branch in one row instead of defining them again, and SHALL give protected path its own row; the merge gate row SHALL no longer define a protected path, and the **Record** row of "Where a human decides" SHALL no longer restate who reads the decision log.

#### Scenario: The glossary points to Where it runs and defines protected path once
- WHEN `(T=$(sed -n '/^## Terms used on this page/,/^## How a ticket moves/p' README.md); echo "rows=$(printf '%s\n' "$T" | grep -cE '^\| (target|instance|runtime|store branch) \|') pointer=$(printf '%s\n' "$T" | grep -c '^| target, instance, runtime, store branch |') protected=$(printf '%s\n' "$T" | grep -c '^| protected path |') merge=$(grep '^| merge gate |' README.md | grep -c 'protected_paths') record=$(grep '^| \*\*Record\*\*' README.md | grep -c 'receive')")`
- THEN it prints exactly `rows=0 pointer=1 protected=1 merge=0 record=0`

### Requirement: History lives in the changelog
README SHALL keep under "Related work and history" the issue references it carries today, and SHALL no longer carry the history this change moves: the 2026-10-04 overlap count, the double count `factory/cost.py` once made, the store moves, the page's own origin story and the regeneration pass's past catches. `docs/design.md`'s model-per-role paragraph SHALL point to changelog entry 70 for the first `factory stats` figures instead of repeating them. `docs/changelog.md` SHALL hold one entry for issue #101 recording the move, numbered without a gap.

#### Scenario: README keeps its issue references and drops the moved history, and the changelog records the move
- WHEN `(R=$(tr '\n' ' ' < README.md | tr -s ' '); X=$(sed -n '/^## Related work and history/,/^## Maintaining this page/p' README.md | tr '\n' ' ' | tr -s ' '); M=$(grep '^\*\*Model per role, starting point\.\*\*' docs/design.md); E=$(grep '^[0-9]*\. After issue #101 ' docs/changelog.md); echo "history=$(printf '%s' "$R" | grep -oF -e '41 and 11 overlapping' -e 'used to count most calls about twice' -e 'First written 2026-10-03' -e 'today this caught' -e 'were moved onto it' | grep -c .) refs=$(printf '%s' "$X" | grep -oE '#[0-9]+' | sort -u | grep -xcE '#(16|17|18|19|20|21|22|23|24|28|35|42|46|47|53|55|61|65|70)') figures=$(printf '%s' "$M" | grep -c '94,860,442') pointer=$(printf '%s' "$M" | grep -c 'changelog entry 70') entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e frozen -e build-harness.spec.md -e context.md -e '41 and 11' -e harness-docs -e 'not yet' | sort -u | grep -c .)"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md)`
- THEN it prints exactly `history=0 refs=19 figures=0 pointer=1 entries=1 terms=6`, then `CONTIGUOUS`

### Requirement: README stays within its line budget
`README.md` SHALL be at most 1,225 lines long; a later change that needs more room raises this bound in its own spec, where the operator approves it at the gate.

#### Scenario: README is at most 1,225 lines
- WHEN `(echo "readme=$(wc -l < README.md | awk '{print ($1 <= 1225 ? "within" : "over")}')")`
- THEN it prints exactly `readme=within`

### Requirement: docs/standards.md holds the operator's writing and design standards
`docs/standards.md` SHALL open with a `# ` title line, and the text after that line SHALL be the operator's approved standards text, whose SHA-256 is `010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e`; a change to that text modifies this requirement in its own spec.

#### Scenario: The standards file holds the approved text
- WHEN `(f=docs/standards.md; echo "title=$(head -1 $f 2>/dev/null | grep -c '^# ') body=$(sed 1d $f 2>/dev/null | LC_ALL=C shasum -a 256 | cut -c1-64)")`
- THEN it prints exactly `title=1 body=010d1300876f602b35efc641a1b7effbd149035695e3161e6606d1718f24d26e`

### Requirement: README points to docs/standards.md
README's "Where things live" table SHALL have exactly one row naming `docs/standards.md`.

#### Scenario: Where things live names the standards file
- WHEN `(echo "row=$(sed -n '/^## Where things live/,/^## Related work and history/p' README.md | grep '^| ' | grep -c 'docs/standards.md')")`
- THEN it prints exactly `row=1`

### Requirement: No role prompt reads docs/standards.md
No file under `docs/prompts/`, `factory/` or `agents/`, and not `docs/writing.md`, SHALL name `docs/standards.md`, so adding it changes no role's behaviour; a spec that changes prompts may modify this requirement.

#### Scenario: Nothing a role reads names the standards file
- WHEN `(echo "readers=$(grep -rlF 'standards.md' docs/prompts docs/writing.md factory agents | grep -c .)")`
- THEN it prints exactly `readers=0`

### Requirement: The north star names its target without the private product
`docs/north-star.md` SHALL describe the factory's current target as "a port of the Nanobot chat bot" in its one sentence on whom the factory serves.

#### Scenario: The north-star sentence names a port of the Nanobot chat bot
- WHEN `(echo "line=$(grep -cxF 'The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).' docs/north-star.md) serves=$(grep -c '^The factory serves its own development' docs/north-star.md)")`
- THEN it prints exactly `line=1 serves=1`

### Requirement: The documents record the standards file
`docs/changelog.md` SHALL hold exactly one entry opening `<n>. After issue #110 `, naming `docs/standards.md`, `docs/writing.md` and `docs/north-star.md`, and its entries SHALL stay numbered without a gap.

#### Scenario: The changelog records issue 110 in one entry without a numbering gap
- WHEN `(E=$(grep '^[0-9]*\. After issue #110 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e 'docs/standards.md' -e 'docs/north-star.md' -e 'docs/writing.md' | sort -u | grep -c .)"; awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md)`
- THEN it prints exactly `entries=1 terms=3`, then `CONTIGUOUS`

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

### Requirement: README draws how a spec changes and feeds later tickets
`README.md`'s "How a ticket moves" SHALL hold a subsection "How a spec changes and feeds later tickets", placed before "Ticket states", whose one Mermaid diagram uses the section's three colour classes. Its edges SHALL draw `request-changes`, `approve-spec --edit`, `planned_from`, the drift check, `spec amend` with `resolve --ruling`, `resolve --to spec-gate`, `resolve --replan`, `archive` writing current truth and `decisions.md`, and `decision add` writing the log. A subgraph titled "a later ticket" SHALL hold that ticket's triage, spec writer, critic and planner.

#### Scenario: The spec's-life diagram draws every route after the critic
- WHEN `(D=$(awk '/^### How a spec changes and feeds later tickets$/{s=1;next} s&&/^#/{s=0} s&&/^[`][`][`]mermaid$/{f=1;next} f&&/^[`][`][`]$/{f=0;s=0} f' README.md); E=$(printf '%s\n' "$D" | grep -E -- '-->|\.->'); y() { printf '%s\n' "$E" | grep -qF -- "$1" && echo yes || echo no; }; L=$(printf '%s\n' "$D" | sed -n '/^ *subgraph .*"a later ticket"/,/^ *end$/p'); echo "classes=$(printf '%s\n' "$D" | grep -cE '^ *classDef (human|orch|store) ') request=$(y request-changes) edit=$(y '--edit') amend=$(y 'spec amend') respec=$(y '--to spec-gate') replan=$(y '--replan') ruling=$(y '--ruling') planned=$(y planned_from) drift=$(y drift) truth=$(y 'current truth') log=$(y decisions.md) writers=$(y 'decision add') later=$(printf '%s\n' "$L" | grep -oE 'Triage|Spec writer|critic|Planner' | sort -u | grep -c .)")`
- THEN it prints exactly `classes=3 request=yes edit=yes amend=yes respec=yes replan=yes ruling=yes planned=yes drift=yes truth=yes log=yes writers=yes later=4`

### Requirement: The clerk node says it exists only on the Workflow-script path
The clerk node of the first diagram in "How a ticket moves" SHALL say that the clerk exists only on the Workflow-script path, that the launch copy carries the settings it does not relay, and that `factory drive` needs no clerk.

#### Scenario: The clerk node names the Workflow-script path, the launch copy and factory drive
- WHEN `(C=$(sed -n '/^## How a ticket moves/,/^### /p' README.md | grep 'clerk agent'); echo "clerk=$(printf '%s\n' "$C" | grep -c .) workflow=$(printf '%s' "$C" | grep -c 'Workflow-script path only') launch=$(printf '%s' "$C" | grep -c 'launch copy') drive=$(printf '%s' "$C" | grep -c 'factory drive')")`
- THEN it prints exactly `clerk=1 workflow=1 launch=1 drive=1`

### Requirement: The diagrams of How a ticket moves are well formed
"How a ticket moves" SHALL hold two Mermaid blocks. Each SHALL open with `flowchart LR` and close its fence, and on every line its quotes, square brackets, parentheses and braces SHALL balance once quoted labels are set aside. This is a structural check, not a parse.

#### Scenario: Both diagrams of How a ticket moves have balanced quotes and brackets
- WHEN `(awk '/^## How a ticket moves/{s=1} /^### Ticket states/{s=0} !s{next} /^[`][`][`]mermaid$/{b++;f=1;n=0;next} f&&/^[`][`][`]$/{f=0;next} !f{next} {n++; l=$0; gsub(/"[^"]*"/,"Q",l); if (n==1 && l!="flowchart LR") bad++; if (index(l,"\"")) bad++; o=l; c1=gsub(/\[/,"",o); c2=gsub(/\]/,"",o); c3=gsub(/\(/,"",o); c4=gsub(/\)/,"",o); c5=gsub(/\{/,"",o); c6=gsub(/\}/,"",o); if (c1!=c2||c3!=c4||c5!=c6) bad++} END{if (f) bad++; print "blocks=" b+0 " bad=" bad+0}' README.md)`
- THEN it prints exactly `blocks=2 bad=0`

### Requirement: The regeneration table names the modules the spec's-life diagram is drawn from
The "How a ticket moves" row of README's "Regenerating this page from scratch" SHALL name `factory/human.py`, `factory/subtickets.py`, `factory/drift.py`, `factory/specstore.py` and `factory/compose.py`.

#### Scenario: The How a ticket moves row names the five modules
- WHEN `(R=$(grep '^| How a ticket moves |' README.md); echo "row=$(printf '%s\n' "$R" | grep -c .) names=$(printf '%s' "$R" | grep -oF -e factory/human.py -e factory/subtickets.py -e factory/drift.py -e factory/specstore.py -e factory/compose.py | sort -u | grep -c .)")`
- THEN it prints exactly `row=1 names=5`

### Requirement: The documents record the footer rule, the unreadable agent copy and the --accept-harness refusal
README's "Accepting a harness revision" SHALL say, in one sentence, that `init`, `paths` and `stats` refuse `--accept-harness`. Step 2 of "Upgrading the runtime" SHALL name `--accept-harness <sha> config`. "Counting what each role catches and costs" SHALL say that `stats` refuses `--accept-harness`. The `.claude/agents/factory-*.md` row SHALL say that init reports a copy it cannot read. `docs/design.md`'s ESCALATIONS bullet SHALL name the dropped `Generated with [Claude Code]` footer, and its `harness.lock` clause SHALL say, in one sentence, that `init`, `paths` and `stats` refuse `--accept-harness`. `docs/changelog.md` SHALL hold one entry naming #88, #113, #114 and #115, numbered without a gap.

#### Scenario: README says which commands refuse the flag, how to accept a revision, and that init reports an unreadable copy
- WHEN `(S=$(sed -n '/^### Accepting a harness revision/,/^### Upgrading the runtime/p' README.md); U=$(sed -n '/^### Upgrading the runtime/,/^### Installing the harness/p' README.md | grep '^2\. '); C=$(sed -n '/^### Counting what each role catches and costs/,/^```/p' README.md); echo "accepting=$(printf '%s' "$S" | python3 -c 'import re, sys; print(sum(1 for s in re.split(r"\.\s", sys.stdin.read()) if all(w in s for w in ("init", "paths", "stats", "--accept-harness")) and "refuse" in s))') upgrade=$(printf '%s' "$U" | grep -c -- '--accept-harness <sha> config') stats=$(printf '%s' "$C" | tr '\n' ' ' | grep -c 'refuses .--accept-harness.') row=$(grep '^| .\.claude/agents/factory-\*\.md. |' README.md | grep -c 'cannot read')")`
- THEN it prints exactly `accepting=1 upgrade=1 stats=1 row=1`

#### Scenario: The design doc states the footer rule and the refusal in the lock clause
- WHEN `(echo "footer=$(grep '^- A non-empty ESCALATIONS line' docs/design.md | grep -cF 'Generated with [Claude Code]') lock=$(grep '^\*\*Role-context block\.\*\*' docs/design.md | python3 -c 'import re, sys; print(sum(1 for s in re.split(r"\.\s", sys.stdin.read()) if all(w in s for w in ("init", "paths", "stats", "--accept-harness")) and "refuse" in s))')")`
- THEN it prints exactly `footer=1 lock=1`

#### Scenario: The changelog records the four issues in one entry without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep -E '^[0-9]+\. ' docs/changelog.md | grep -F '#88' | grep -F '#113' | grep -F '#114' | grep -F '#115'); printf '%s\n' "$E" | grep -c .; printf '%s' "$E" | grep -oF -e 'Generated with' -e stale_agents -e '--accept-harness' -e '/bin/sh' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `1`, then `4`

### Requirement: The north star says how the factory's work is measured and reviewed
`docs/north-star.md` SHALL hold, as its second `## ` section, "How we know it is working". That section SHALL name the primary metric, its constraint, cost as the second measure, operator decisions and interventions standing in for hours of operator attention, spec-factory's merges reported on a line of their own, the scorecard's five numbers as table rows, the plain-session baseline, the upstream benchmark, change failure rate, the baseline review `docs/reviews/2026-10-19.md`, and a review every two weeks from `docs/reviews/TEMPLATE.md` that rewrites `STATUS.md`, the first from the template on 2026-11-02. The file MUST keep its four success measures and its sentence on whom the factory serves.

#### Scenario: The north star holds the measurement section and keeps its measures and target sentence
- WHEN `(N=docs/north-star.md; X=$(awk '/^## How we know it is working$/{f=1;next} f&&/^## /{f=0} f' $N); S=$(printf '%s' "$X" | tr '\n' ' ' | tr -s ' '); echo "heading=$(grep -cx '## How we know it is working' $N) second=$(grep '^## ' $N | sed -n 2p | grep -cx '## How we know it is working') terms=$(printf '%s' "$S" | grep -oF -e 'correct target changes per hour of operator attention' -e 'escaped defects do not rise' -e 'tokens and wall time per change' -e 'in place of hours of operator attention' -e 'on a line of their own' -e 'plain-session baseline' -e 'upstream benchmark' -e 'change failure rate' -e 'every two weeks' -e 'docs/reviews/TEMPLATE.md' -e 'docs/reviews/2026-10-19.md' -e 'STATUS.md' -e '2026-11-02' | sort -u | grep -c .) rows=$(printf '%s\n' "$X" | grep -cE '^\| (Target changes merged|Escapes|Operator decisions and interventions per change|Tokens and wall time per change|Lead time) \|') measures=$(sed -n '/^Success is measured as:$/,/^$/p' $N | grep -c '^- ') serves=$(grep -cxF 'The factory serves its own development (spec-factory) and its targets (today, a port of the Nanobot chat bot).' $N)")`
- THEN it prints exactly `heading=1 second=1 terms=13 rows=5 measures=4 serves=1`

### Requirement: The north star holds the rule for factory work
`docs/north-star.md`'s "How it decides where effort goes" SHALL introduce four working rules, and one of them SHALL be "Factory work serves a target or a number". That rule SHALL admit a factory ticket only if it fixes a defect that hit a target ticket, or names the scorecard number it moves and re-measures that number after it ships, and SHALL say that the operator applies it at the spec gate.

#### Scenario: The north star's working rules include the rule for factory work
- WHEN `(N=docs/north-star.md; B=$(sed -n '/^## How it decides where effort goes$/,/^## Where it is heading$/p' $N | awk '/^- \*\*Factory work serves a target or a number\.\*\*/{f=1;print;next} f&&/^(- \*\*|$|#)/{f=0} f' | tr '\n' ' ' | tr -s ' '); echo "rule=$(printf '%s' "$B" | grep -c 'Factory work serves') terms=$(printf '%s' "$B" | grep -oF -e 'fixes a defect that hit a target ticket' -e 'names the scorecard number it moves' -e 're-measures that number after it ships' -e 'spec gate' | sort -u | grep -c .) four=$(grep -cx 'And four working rules that follow from them:' $N) three=$(grep -cx 'And three working rules that follow from them:' $N)")`
- THEN it prints exactly `rule=1 terms=4 four=1 three=0`

### Requirement: README shows the north star on its first screen
`README.md` SHALL hold one paragraph opening `**North star.**`, placed before "What problem it solves", that states the primary metric per hour of operator attention and names `docs/north-star.md`, `STATUS.md` and `docs/reviews/`. README MUST stay within its 1,225-line budget.

#### Scenario: README opens with the north-star paragraph and stays within its budget
- WHEN `(H=$(grep -n '^## What problem it solves$' README.md | cut -d: -f1); B=$(awk -v h="$H" 'NR>=h{exit} /^\*\*North star\.\*\*/{f=1} f&&/^$/{f=0} f' README.md | tr '\n' ' ' | tr -s ' '); echo "block=$(grep -c '^\*\*North star\.\*\*' README.md) top=$(printf '%s' "$B" | grep -c '^\*\*North star\.\*\*') metric=$(printf '%s' "$B" | grep -c 'per hour of operator attention') links=$(printf '%s' "$B" | grep -oF -e 'docs/north-star.md' -e 'STATUS.md' -e 'docs/reviews/' | sort -u | grep -c .) readme=$(wc -l < README.md | awk '{print ($1 <= 1225 ? "within" : "over")}')")`
- THEN it prints exactly `block=1 top=1 metric=1 links=3 readme=within`

### Requirement: README's filing steps state the rule for factory work
README's "Filing a request from an issue tracker" SHALL say that a request to change the factory itself goes ahead only if it fixes a defect that hit a ticket of the product the factory builds, or names the scorecard number it moves and re-measures it after it ships. It SHALL also say that the operator applies the rule at the spec gate.

#### Scenario: The filing section states the rule for factory work
- WHEN `(F=$(sed -n '/^### Filing a request from an issue tracker$/,/^### Running many tickets/p' README.md | tr '\n' ' ' | tr -s ' '); echo "terms=$(printf '%s' "$F" | grep -oF -e 'change the factory itself goes ahead only if' -e 'fixes a defect that hit a ticket of the product' -e 'names the scorecard number it moves' -e 're-measures it after it ships' -e 'spec gate' | sort -u | grep -c .)")`
- THEN it prints exactly `terms=5`

### Requirement: README's Where things live names the new files
README's "Where things live" table SHALL have exactly one row naming `STATUS.md`, one naming `docs/reviews/` and one naming `CONTRIBUTING.md`.

#### Scenario: Where things live has a row for each new file
- WHEN `(Q=$(printf '\140'); W=$(sed -n '/^## Where things live$/,/^## Related work and history$/p' README.md | grep '^| '); echo "status=$(printf '%s\n' "$W" | grep -c "${Q}STATUS.md${Q}") reviews=$(printf '%s\n' "$W" | grep -c "${Q}docs/reviews/${Q}") contributing=$(printf '%s\n' "$W" | grep -c "${Q}CONTRIBUTING.md${Q}")")`
- THEN it prints exactly `status=1 reviews=1 contributing=1`

### Requirement: CONTRIBUTING.md says how work is proposed and chosen
`CONTRIBUTING.md` SHALL exist at the repository root. It SHALL give the steps Issue, Factory ticket and Spec gate as a numbered list in that order, state the rule for factory work, link `docs/north-star.md`, and carry no whitespace error.

#### Scenario: CONTRIBUTING.md gives the three steps and the rule, and links the north star
- WHEN `(C=CONTRIBUTING.md; [ -f $C ] || { echo "missing=$C"; exit 0; }; T=$(tr '\n' ' ' < $C | tr -s ' '); E=$(git hash-object -t tree /dev/null); echo "steps=$(grep -E '^[0-9]+\. \*\*' $C | sed -E 's/^[0-9]+\. \*\*([^*]*)\*\*.*/\1/' | tr '\n' '|') rule=$(printf '%s' "$T" | grep -oF -e 'fixes a defect that hit a target ticket' -e 'names the scorecard number it moves' -e 're-measures that number after it ships' -e 'spec gate' | sort -u | grep -c .) northstar=$(grep -c '](docs/north-star.md)' $C | awk '{print ($1 > 0)}') ws=$(git diff --check $E HEAD -- $C >/dev/null && echo clean || echo errors)")`
- THEN it prints exactly `steps=Issue.|Factory ticket.|Spec gate.| rule=4 northstar=1 ws=clean`

### Requirement: STATUS.md holds the north star, the baseline's figures, the focus, the queue and the experiments
`STATUS.md` SHALL exist at the repository root, at most 60 lines long. It SHALL open its body with the north star in one line, and hold the sections Scorecard, Current focus, Top of the queue, Open experiments and Links, in that order. It SHALL link `docs/north-star.md`, the latest review `docs/reviews/2026-10-19.md`, the folder `docs/reviews/`, the repository's issues and the store branch, and carry no whitespace error. Its Scorecard section SHALL link the baseline review, say its figures were counted by hand, and name `factory stats`. Its Scorecard table SHALL hold six rows with a column for the Nanobot port and one for spec-factory. Each cell MUST appear as a cell of that instance's table in `docs/reviews/2026-10-19.md`, and each figure in the section's prose MUST appear in that review.

#### Scenario: STATUS.md has its sections and links, and quotes only the baseline review's figures
- WHEN `(F=STATUS.md; R=docs/reviews/2026-10-19.md; [ -f $F ] || { echo "missing=$F"; exit 0; }; E=$(git hash-object -t tree /dev/null); C=$(sed -n '/^## Scorecard$/,/^## /p' $F | sed '1d;$d'); P=$(sed -n '/^## The Nanobot port$/,/^## Spec-factory/p' $R 2>/dev/null); G=$(sed -n '/^## Spec-factory/,/^## Escapes$/p' $R 2>/dev/null); cells=$(printf '%s\n' "$C" | grep -E '^\| [A-Z]' | sed 1d | while IFS='|' read -r _ _ a b _; do a=$(printf '%s' "$a" | sed 's/^ *//; s/ *$//'); b=$(printf '%s' "$b" | sed 's/^ *//; s/ *$//'); printf '%s\n' "$P" | grep -qF -e "| $a |" -e "| $a (" || echo x; printf '%s\n' "$G" | grep -qF -e "| $b |" -e "| $b (" || echo x; done | grep -c x); U=0; for t in $(printf '%s\n' "$C" | grep -v '^|' | sed -E 's/\[[^]]*\]\([^)]*\)//g; s/#[0-9]+//g; s/[0-9]{4}-[0-9]{2}-[0-9]{2}//g' | grep -oE '[0-9]+(\.[0-9]+)?'); do grep -qE "(^|[^0-9.])$(printf '%s' "$t" | sed 's/\./\\./')([^0-9.]|\$)" $R 2>/dev/null || U=$((U+1)); done; echo "lines=$(wc -l < $F | awk '{print ($1 <= 60 ? "within" : "over")}') sections=$(grep '^## ' $F | tr '\n' '|') northstar=$(grep -c '^\*\*North star:\*\* correct target changes per hour of operator attention' $F) links=$(grep -oF -e '](docs/north-star.md)' -e '](docs/reviews/)' -e '](docs/reviews/2026-10-19.md)' -e 'https://github.com/danielphang/spec-factory/issues' -e 'https://github.com/danielphang/spec-factory/tree/factory-store' $F | sort -u | grep -c .) scorecard=$(printf '%s' "$C" | tr '\n' ' ' | grep -oF -e '](docs/reviews/2026-10-19.md)' -e 'counted by hand' -e '`factory stats`' | sort -u | grep -c .) rows=$(printf '%s\n' "$C" | grep -E '^\| [A-Z]' | sed 1d | grep -c .) cells_unsourced=$cells prose_unsourced=$U ws=$(git diff --check $E HEAD -- $F >/dev/null && echo clean || echo errors)")`
- THEN it prints exactly `lines=within sections=## Scorecard|## Current focus|## Top of the queue|## Open experiments|## Links| northstar=1 links=5 scorecard=3 rows=6 cells_unsourced=0 prose_unsourced=0 ws=clean`

### Requirement: The review template holds the six sections a review fills in
`docs/reviews/TEMPLATE.md` SHALL hold six numbered `## ` sections in this order:
1. the scorecard against the last review, taken from `factory stats`, naming the baseline review as the one counted by hand;
2. what was worked on;
3. what was chosen not to do, linking `docs/decided-against.md`;
4. successes and failures;
5. experiments and side work, naming the `experiment` label;
6. decisions and the new queue order.

It SHALL also link `STATUS.md`.

#### Scenario: The review template's sections are the six the request lists, in order
- WHEN `(F=docs/reviews/TEMPLATE.md; [ -f $F ] || { echo "missing=$F"; exit 0; }; Q=$(printf '\140'); grep '^## ' $F; y() { [ "$1" -gt 0 ] && echo yes || echo no; }; echo "decided=$(y $(sed -n '/^## 3\. /,/^## 4\. /p' $F | grep -c '](../decided-against.md)')) experiment=$(y $(sed -n '/^## 5\. /,/^## 6\. /p' $F | grep -c "${Q}experiment${Q}")) stats=$(y $(sed -n '/^## 1\. /,/^## 2\. /p' $F | grep -c 'factory stats')) baseline=$(y $(sed -n '/^## 1\. /,/^## 2\. /p' $F | grep -c '](2026-10-19.md)')) status=$(y $(grep -c '](../../STATUS.md)' $F))")`
- THEN it prints exactly `## 1. Scorecard against the last review`, `## 2. What we worked on`, `## 3. What we chose not to do`, `## 4. Successes and failures`, `## 5. Experiments and side work`, `## 6. Decisions and the new queue order`, `decided=yes experiment=yes stats=yes baseline=yes status=yes`, one per line

### Requirement: The baseline review is the operator's baseline, verbatim
`docs/reviews/2026-10-19.md` SHALL exist. Its first line SHALL be `# Review 2026-10-19: baseline scorecard, 2026-10-03 to 2026-10-19`. Every line after the first SHALL be byte for byte the operator's baseline after its own title line, as recorded on the store branch at `02e403f` in `requests/T-0055.md`. The file SHALL carry no whitespace error.

#### Scenario: The baseline review matches the operator's text after its first line
- WHEN `(F=docs/reviews/2026-10-19.md; [ -f $F ] || { echo "missing=$F"; exit 0; }; E=$(git hash-object -t tree /dev/null); a=$(sed 1d $F | git hash-object --stdin); b=$(git show 02e403f:requests/T-0055.md | sed -n '/^--- baseline begins ---$/,/^--- baseline ends ---$/p' | sed '1,2d;$d' | git hash-object --stdin); echo "head=$(head -1 $F)"; echo "body=$([ "$a" = "$b" ] && echo verbatim || echo differs) ws=$(git diff --check $E HEAD -- $F >/dev/null && echo clean || echo errors)")`
- THEN it prints exactly `head=# Review 2026-10-19: baseline scorecard, 2026-10-03 to 2026-10-19`, then `body=verbatim ws=clean`

### Requirement: The new pages' relative links resolve
Every relative Markdown link in `STATUS.md`, `CONTRIBUTING.md` and `docs/reviews/TEMPLATE.md` SHALL name a path that exists, resolved from the linking file's directory, and each of the three SHALL hold at least one such link.

#### Scenario: No relative link in the three new pages is broken
- WHEN `(for f in STATUS.md CONTRIBUTING.md docs/reviews/TEMPLATE.md; do [ -f "$f" ] || { echo "$f missing"; continue; }; d=$(dirname "$f"); n=0; bad=0; for l in $(grep -oE '\]\([^)#]+\)' "$f" | sed -E 's/^\]\(//; s/\)$//' | grep -v '^[a-z]*:'); do n=$((n+1)); [ -e "$d/$l" ] || bad=$((bad+1)); done; echo "$f relative=$([ $n -gt 0 ] && echo some || echo none) broken=$bad"; done)`
- THEN it prints exactly `STATUS.md relative=some broken=0`, `CONTRIBUTING.md relative=some broken=0`, `docs/reviews/TEMPLATE.md relative=some broken=0`, one per line

### Requirement: The changelog records issue 116
`docs/changelog.md` SHALL hold exactly one entry opening `<n>. After issue #116 `. The entry SHALL name `docs/north-star.md`, `STATUS.md`, `CONTRIBUTING.md`, `docs/reviews/TEMPLATE.md`, `docs/reviews/2026-10-19.md`, the primary metric and the spec gate. The entries SHALL stay numbered without a gap, and the changelog SHALL end with its `Declined:` line.

#### Scenario: The changelog records issue 116 in one entry without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; E=$(grep '^[0-9]*\. After issue #116 ' docs/changelog.md); echo "entries=$(printf '%s\n' "$E" | grep -c .) terms=$(printf '%s' "$E" | grep -oF -e 'docs/north-star.md' -e 'STATUS.md' -e 'CONTRIBUTING.md' -e 'docs/reviews/TEMPLATE.md' -e 'docs/reviews/2026-10-19.md' -e 'per hour of operator attention' -e 'spec gate' | sort -u | grep -c .) last=$(tail -1 docs/changelog.md | grep -c '^Declined:')")`
- THEN it prints `CONTIGUOUS`, then `entries=1 terms=7 last=1`

### Requirement: The documents record the scorecard, escape and intervention records, and workflow token records
README SHALL describe `factory stats --scorecard` and `target_is_factory` in "Counting what each role catches and costs", with the run token record that `run finish --transcripts` writes in place of the claim that only driver runs carry a cost record; SHALL give `factory escape add` and `factory intervention add` their rows in "Where a human decides", the **Escape** row saying the store keeps only the link's SHA-256 hash; SHALL list the transcript record among the six pieces in "What depends on Claude Code"; and SHALL give the three a short Built entry that points to that subsection and says they have not yet run on a real store; `factory/instance.template.yaml` SHALL document `target_is_factory`.

#### Scenario: README and the instance template describe the scorecard, the two records and the token record
- WHEN `(r=README.md; y() { [ "$1" -gt 0 ] && echo yes || echo no; }; C=$(sed -n '/^### Counting what each role catches and costs/,/^## /p' $r); H=$(sed -n '/^## Where a human decides/,/^### What you read at each stop/p' $r); D=$(sed -n '/^### What depends on Claude Code/,/^## Terms used/p' $r); echo "scorecard=$(y $(printf '%s\n' "$C" | grep -c -- '--scorecard')) setting=$(y $(printf '%s\n' "$C" | grep -c 'target_is_factory')) escape=$(y $(printf '%s\n' "$H" | grep '^| \*\*Escape\*\* |' | grep -c 'factory escape add')) hash=$(y $(printf '%s\n' "$H" | grep '^| \*\*Escape\*\* |' | grep -c 'SHA-256')) intervene=$(y $(printf '%s\n' "$H" | grep '^| \*\*Intervene\*\* |' | grep -c 'factory intervention add')) record=$(y $(printf '%s\n' "$C" | tr '\n' ' ' | grep -c 'run finish --transcripts')) old=$(y $(grep -c 'Any other run has its tokens only in the transcript' $r)) depends=$(y $(printf '%s\n' "$D" | grep '^| ' | grep -c 'run finish --transcripts')) pieces=$(y $(printf '%s\n' "$D" | grep -c 'Six pieces assume Claude Code')) template=$(y $(grep -c 'target_is_factory' factory/instance.template.yaml))"; awk -v h='- **The scorecard, escapes and workflow token records.**' 'index($0,h)==1{f=1;print;next} f&&/^(- \*\*|$|#)/{f=0} f' $r | awk '{t=t" "$0} END{gsub(/ +/," ",t); print ((NR>0 && NR<=3 && index(t,"Counting what each role catches") && index(t,"Not yet run on a real store")) ? "built=pointer" : "built=long")}')`
- THEN it prints exactly `scorecard=yes setting=yes escape=yes hash=yes intervene=yes record=yes old=no depends=yes pieces=yes template=yes`, then `built=pointer`
