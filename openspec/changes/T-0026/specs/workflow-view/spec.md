## ADDED Requirements

### Requirement: A run opens by naming its ticket
Each workflow script MUST print, as its first narrator line, the ticket id, its short title and its stored state, as `<id> · <short title> · <state>`, or `<id> · <state>` when the ticket has no title.

#### Scenario: The intake run opens with the ticket, its short title and its state
Run every command in this change from the repository root of the checkout under test, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the six fixture files written by the block below, run once at column 0 as shown (every later scenario of this change reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0026-view.mjs <<'EOF'
// node t0026-view.mjs <workflow.js> '<replies JSON>': runs one workflow script with a stub clerk, as
// t0023-wf.mjs does (same reply keys, list replies used in turn, last one repeats), and prints, in order,
// `log: <message>` for every narrator line, `label: <label>` for every agent call and `cmd: <command>`
// for every clerk command, verbatim.
import { readFileSync } from 'node:fs'
const [file, replies] = process.argv.slice(2)
const R = { 'config': { out: { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } },
  'run start': { out: { ok: true, run_id: 'run-0009-x', worktree: '/w' } }, ...JSON.parse(replies) }
const src = readFileSync(file, 'utf8').replace(/^export const meta/m, 'const meta')
const lines = []
const agent = async (prompt, opts) => {
  lines.push(`label: ${opts && opts.label}`)
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  const cmd = m[1].replace(/^.*?bin\/factory /s, '')
  lines.push(`cmd: ${m[1]}`)
  const key = Object.keys(R).filter(k => cmd.startsWith(k)).sort((a, b) => b.length - a.length)[0]
  let r = key ? R[key] : { out: { ok: true } }
  if (Array.isArray(r)) r = r.length > 1 ? r.shift() : r[0]
  return { stdout: 'raw' in r ? r.raw : JSON.stringify(r.out), exit: r.exit || 0, stderr: '' }
}
const log = (msg) => lines.push(`log: ${msg}`)
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r', state: '/tmp/s' }, agent, log, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(lines.join('\n'))
EOF
cat > ${TMPDIR:-/tmp}/t0026-intake.json <<'EOF'
{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}, "title": "Workflow view shows a short task title beside every ticket id, in narrator lines and agent labels"}}, "run finish": [{"out": {"ok": true, "status": "ACCEPT"}}, {"out": {"ok": true, "status": "READY-FOR-CRITIC"}}, {"out": {"ok": true, "status": "APPROVE"}}], "ticket transition": {"out": {"ok": true, "round": {"spec": 1}}}}
EOF
cat > ${TMPDIR:-/tmp}/t0026-park.json <<'EOF'
{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}, "title": "Harness hygiene: ruling on a BLOCKED park, park reasons, run-record whitespace and more"}}, "run finish": {"out": {"ok": true, "status": "NEEDS-HUMAN"}}}
EOF
cat > ${TMPDIR:-/tmp}/t0026-short.json <<'EOF'
{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}, "title": "Fix the label"}}, "run finish": {"out": {"ok": true, "status": "REJECT"}}, "ticket transition": {"out": {"ok": true}}}
EOF
cat > ${TMPDIR:-/tmp}/t0026-notitle.json <<'EOF'
{"ticket show": {"out": {"ok": true, "state": "ready-for-triage", "round": {"spec": 0}}}, "run finish": {"out": {"ok": true, "status": "REJECT"}}, "ticket transition": {"out": {"ok": true}}}
EOF
cat > ${TMPDIR:-/tmp}/t0026-build.json <<'EOF'
{"ticket show T-0001 ": {"out": {"ok": true, "state": "planned", "title": "Isolate the store from the integration branch: store commits move main and force catch-up runs"}}, "ticket ready-implementers": [{"out": {"ok": true, "ready": ["T-0001.1"], "resumable": [], "remaining": ["T-0001.1"], "subtickets": ["T-0001.1"], "closed": []}}, {"out": {"ok": true, "ready": [], "resumable": [], "remaining": [], "subtickets": ["T-0001.1"], "closed": []}}], "ticket show T-0001.1": {"out": {"ok": true, "state": "ready-for-implementer", "title": "init puts a new store on its factory-store branch"}}, "ticket head": {"out": {"ok": true, "head": "abababababababababababababababababababab"}}, "run finish": [{"out": {"ok": true, "status": "READY-FOR-REVIEW"}}, {"out": {"ok": true, "status": "APPROVE"}}, {"out": {"ok": true, "status": "VERIFIED"}}], "ticket join": {"out": {"ok": true, "decision": "merge", "reason": "all green"}}, "merge": {"out": {"ok": true, "main_after": "4f8f1d5"}}, "ticket parent-check": {"out": {"ok": true, "state": "ready-for-parent-verify", "reuse": "run-0001-verifier"}}, "archive": {"out": {"ok": true, "archived_to": "x"}}}
EOF
```

- WHEN `(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/intake.js "$(cat ${TMPDIR:-/tmp}/t0026-intake.json)" | sed -n 's/^log: //p' | head -1)`
- THEN it prints exactly `T-0001 · Workflow view shows a short task title beside every ticket… · ready-for-triage`

#### Scenario: A ticket with no title opens with its bare id and keeps bare-id labels
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/intake.js "$(cat ${TMPDIR:-/tmp}/t0026-notitle.json)" | grep -e '^log: ' -e '^label: triage')`
- THEN it prints exactly `log: T-0001 · ready-for-triage`, `label: triage T-0001`, `log: T-0001: triage run-0009-x: REJECT`, `log: T-0001: → closed`, one per line

### Requirement: The short title is the title cut at a word boundary
The short title MUST be the whole title when it has 60 characters or fewer; a longer title SHALL be cut at the last space within its first 61 characters (index 60 or earlier), so that at most 60 characters are kept, with trailing punctuation dropped and `…` appended.

#### Scenario: A long title is cut at a word boundary and loses its trailing comma
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/intake.js "$(cat ${TMPDIR:-/tmp}/t0026-park.json)" | sed -n 's/^log: //p')`
- THEN it prints exactly `T-0001 · Harness hygiene: ruling on a BLOCKED park, park reasons… · ready-for-triage`, then `T-0001 · Harness hygiene: ruling on a BLOCKED park, park reasons…: triage run-0009-x: NEEDS-HUMAN`, then `T-0001 · Harness hygiene: ruling on a BLOCKED park, park reasons…: parked: NEEDS-HUMAN from triage`

#### Scenario: A short title is shown whole
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/intake.js "$(cat ${TMPDIR:-/tmp}/t0026-short.json)" | sed -n 's/^log: //p')`
- THEN it prints exactly `T-0001 · Fix the label · ready-for-triage`, then `T-0001 · Fix the label: triage run-0009-x: REJECT`, then `T-0001 · Fix the label: → closed`

### Requirement: Every agent row names its ticket and short title
Once a ticket's title has been read, every role label and every clerk label MUST carry `<id> · <short title>` of the ticket that agent works on, a sub-ticket's own title for a sub-ticket; clerk labels SHALL read `clerk <id>[ · <short title>]: <action>`.

#### Scenario: Every intake row after the ticket is read carries its short title
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(O=$(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/intake.js "$(cat ${TMPDIR:-/tmp}/t0026-intake.json)"); T='T-0001 · Workflow view shows a short task title beside every ticket…'; echo "roles=$(echo "$O" | grep -cxF -e "label: triage $T" -e "label: spec_writer $T" -e "label: critic $T") clerk=$(echo "$O" | grep -cF "label: clerk $T: ") untitled=$(echo "$O" | grep '^label: ' | grep -vc ' · ')")`
- THEN it prints exactly `roles=3 clerk=13 untitled=2`

#### Scenario: Build rows carry the sub-ticket's own title, and the parent's rows the parent's
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(O=$(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/build.js "$(cat ${TMPDIR:-/tmp}/t0026-build.json)"); P='T-0001 · Isolate the store from the integration branch: store commits…'; C='T-0001.1 · init puts a new store on its factory-store branch'; echo "start=$(echo "$O" | sed -n 's/^log: //p' | head -1 | grep -cxF "$P · planned") roles=$(echo "$O" | grep -cxF -e "label: implementer $C" -e "label: reviewer $C" -e "label: verifier $C") sub_clerk=$(echo "$O" | grep -cF "label: clerk $C: ") parent_clerk=$(echo "$O" | grep -cF "label: clerk $P: ") untitled=$(echo "$O" | grep '^label: ' | grep -vc ' · ')")`
- THEN it prints exactly `start=1 roles=3 sub_clerk=19 parent_clerk=6 untitled=3`

### Requirement: Every narrator line names its ticket, and every state change is narrated
Every narrator line after the start line MUST begin with `<id>[ · <short title>]: ` for the ticket it is about, and each transition the store accepts SHALL print `<id>[ · <short title>]: → <state>`.

#### Scenario: Each intake state change gets a narrator line
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(O=$(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/intake.js "$(cat ${TMPDIR:-/tmp}/t0026-intake.json)"); T='T-0001 · Workflow view shows a short task title beside every ticket…'; echo "transitions=$(echo "$O" | grep -cxF -e "log: $T: → ready-for-spec-writer" -e "log: $T: → ready-for-critic" -e "log: $T: → awaiting-spec-gate") bare=$(echo "$O" | grep '^log: ' | grep -vc "^log: $T")")`
- THEN it prints exactly `transitions=3 bare=0`

#### Scenario: Build state changes and the merge are narrated under the right ticket
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(O=$(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/build.js "$(cat ${TMPDIR:-/tmp}/t0026-build.json)"); P='T-0001 · Isolate the store from the integration branch: store commits…'; C='T-0001.1 · init puts a new store on its factory-store branch'; echo "changes=$(echo "$O" | grep -cxF -e "log: $C: → checks-in-flight" -e "log: $C: → ready-for-merge" -e "log: $C: merged: 4f8f1d5" -e "log: $P: → closed") bare=$(echo "$O" | grep '^log: ' | grep -vc -e "^log: $P" -e "^log: $C")")`
- THEN it prints exactly `changes=4 bare=0`

### Requirement: Store commands and routing are unchanged
The store commands both scripts send, and their order, MUST stay byte-identical; only label and narrator text SHALL change, and among harness and document paths only the two workflow scripts SHALL change.

#### Scenario: The clerk commands are byte-identical on five paths
Needs the GIVEN block of "The intake run opens with the ticket, its short title and its state" run once.
- WHEN `(for w in intake:intake intake:park intake:short intake:notitle build:build; do echo "${w#*:} $(node ${TMPDIR:-/tmp}/t0026-view.mjs factory/workflows/${w%%:*}.js "$(cat ${TMPDIR:-/tmp}/t0026-${w#*:}.json)" | grep '^cmd: ' | cksum)"; done)`
- THEN it prints exactly `intake 1072986007 1493`, `park 536447330 571`, `short 24042256 547`, `notitle 24042256 547`, `build 3636463416 2810`, one per line

#### Scenario: Only the two workflow scripts change
- WHEN `(git diff --name-only main...HEAD -- factory bin agents tests docs dev README.md pyproject.toml uv.lock)`
- THEN it prints exactly `factory/workflows/build.js`, then `factory/workflows/intake.js`


