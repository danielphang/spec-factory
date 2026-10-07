## ADDED Requirements

### Requirement: The prompts tell the reviewer what the gate checks and the spec writer how to declare
Every copy of the code reviewer prompt (the `docs/design.md` §6 block, `docs/prompts/06-code-reviewer.md`, `factory/prompts/reviewer.md`) SHALL carry check 6's new last sentence and MUST NOT say `will require a human approval`. Every copy of the spec writer prompt SHALL give the `Protected paths:` line under Risk and the rule of one path or glob per entry with no brace lists. Each design block and its `docs/prompts/` file MUST stay byte-identical, and each `factory/prompts/` copy SHALL differ from its `docs/prompts/` file only where it did on `main`.

#### Scenario: Every reviewer prompt copy states what the merge gate checks
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0033-rev.txt; T=$(mktemp -d); sed -n '/^## 6\. Code reviewer/,/^## 7\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/06-code-reviewer.md factory/prompts/reviewer.md; do J=$(tr '\n' ' ' < $f | tr -s ' '); echo "gate=$(echo "$J" | grep -c "The merge gate merges a path the approved spec's Risk section declares with no further approval, and refuses and parks one it does not declare") promise=$(echo "$J" | grep -c 'will require a human approval')"; done; git show main:factory/prompts/reviewer.md > $T/a; git show main:docs/prompts/06-code-reviewer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/06-code-reviewer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/reviewer.md docs/prompts/06-code-reviewer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `gate=1 promise=0`, then `copy=SAME fill=unchanged`

#### Scenario: Every spec writer prompt copy gives the declaration line
- WHEN `(F=$(printf '\140\140\140'); X=${TMPDIR:-/tmp}/t0033-sw.txt; T=$(mktemp -d); sed -n '/^## 2\. Spec writer/,/^## 3\. /p' docs/design.md | sed -n "/^${F}text\$/,/^${F}\$/p" | sed '1d;$d' > $X; for f in $X docs/prompts/02-spec-writer.md factory/prompts/spec_writer.md; do echo "reads=$(grep -c 'declared on one line the merge gate reads:$' $f) form=$(grep -c '^ *Protected paths: none | .<path or glob>., .<path or glob>.$' $f) braces=$(grep -c '^ *one path or glob per entry, no brace lists$' $f)"; done; git show main:factory/prompts/spec_writer.md > $T/a; git show main:docs/prompts/02-spec-writer.md > $T/b; echo "copy=$(cmp -s $X docs/prompts/02-spec-writer.md && echo SAME || echo DIFF) fill=$([ "$(diff factory/prompts/spec_writer.md docs/prompts/02-spec-writer.md | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)")`
- THEN it prints three lines, each exactly `reads=1 form=1 braces=1`, then `copy=SAME fill=unchanged`

### Requirement: The documents record the protected-path rule at merge
`docs/design.md` SHALL drop the per-PR approval for protected paths, describe the declared-path rule in piece 8 and the Protected paths gate row, and route a reviewer ESCALATE back to its checks; `dev/build-harness.spec.md` SHALL describe the same rule; `docs/changelog.md` SHALL gain an entry for issue #57 and stay numbered without a gap; `README.md` SHALL describe the check and `--accept-paths`; and the change MUST add no whitespace errors.

#### Scenario: The design doc and build spec drop the per-PR approval for protected paths
- WHEN `(echo "gates=$(grep -c 'a PR touching a protected path, the daily escalation queue' docs/design.md) either=$(grep -c 'A change to either needs a human approval record before it merges' docs/design.md) onpr=$(grep -c 'any other guardrail or protected path needs a human approval on the PR itself' docs/design.md) piece8=$(grep '^| 8 |' docs/design.md | grep -c 'Protected paths:') piece9=$(grep -c 'review protected PRs' docs/design.md) gaterow=$(grep '^| Protected paths |' docs/design.md | grep -c -- '--accept-paths') stale=$(grep -c 'records the piece-8 approval; the merge gate does not merge without it' docs/design.md) reviewer_rule=$(grep -c '^  - A reviewer ESCALATE returns to its checks' docs/design.md) old_route=$(grep -c 'or a reviewer ESCALATE returns to the implementer' docs/design.md) build=$(grep -c 'protected path pyproject.toml needs human approval on H' dev/build-harness.spec.md) build_new=$(grep '^25\. ' dev/build-harness.spec.md | grep -c 'not declared')")`
- THEN it prints exactly `gates=0 either=0 onpr=0 piece8=1 piece9=0 gaterow=1 stale=0 reviewer_rule=1 old_route=0 build=0 build_new=1`

#### Scenario: The changelog records issue 57's change without a numbering gap
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. After issue #57 ' docs/changelog.md | grep -oF -e 'Risk' -e '--accept-paths' -e 'BLOCKED from merge gate' -e 'checks' -e 'Protected paths:' | sort -u | grep -c .)`
- THEN it prints `CONTIGUOUS`, then `5`

#### Scenario: README describes the protected-path check and the new resolve verb
- WHEN `(echo "built=$(grep -c '^- \*\*Protected paths at merge\.\*\*' README.md) unstick=$(grep '^| \*\*Unstick\*\*' README.md | grep -c -- '--accept-paths') merges=$(sed -n '/^- \*\*Merges, one at a time\.\*\*/,/^- \*\*Setting up the store\.\*\*/p' README.md | grep -c 'Risk section' | awk '{print ($1 > 0)}')")`
- THEN it prints exactly `built=1 unstick=1 merges=1`

#### Scenario: The protected-path change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

