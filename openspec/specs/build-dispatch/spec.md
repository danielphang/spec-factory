# build-dispatch

## Requirements

### Requirement: A park reason carries the failing command's error
When a store command fails and its relayed stderr is empty, the workflow scripts MUST put the refusal's JSON `error`, or else the exit code, after the reason's prefix, so that no park reason ends blank.

#### Scenario: A refused archive or sub-ticket add parks with the refusal text
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": false, "error": "no spec store (factory init not run)"}, "exit": 2}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "ST-2: no Depends on line"}, "exit": 2}}')`
- THEN it prints exactly `park: archive: no spec store (factory init not run)`, then `start: planner`, then `park: harness-bug: subticket add: ST-2: no Depends on line`

#### Scenario: A refused run start during intake parks with the refusal text
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run start": {"out": {"ok": false, "error": "T-0001 is parked, not ready-for-triage"}, "exit": 2}}')`
- THEN it prints exactly `start: triage`, then `park: harness-bug: run start triage: T-0001 is parked, not ready-for-triage`

#### Scenario: A command that prints no JSON parks with its exit code
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-parent-verify"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"raw": "", "exit": 1}}')`
- THEN it prints exactly `park: archive: exit 1, no JSON on stdout`

### Requirement: The build runs only the checkers a commit still needs
When a sub-ticket reaches the checks without an implementer run in that pass, the build MUST run only the checkers that have no result row on its commit; after an implementer run it SHALL run both.

#### Scenario: A redispatched sub-ticket runs only the checker whose row was set aside
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"verifier": "VERIFIED", "ci": "PASS"}, "missing": ["reviewer"]}}, "run finish": {"out": {"ok": true, "status": "APPROVE"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: reviewer`, then `park: stub stop`

#### Scenario: After an implementer run both checkers run
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "REQUEST-CHANGES", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, one per line

### Requirement: The workflows' clerk commands carry the dispatcher marker
Every store command that `factory/workflows/intake.js` and `factory/workflows/build.js` send to the clerk MUST carry `FACTORY_DISPATCH=1` in its environment assignments, so that a dispatch SHALL still complete on a live store while its own role run is in flight.

#### Scenario: Every clerk command of both workflows carries the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(echo "intake: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/intake.js)"; echo "build: $(node ${TMPDIR:-/tmp}/t0024-count.mjs factory/workflows/build.js)")`
- THEN it prints exactly `intake: sent unmarked=0`, then `build: sent unmarked=0`

#### Scenario: An intake run against a real store reaches its end with its run in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once. The clerk commands run for real on a scratch instance's own store, from the checkout under test, and the triage run is in flight when the workflow records its result.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory; git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init && (cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1 && printf '# F\n\nDo x.\n' > $T/req.md && $B ticket new --file $T/req.md >/dev/null) && echo "returned=$(node ${TMPDIR:-/tmp}/t0024-e2e.mjs $T/tgt/.factory) stored=$(cd $T/tgt && $B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `returned=closed stored=closed`

### Requirement: An implementer starts only when each sibling-added test it may change came from a merged sibling
`factory run start --role implementer` on a sub-ticket MUST refuse with exit 2, writing no run, worktree, branch or in-flight entry, with an error that starts `BLOCKED from harness: ` and names the file, when a line `` `<file>` (added by <ID>) `` inside its "Tests to change" field names a file that existed at the parent's base, or whose first adding commit on the integration branch since that base lies inside no merged sibling's recorded merge. It SHALL accept a file a merged sibling's merge added, and SHALL ignore such a line outside that field.

#### Scenario: A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the two fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0022-sib.sh <<'EOF'
# Sourced from the repo root with E set to a test file path. Builds a scratch store whose parent
# T-0001 is planned as ST-1 and ST-2: ST-2 depends on ST-1 and lists `$E` under Tests to change as
# added by ST-1. Builds a scratch target whose main holds tests/test_old.py from before the plan,
# tests/test_interim.py from ST-1's recorded merge, and tests/test_operator.py from a later direct
# commit that is no sibling's merge. ST-2's Scope line mentions tests/test_old.py in the same form.
# T-0001.1 is merged; T-0001.2 is ready for its implementer.
T22=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T22/store FACTORY_REPO=$T22/t FACTORY_INTEGRATION_BRANCH=main
printf '# Fixture\n\nThe bot should do the thing.\n' > $T22/req.md && printf '## Problem\nx\n' > $T22/spec.md
bin/factory ticket new --file $T22/req.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-spec-writer --by t >/dev/null
bin/factory spec add T-0001 --file $T22/spec.md >/dev/null
bin/factory ticket transition T-0001 --to ready-for-critic --by t --round spec:init >/dev/null
bin/factory ticket transition T-0001 --to awaiting-spec-gate --by t >/dev/null
bin/factory approve-spec T-0001 >/dev/null
git init -q -b main $T22/t && mkdir $T22/t/tests && echo 'def test_old(): pass' > $T22/t/tests/test_old.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm base && A=$(git -C $T22/t rev-parse HEAD)
git -C $T22/t checkout -qb sib && echo 'def test_interim(): pass' > $T22/t/tests/test_interim.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm interim && git -C $T22/t checkout -q main
git -C $T22/t -c user.email=f@x -c user.name=f merge -q --no-ff -m 'Merge ST-1' sib && B=$(git -C $T22/t rev-parse HEAD)
echo 'def test_operator(): pass' > $T22/t/tests/test_operator.py
git -C $T22/t add -A && git -C $T22/t -c user.email=f@x -c user.name=f commit -qm operator
printf 'ST-1 / Interim\nDepends on: none\nParallel-safe: yes\nInterim tests: `tests/test_interim.py`, broken by ST-2\n\nST-2 / Final\nDepends on: ST-1\nParallel-safe: yes\nScope: B, which reads `tests/test_old.py` (added by the base commit)\nTests to change:\n- `%s` (added by ST-1): ST-2 replaces the interim behaviour\nProtected paths: none\n' "$E" > $T22/plan.md
bin/factory subticket add T-0001 --file $T22/plan.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
bin/factory ticket set T-0001.1 status=merged "merge.base_before='$A'" "merge.main_after='$B'" >/dev/null
bin/factory ticket set T-0001 "parent_base='$A'" >/dev/null
bin/factory ticket set T-0001.2 status=ready-for-implementer >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0022-build.mjs <<'EOF'
// node t0022-build.mjs, from the checkout under test after sourcing t0022-sib.sh: runs
// factory/workflows/build.js on parent T-0001 of the store $FACTORY_STATE. Each clerk command runs
// for real (sh -c, from this checkout, environment unchanged); each role run returns an empty
// output, which the workflow records as a killed run. Prints each park, as `park <id>: <reason>`.
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return ''
  const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
  return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
}
const log = (s) => { const p = String(s).match(/^(\S+) parked: (.*)$/s); if (p) console.log(`park ${p[1]}: ${p[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 >/dev/null 2>&1; echo "exit=$? $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p') runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `exit=0 ready-for-implementer runs=1`

#### Scenario: A listed test that predates the plan, came from no sibling's merge, or was never added is refused before the implementer starts
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once.
- WHEN `(for E in tests/test_old.py tests/test_operator.py tests/test_never.py; do (. ${TMPDIR:-/tmp}/t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 >$T22/o 2>/dev/null; x=$?; J=$(tail -1 $T22/o); echo "exit=$x blocked=$(echo "$J" | grep -c '"error": "BLOCKED from harness: ') names=$(echo "$J" | grep -cF "$E") runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .) branch=$(git -C $FACTORY_REPO branch --list 'factory/T-0001.2' | grep -c .) $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')"); done)`
- THEN it prints three lines, each exactly `exit=2 blocked=1 names=1 runs=0 branch=0 ready-for-implementer`

### Requirement: The build parks a harness-blocked sub-ticket as BLOCKED, so a ruling returns it
When an implementer's run start is refused with an error that starts `BLOCKED `, the build workflow SHALL park the sub-ticket with that error, verbatim, as the reason, so that `factory resolve <id> --ruling F` MUST accept the park and return the sub-ticket to `ready-for-implementer`.

#### Scenario: The build parks the blocked sub-ticket with the harness's reason, and a ruling sends it back
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once.
- WHEN `(E=tests/test_old.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && node ${TMPDIR:-/tmp}/t0022-build.mjs | sed 's/\(BLOCKED from harness:\).*/\1/'; printf 'Ruling: x\n' > $T22/r.md; bin/factory resolve T-0001.2 --ruling $T22/r.md >/dev/null 2>&1; echo "ruling=$? $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')")`
- THEN it prints exactly `park T-0001.2: BLOCKED from harness:`, then `ruling=0 ready-for-implementer`

### Requirement: The build asks the whole-spec step before it runs the planner
At `ready-for-planner`, `factory/workflows/build.js` MUST first run `plan whole-spec`. On `"planner": "skipped"` it SHALL move the parent to `planned` and build the sub-ticket with no planner run. On any other success it SHALL run the planner as before. On a refusal it MUST park the parent with `harness-bug: plan whole-spec: <error>`.

#### Scenario: A qualifying spec reaches its implementer with no planner run, and a refused whole-spec step parks with its error
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "ready-for-planner"}}, "plan whole-spec": {"out": {"ok": true, "planner": "skipped", "reason": "fixture", "subtickets": [{"id": "T-0001.1"}]}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "run finish": {"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, "ticket join": {"out": {"ok": true, "decision": "park", "reason": "stub stop"}}}'; node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "plan whole-spec": {"out": {"ok": false, "error": "T-0001 has no approved spec"}, "exit": 2}}')`
- THEN it prints exactly `start: implementer`, `start: reviewer`, `start: verifier`, `park: stub stop`, `park: harness-bug: plan whole-spec: T-0001 has no approved spec`, one per line

#### Scenario: A spec that needs the planner still gets a planner run
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-planner"}}, "plan whole-spec": {"out": {"ok": true, "planner": "needed", "reason": "the spec writer marked it NEEDS-SPLIT"}}, "run finish": {"out": {"ok": true, "status": "PLANNED"}}, "subticket add": {"out": {"ok": false, "error": "stub stop"}, "exit": 2}}')`
- THEN it prints exactly `start: planner`, then `park: harness-bug: subticket add: stub stop`

### Requirement: A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT
When a role run ends without an output file, or with a blank one, whatever the agent call returned, `run finish` MUST record it as `EMPTY-OUTPUT` and never as `KILLED`. The workflow MUST keep the agent's non-blank last message as that run's `last-message.md` and re-dispatch the same role once. A second `EMPTY-OUTPUT` in a row SHALL park the ticket as `EMPTY-OUTPUT from <role>`, with no result row for that run.

#### Scenario: A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. This scenario needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- GIVEN the two fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0032-checks.sh <<'EOF'
# Sourced from the repo root after t0023-parent.sh: T-0001 is planned as one sub-ticket, T-0001.1,
# whose branch factory/T-0001.1 holds one commit; T-0001.1 is at checks-in-flight on that head $H,
# with no result rows, so the build runs both checkers on it.
printf 'ST-1 / Do it\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md
bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null
bin/factory ticket transition T-0001 --to planned --by t >/dev/null
git -C $T23/t checkout -qb factory/T-0001.1 && echo x > $T23/t/x.txt && git -C $T23/t add x.txt
git -C $T23/t -c user.email=f@x -c user.name=f commit -qm work && git -C $T23/t checkout -q main
H=$(git -C $T23/t rev-parse factory/T-0001.1)
bin/factory ticket set T-0001.1 status=checks-in-flight branch=factory/T-0001.1 head=$H >/dev/null
EOF
cat > ${TMPDIR:-/tmp}/t0032-build.mjs <<'EOF'
// node t0032-build.mjs '<plays JSON>', from the checkout under test after sourcing t0023-parent.sh
// and t0032-checks.sh: runs factory/workflows/build.js on parent T-0001 of the store $FACTORY_STATE.
// Each clerk command runs for real (sh -c, from this checkout, environment unchanged). Each role
// run plays the next entry of its role's list in <plays> (the last one repeats):
//   {"say": "<text>"}     returns <text> (or null) as its final message and writes no output file;
//   {"write": "<STATUS>"} writes an output with the run's head as its Commit: line (and, for the
//                         verifier, "Gate suite: PASS") and that STATUS, and returns the same text.
// Prints each park, as `park <id>: <reason>`.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const plays = JSON.parse(process.argv[2]), n = {}
const src = readFileSync('factory/workflows/build.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const r = prompt.match(/(\S+\/runs\/run-\d+-([a-z_]+))\/input\.md/)
  const list = plays[r[2]] || [{ say: '' }]
  n[r[2]] = (n[r[2]] || 0) + 1
  const p = list[Math.min(n[r[2]], list.length) - 1]
  if ('say' in p) return p.say
  const head = (readFileSync(`${r[1]}/meta.yaml`, 'utf8').match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  const text = `Commit: ${head}\n` + (r[2] === 'verifier' ? 'Gate suite: PASS\n' : '') + `STATUS: ${p.write}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  writeFileSync(`${r[1]}/output.md`, text)
  return text
}
const log = (s) => { const q = String(s).match(/^(\S+) parked: (.*)$/s); if (q) console.log(`park ${q[1]}: ${q[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: 'main', inlineRoles: true }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(M="Both suite runs are still in progress; I'll write the review once the monitor reports their final lines."; . ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs "{\"reviewer\": [{\"say\": \"$M\"}], \"verifier\": [{\"write\": \"VERIFIED\"}]}"; for r in reviewer verifier; do echo "$r: $(for d in $(ls -d $FACTORY_STATE/runs/*-$r); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')"; done; echo "kept=$(find $FACTORY_STATE/runs -path '*-reviewer/last-message.md' -exec grep -lxF "$M" {} + | grep -c .) $(bin/factory results show T-0001.1 | tail -1 | grep -o '"rows": {[^}]*}')")`
- THEN it prints exactly `park T-0001.1: EMPTY-OUTPUT from reviewer`, then `reviewer: EMPTY-OUTPUT EMPTY-OUTPUT ` (two reviewer runs, both empty), then `verifier: VERIFIED `, then `kept=2 "rows": {"ci": "PASS", "verifier": "VERIFIED"}` (both last messages kept verbatim, apostrophe included; no reviewer row, so a `--redispatch` re-runs only the reviewer)

#### Scenario: One empty reviewer run followed by a real one routes on the real one
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once. The first reviewer call returns `null`; the verifier's SPEC-DEFECT gives the join a fixed stop.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs '{"reviewer": [{"say": null}, {"write": "APPROVE"}], "verifier": [{"write": "SPEC-DEFECT"}]}'; echo "reviewer: $(for d in $(ls -d $FACTORY_STATE/runs/*-reviewer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.1: SPEC-DEFECT from verifier`, then `reviewer: EMPTY-OUTPUT APPROVE `

#### Scenario: An implementer that returns nothing twice parks as EMPTY-OUTPUT
Needs the GIVEN block of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" run once. In that fixture every role run returns an empty string.
- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && node ${TMPDIR:-/tmp}/t0022-build.mjs; echo "implementer: $(for d in $(ls -d $FACTORY_STATE/runs/*-implementer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.2: EMPTY-OUTPUT from implementer`, then `implementer: EMPTY-OUTPUT EMPTY-OUTPUT `

#### Scenario: An intake role's second empty output in a row parks as EMPTY-OUTPUT
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once. The stub store answers every `run finish` with `EMPTY-OUTPUT`.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/intake.js '{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run finish": {"out": {"ok": true, "run_id": "run-0009-x", "status": "EMPTY-OUTPUT", "escalations": []}}}')`
- THEN it prints exactly `start: triage`, then `start: triage`, then `park: EMPTY-OUTPUT from triage`

### Requirement: A role run that writes its output runs once and routes on its STATUS
A role run whose output file holds a STATUS MUST NOT be re-dispatched, and the build SHALL route on that STATUS as before.

#### Scenario: A reviewer that writes its output runs once
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && node ${TMPDIR:-/tmp}/t0032-build.mjs '{"reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "SPEC-DEFECT"}]}'; echo "reviewer: $(for d in $(ls -d $FACTORY_STATE/runs/*-reviewer); do sed -n 's/^status: //p' $d/meta.yaml; done | tr '\n' ' ')")`
- THEN it prints exactly `park T-0001.1: SPEC-DEFECT from verifier`, then `reviewer: APPROVE `

### Requirement: The build counts only the current plan's sub-tickets
The build MUST NOT park a parent for a superseded sub-ticket the human closed, and SHALL dispatch the current plan's ready sub-tickets. A closed sub-ticket of the current plan MUST still park the parent with `sub-ticket closed by a human: <id>`.

#### Scenario: The build of a re-planned parent dispatches the new sub-ticket instead of parking on the old one
Needs the GIVEN blocks of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored", "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once. In `t0022-build.mjs` every role run returns an empty string, so the implementer of the dispatched sub-ticket ends EMPTY-OUTPUT twice.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null; node ${TMPDIR:-/tmp}/t0022-build.mjs)`
- THEN it prints exactly `park T-0001.4: EMPTY-OUTPUT from implementer`

#### Scenario: A sub-ticket of the current plan that a human closed still parks the parent
Needs the GIVEN blocks of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" and "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\n' > $T23/plan1.md && bin/factory subticket add T-0001 --file $T23/plan1.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket transition T-0001.2 --to closed --by t >/dev/null; node ${TMPDIR:-/tmp}/t0022-build.mjs)`
- THEN it prints exactly `park T-0001: sub-ticket closed by a human: T-0001.2`

### Requirement: A parent's final check and close count only the current plan's sub-tickets
`factory ticket parent-check` SHALL move a planned parent to `ready-for-parent-verify` when every current sub-ticket has merged, and `ticket transition <parent> --to closed` MUST accept a VERIFIED final check whatever its superseded sub-tickets' states.

#### Scenario: With the new plan merged, the re-planned parent reaches its final check and closes
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" and "After a re-spec and a re-plan, only the new plan's sub-tickets count and the old records are kept" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0038-respec.sh && printf 'ST-1 / Redo\nDepends on: T-0001.1\nParallel-safe: yes\n' > $T23/plan2.md && bin/factory subticket add T-0001 --file $T23/plan2.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && bin/factory ticket set T-0001.4 status=merged >/dev/null; echo "check: $(bin/factory ticket parent-check T-0001 | tail -1 | grep -o '"state": "[^"]*"')"; R=$(bin/factory run start --role verifier --ticket T-0001 2>/dev/null | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p'); if [ -n "$R" ]; then H=$(sed -n "s/^head: '*\([0-9a-f]*\).*/\1/p" $FACTORY_STATE/runs/$R/meta.yaml); printf "Commit: $H\nGate suite: PASS\nSTATUS: VERIFIED\nCONFIDENCE: high, fixture\nESCALATIONS: none\n" > $FACTORY_STATE/runs/$R/output.md; bin/factory run finish $R >/dev/null 2>&1; fi; bin/factory ticket transition T-0001 --to closed --by t >/dev/null 2>&1; echo "close=$? $(bin/factory ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `check: "state": "ready-for-parent-verify"`, then `close=0 closed`

### Requirement: The build parks a merge the gate blocked, with the gate's reason
When `factory merge` is refused with an error that starts `BLOCKED `, `factory/workflows/build.js` MUST park the sub-ticket with that error, verbatim, as the reason, and SHALL NOT record it as a harness bug.

#### Scenario: The build parks a merge refused for protected paths with the gate's reason
Needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0023-wf.mjs factory/workflows/build.js '{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": [], "resumable": ["T-0001.1"], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "checks-in-flight"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "results show": {"out": {"ok": true, "rows": {"reviewer": "APPROVE", "verifier": "VERIFIED", "ci": "PASS"}, "missing": []}}, "ticket join": {"out": {"ok": true, "decision": "merge", "reason": "ci PASS + APPROVE + VERIFIED on the current head"}}, "merge": {"out": {"ok": false, "error": "BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py"}, "exit": 2}}')`
- THEN it prints exactly `park: BLOCKED from merge gate: protected paths not declared in T-0001 spec v1: core/b.py`

### Requirement: A sub-ticket whose spec drifted parks before its first implementer run
`factory run start --role implementer` on a sub-ticket with no implementer run and no ruling on file MUST refuse with exit 2, writing no run, with an error that starts `BLOCKED from harness: spec drift: `, when its Acceptance field names a sibling of the current plan that has not merged and is not among its dependencies, or when a test file changed on the integration branch since the parent's approved version was written, in a commit that changed a file that version's design names, and no Tests to change list names it; the build SHALL park it with that error, and a ruling SHALL let the next run start.

#### Scenario: A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n\nST-2 / Second\nDepends on: none\nParallel-safe: yes\nAcceptance:\n- REGRESSION: ST-1 scenarios still pass\n' && J=$(bin/factory run start --role implementer --ticket T-0001.2 2>/dev/null | tail -1); echo "unmerged: blocked=$(echo "$J" | grep -c '"error": "BLOCKED from harness: spec drift: ') names=$(echo "$J" | grep -c 'T-0001.1') runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .) $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')"; bin/factory ticket set T-0001.1 status=merged >/dev/null; bin/factory run start --role implementer --ticket T-0001.2 >/dev/null 2>&1; echo "merged: exit=$? runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `unmerged: blocked=1 names=1 runs=0 ready-for-implementer`, then `merged: exit=0 runs=1`

#### Scenario: A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start
Needs the GIVEN blocks of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" and of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" (current truth, build-dispatch) run once. In `t0022-build.mjs` every role run returns an empty string.
- WHEN `(. ${TMPDIR:-/tmp}/t0027-amend.sh && plan 'ST-1 / First\nDepends on: none\nParallel-safe: yes\n' && land src/greet.py tests/test_greet.py && land src/other.py tests/test_other.py && node ${TMPDIR:-/tmp}/t0022-build.mjs | sed 's/\(spec drift:\).*/\1/'; R=$(bin/factory ticket show T-0001.1 --json | tail -1); echo "greet=$(echo "$R" | grep -c 'tests/test_greet.py') other=$(echo "$R" | grep -c 'tests/test_other.py') runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c implementer)"; printf 'Ruling: the new test may change.\n' > $T27/r.md; bin/factory resolve T-0001.1 --ruling $T27/r.md >/dev/null 2>&1; bin/factory run start --role implementer --ticket T-0001.1 >/dev/null 2>&1; echo "ruled: exit=$? runs=$(ls $FACTORY_STATE/runs | grep -c implementer)")`
- THEN it prints exactly `park T-0001.1: BLOCKED from harness: spec drift:`, then `greet=1 other=0 runs=0`, then `ruled: exit=0 runs=1`

### Requirement: Changes that leave a sub-ticket's spec intact do not park it
A sub-ticket's first implementer run SHALL start when the commits since its parent's approved version was written change no file that version's design names, when every test they change is listed under Tests to change, or when an amendment was written after them.

#### Scenario: Unrelated changes, a listed test and an amendment written after the change let the implementer start
Needs the GIVEN block of "An intent-unchanged amendment re-pins the change and keeps the plan's tasks" run once.
- WHEN `(for c in other listed amended; do (. ${TMPDIR:-/tmp}/t0027-amend.sh && T='\nTests to change: none\n'; [ $c = listed ] && T='\nTests to change:\n- \140tests/test_greet.py\140: pins the old greeting\n'; plan "ST-1 / First\nDepends on: none\nParallel-safe: yes$T" && if [ $c = other ]; then land src/other.py tests/test_other.py; else land src/greet.py tests/test_greet.py; fi && if [ $c = amended ]; then bin/factory spec amend T-0001 --file $T27/v2.md --reason "Seed the greeting." --intent unchanged >/dev/null 2>&1; fi; bin/factory run start --role implementer --ticket T-0001.1 >/dev/null 2>&1; echo "$c: exit=$? runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c implementer)"); done)`
- THEN it prints exactly `other: exit=0 runs=1`, then `listed: exit=0 runs=1`, then `amended: exit=0 runs=1`

### Requirement: The driver takes a ticket through intake on the intake script's route
`factory drive TICKET --phase intake` MUST take a ticket from its stored intake state to the same end state, with the same ticket records, runs, result rows and log events, apart from ids and times, as `factory/workflows/intake.js` does when given the same role outputs, and it SHALL start no process other than one `claude` per role run.

#### Scenario: The driver takes the intake fixtures through the same routes as the intake script
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. This scenario also needs the GIVEN block of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) run once.
- GIVEN the six fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0040-claude <<'EOF'
#!/usr/bin/env node
// Stands in for `claude`. Run from a role run's directory (runs/run-NNNN-<role>). Appends one JSON line
// to $T40_LOG: its argv, its working directory, its pid and FACTORY_DISPATCH. Plays the next entry of
// its role's list in $T40_PLAYS (the last one repeats), counted in $T40_LOG.n-<role>. An entry may
// first sleep ("sleep": seconds), then:
//   {"write": "<STATUS>"}  writes output.md (a Commit: line with the run's head when meta.yaml has one;
//                          "Gate suite: PASS" for a verifier) and replies with the same text;
//   {"say": "<text>"}      writes nothing and replies with <text>;
//   {"fail": "<text>"}     writes nothing, replies with is_error and <text>, and exits 1.
// The reply is one JSON object on stdout, shaped like `claude -p --output-format json`. Each finished
// call appends "<start> <end>" (seconds) to $T40_LOG.times.
const fs = require('fs'), path = require('path')
const cwd = process.cwd(), log = process.env.T40_LOG, t0 = Date.now() / 1000
fs.appendFileSync(log, JSON.stringify({ argv: process.argv.slice(2), cwd, pid: process.pid, dispatch: process.env.FACTORY_DISPATCH || null }) + '\n')
const role = (path.basename(cwd).match(/^run-\d+-([a-z_]+)$/) || [])[1]
const list = (JSON.parse(process.env.T40_PLAYS || '{}')[role]) || [{ say: '' }]
const nf = `${log}.n-${role}`, n = (fs.existsSync(nf) ? +fs.readFileSync(nf, 'utf8') : 0) + 1
fs.writeFileSync(nf, String(n))
const p = list[Math.min(n, list.length) - 1]
if (p.sleep) Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, p.sleep * 1000)
let text = '', err = false
if ('write' in p) {
  const head = (fs.readFileSync('meta.yaml', 'utf8').match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  text = (head ? `Commit: ${head}\n` : '') + (role === 'verifier' ? 'Gate suite: PASS\n' : '') +
    `STATUS: ${p.write}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  fs.writeFileSync('output.md', text)
} else if ('fail' in p) { text = p.fail; err = true } else { text = p.say }
fs.appendFileSync(`${log}.times`, `${t0} ${Date.now() / 1000}\n`)
process.stdout.write(JSON.stringify({ type: 'result', subtype: err ? 'error_during_execution' : 'success', is_error: err,
  result: text, session_id: `stub-${path.basename(cwd)}`, total_cost_usd: 0.25, num_turns: 1,
  usage: { input_tokens: 10, cache_creation_input_tokens: 20, cache_read_input_tokens: 30, output_tokens: 5 } }) + '\n')
process.exit(err ? 1 : 0)
EOF
chmod +x ${TMPDIR:-/tmp}/t0040-claude && mkdir -p ${TMPDIR:-/tmp}/t0040-bin && ln -sf ${TMPDIR:-/tmp}/t0040-claude ${TMPDIR:-/tmp}/t0040-bin/claude
cat > ${TMPDIR:-/tmp}/t0040-wf.mjs <<'EOF'
// node t0040-wf.mjs <workflow script> <ticket>, from the checkout under test: runs that Workflow-tool
// script on <ticket> of the store $FACTORY_STATE. Each clerk command runs for real (sh -c, from this
// checkout). Each role call runs t0040-claude from the run's directory and returns its reply's
// `result`; a reply with is_error is thrown, as a failed agent call is.
import { readFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const [script, ticket] = process.argv.slice(2)
const src = readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const run = prompt.match(/(\S+\/runs\/run-\d+-[a-z_]+)\/input\.md/)[1]
  const cp = spawnSync(`${process.env.TMPDIR || '/tmp'}/t0040-claude`, ['-p', prompt], { cwd: run, encoding: 'utf8' })
  const reply = JSON.parse(cp.stdout)
  if (reply.is_error) throw new Error(reply.result)
  return reply.result
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket, repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: process.env.FACTORY_INTEGRATION_BRANCH, inlineRoles: true }, agent, () => {}, () => {},
  async (fs) => Promise.all(fs.map(f => f())))
EOF
cat > ${TMPDIR:-/tmp}/t0040-records.py <<'EOF'
# .venv/bin/python t0040-records.py <store>: prints the store's records in an order-free form, so two
# stores that took the same route print the same lines: each ticket's state, rounds and park reason;
# each run as role, ticket and status (no ids or times); each result row; log events counted by kind
# and ticket.
import collections, json, pathlib, sys, yaml
s = pathlib.Path(sys.argv[1]); y = lambda p: yaml.safe_load(p.read_text())
for p in sorted((s / "tickets").glob("*.yaml")):
    t = y(p); print("ticket", t["id"], t["status"], "spec=%s pr=%s" % (t["round"].get("spec"), t["round"].get("pr")),
                    "reason=" + str((t.get("parked") or {}).get("reason") or "").strip())
for line in sorted("run %s %s %s" % (m["role"], m["ticket"], m["status"]) for m in map(y, s.glob("runs/*/meta.yaml"))):
    print(line)
for line in sorted("result %s %s %s" % (r.get("ticket"), r.get("role"), r.get("status")) for r in map(y, s.glob("results/*/*.yaml"))):
    print(line)
ev = collections.Counter((e["event"], e.get("ticket")) for f in sorted(s.glob("log/*.jsonl")) for e in map(json.loads, f.read_text().splitlines()))
for (k, t), n in sorted(ev.items(), key=str):
    print("event", k, t, n)
EOF
cat > ${TMPDIR:-/tmp}/t0040-parity.sh <<'EOF'
# Sourced from the repo root with PHASE (intake or build) and P (plays, as for t0040-claude) set.
# Builds two identical fixtures: for intake, a throwaway store whose T-0001 is ready for triage; for
# build, t0023-parent.sh's store, whose T-0001 is ready for its planner. Runs the Workflow-tool script
# on one (under node) and `factory drive T-0001 --phase $PHASE` on the other, each role played by
# t0040-claude. Leaves in $D, per side (script, drive): <side>.records, <side>.log (t0040-claude's
# calls), <side>.out and <side>.err (stdout and stderr) and <side>.state (the store's path). Prints
# `<T-0001's state after drive> script=<calls>/<runs> drive=<calls>/<runs> same|differ`.
D=$(cd "$(mktemp -d)" && pwd -P)
for side in script drive; do (
  if [ $PHASE = intake ]; then T40=$(mktemp -d); export FACTORY_STATE=$T40/store
    printf '# Fixture\n\nThe bot should do the thing.\n' > $T40/req.md && bin/factory ticket new --file $T40/req.md >/dev/null
  else . ${TMPDIR:-/tmp}/t0023-parent.sh; T40=$T23; fi
  export T40_LOG=$D/$side.log T40_PLAYS="$P"; : > $T40_LOG; echo $FACTORY_STATE > $D/$side.state
  if [ $side = script ]; then node ${TMPDIR:-/tmp}/t0040-wf.mjs factory/workflows/$PHASE.js T-0001 > $D/$side.out 2> $D/$side.err
  else PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH bin/factory drive T-0001 --phase $PHASE > $D/$side.out 2> $D/$side.err; fi
  .venv/bin/python ${TMPDIR:-/tmp}/t0040-records.py $FACTORY_STATE > $D/$side.records
  echo "$(grep -c . $T40_LOG)/$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .)" > $D/$side.count ); done
echo "$(sed -n 's/^ticket T-0001 \([^ ]*\) .*/\1/p' $D/drive.records) script=$(cat $D/script.count) drive=$(cat $D/drive.count) $(cmp -s $D/script.records $D/drive.records && echo same || echo differ)"
EOF
cat > ${TMPDIR:-/tmp}/t0040-calls.py <<'EOF'
# .venv/bin/python t0040-calls.py <t0040-claude log>: one line per call, sorted: `<role> ok`, or
# `<role> bad: <what>`. A call is ok when it ran from its run's directory without FACTORY_DISPATCH,
# with argv `-p <prompt>` then options given once each: --model (the run's model), --output-format
# json, --permission-mode auto, --append-system-prompt-file <run>/system-prompt.txt, --tools and
# --allowedTools (one comma-separated argument each), and optionally --add-dir and --effort; no
# --bare and no --system-prompt-file. The prompt names only the run's input and output files. Every
# Edit allow rule covers only <run>/output.md, <run>/scratch/, the temporary directory, or for the
# implementer its worktree, which one rule covers; Edit is a tool only for the implementer.
import json, os, re, sys, tempfile, yaml
R = os.path.realpath; out = []
for c in map(json.loads, open(sys.argv[1]).read().splitlines()):
    run = R(c["cwd"]); m = yaml.safe_load(open(os.path.join(run, "meta.yaml"))); role = m["role"]; bad = []
    a = c["argv"]; opts = {}
    if a[:1] != ["-p"] or len(a) < 2: bad.append("no -p prompt")
    p = re.fullmatch(r"Your entire input is the file (\S+)/input\.md; read it first and follow it\. "
                     r"Write your complete output to (\S+)/output\.md and return the same text\.", a[1] if len(a) > 1 else "")
    if not p or R(p[1]) != run or R(p[2]) != run: bad.append("prompt")
    for k, v in zip(a[2::2], a[3::2]):
        if k in opts: bad.append("twice " + k)
        opts[k] = v
    if len(a[2:]) % 2: bad.append("odd options")
    want = {"--model": m["model"], "--output-format": "json", "--permission-mode": "auto"}
    bad += ["%s=%s" % (k, opts.get(k)) for k, v in want.items() if opts.get(k) != v]
    if R(opts.get("--append-system-prompt-file", "/")) != os.path.join(run, "system-prompt.txt"): bad.append("system prompt")
    bad += [k for k in opts if k not in ("--model", "--output-format", "--permission-mode", "--append-system-prompt-file",
                                         "--tools", "--allowedTools", "--add-dir", "--effort")]
    if c["dispatch"] is not None: bad.append("FACTORY_DISPATCH")
    tools = opts.get("--tools", "").split(","); allow = opts.get("--allowedTools", "").split(",")
    if ("Edit" in tools) != (role == "implementer"): bad.append("Edit tool")
    ok = [os.path.join(run, "output.md"), os.path.join(run, "scratch") + "/**", R(tempfile.gettempdir()) + "/**"]
    wt = R(m["worktree"]) + "/**" if m.get("worktree") else None
    edits = [R("/" + e[7:-1].rstrip("*").rstrip("/")) + ("/**" if e.endswith("/**)") else "") for e in allow if e.startswith("Edit(//")]
    if any(e.startswith("Edit") and not e.startswith("Edit(//") for e in allow): bad.append("Edit rule form")
    bad += ["edit " + e for e in edits if e not in ok and not (role == "implementer" and e == wt)]
    if role == "implementer" and wt not in edits: bad.append("no worktree edit")
    out.append("%s %s" % (role, "ok" if not bad else "bad: " + ", ".join(bad)))
print("\n".join(sorted(out)))
EOF
```

- WHEN `(for P in '{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}, {"write": "APPROVE"}]}' '{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}]}' '{"triage": [{"say": "still waiting on my commands"}]}' '{"triage": [{"fail": "usage limit reached"}]}'; do (PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh); done)`
- THEN it prints exactly `awaiting-spec-gate script=5/5 drive=5/5 same`, `parked script=5/5 drive=5/5 same`, `parked script=2/2 drive=2/2 same`, `parked script=1/1 drive=1/1 same`, one per line

### Requirement: The driver takes an approved ticket through the build on the build script's route
`factory drive TICKET --phase build` MUST take an approved parent from its stored build state to the same end state, with the same ticket records, runs, result rows and log events, apart from ids and times, as `factory/workflows/build.js` does when given the same role outputs.

#### Scenario: The driver takes the build fixtures through the same routes as the build script
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(for P in '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}' '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "REQUEST-CHANGES"}], "verifier": [{"write": "VERIFIED"}]}' '{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"say": ""}], "verifier": [{"write": "SPEC-DEFECT"}]}' '{"implementer": [{"write": "BLOCKED"}]}'; do (PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh); done)`
- THEN it prints exactly `parked script=4/4 drive=4/4 same`, `planned script=6/6 drive=6/6 same`, `planned script=4/4 drive=4/4 same`, `planned script=1/1 drive=1/1 same`, one per line

### Requirement: Each role run is one headless claude process with its role's prompt, model and tool limits
For every role run, the driver MUST start exactly one `claude` process from the run's directory, without `FACTORY_DISPATCH` in its environment, with argv `-p` and a prompt naming only the run's input and output files, then `--model` with the run's model, `--output-format json`, `--permission-mode auto`, `--append-system-prompt-file <run>/system-prompt.txt`, `--tools` and `--allowedTools`, and no `--bare`. Its `Edit` allow rules SHALL cover only the run's `output.md`, its `scratch/`, the temporary directory and, for the implementer alone, its worktree, and only the implementer SHALL have the `Edit` tool.

#### Scenario: Each role runs as one claude process with its prompt, model and tool limits
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; .venv/bin/python ${TMPDIR:-/tmp}/t0040-calls.py $D/drive.log; P='{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}'; PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; .venv/bin/python ${TMPDIR:-/tmp}/t0040-calls.py $D/drive.log)`
- THEN it prints exactly `critic ok`, `spec_writer ok`, `triage ok`, `implementer ok`, `reviewer ok`, `verifier ok`, `verifier ok`, one per line

### Requirement: A role process's reply is recorded with its run
After each role process ends, the run's directory MUST hold the process's stdout as `reply.json`, and the run's `meta.yaml` SHALL record its `session_id`, `total_cost_usd`, `num_turns` and `usage` under `claude:`.

#### Scenario: Each role run records its process's reply
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; .venv/bin/python -c 'import json,pathlib,sys,yaml; s=pathlib.Path(sys.argv[1]); ms=[yaml.safe_load(p.read_text()) for p in sorted(s.glob("runs/*/meta.yaml"))]; ok=lambda m,c: c.get("session_id")=="stub-"+m["run_id"] and c.get("total_cost_usd")==0.25 and c.get("num_turns")==1 and (c.get("usage") or {}).get("output_tokens")==5 and json.loads((s/"runs"/m["run_id"]/"reply.json").read_text())["session_id"]==c["session_id"]; print(" ".join("%s=%s" % (m["role"], "ok" if ok(m, m.get("claude") or {}) else "missing") for m in ms) or "none")' $(cat $D/drive.state))`
- THEN it prints exactly `triage=ok spec_writer=ok critic=ok`

### Requirement: The checkers run at once, and sub-tickets run concurrently up to a limit
The driver MUST run a head's reviewer and verifier as two concurrent processes, and SHALL build ready sub-tickets concurrently, at most `--parallel N` at a time, 2 when the option is not given.

#### Scenario: The checkers run at once, and sub-tickets up to the parallel limit
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once. Two sub-tickets with no dependency wait at `checks-in-flight`, each on its own commit; every checker sleeps 4 seconds, and the verifier's SPEC-DEFECT parks each one.
- WHEN `(for par in 1 default; do (. ${TMPDIR:-/tmp}/t0023-parent.sh && printf 'ST-1 / One\nDepends on: none\nParallel-safe: yes\n\nST-2 / Two\nDepends on: none\nParallel-safe: yes\n' > $T23/plan.md && bin/factory subticket add T-0001 --file $T23/plan.md >/dev/null && bin/factory ticket transition T-0001 --to planned --by t >/dev/null && for i in 1 2; do git -C $T23/t checkout -qb factory/T-0001.$i main && echo $i > $T23/t/f$i.txt && git -C $T23/t add f$i.txt && git -C $T23/t -c user.email=f@x -c user.name=f commit -qm w$i && git -C $T23/t checkout -q main && bin/factory ticket set T-0001.$i status=checks-in-flight branch=factory/T-0001.$i head=$(git -C $T23/t rev-parse factory/T-0001.$i) >/dev/null; done; export T40_LOG=$T23/claude.log T40_PLAYS='{"reviewer": [{"sleep": 4, "write": "APPROVE"}], "verifier": [{"sleep": 4, "write": "SPEC-DEFECT"}]}'; : > $T40_LOG; : > $T40_LOG.times; A=; [ $par = 1 ] && A='--parallel 1'; PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH bin/factory drive T-0001 --phase build $A >/dev/null 2>&1; echo "parallel=$par: calls=$(grep -c . $T40_LOG) max=$(.venv/bin/python -c 'import sys; t=[tuple(map(float, l.split())) for l in open(sys.argv[1])]; print(max([sum(a <= s < b for a, b in t) for s, _ in t] or [0]))' $T40_LOG.times) $(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') $(bin/factory ticket show T-0001.2 | sed -n 's/^status: //p')"); done)`
- THEN it prints exactly `parallel=1: calls=4 max=2 parked parked`, then `parallel=default: calls=4 max=4 parked parked`

### Requirement: The driver reports each step on one line and in a status file
Every line the driver prints on stdout before its last MUST have the form `<ticket id> "<title>": <step>`, naming the ticket the step concerns, a sub-ticket included. The last line SHALL be the result as one JSON object, and the store's `drive/<ticket>.yaml` SHALL hold the ticket, its title, the role processes still running and, once the driver ends, its result under `ended`; the store's `.gitignore` SHALL exclude `drive/`.

#### Scenario: Every intake step line names its ticket and title, and the status file shows the end
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "REVISE"}, {"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; O=$D/drive.out; echo "steps=$([ $(sed '$d' $O | grep -c .) -ge 10 ] && echo yes || echo no) untagged=$(sed '$d' $O | grep -vcE '^T-0001 "Fixture": ') last=$(tail -1 $O | grep -c '"state": "awaiting-spec-gate"') status=$(.venv/bin/python -c 'import sys,yaml; d=yaml.safe_load(open(sys.argv[1])); print(d["ticket"], d["title"], d["ended"]["state"], len(d["running"]))' $(cat $D/drive.state)/drive/T-0001.yaml 2>/dev/null) ignored=$(cat $(cat $D/drive.state)/.gitignore 2>/dev/null | grep -cx 'drive/')")`
- THEN it prints exactly `steps=yes untagged=0 last=1 status=T-0001 Fixture awaiting-spec-gate 0 ignored=1`

#### Scenario: Build step lines name the sub-ticket they concern
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}'; PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; O=$D/drive.out; echo "untagged=$(sed '$d' $O | grep -vcE '^T-0001(\.1)? "[^"]+": ') sub=$([ $(grep -cE '^T-0001\.1 "[^"]+": ' $O) -ge 6 ] && echo yes || echo no) last=$(tail -1 $O | grep -c '"state": "parked"')")`
- THEN it prints exactly `untagged=0 sub=yes last=1`

### Requirement: A stopped driver ends its role processes and resumes from the stored state
On SIGTERM or SIGINT the driver MUST end every role process it started, record each of its in-flight runs as `KILLED`, leave the ticket in its stored state unparked with nothing in flight, print a last line with `"stopped"` and exit with 128 plus the signal number; `factory drive TICKET` run again SHALL continue from the stored state, choosing the phase from that state when `--phase` is not given.

#### Scenario: A stopped driver ends its role process, records the run as killed and resumes from the stored state
Needs the GIVEN block of "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(T40=$(mktemp -d); export FACTORY_STATE=$T40/store T40_LOG=$T40/claude.log PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH; printf '# Fixture\n\nThe bot should do the thing.\n' > $T40/req.md && bin/factory ticket new --file $T40/req.md >/dev/null; T40_PLAYS='{"triage": [{"sleep": 60, "write": "ACCEPT"}]}' bin/factory drive T-0001 > $T40/out 2>/dev/null & p=$!; for i in $(seq 50); do [ -s $T40_LOG ] && break; sleep 0.2; done; sleep 1; r=$(grep -c '^- run: run-0001-triage' $FACTORY_STATE/drive/T-0001.yaml 2>/dev/null); kill -TERM $p 2>/dev/null; wait $p; x=$?; c=$(sed -n 's/.*"pid":\([0-9]*\).*/\1/p' $T40_LOG 2>/dev/null); echo "stop: exit=$x running=${r:-0} run=$(sed -n 's/^status: //p' $FACTORY_STATE/runs/run-0001-triage/meta.yaml 2>/dev/null) $(sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml) $(grep '^in_flight' $FACTORY_STATE/tickets/T-0001.yaml) child=$(kill -0 ${c:-999999} 2>/dev/null && echo alive || echo gone) last=$(tail -1 $T40/out | grep -c '"stopped": "SIGTERM"')"; T40_PLAYS='{"triage": [{"write": "REJECT"}]}' bin/factory drive T-0001 >/dev/null 2>&1; echo "resumed: exit=$? $(sed -n 's/^status: //p' $FACTORY_STATE/tickets/T-0001.yaml) calls=$(grep -c . $T40_LOG 2>/dev/null)")`
- THEN it prints exactly `stop: exit=143 running=1 run=KILLED ready-for-triage in_flight: [] child=gone last=1`, then `resumed: exit=0 closed calls=2`

### Requirement: The driver marks its own store calls, never its role processes, and passes a configured effort
`factory drive` MUST be refused by the live-store fence like any write, so that unmarked it is refused while a run is in flight on the target's own store and it is refused from inside that store's `runs/` even when marked. Once started, its store calls SHALL carry the dispatcher marker, its role processes SHALL NOT, and a role with a level under `effort:` in `instance.yaml` SHALL get `--effort <level>`.

#### Scenario: The driver marks its own store calls, never its roles', and passes a configured effort
Needs the GIVEN blocks of "Unmarked writes from inside the target are refused while a run is in flight, init included" (current truth, live-store-guard) and "The driver takes the intake fixtures through the same routes as the intake script" run once. T-0001's triage run stays in flight throughout; T-0002 is driven.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B ticket new --file $T/req2.md >/dev/null && printf 'effort:\n  triage: low\n' >> $T/tgt/.factory/instance.yaml && cd $T/tgt && export T40_LOG=$T/claude.log T40_PLAYS='{"triage": [{"write": "REJECT"}]}' PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH && : > $T40_LOG && $B drive T-0002 --phase intake >/dev/null 2>&1; u=$?; FACTORY_DISPATCH=1 $B drive T-0002 --phase intake >/dev/null 2>&1; m=$?; cd $W && FACTORY_DISPATCH=1 $B drive T-0002 --phase intake >/dev/null 2>&1; i=$?; echo "unmarked=$u marked=$m $($B ticket show T-0002 | sed -n 's/^status: //p') calls=$(grep -c . $T40_LOG) effort=$(grep -c '"--effort","low"' $T40_LOG) dispatch=$(grep -c '"dispatch":null' $T40_LOG) inside=$i")`
- THEN it prints exactly `unmarked=2 marked=0 closed calls=1 effort=1 dispatch=1 inside=2`

### Requirement: The Workflow scripts keep working beside the driver
`factory/workflows/intake.js` and `factory/workflows/build.js` SHALL still take a ticket through their routes unchanged until a later ticket retires them.

#### Scenario: The Workflow scripts still take both fixtures to the end of their routes
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution) and "The driver takes the intake fixtures through the same routes as the intake script" run once.
- WHEN `(P='{"implementer": [{"write": "READY-FOR-REVIEW"}], "reviewer": [{"write": "APPROVE"}], "verifier": [{"write": "VERIFIED"}]}'; PHASE=build; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; grep '^ticket' $D/script.records | cut -d' ' -f2,3 | paste -sd' ' -; P='{"triage": [{"write": "ACCEPT"}], "spec_writer": [{"write": "READY-FOR-CRITIC"}], "critic": [{"write": "APPROVE"}]}'; PHASE=intake; . ${TMPDIR:-/tmp}/t0040-parity.sh >/dev/null; grep '^ticket' $D/script.records | cut -d' ' -f2,3 | paste -sd' ' -)`
- THEN it prints exactly `T-0001.1 merged T-0001 parked`, then `T-0001 awaiting-spec-gate`
