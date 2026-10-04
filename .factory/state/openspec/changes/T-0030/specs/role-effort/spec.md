## ADDED Requirements
### Requirement: An instance's effort map reaches each role's agent call and run record
A role listed in the instance's `effort:` map SHALL have that level passed to its agent call and recorded as `effort` in its run's `meta.yaml`; a role with no entry MUST get no effort argument and `effort: null`; the store-command agent SHALL stay at `low`; and `meta.yaml` SHALL record whether the run was inline.

#### Scenario: The intake workflow gives triage the effort the instance sets and records it
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once. The store commands run for real on a scratch instance's own store.
- WHEN `(B=$PWD/bin/factory; for c in high:inline none:typed; do e=${c%%:*}; m=${c##*:}; T=$(cd "$(mktemp -d)" && pwd -P); git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && { [ $e = none ] || printf 'effort:\n  triage: %s\n' $e >> .factory/instance.yaml; } && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && M=$T/tgt/.factory/state/runs/run-0001-triage/meta.yaml && echo "$(node ${TMPDIR:-/tmp}/t0030-e2e.mjs $T/tgt/.factory $([ $m = inline ] && echo 1)) meta_effort=$(sed -n 's/^effort: *//p' $M | grep . || echo absent) inline=$(sed -n 's/^inline: *//p' $M | grep . || echo absent)"; done)`
- THEN it prints exactly `role effort=high clerk effort=low meta_effort=high inline=true`, then `role effort=none clerk effort=low meta_effort=null inline=false`

#### Scenario: The build workflow passes the run's effort to each build role's agent call
Needs the GIVEN block of "Every agent type the workflows ask for has a definition" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0030-wf.mjs factory/workflows/build.js "$(sed 's/"run finish"/"run start": {"out": {"ok": true, "run_id": "run-0009-x", "worktree": "\/w", "effort": "max"}}, "run finish"/' ${TMPDIR:-/tmp}/t0030-build.json)")`
- THEN it prints exactly `factory-planner effort=max`, `factory-implementer effort=max`, `factory-reviewer effort=max`, `factory-verifier effort=max`, `clerk effort=low`, one per line

### Requirement: run start refuses an effort map with an unknown role or level
`factory run start` MUST refuse with exit 2, naming the bad entry and starting no run, when the instance's `effort:` map has a level other than `low`, `medium`, `high`, `xhigh` or `max`, or a key that is not one of the seven roles.

#### Scenario: An effort map with an unknown level or role is refused
- WHEN `(for e in 'triage: extreme' 'triag: high'; do T=$(cd "$(mktemp -d)" && pwd -P); cp -R tests/factory/fixtures/instance $T/inst && printf 'effort:\n  %s\n' "$e" >> $T/inst/instance.yaml && printf '# F\n\nDo x.\n' > $T/req.md && FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/s bin/factory ticket new --file $T/req.md >/dev/null && FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/s bin/factory run start --role triage --ticket T-0001 >/dev/null 2>$T/err; echo "exit=$? named=$(grep -cw -e extreme -e triag $T/err) runs=$(ls $T/s/runs 2>/dev/null | grep -c .)"; done)`
- THEN it prints exactly `exit=2 named=1 runs=0`, twice, one per line

