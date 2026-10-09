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

### Requirement: The merge gate refuses a changed protected path the pinned spec does not declare
`factory merge` MUST refuse with exit 2, merging nothing and changing no ticket field, when a path in `git diff --name-only --no-renames <integration>...<head>` matches an in-repo `protected_paths` glob and is neither declared on a `Protected paths:` line of the Risk section of the pinned spec nor in the ticket's `accepted_paths`. Its error SHALL start `BLOCKED from merge gate: ` and name each such path and no declared one. A declaration in another ticket's spec, or a Risk line in any other form, SHALL declare nothing.

#### Scenario: An undeclared protected path is refused at merge, by name, and nothing merges
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0033-gate.sh <<'EOF'
# Sourced from the repo root, with $1 the line T-0001's approved spec carries in its Risk section
# (each ^ in it stands for a backtick) and $2 the changes the sub-ticket's one commit makes,
# space-separated: `p` appends to file p (creating it), `p-` deletes p, `p>q` renames p to q.
# Builds a scratch instance whose protected paths are `core/**`, `bin/tool` and `~/.secret/**`,
# and a target whose main holds core/a.py, core/b.py, bin/tool and docs/d.md. T-0002's approved
# spec declares `core/b.py`. T-0001 is planned as T-0001.1, whose branch factory/T-0001.1 holds
# that one commit, head $H, with reviewer APPROVE, verifier VERIFIED and gate PASS recorded on $H;
# T-0001.1 is at checks-in-flight. Leaves $B, $T, $H and $M (main's tip).
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
mkdir $T/inst && cp tests/factory/fixtures/instance/context.md $T/inst/
grep -v '^protected_paths:\|^  infra:' tests/factory/fixtures/instance/instance.yaml > $T/inst/instance.yaml
printf '%s\n' 'protected_paths:' '  harness: ["core/**", "bin/tool"]' '  credentials: ["~/.secret/**"]' >> $T/inst/instance.yaml
export FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/store FACTORY_REPO=$T/t FACTORY_INTEGRATION_BRANCH=main
git init -q -b main $T/t && git -C $T/t config user.email f@x && git -C $T/t config user.name f
mkdir -p $T/t/core $T/t/bin $T/t/docs && for f in core/a.py core/b.py bin/tool docs/d.md; do echo x > $T/t/$f; done
git -C $T/t add -A && git -C $T/t commit -q -m init
for id in T-0001 T-0002; do
  [ $id = T-0001 ] && L=$(printf '%s' "$1" | tr '^' '\140') || L='Protected paths: `core/b.py`'
  printf "# F $id\n\nDo x.\n" > $T/req.md
  printf '=== proposal.md\n## Problem\nx\n## Risk\nBlast radius: small.\n%s\n=== design.md\n## Proposed change\nA. x\n' "$L" > $T/spec.md
  $B ticket new --file $T/req.md >/dev/null
  $B ticket transition $id --to ready-for-spec-writer --by t >/dev/null && $B spec add $id --file $T/spec.md >/dev/null
  $B ticket transition $id --to ready-for-critic --by t --round spec:init >/dev/null
  $B ticket transition $id --to awaiting-spec-gate --by t >/dev/null && $B approve-spec $id >/dev/null
done
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T/plan.md && $B subticket add T-0001 --file $T/plan.md >/dev/null
$B ticket transition T-0001 --to planned --by t >/dev/null
git -C $T/t checkout -q -b factory/T-0001.1
for f in $(echo "$2"); do
  case $f in
    *'>'*) mkdir -p $T/t/$(dirname ${f#*>}) && git -C $T/t mv ${f%%>*} ${f#*>} ;;
    *-) git -C $T/t rm -q ${f%-} ;;
    *) mkdir -p $T/t/$(dirname $f) && echo y >> $T/t/$f && git -C $T/t add $f ;;
  esac
done
git -C $T/t commit -q -m work && H=$(git -C $T/t rev-parse HEAD) && git -C $T/t checkout -q main && M=$(git -C $T/t rev-parse main)
$B ticket set T-0001.1 status=checks-in-flight branch=factory/T-0001.1 head=$H >/dev/null
printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/v.md
printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T/r.md
$B results record T-0001.1 --head $H --role verifier --output $T/v.md --run run-0001-verifier >/dev/null
$B results record T-0001.1 --head $H --role reviewer --output $T/r.md --run run-0002-reviewer >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0033-gate.sh 'Protected paths: ^core/a.py^' 'core/a.py core/b.py bin/tool docs/d.md' && $B merge T-0001.1 >$T/o 2>/dev/null; x=$?; J=$(tail -1 $T/o); echo "exit=$x blocked=$(echo "$J" | grep -c '"error": "BLOCKED from merge gate: ') named=$(echo "$J" | grep -o 'core/b\.py\|bin/tool' | sort -u | grep -c .) declared=$(echo "$J" | grep -c 'core/a\.py\|docs/d\.md') main=$([ "$(git -C $T/t rev-parse main)" = "$M" ] && echo unchanged || echo moved) $($B ticket show T-0001.1 | sed -n 's/^status: //p')")`
- THEN it prints exactly `exit=2 blocked=1 named=2 declared=0 main=unchanged checks-in-flight`. `named=2`: the error names both undeclared protected paths. `declared=0`: it names neither the declared protected path nor the unprotected one.

#### Scenario: Another ticket's declaration, a protected file moved away, or a Risk line in another form authorizes nothing
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once. The three cases: T-0001 declares nothing while T-0002 declares `core/b.py`; the sub-ticket renames `core/b.py` out of the protected tree; T-0001's only mention of `core/b.py` is a line `Not touched: ` followed by it.
- WHEN `(for c in 'Protected paths: none|core/b.py' 'Protected paths: none|core/b.py>docs/b.py' 'Not touched: ^core/b.py^|core/b.py'; do (. ${TMPDIR:-/tmp}/t0033-gate.sh "${c%%|*}" "${c#*|}" && $B merge T-0001.1 >$T/o 2>/dev/null; x=$?; echo "exit=$x named=$(tail -1 $T/o | grep -c 'core/b\.py') main=$([ "$(git -C $T/t rev-parse main)" = "$M" ] && echo unchanged || echo moved)"); done)`
- THEN it prints three lines, each exactly `exit=2 named=1 main=unchanged`

### Requirement: A declared or unprotected path merges with no further approval
`factory merge` SHALL merge, as before, a sub-ticket whose changed protected paths are all declared on its pinned spec's `Protected paths:` line, by exact path or glob, and one that changes no protected path.

#### Scenario: A declared protected path, or an unprotected one, merges with no further approval
Needs the GIVEN block of "An undeclared protected path is refused at merge, by name, and nothing merges" run once.
- WHEN `(for c in 'Protected paths: ^core/**^, ^bin/tool^|core/a.py core/new/c.py bin/tool' 'Protected paths: none|docs/d.md docs/e.md'; do (. ${TMPDIR:-/tmp}/t0033-gate.sh "${c%%|*}" "${c#*|}" && $B merge T-0001.1 >/dev/null 2>&1; echo "exit=$? $($B ticket show T-0001.1 | sed -n 's/^status: //p')"); done)`
- THEN it prints exactly `exit=0 merged`, twice
