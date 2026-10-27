# truth-check

## Requirements

### Requirement: factory truth check replays each current-truth scenario under bash in the checkout under test and fails on a wrong print
`factory truth check` SHALL run, under `bash`, from the top of the git checkout that holds the caller's directory, the WHEN of every current-truth scenario it can read, after the GIVEN blocks that scenario needs. It SHALL compare the WHEN's standard output with the THEN by the exact-print rule, and print one line per scenario: `PASS`, `FAIL` or `SKIPPED`, its capability and its name. It SHALL also print the expected and printed lines under each failure, and a last line with the counts and the wall time in seconds. It MUST exit 1 when any scenario fails, and 0 otherwise. The first line SHALL name the checkout, the store and the folded deltas. `--capability NAME`, repeatable, SHALL limit the run to those capabilities. Capabilities SHALL run at the same time, each in its own fresh HOME and TMPDIR, with no `FACTORY_` variable in its scenarios' environment. An unknown capability, a store with no `openspec/specs`, and a caller outside a git checkout MUST be refused with exit 2.

#### Scenario: Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0059-truth.sh <<'EOF'
# Sourced from the repo root of the checkout under test. Builds a scratch target $G (a git repo
# whose main prints `hello` and whose branch factory/T-0001.1 prints `hello, world`) and a scratch
# store $S holding three current-truth capabilities (alpha, beta, gamma), five tickets and four
# change folders. T-0001 (sub-ticket T-0001.1 at its checks) and T-0002 (sub-ticket T-0002.1
# merged) are open; T-0003 is closed with a merged sub-ticket; T-0004 is open with nothing merged.
# $K is a checker's checkout of T-0001.1 under $S/runs/, $W the implementer's worktree under
# $S/worktrees/. Defines `check [args]`: runs truth check on $S from the current directory with
# T59_HOME and T59_TMP set to the caller's HOME and TMPDIR, output in $T/o, exit code in $T/x.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; S=$T/s; G=$T/tgt; F=$(printf '\140\140\140')
spec() { mkdir -p "$(dirname "$1")"; sed "s/^FENCE/$F/" > "$1"; }
git init -q -b main $G && cd $G && git config user.email f@x && git config user.name f
echo 'echo hello' > greet.sh && git add -A && git commit -q -m init
git checkout -q -b factory/T-0001.1 && echo 'echo hello, world' > greet.sh && git commit -q -am world && git checkout -q main
cd - >/dev/null
mkdir -p $S/tickets $S/runs/run-0002-verifier $S/worktrees
for t in 'T-0001 planned null' 'T-0001.1 checks-in-flight T-0001' 'T-0002 planned null' 'T-0002.1 merged T-0002' \
         'T-0003 closed null' 'T-0003.1 merged T-0003' 'T-0004 planned null'; do
  set -- $t; printf 'id: %s\nstatus: %s\nparent: %s\n' $1 $2 $3 > $S/tickets/$1.yaml
done
printf 'role: verifier\nticket: T-0001.1\n' > $S/runs/run-0002-verifier/meta.yaml
git -C $G worktree add -q --detach $S/runs/run-0002-verifier/wt factory/T-0001.1 && K=$S/runs/run-0002-verifier/wt
git -C $G worktree add -q $S/worktrees/T-0001.1 factory/T-0001.1 && W=$S/worktrees/T-0001.1
spec $S/openspec/specs/alpha/spec.md <<'EOS'
# alpha

## Requirements

### Requirement: Alpha greets
The greeting SHALL be printed.

#### Scenario: The greeting is printed exactly
- WHEN `(sh greet.sh)`
- THEN it prints exactly `hello`

### Requirement: Alpha reads its THENs
The check SHALL read each THEN by the exact-print rule.

#### Scenario: Two lines are read as a list
- WHEN `(sh greet.sh | sed 's/,.*//'; echo bye)`
- THEN it prints `hello`, then `bye` (the farewell second)

#### Scenario: A wrong greeting fails
- WHEN `(echo hullo)`
- THEN it prints exactly `hello`

#### Scenario: An exit status counts only when the THEN names it
- WHEN `(echo ok; exit 3)`
- THEN it prints `ok` and exits 0

#### Scenario: An exit status the THEN does not name is not compared
- WHEN `(echo ok; exit 3)`
- THEN it prints exactly `ok`

#### Scenario: A block of lines is compared line by line
- WHEN `(printf 'a  b\nc\n')`
- THEN it prints exactly these 2 lines:

FENCE
a  b
c
FENCE

#### Scenario: A counted list of lines is read
- WHEN `(echo one; echo two)`
- THEN it prints exactly two lines: `one`, then `two`

#### Scenario: Lines that repeat one text are read
- WHEN `(echo same; echo same)`
- THEN it prints exactly two lines, each `same`

#### Scenario: A prose THEN is skipped
- WHEN `(sh greet.sh)`
- THEN it prints a friendly greeting

#### Scenario: A fixture is written once
- GIVEN the fixture file written by the block below, run once at column 0 as shown

FENCEsh
echo given >> ${TMPDIR:-/tmp}/t0059-given.txt
FENCE

- WHEN `(cat ${TMPDIR:-/tmp}/t0059-given.txt)`
- THEN it prints exactly `given`
EOS
spec $S/openspec/specs/beta/spec.md <<'EOS'
# beta

## Requirements

### Requirement: Beta reuses a fixture and checks its environment
Each scenario SHALL run in its own environment.

#### Scenario: Another capability's fixture is reused
Needs the GIVEN block of "A fixture is written once" (alpha) run once.
- WHEN `(cat ${TMPDIR:-/tmp}/t0059-given.txt)`
- THEN it prints exactly `given`

#### Scenario: A scenario runs with a fresh HOME and TMPDIR and no FACTORY_ variable
- WHEN `(echo "home=$([ "$HOME" = "$T59_HOME" ] && echo caller || echo fresh) tmp=$([ "${TMPDIR:-/tmp}" = "$T59_TMP" ] && echo caller || echo own) factory=$(env | grep -c '^FACTORY_')")`
- THEN it prints exactly `home=fresh tmp=own factory=0`

#### Scenario: A missing fixture is skipped
Needs the GIVEN block of "No such scenario" run once.
- WHEN `(echo x)`
- THEN it prints exactly `x`

#### Scenario: A scenario can be skipped by its WHEN
- WHEN `(echo slow-marker)`
- THEN it prints exactly `slow-marker`
EOS
spec $S/openspec/specs/gamma/spec.md <<'EOS'
# gamma

## Requirements

### Requirement: Gamma counts
Gamma SHALL count.

#### Scenario: Gamma prints one
- WHEN `(echo 1)`
- THEN it prints exactly `1`

### Requirement: Gamma stays
Gamma SHALL stay.

#### Scenario: Gamma prints two
- WHEN `(echo 2)`
- THEN it prints exactly `2`
EOS
spec $S/openspec/changes/T-0001/specs/alpha/spec.md <<'EOS'
## MODIFIED Requirements

### Requirement: Alpha greets
The greeting SHALL name the world.

#### Scenario: The greeting names the world
- WHEN `(sh greet.sh)`
- THEN it prints exactly `hello, world`
EOS
spec $S/openspec/changes/T-0002/specs/gamma/spec.md <<'EOS'
## MODIFIED Requirements

### Requirement: Gamma counts
Gamma SHALL count to ten.

#### Scenario: Gamma prints one, then ten
- WHEN `(echo 1; echo 10)`
- THEN it prints exactly `1`, then `10`
EOS
spec $S/openspec/changes/T-0003/specs/gamma/spec.md <<'EOS'
## REMOVED Requirements

### Requirement: Gamma stays
Closed without archive.
EOS
spec $S/openspec/changes/T-0004/specs/gamma/spec.md <<'EOS'
## REMOVED Requirements

### Requirement: Gamma counts
Nothing of T-0004 has merged.
EOS
check() { T59_HOME=$HOME T59_TMP=${TMPDIR:-/tmp} $B truth check --store $S "$@" > $T/o 2>$T/e; echo $? > $T/x; }
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $G && check; echo "exit=$(cat $T/x)"; sed -nE 's/^(PASS|FAIL|SKIPPED) (alpha|beta): ([^:]*).*/\1 \3/p' $T/o; tail -1 $T/o | sed -E 's/wall time [0-9]+ s$/wall time N s/')`
- THEN it prints exactly these 16 lines:

```
exit=1
PASS The greeting is printed exactly
PASS Two lines are read as a list
FAIL A wrong greeting fails
FAIL An exit status counts only when the THEN names it
PASS An exit status the THEN does not name is not compared
PASS A block of lines is compared line by line
PASS A counted list of lines is read
PASS Lines that repeat one text are read
SKIPPED A prose THEN is skipped
PASS A fixture is written once
PASS Another capability's fixture is reused
PASS A scenario runs with a fresh HOME and TMPDIR and no FACTORY_ variable
SKIPPED A missing fixture is skipped
PASS A scenario can be skipped by its WHEN
16 scenarios: 11 passed, 2 failed, 3 skipped; wall time N s
```

#### Scenario: The first line names the checkout, the store and the folded deltas, and a failure shows what was expected and what was printed
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $G && check; head -1 $T/o | sed "s#$G#G#; s#$S#S#"; sed -n '/^FAIL alpha: A wrong greeting fails$/,/^[A-Z]/p' $T/o | sed '1d;$d')`
- THEN it prints exactly `truth check: G against S; folded: T-0002`, then `  expected:`, then `    hello`, then `  got:`, then `    hullo`, then `  exit 0`

#### Scenario: --capability limits the run, and an unknown capability, a store with no current truth and a caller outside git are refused
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && mkdir $T/empty && cd $G && check --capability gamma; echo "one: exit=$(cat $T/x) $(grep -cE '^(PASS|FAIL|SKIPPED) ' $T/o) $(grep -cE '^(PASS|FAIL|SKIPPED) gamma: ' $T/o)"; check --capability nope; echo "unknown: exit=$(cat $T/x) named=$(grep -c nope $T/e)"; $B truth check --store $T/empty >/dev/null 2>&1; echo "no-truth: exit=$?"; cd $T/empty && check; echo "no-git: exit=$(cat $T/x)")`
- THEN it prints exactly `one: exit=0 2 2`, then `unknown: exit=2 named=1`, then `no-truth: exit=2`, then `no-git: exit=2`

#### Scenario: Capabilities run at the same time
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once. Each of the two capabilities holds one scenario that sleeps three seconds.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && for c in one two; do mkdir -p $T/p/openspec/specs/$c && printf '# %s\n\n## Requirements\n\n### Requirement: %s sleeps\nIt SHALL sleep.\n\n#### Scenario: %s sleeps three seconds\n- WHEN `(sleep 3; echo slept)`\n- THEN it prints exactly `slept`\n' $c $c $c > $T/p/openspec/specs/$c/spec.md; done; cd $G && $B truth check --store $T/p | tail -1 | sed -nE 's/^2 scenarios: 2 passed, 0 failed, 0 skipped; wall time ([0-9]+) s$/\1/p' | awk '{print ($1 < 5 ? "together" : "one after another")}')`
- THEN it prints exactly `together`

### Requirement: A scenario the check cannot run mechanically is listed as skipped with its reason and counted
A scenario whose THEN the exact-print rule cannot read in full, whose named GIVEN block current truth does not hold, or whose WHEN contains a text given with `--skip-when-contains` MUST be listed as `SKIPPED` with its reason, and counted as skipped in the last line. It MUST never be counted as passed.

#### Scenario: Prose THENs, missing GIVEN blocks and WHENs the caller skips are listed with their reasons and counted as skipped
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $G && check --skip-when-contains slow-marker; grep '^SKIPPED ' $T/o | sed 's/^SKIPPED //'; tail -1 $T/o | sed -E 's/wall time [0-9]+ s$/wall time N s/')`
- THEN it prints exactly these 5 lines:

```
alpha: A prose THEN is skipped: THEN is not an exact print: it prints a friendly greeting
beta: A missing fixture is skipped: needs the GIVEN block of "No such scenario", which current truth does not hold
beta: A scenario can be skipped by its WHEN: its WHEN contains "slow-marker", which this run skips
gamma: Gamma prints one, then ten: in the approved delta of T-0002, which that ticket's verifier checks
16 scenarios: 10 passed, 2 failed, 4 skipped; wall time N s
```

### Requirement: On a ticket's checkout the check folds that ticket's approved delta, and every unarchived delta with merged code, before it runs
When the checkout under test is a ticket's implementer worktree (`<store>/worktrees/<id>`) or checker checkout (`<store>/runs/<run>/wt`), `factory truth check` SHALL fold into current truth the approved delta of that ticket's parent, or of the ticket itself when it has no parent, as archive folds it. From any checkout it SHALL also fold the delta of every change not yet archived whose ticket is not closed and has a merged sub-ticket. Each scenario in an ADDED or MODIFIED requirement of a folded delta SHALL be listed SKIPPED, naming that ticket. A folded delta that does not apply to current truth MUST be refused with exit 2, naming its ticket, and no scenario run.

#### Scenario: On a checker's checkout of a sub-ticket its parent's delta is folded and the delta's own scenarios are skipped
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once. On T-0001.1's branch the greeting is `hello, world`, which T-0001's delta expects; current truth still expects `hello`.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $K && check; head -1 $T/o | sed "s#$K#K#; s#$S#S#"; grep -E '^(PASS|FAIL|SKIPPED) (alpha: The greeting|gamma: )' $T/o; tail -1 $T/o | sed -E 's/wall time [0-9]+ s$/wall time N s/')`
- THEN it prints exactly these 5 lines:

```
truth check: K against S; folded: T-0001, T-0002
SKIPPED alpha: The greeting names the world: in the approved delta of T-0001, which that ticket's verifier checks
SKIPPED gamma: Gamma prints one, then ten: in the approved delta of T-0002, which that ticket's verifier checks
PASS gamma: Gamma prints two
16 scenarios: 10 passed, 2 failed, 4 skipped; wall time N s
```

#### Scenario: The implementer's worktree folds the same deltas
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $W && check; head -1 $T/o | sed "s#$W#W#; s#$S#S#"; grep -E '^(PASS|FAIL|SKIPPED) alpha: The greeting' $T/o)`
- THEN it prints exactly `truth check: W against S; folded: T-0001, T-0002`, then `SKIPPED alpha: The greeting names the world: in the approved delta of T-0001, which that ticket's verifier checks`

#### Scenario: From the integration branch only an open ticket's delta with a merged sub-ticket is folded
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once. T-0001 has nothing merged, T-0003 is closed and T-0004 has nothing merged; T-0004's delta would remove "Gamma counts".
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $G && check; grep -E '^(PASS|FAIL|SKIPPED) (alpha: The greeting|gamma: )' $T/o)`
- THEN it prints exactly `PASS alpha: The greeting is printed exactly`, then `SKIPPED gamma: Gamma prints one, then ten: in the approved delta of T-0002, which that ticket's verifier checks`, then `PASS gamma: Gamma prints two`

#### Scenario: A folded delta that no longer applies is refused, naming its ticket, and nothing runs
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && printf 'id: T-0005\nstatus: planned\nparent: null\n' > $S/tickets/T-0005.yaml && printf 'id: T-0005.1\nstatus: merged\nparent: T-0005\n' > $S/tickets/T-0005.1.yaml && mkdir -p $S/openspec/changes/T-0005/specs/gamma && printf '## MODIFIED Requirements\n\n### Requirement: Gamma is gone\nGamma SHALL go.\n' > $S/openspec/changes/T-0005/specs/gamma/spec.md && cd $G && check; echo "exit=$(cat $T/x) named=$(grep -c T-0005 $T/e) results=$(grep -cE '^(PASS|FAIL|SKIPPED) ' $T/o)")`
- THEN it prints exactly `exit=2 named=1 results=0`

### Requirement: truth check only reads, so it runs during a run, from inside the store and under any harness revision, and refuses --accept-harness
`factory truth check` MUST run on an instance's own store while a run is in flight there, from inside that store's `runs/`, and when the instance's `harness.lock` names another revision, and it MUST write nothing to the store or the instance. With no `--store` it SHALL read the store of the instance found from the caller's directory. Given `--accept-harness`, it MUST be refused with exit 2 and `{"ok": false, …}` on stdout, naming `factory --accept-harness <sha> config` with the same sha.

#### Scenario: truth check reads a live store with a run in flight, from inside its runs/, under another harness revision, and writes nothing
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" (current truth, live-store-guard) run once. T-0001's triage run is in flight on the target's own store, and the lock is overwritten to name another revision, so an ordinary read is refused.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && mkdir -p $S/openspec/specs && echo 0000000000000000000000000000000000000000 > $T/tgt/.factory/harness.lock && S0=$(snap); cd $T/tgt && $B truth check > $T/o1 2>&1; a=$?; cd $W && $B truth check --store $S > $T/o2 2>&1; b=$?; cd $T/tgt && $B ticket show T-0001 >/dev/null 2>&1; c=$?; echo "here=$a inside=$b store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) total=$(tail -1 $T/o1 | sed 's/;.*//') locked=$c")`
- THEN it prints exactly `here=0 inside=0 store=unchanged total=0 scenarios: 0 passed, 0 failed, 0 skipped locked=2`

#### Scenario: truth check refuses --accept-harness and names config
Needs the GIVEN block of "Each scenario of a fixture truth gets one result line, and the last line counts them and gives the wall time" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0059-truth.sh && cd $G && $B --accept-harness 0123456789abcdef0123456789abcdef01234567 truth check --store $S > $T/o 2>$T/e; echo "exit=$? hint=$(grep -cF 'factory --accept-harness 0123456789abcdef0123456789abcdef01234567 config' $T/e) json=$(tail -1 $T/o | grep -c '"ok": false')")`
- THEN it prints exactly `exit=2 hint=1 json=1`
