# store-setup

## Requirements

### Requirement: Run records are exempt from whitespace checks
A store that `init` or `run start` has touched MUST hold a `.gitattributes` with the line `runs/** -whitespace`, so that `git diff --check` SHALL NOT report run records while it still reports every other store file.

#### Scenario: Run records in a store pass whitespace checks and other store files do not
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(T=$(mktemp -d) && git init -q -b main $T/r && git -C $T/r -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && FACTORY_STATE=$T/r/store bin/factory init >/dev/null && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m store && mkdir -p $T/r/store/runs/run-0001-verifier && printf 'context \n x\n' > $T/r/store/runs/run-0001-verifier/diff.patch && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m record && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "runs=$?"; printf 'x \n' > $T/r/store/notes.md && git -C $T/r add -A && git -C $T/r -c user.email=f@x -c user.name=f commit -q -m notes && git -C $T/r diff --check HEAD~1 HEAD >/dev/null; echo "other=$?")`
- THEN it prints `runs=0`, then `other=2`

#### Scenario: A run start adds the whitespace rule to an existing store
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && bin/factory run start --role planner --ticket T-0001 >/dev/null && echo "rule=$(cat $FACTORY_STATE/.gitattributes 2>/dev/null | grep -cxF 'runs/** -whitespace')")`
- THEN it prints `rule=1`

### Requirement: No half instance, and a missing briefing refuses
`factory init` MUST refuse with exit 2, writing nothing, when it would create an instance while `FACTORY_STATE` names another store; `run compose` MUST refuse with exit 2, writing no input, when the instance has no `context.md`.

#### Scenario: init refuses to create an instance on a throwaway store and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && FACTORY_STATE=$T/s $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e $T/tgt/.factory ] && echo written || echo none) store=$([ -e $T/s ] && echo written || echo none) names_state=$(grep -c FACTORY_STATE $T/err)")`
- THEN it prints `exit=2 instance=none store=none names_state=1`

#### Scenario: A missing briefing refuses the compose with exit 2
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && rm .factory/context.md && export FACTORY_STATE=$T/s && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null && $B run compose run-0001-triage >/dev/null 2>$T/err; echo "exit=$? input=$([ -e $T/s/runs/run-0001-triage/input.md ] && echo written || echo none) names_context=$(grep -c 'context.md' $T/err)")`
- THEN it prints `exit=2 input=none names_context=1`

### Requirement: Relative environment paths resolve from the caller's directory
A relative `FACTORY_STATE`, `FACTORY_INSTANCE` or `FACTORY_REPO` MUST resolve against the directory the command was run from; an absolute value SHALL be used as given.

#### Scenario: Relative FACTORY_STATE, FACTORY_INSTANCE and FACTORY_REPO resolve against the caller's directory
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); s=$(cd $T && FACTORY_INSTANCE=$F FACTORY_STATE=rel/store $B paths | tail -1); i=$(cd $F/.. && FACTORY_INSTANCE=instance $B paths | tail -1); r=$(cd $T && FACTORY_INSTANCE=$F FACTORY_REPO=rel $B paths | tail -1); echo "state=$(echo "$s" | grep -cF "\"state\": \"$T/rel/store\"") instance=$(echo "$i" | grep -cF "\"instance\": \"$F\"") repo=$(echo "$r" | grep -cF "\"state\": \"$T/rel/.factory/state\"")")`
- THEN it prints `state=1 instance=1 repo=1`

#### Scenario: An absolute FACTORY_STATE is used as given
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; F=$(cd tests/factory/fixtures/instance && pwd -P); cd / && echo "absolute=$(FACTORY_INSTANCE=$F FACTORY_STATE=$T/abs $B paths | tail -1 | grep -cF "\"state\": \"$T/abs\"")")`
- THEN it prints `absolute=1`

### Requirement: A new instance's store is a checkout of its own branch
`factory init` SHALL create a missing own store as a git worktree of branch `factory-store`, which the integration checkout does not see. It SHALL check that branch out when it already exists locally or on exactly one remote, so that a store commit never moves the integration branch.

#### Scenario: init creates the store on the factory-store branch, out of the integration checkout's sight
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1; echo "branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/state/')")`
- THEN it prints `branch=factory-store seen_by_main=0`

#### Scenario: init on a clone restores the store from the pushed branch
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/src && cd $T/src && git commit -q --allow-empty -m init && $B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T/src $T/c && cd $T/c && rm -rf .factory/state && $B init >/dev/null 2>&1; echo "exit=$? branch=$(git -C .factory/state symbolic-ref --short HEAD 2>/dev/null) restored=$(ls .factory/state/decisions.md 2>/dev/null | grep -c .)")`
- THEN it prints `exit=0 branch=factory-store restored=1`

### Requirement: init refuses when more than one remote carries the store branch
`factory init` MUST refuse with exit 2, creating no store and no local branch, when the own store is missing, no local `factory-store` exists and more than one remote carries it; the refusal MUST name each `<remote>/factory-store`.

#### Scenario: init on a clone with two remotes carrying the store branch refuses and names both
- GIVEN the three fixture files written by the block below, run once at column 0 as shown. Every later scenario of this change that names them reuses them.

```sh
cat > ${TMPDIR:-/tmp}/t0025-old.sh <<'EOF'
# Sourced from the repo root: a target whose store is a plain directory tracked on main, as both
# instances keep it today. Leaves the shell in the target; PRE is the commit that last tracked it.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
mkdir -p .factory/state && $B init --repo-name demo >/dev/null 2>&1
printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null
git add -A && git commit -q -m "instance, with its store on main" && PRE=$(git rev-parse HEAD)
EOF
cat > ${TMPDIR:-/tmp}/t0025-b1.sh <<'EOF'
# Sourced from the repo root: a target whose store at .factory/state is already a git worktree of
# an unborn factory-store branch, built with git alone (so it is the same layout whatever the
# harness does), then given an instance by init. Leaves the shell in the target.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
git worktree add -q --orphan -b factory-store .factory/state && echo /.factory/state/ >> "$(git rev-parse --git-path info/exclude)"
$B init --repo-name demo >/dev/null 2>&1
EOF
cat > ${TMPDIR:-/tmp}/t0025-gate.sh <<'EOF'
# Sourced from the repo root: a target made by init, its instance committed on main, and T-0001 on
# branch factory/T-0001 with reviewer APPROVE, verifier VERIFIED and gate PASS on its head H.
# Leaves the shell in the target.
B=$PWD/bin/factory; T25=$(cd "$(mktemp -d)" && pwd -P)
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
git init -q -b main $T25/tgt && cd $T25/tgt && git commit -q --allow-empty -m init
$B init --repo-name demo >/dev/null 2>&1 && git add -A && git commit -q -m instance
git checkout -q -b factory/T-0001 && echo x > x.txt && git add x.txt && git commit -q -m work
H=$(git rev-parse HEAD) && git checkout -q main
printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null
$B ticket set T-0001 status=checks-in-flight branch=factory/T-0001 head=$H >/dev/null
printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T25/v.md
printf "Commit: $H\nSTATUS: APPROVE\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $T25/rv.md
$B results record T-0001 --head $H --role verifier --output $T25/v.md --run run-0001-verifier >/dev/null
$B results record T-0001 --head $H --role reviewer --output $T25/rv.md --run run-0002-reviewer >/dev/null
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git add -A && git commit -q -m instance && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git clone -q $T25/tgt $T25/c && cd $T25/c && git remote add nas $T25/tgt && git fetch -q nas && $B init >/dev/null 2>$T25/err; echo "exit=$? store=$([ -e .factory/state ] && echo written || echo none) local_branch=$(git branch --list factory-store | grep -c .) names=$(grep -c 'origin/factory-store' $T25/err),$(grep -c 'nas/factory-store' $T25/err)")`
- THEN it prints `exit=2 store=none local_branch=0 names=1,1`

### Requirement: init refuses to run from inside the store checkout
`factory init`, run with `FACTORY_INSTANCE` unset from a directory whose git top level is a checkout of `factory-store`, or is the store of the instance found from that directory or a checkout of the same repository inside that store, MUST refuse with exit 2 and write nothing, whichever commit the store has checked out, so that it never creates an instance inside the live store; other commands run from there SHALL still find the live instance, and `init` in a separate repository under the store SHALL still create that repository's instance.

#### Scenario: init from a scratch directory inside the store checkout refuses and leaves the store unchanged
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=2 phantom=none store=unchanged`, then `found=ready-for-triage`

#### Scenario: init from the store checkout on a detached HEAD refuses
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && git -C .factory/state add -A && git -C .factory/state commit -q -m "store: first" && git -C .factory/state checkout -q --detach && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git -C .factory/state status --porcelain --untracked-files=all > $T25/before && cd .factory/state/runs/run-0001-triage/scratch && $B init --repo-name x >/dev/null 2>&1; echo "exit=$? detached=$(git -C $T25/tgt/.factory/state symbolic-ref -q HEAD >/dev/null && echo no || echo yes) phantom=$([ -e $T25/tgt/.factory/state/.factory ] && echo written || echo none) store=$(git -C $T25/tgt/.factory/state status --porcelain --untracked-files=all | cmp -s $T25/before - && echo unchanged || echo changed)"; echo "found=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=2 detached=yes phantom=none store=unchanged`, then `found=ready-for-triage`

#### Scenario: init in a separate repository under a run's scratch directory still creates its instance
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-b1.sh && printf '# F\n\nDo x.\n' > $T25/r.md && $B ticket new --file $T25/r.md >/dev/null && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && cd .factory/state/runs/run-0001-triage/scratch && git init -q -b main other && cd other && git commit -q --allow-empty -m init && $B init --repo-name other >/dev/null 2>&1; echo "exit=$? instance=$([ -f .factory/instance.yaml ] && echo written || echo none) live=$(cd $T25/tgt && $B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0 instance=written live=ready-for-triage`

### Requirement: init refuses a store path the integration branch has tracked
`factory init` MUST refuse with exit 2, writing nothing and naming the path, when it would create the own store at a path under which the integration branch has ever tracked a file.

#### Scenario: init refuses a once-tracked store path and writes nothing
- WHEN `(T=$(mktemp -d); B=$PWD/bin/factory; export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x; git init -q -b main $T/tgt && cd $T/tgt && mkdir -p .factory/state && echo old > .factory/state/old.md && git add -A && git commit -q -m "old store" && git rm -q -r .factory/state && git commit -q -m "store removed" && $B init --repo-name demo >/dev/null 2>$T/err; echo "exit=$? instance=$([ -e .factory ] && echo written || echo none) names_path=$(grep -q '\.factory/state' $T/err && echo 1 || echo 0)")`
- THEN it prints `exit=2 instance=none names_path=1`

### Requirement: store migrate moves a tracked store onto its branch and keeps every record
`factory store migrate --to PATH` on an idle, fully committed own store that is tracked on the integration branch SHALL do all of the following:
- put the store's last committed tree on a new `factory-store` branch, checked out at PATH;
- copy the store's ignored run files to PATH, and verify the copy before removing anything;
- untrack and remove the old path;
- set `state_dir` to PATH, so that later commands use the moved store.

#### Scenario: store migrate carries the store to factory-store at the new path
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && mkdir -p .factory/state/runs/run-0001-triage/scratch && echo n > .factory/state/runs/run-0001-triage/scratch/n.txt && $B store migrate --to .factory/store >/dev/null 2>&1; echo "exit=$?"; echo "branch=$(git -C .factory/store symbolic-ref --short HEAD 2>/dev/null) same_tree=$([ "$(git rev-parse -q --verify 'factory-store^{tree}')" = "$(git rev-parse $PRE:.factory/state)" ] && echo yes || echo no) scratch=$(cat .factory/store/runs/run-0001-triage/scratch/n.txt 2>/dev/null) old=$([ -e .factory/state ] && echo kept || echo gone) main_tracks=$(git ls-files .factory/state | grep -c .) seen_by_main=$(git status --porcelain --untracked-files=all | grep -c '^?? .factory/store/')"; echo "state_dir=$(sed -n 's/^state_dir: *//p' .factory/instance.yaml) ticket=$($B ticket show T-0001 2>/dev/null | sed -n 's/^status: //p')")`
- THEN it prints `exit=0`, then `branch=factory-store same_tree=yes scratch=n old=gone main_tracks=0 seen_by_main=0`, then `state_dir=.factory/store ticket=ready-for-triage`

### Requirement: store migrate refuses while the store is in use or uncommitted
`factory store migrate` MUST refuse with exit 2, creating no branch and no new path, when a store file is uncommitted or a run is in flight. The refusal MUST name the uncommitted files or the runs in flight.

#### Scenario: store migrate refuses an uncommitted store and a run in flight
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && echo edit >> .factory/state/decisions.md; $B store migrate --to .factory/store >/dev/null 2>$T25/e1; echo "uncommitted: exit=$? names=$(grep -c 'decisions.md' $T25/e1) branch=$(git branch --list factory-store | grep -c .)"; git checkout -q -- .factory/state/decisions.md && $B run start --role triage --ticket T-0001 >/dev/null 2>&1 && git add -A && git commit -q -m "run started"; FACTORY_DISPATCH=1 $B store migrate --to .factory/store >/dev/null 2>$T25/e2; echo "in flight: exit=$? names=$(grep -c 'run-0001-triage' $T25/e2) branch=$(git branch --list factory-store | grep -c .) new=$([ -e .factory/store ] && echo written || echo none)")`
- THEN it prints `uncommitted: exit=2 names=1 branch=0`, then `in flight: exit=2 names=1 branch=0 new=none`

### Requirement: A checkout of an older commit leaves a moved store untouched
After `store migrate`, checking out a commit from before the move in the integration checkout, and then checking out the integration branch again, MUST leave every file of the moved store as it was, uncommitted ones included.

#### Scenario: A checkout of an older commit leaves the moved store untouched
Needs the GIVEN block of "init on a clone with two remotes carrying the store branch refuses and names both" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0025-old.sh && $B store migrate --to .factory/store >/dev/null 2>&1 && git commit -q -a -m "store moved to its branch"; (echo live > .factory/store/live.md) 2>/dev/null; git checkout -q $PRE 2>/dev/null && git checkout -q main 2>/dev/null; echo "live=$(cat .factory/store/live.md 2>/dev/null || echo lost) on=$(git symbolic-ref --short HEAD)")`
- THEN it prints `live=live on=main`
