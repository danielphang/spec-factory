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
