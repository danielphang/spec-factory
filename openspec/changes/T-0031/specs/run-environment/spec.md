## ADDED Requirements

### Requirement: The running-code wrapper drops an inherited virtual environment
The running-code wrapper in every role's input, and around every gate command, MUST remove `$VIRTUAL_ENV/bin` from `PATH` and unset `VIRTUAL_ENV` and `PYTHONHOME` before it sets the fresh HOME and exports `run_env`, and SHALL still give each command a fresh HOME and the `run_env` exports.

#### Scenario: A role's wrapper and its wrapped gate command drop an inherited virtual environment
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`. Each WHEN runs in a subshell.
- GIVEN the fixture file written by the block below, run once at column 0 as shown (every later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0031-env.sh <<'EOF'
# Sourced from the repo root, with SYNC set to an environment_sync value for instance.yaml, or empty
# for none. Makes a scratch target with its own instance, used on a throwaway store $S, whose T-0001
# is approved and split into T-0001.1, ready for its implementer. The instance exports T31_CACHE
# through run_env and has one gate command, which runs the probe. $V is a fake virtualenv holding a
# `python`. The shell is left in the target.
B=$PWD/bin/factory; T31=$(cd "$(mktemp -d)" && pwd -P); V=$T31/venv
export GIT_AUTHOR_NAME=f GIT_AUTHOR_EMAIL=f@x GIT_COMMITTER_NAME=f GIT_COMMITTER_EMAIL=f@x
rid() { tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'; }
has() { grep -qF -- "$1" "$2" 2>/dev/null && echo 1 || echo 0; }
wrapper() { sed -n 's/^.*home directory: `\([^`]*\)`\. Put your command.*$/\1/p' "$1" | sed "s#<command>#$2#"; }
gate() { sed -n 's/^.*each is already wrapped): `\([^`]*\)`$/\1/p' "$1"; }
mkdir -p $V/bin && printf '#!/bin/sh\necho fake\n' > $V/bin/python && chmod +x $V/bin/python
printf 'echo "ve=${VIRTUAL_ENV:-unset} ph=${PYTHONHOME:-unset} fake_python=$(command -v python | grep -c %s) cache=${T31_CACHE:-unset} home=$([ "$HOME" = "%s" ] && echo caller || echo fresh)"\n' "$V/bin" "$HOME" > $T31/probe.sh
git init -q -b main $T31/tgt && cd $T31/tgt && git commit -q --allow-empty -m init
$B init --repo-name demo >/dev/null 2>&1
grep -v -e '^run_env:' -e '^gate_commands:' -e '^environment_sync:' .factory/instance.yaml > $T31/i.yaml
printf 'run_env: {T31_CACHE: /tmp/t31-cache}\ngate_commands: [". %s/probe.sh"]\n%s\n' "$T31" "${SYNC:+environment_sync: $SYNC}" >> $T31/i.yaml && mv $T31/i.yaml .factory/instance.yaml
export FACTORY_STATE=$T31/store; S=$T31/store
printf '# F\n\nDo x.\n' > $T31/req.md && printf '## Problem\nx\n' > $T31/spec.md
$B ticket new --file $T31/req.md >/dev/null
$B ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
$B spec add T-0001 --file $T31/spec.md >/dev/null
$B ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
$B ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
$B approve-spec T-0001 >/dev/null
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T31/plan.md && $B subticket add T-0001 --file $T31/plan.md >/dev/null
EOF
```

- WHEN `(SYNC=; . ${TMPDIR:-/tmp}/t0031-env.sh && R=$($B run start --role implementer --ticket T-0001.1 | rid) && $B run compose $R >/dev/null && for c in "$(wrapper $S/runs/$R/input.md ". $T31/probe.sh")" "$(gate $S/runs/$R/input.md)"; do VIRTUAL_ENV=$V PYTHONHOME=$V PATH=$V/bin:$PATH sh -c "$c"; done)`
- THEN it prints exactly two lines, each `ve=unset ph=unset fake_python=0 cache=/tmp/t31-cache home=fresh` (the first from the role's wrapper, the second from the wrapped gate command)

### Requirement: Each build checkout is synced before its role starts
When the instance sets `environment_sync`, `run start` for the implementer, reviewer and verifier SHALL run that command once in the run's checkout, at every run start, after the environment files are copied, through the running-code wrapper. The role's input SHALL then name the command and say the environment is already synced.

#### Scenario: An implementer's worktree is synced through the wrapper at every dispatch, and its input says so
Needs the GIVEN block of "A role's wrapper and its wrapped gate command drop an inherited virtual environment" run once.
- WHEN `(SYNC="'env > synced.env'"; . ${TMPDIR:-/tmp}/t0031-env.sh && E=$S/worktrees/T-0001.1/synced.env && R=$(VIRTUAL_ENV=$V PATH=$V/bin:$PATH $B run start --role implementer --ticket T-0001.1 | rid) && $B run compose $R >/dev/null && echo "first: synced=$([ -f $E ] && echo yes || echo no) ve=$(grep -c '^VIRTUAL_ENV=' $E 2>/dev/null) venv_on_path=$(grep '^PATH=' $E 2>/dev/null | grep -c "$V/bin") cache=$(has T31_CACHE=/tmp/t31-cache $E) home=$(grep -qx "HOME=$HOME" $E 2>/dev/null && echo caller || echo fresh) noted=$(grep 'env > synced.env' $S/runs/$R/input.md | grep -c 'already synced')" && $B run finish $R --status-override KILLED >/dev/null && rm -f $E && VIRTUAL_ENV=$V PATH=$V/bin:$PATH $B run start --role implementer --ticket T-0001.1 >/dev/null && echo "again: synced=$([ -f $E ] && echo yes || echo no)")`
- THEN it prints exactly `first: synced=yes ve=0 venv_on_path=0 cache=1 home=fresh noted=1`, then `again: synced=yes`

#### Scenario: A checker's checkout is synced before the checker starts, and its input says so
Needs the GIVEN block of "A role's wrapper and its wrapped gate command drop an inherited virtual environment" run once.
- WHEN `(SYNC="'env > synced.env'"; . ${TMPDIR:-/tmp}/t0031-env.sh && git checkout -q -b factory/T-0001.1 && git commit -q --allow-empty -m work && H=$(git rev-parse HEAD) && git checkout -q main && $B ticket set T-0001.1 status=checks-in-flight branch=factory/T-0001.1 head=$H >/dev/null && R=$(VIRTUAL_ENV=$V PATH=$V/bin:$PATH $B run start --role reviewer --ticket T-0001.1 | rid) && $B run compose $R >/dev/null && E=$S/runs/$R/wt/synced.env && echo "synced=$([ -f $E ] && echo yes || echo no) ve=$(grep -c '^VIRTUAL_ENV=' $E 2>/dev/null) venv_on_path=$(grep '^PATH=' $E 2>/dev/null | grep -c "$V/bin") noted=$(grep 'env > synced.env' $S/runs/$R/input.md | grep -c 'already synced')")`
- THEN it prints exactly `synced=yes ve=0 venv_on_path=0 noted=1`

### Requirement: A failed sync stops the run before it starts
When `environment_sync` exits non-zero, `run start` MUST refuse with exit 2, naming `environment_sync` and the exit code and giving the command's output. It MUST leave no run in flight and no checker checkout behind.

#### Scenario: A failed sync refuses the run start, names the sync, and leaves no run or checker checkout
Needs the GIVEN block of "A role's wrapper and its wrapped gate command drop an inherited virtual environment" run once. The sync command computes its output text and exit code, so that neither `sync-2` nor `exit 3` appears in the command itself.
- WHEN `(SYNC="'echo sync-\$((1+1)) >&2; exit \$((2+1))'"; . ${TMPDIR:-/tmp}/t0031-env.sh && $B run start --role implementer --ticket T-0001.1 >/dev/null 2>$T31/e1; i=$?; git -C $S/worktrees/T-0001.1 commit -q --allow-empty -m work && H=$(git -C $S/worktrees/T-0001.1 rev-parse HEAD) && $B ticket set T-0001.1 status=checks-in-flight head=$H >/dev/null && $B run start --role reviewer --ticket T-0001.1 >/dev/null 2>$T31/e2; r=$?; echo "implementer: exit=$i named=$(has environment_sync $T31/e1) code=$(has 'exit 3' $T31/e1) output=$(has sync-2 $T31/e1)"; echo "reviewer: exit=$r named=$(has environment_sync $T31/e2) code=$(has 'exit 3' $T31/e2) output=$(has sync-2 $T31/e2)"; echo "in_flight=$($B ticket show T-0001.1 --json | tail -1 | grep -c '"in_flight": \[\]') checker_checkouts=$(git worktree list | grep -c '/runs/')")`
- THEN it prints exactly `implementer: exit=2 named=1 code=1 output=1`, then `reviewer: exit=2 named=1 code=1 output=1`, then `in_flight=1 checker_checkouts=0`

### Requirement: Without environment_sync, run start and the input are unchanged
When the instance does not set `environment_sync`, `run start` SHALL run no command in the checkout, record no sync, and the role's input SHALL carry no sync line.

#### Scenario: Without environment_sync, run start and the input are as before
Needs the GIVEN block of "A role's wrapper and its wrapped gate command drop an inherited virtual environment" run once.
- WHEN `(SYNC=; . ${TMPDIR:-/tmp}/t0031-env.sh && R=$($B run start --role implementer --ticket T-0001.1 | rid) && $B run compose $R >/dev/null && echo "started=$([ -n "$R" ] && echo yes || echo no) noted=$(grep -c 'already synced' $S/runs/$R/input.md) recorded=$(grep -c '^environment_sync:' $S/runs/$R/meta.yaml) files=$(git -C $S/worktrees/T-0001.1 status --porcelain --untracked-files=all | grep -c .)")`
- THEN it prints exactly `started=yes noted=0 recorded=0 files=0`

