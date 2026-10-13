## ADDED Requirements

### Requirement: Run start takes each role's model from the instance and refuses a --model that names another
`factory run start` MUST record, in the run's `meta.yaml`, its `run.started` event and its printed JSON, the model that the instance's `models` names for the role. When given a `--model` that differs from that model, it SHALL refuse with exit 2 and the error `model <given> refused for <role>: the instance names <instance model>`, reserving no run, writing no event and adding nothing to the ticket's in-flight list.

#### Scenario: A run start given a model the instance does not name is refused and writes nothing, and one without --model records the instance's model
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell. The instance here names `sonnet` for triage, so the check cannot pass by matching a default.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); mkdir $T/inst && sed 's/^  triage: opus$/  triage: sonnet/' factory/instance.template.yaml > $T/inst/instance.yaml && export FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/store && printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; bin/factory run start --role triage --ticket T-0001 --model opus >$T/o 2>$T/e; echo "refused: exit=$? $(cat $T/e) runs=$(ls $FACTORY_STATE/runs 2>/dev/null | grep -c .) started=$(cat $FACTORY_STATE/log/*.jsonl | grep -c '"run.started"')"; bin/factory run start --role triage --ticket T-0001 >$T/o2 2>/dev/null; echo "default: exit=$? returned=$(tail -1 $T/o2 | sed -n 's/.*"model": "\([a-z]*\)".*/\1/p') recorded=$(sed -n 's/^model: //p' $FACTORY_STATE/runs/run-0001-triage/meta.yaml 2>/dev/null) logged=$(cat $FACTORY_STATE/log/*.jsonl | grep '"run.started"' | sed -n 's/.*"model": "\([a-z]*\)".*/\1/p' | paste -sd, -)")`
- THEN it prints exactly `refused: exit=2 model opus refused for triage: the instance names sonnet runs=0 started=0`, then `default: exit=0 returned=sonnet recorded=sonnet logged=sonnet`

#### Scenario: A run start given the instance's own model is accepted and records it
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); mkdir $T/inst && sed 's/^  triage: opus$/  triage: sonnet/' factory/instance.template.yaml > $T/inst/instance.yaml && export FACTORY_INSTANCE=$T/inst FACTORY_STATE=$T/store && printf '# F\n\nDo x.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; bin/factory run start --role triage --ticket T-0001 --model sonnet >$T/o 2>/dev/null; echo "exit=$? returned=$(tail -1 $T/o | sed -n 's/.*"model": "\([a-z]*\)".*/\1/p') recorded=$(sed -n 's/^model: //p' $FACTORY_STATE/runs/run-0001-triage/meta.yaml)")`
- THEN it prints exactly `exit=0 returned=sonnet recorded=sonnet`

### Requirement: A Workflow run whose relayed configuration names the wrong model parks at that role's run start
When the configuration that the clerk relays to `factory/workflows/intake.js` or `factory/workflows/build.js` names, for a role, a model other than the instance's, the script SHALL park the ticket at that role's run start with the reason `harness-bug: run start <role>: model <relayed> refused for <role>: the instance names <instance model>`. It MUST launch no agent of that role and record no run of it. A role whose relayed model is the instance's SHALL be launched on that model.

#### Scenario: An intake run told the wrong triage model parks before triage starts, and one told the right model runs triage on it
- GIVEN the fixture file written by the block below, run once at column 0 as shown (the later scenario of this change that names it reuses it)

```sh
cat > ${TMPDIR:-/tmp}/t0050-wf.mjs <<'EOF'
// node t0050-wf.mjs <workflow script> <ticket>, from the checkout under test: runs that Workflow-tool
// script on <ticket> of the store $FACTORY_STATE. Each clerk command runs for real (sh -c, from this
// checkout), except that when T50_SWAP is `<role>=<model>`, the stdout of `factory config` names
// <model> for <role>, as a clerk that retyped it would. Each role call prints
// `agent <role> <ticket> model=<the model it was launched on>`, writes an output with the STATUS that
// T50_PLAYS ({"<role>": "<STATUS>"}) gives its role (with the run's head as its Commit: line and, for
// the verifier, "Gate suite: PASS"), and returns the same text. Each park prints `park <id>: <reason>`.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const [script, ticket] = process.argv.slice(2)
const plays = JSON.parse(process.env.T50_PLAYS || '{}')
const [swapRole, swapModel] = (process.env.T50_SWAP || '=').split('=')
const src = readFileSync(script, 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt, opts) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    let stdout = cp.stdout
    if (swapRole && /bin\/factory config$/.test(m[1])) {
      const c = JSON.parse(stdout.trim().split('\n').pop()); c.models[swapRole] = swapModel; stdout = JSON.stringify(c) + '\n'
    }
    return { stdout, exit: cp.status, stderr: cp.stderr }
  }
  console.log(`agent ${opts.label} model=${opts.model}`)
  const r = prompt.match(/(\S+\/runs\/run-\d+-([a-z_]+))\/input\.md/)
  const head = (readFileSync(`${r[1]}/meta.yaml`, 'utf8').match(/^head: '?([0-9a-f]{40})/m) || [])[1]
  const text = (head ? `Commit: ${head}\n` : '') + (r[2] === 'verifier' ? 'Gate suite: PASS\n' : '') +
    `STATUS: ${plays[r[2]] || 'NONE'}\nCONFIDENCE: high, stub\nESCALATIONS: none\n`
  writeFileSync(`${r[1]}/output.md`, text)
  return text
}
const log = (s) => { const q = String(s).match(/^(\S+) parked: (.*)$/s); if (q) console.log(`park ${q[1]}: ${q[2]}`) }
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket, repo: process.cwd(), state: process.env.FACTORY_STATE, target: process.env.FACTORY_REPO,
  integration: process.env.FACTORY_INTEGRATION_BRANCH || 'main', inlineRoles: true }, agent, log, () => {},
  async (fs) => Promise.all(fs.map(f => f())))
EOF
```

- WHEN `(for swap in '' triage=fable; do (T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store T50_SWAP=$swap T50_PLAYS='{"triage": "REJECT"}'; printf '# Fixture\n\nThe bot should do the thing.\n' > $T/req.md && bin/factory ticket new --file $T/req.md >/dev/null; node ${TMPDIR:-/tmp}/t0050-wf.mjs factory/workflows/intake.js T-0001 | grep .; echo "swap=${swap:-none} $(bin/factory ticket show T-0001 | sed -n 's/^status: //p') runs=$(for d in $(ls $FACTORY_STATE/runs 2>/dev/null); do echo "${d#run-????-}=$(sed -n 's/^model: //p' $FACTORY_STATE/runs/$d/meta.yaml)"; done | sort | paste -sd' ' -)"); done)`
- THEN it prints exactly `agent triage T-0001 model=opus`, `swap=none closed runs=triage=opus`, `park T-0001: harness-bug: run start triage: model fable refused for triage: the instance names opus`, `swap=triage=fable parked runs=`, one per line

#### Scenario: A build told the wrong verifier model parks the sub-ticket before any verifier starts, and the reviewer still runs on its own model
Needs the GIVEN blocks of "A ruling on a BLOCKED park returns the sub-ticket to its implementer with the ruling" (current truth, human-resolution), "A reviewer that ends its turn waiting on its own commands is re-dispatched once, then parks as EMPTY-OUTPUT beside the verifier's passing rows" (current truth, build-dispatch) and "An intake run told the wrong triage model parks before triage starts, and one told the right model runs triage on it" run once. T-0001.1 waits at its checks, so the build starts its reviewer and verifier together. This is the incident's route.
- WHEN `(. ${TMPDIR:-/tmp}/t0023-parent.sh && . ${TMPDIR:-/tmp}/t0032-checks.sh && export T50_SWAP=verifier=fable T50_PLAYS='{"reviewer": "APPROVE", "verifier": "VERIFIED"}'; node ${TMPDIR:-/tmp}/t0050-wf.mjs factory/workflows/build.js T-0001 | grep . | sort; echo "$(bin/factory ticket show T-0001.1 | sed -n 's/^status: //p') runs=$(for d in $(ls $FACTORY_STATE/runs 2>/dev/null); do echo "${d#run-????-}=$(sed -n 's/^model: //p' $FACTORY_STATE/runs/$d/meta.yaml)"; done | sort | paste -sd' ' -)")`
- THEN it prints exactly `agent reviewer T-0001.1 model=fable`, `park T-0001.1: harness-bug: run start verifier: model fable refused for verifier: the instance names opus`, `parked runs=reviewer=fable`, one per line

### Requirement: Existing callers of run start keep working
The driver and the harness suite MUST still start every role run they start today; the only existing test files this change edits SHALL be the two fixtures that passed a model the instance does not name.

#### Scenario: The harness suite passes with only the two fixtures that passed a wrong model changed
Per the standing T-0023 decision, the command gives pytest its own temporary directory under `/tmp` and removes it when it ends.
- WHEN `(P=$(mktemp -d /tmp/t0050-suite.XXXXXX) && TMPDIR=$P uv run --frozen pytest -q -p no:cacheprovider tests/factory 2>&1 | tail -1; rm -rf "$P"; git diff --name-only --diff-filter=DMR main...HEAD -- tests)`
- THEN the first line reports a number of passed tests and no `failed` or `error`, and every later line, if any, is `tests/factory/test_coding_standard.py` or `tests/factory/test_turn_economy.py`

