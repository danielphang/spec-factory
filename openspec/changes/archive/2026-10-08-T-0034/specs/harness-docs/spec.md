## ADDED Requirements

### Requirement: The spec writer and the critic carry the turn-economy rules
Every copy of the spec writer prompt SHALL tell it to batch independent reads and commands, read line ranges once grep has found them, keep long output in a scratch file, and write the spec in as few writes as it can. Every copy of the critic prompt SHALL carry the same reading rules, cap any one claim at 2 paths and 1 command, forbid test-suite runs and builds, and turn a claim that needs one into a finding or a question. Each design block MUST stay byte-identical to its `docs/prompts/` copy, and each run copy SHALL differ from it only as it did on `main`.

#### Scenario: Every spec writer and critic copy carries the turn-economy rules and the critic's no-build rule
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); Q=$(printf '\140\140\140'); printf '%s\n' 'Put independent reads and commands in one turn' 'read that line range, not the whole file' 'to a file in your scratch directory and grep or tail it' > $T/both; { cat $T/both; echo 'Write the spec in as few writes as you can'; } > $T/spec_writer; { cat $T/both; printf '%s\n' 'Ground any one claim with at most 2 paths and 1 command' 'Run no test suite and build nothing' 'is a finding for the writer, or a question'; } > $T/critic; for r in "2. Spec writer|02-spec-writer.md|spec_writer" "3. Spec critic|03-spec-critic.md|critic"; do h=${r%%|*}; x=${r#*|}; c=${x%%|*}; f=${x#*|}; git show main:factory/prompts/$f.md > $T/a; git show main:docs/prompts/$c > $T/b; echo "$f copy=$(awk -v h="## $h" -v q="$Q" '$0==h{s=1;next} s&&$0==q"text"{p=1;next} p&&$0==q{exit} p' docs/design.md | cmp -s - docs/prompts/$c && echo SAME || echo DIFF) doc=$(tr '\n' ' ' < docs/prompts/$c | tr -s ' ' | grep -oF -f $T/$f | sort -u | grep -c .)/$(grep -c . $T/$f) run=$(tr '\n' ' ' < factory/prompts/$f.md | tr -s ' ' | grep -oF -f $T/$f | sort -u | grep -c .)/$(grep -c . $T/$f) fill=$([ "$(diff factory/prompts/$f.md docs/prompts/$c | grep '^[<>]')" = "$(diff $T/a $T/b | grep '^[<>]')" ] && echo unchanged || echo changed)"; done)`
- THEN it prints exactly `spec_writer copy=SAME doc=4/4 run=4/4 fill=unchanged`, then `critic copy=SAME doc=6/6 run=6/6 fill=unchanged`. `doc` and `run` count the rule phrases found in the documented copy and the run copy, each joined into one line so a phrase may wrap.

### Requirement: Spec writer and critic runs receive the turn-economy rules
The system prompt that `run start` writes for a spec writer run SHALL contain the writer's turn-economy rule, and the one it writes for a critic run SHALL contain the critic's reading rules, its per-claim cap and its no-suite, no-build rule.

#### Scenario: Spec writer and critic run prompts carry the new rules
- WHEN `(T=$(mktemp -d); export FACTORY_STATE=$T/s; for i in 1 2; do printf "# F$i\n\nDo x.\n" > $T/req$i.md; bin/factory ticket new --file $T/req$i.md >/dev/null; done; bin/factory ticket set T-0001 status=ready-for-spec-writer >/dev/null; bin/factory ticket set T-0002 status=ready-for-critic >/dev/null; bin/factory run start --role spec_writer --ticket T-0001 >/dev/null 2>&1; bin/factory run start --role critic --ticket T-0002 >/dev/null 2>&1; W=$(tr '\n' ' ' < $FACTORY_STATE/runs/run-0001-spec_writer/system-prompt.txt | tr -s ' '); C=$(tr '\n' ' ' < $FACTORY_STATE/runs/run-0002-critic/system-prompt.txt | tr -s ' '); echo "spec_writer batch=$(printf "%s" "$W" | grep -c 'Put independent reads and commands in one turn') writes=$(printf "%s" "$W" | grep -c 'Write the spec in as few writes as you can')"; echo "critic batch=$(printf "%s" "$C" | grep -c 'Put independent reads and commands in one turn') suite=$(printf "%s" "$C" | grep -c 'Run no test suite and build nothing') cap=$(printf "%s" "$C" | grep -c 'Ground any one claim with at most 2 paths and 1 command')")`
- THEN it prints exactly `spec_writer batch=1 writes=1`, then `critic batch=1 suite=1 cap=1`

### Requirement: Nothing else in the two prompts changes
The change MUST NOT remove or alter any existing line of the spec writer or critic prompt copies. The critic's RUBRIC, CONVERGENCE and OUTPUT sections and the writer's ROLE, INPUT, PROCESS and FORMAT sections SHALL stay byte for byte as on `main`, and no other file under `docs/prompts/`, `factory/prompts/` or `agents/` SHALL change.

#### Scenario: Rubric, round limit, format and every other prompt are unchanged
- WHEN `(T=$(mktemp -d); n=0; for x in "docs/prompts/02-spec-writer.md|1,/^RULES\$/p" "docs/prompts/02-spec-writer.md|/^FORMAT\$/,\$p" "factory/prompts/spec_writer.md|1,/^RULES\$/p" "factory/prompts/spec_writer.md|/^FORMAT\$/,\$p" "docs/prompts/03-spec-critic.md|1,/^PROCESS\$/p" "docs/prompts/03-spec-critic.md|/^ANTI-GOODHARTING/,\$p" "factory/prompts/critic.md|1,/^PROCESS\$/p" "factory/prompts/critic.md|/^ANTI-GOODHARTING/,\$p"; do f=${x%%|*}; s=${x#*|}; git show main:$f | sed -n "$s" > $T/a; sed -n "$s" $f > $T/b; [ -s $T/a ] || n=$((n+100)); cmp -s $T/a $T/b || { n=$((n+1)); echo "changed: $f $s"; }; done; echo "sections_changed=$n removed=$(git diff main...HEAD -- docs/prompts/02-spec-writer.md docs/prompts/03-spec-critic.md factory/prompts/spec_writer.md factory/prompts/critic.md | grep -v '^---' | grep -c '^-') others=$(git diff --name-only main...HEAD -- docs/prompts factory/prompts agents | grep -vxF -e docs/prompts/02-spec-writer.md -e docs/prompts/03-spec-critic.md -e factory/prompts/spec_writer.md -e factory/prompts/critic.md | grep -c .)")`
- THEN it prints only `sections_changed=0 removed=0 others=0`

### Requirement: The documents record the turn-economy change
`docs/changelog.md` SHALL gain one entry for issue #73 as its last numbered entry, numbered without a gap. `docs/principles.md` principle 2 SHALL name the critic's new rule among its mechanisms and SHALL say part B.2 is done by #41 for the code reviewer and by #73 for the critic. The change MUST add no whitespace errors.

#### Scenario: The changelog and the principles page record the change
- WHEN `(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md; grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -oF -e '#73' -e 'line range' -e 'scratch directory' -e 'no test suite' -e 'two paths and one command' | sort -u | grep -c .; P=$(sed -n '/^### 2\. /,/^### 3\. /p' docs/principles.md | tr '\n' ' ' | tr -s ' '); echo "implemented=$(printf '%s' "$P" | grep -c 'runs no test suite and builds nothing (#73, .factory/prompts/critic.md.)') status=$(printf '%s' "$P" | grep -c 'done by #41 for the code reviewer and by #73 for the critic')")`
- THEN it prints exactly `CONTIGUOUS`, then `5`, then `implemented=1 status=1`

#### Scenario: The turn-economy change adds no whitespace errors
- WHEN `(git diff --check main...HEAD; echo "exit=$?")`
- THEN it prints only `exit=0`

