=== proposal.md
## Problem

The operator cannot tell, at a glance, what task a factory run is working on. Every row in the run's live progress display names the work by a bare ticket id, such as `T-0018`, and the operator does not remember which id is which task. Each glance at the display, often on a phone, means looking the id up.

Some background on the parts involved. The factory moves each request through a chain of AI agents. Each request is a ticket with an id (`T-0026`) and a one-line title. A large ticket is split into sub-tickets (`T-0025.1`), each with its own title. Two scripts drive the agents: one takes a ticket from request to an approved spec, and one builds an approved ticket. Both run inside Claude Code's Workflow tool, whose progress display (in the terminal and in the mobile app) shows two kinds of text:

- an agent label: one row per agent the script starts. Besides the role agents (triage, spec writer, implementer and so on), the scripts start a small "clerk" agent for every read or write of the ticket store, the database of ticket records. So most rows are clerk rows.
- a narrator line: a free-text message the script prints above the rows.

Today the role rows read `triage T-0012`, the clerk rows read `clerk: run start triage` with no ticket at all, and the narrator lines name the ticket by bare id or not at all. Nothing on the display says what the task is.

This change adds a short version of the ticket's title beside every ticket id in both scripts. The short title is the title cut to at most 60 characters at a word boundary. It appears in four places: a narrator line when a run starts, giving the ticket, its short title and its state; a narrator line each time the ticket's state changes; every role row; and every clerk row. A sub-ticket's rows and lines carry the sub-ticket's own title. Only display text changes: the store commands the scripts send and the way they route on each agent's result stay exactly as they are.

## Evidence

I ran each workflow script on this checkout under node, with a stand-in for the clerk agent. The stand-in returns canned store replies instead of running commands, and records every agent label, every narrator line and every store command. The acceptance scenarios already in force for the build and intake scripts drive them the same way. The full setup is the first block of the first acceptance scenario below.

An intake run of a ticket titled "Workflow view shows a short task title beside every ticket id, in narrator lines and agent labels" printed these labels and lines (excerpt):

```
label: clerk: run start triage
label: triage T-0001
log: triage run-0009-x: ACCEPT
label: clerk: transition -> ready-for-spec-writer
...
log: critic run-0009-x: APPROVE
label: clerk: transition -> awaiting-spec-gate
log: T-0001: spec approved by critic in round 1; awaiting the human gate (bin/factory approve-spec T-0001)
```

No label or line carries the title. Of 18 labels, none carries it: `roles=0 clerk=0 untitled=18`. Three state changes produced no narrator line of their own: `transitions=0`. The first narrator line appears only after the first agent has finished.

A build run of a parent ticket with one sub-ticket printed 31 labels, none with a title (`untitled=31`). Its narrator lines name the sub-ticket in brackets after a run id, for example `log: implementer run-0009-x (T-0001.1): READY-FOR-REVIEW`. The transitions to `checks-in-flight`, `ready-for-merge` and `closed` produced no narrator line (`changes=0`).

Where the code builds this text:

- `factory/workflows/intake.js:54` and `factory/workflows/build.js:45` build every clerk label as `` `clerk: ${label}` ``.
- Role labels are `` `${role} ${TICKET}` `` and `` `${role} (stub) ${TICKET}` `` (intake.js:97 and :91), and `` `${role} ${ticket}` `` and `` `${role} (stub) ${ticket}` `` (build.js:88 and :82).
- The narrator lines are the `log()` calls at intake.js:72, 112, 113 and 166, and at build.js:63, 111, 112, 172, 176, 232, 240, 243 and 260. None names a title. The request said "the scripts never call `log()`". That is not so; the existing calls name only an id, which is the problem.
- The title is already in hand. Both scripts call `ticket show <id> --json` for the parent (intake.js:126, build.js:198), and build.js:126 makes the same call for each sub-ticket. The JSON carries `"title"` (`factory/cli.py:88`).

The request's GitHub-issue part has no reliable source:

- None of the requests under `.factory/state/requests/` has an `issue:` header (`grep -c '^issue:'` found 0 files).
- `ticket show --json` does not return a request's header.
- Two request titles carry a `#NN`, and only one of them names the ticket's own issue. `T-0015`'s title says "(rescoped #20)", and `dev/issues.md` row 20 is that ticket's issue. `T-0020`'s title says "(split from #36)", but its issue is #38 (`dev/issues.md` row 38).

In the first round I applied a prototype of the proposed change to copies of both scripts and ran every scenario below against the copies and against this checkout. Every NEW scenario printed its THEN on the copies and the "fails today" output on this checkout. The byte-identical-commands checksums matched on both. The scripts' existing acceptance scenarios (park reasons, which checkers run, the dispatcher marker) printed the same output on the copies as on this checkout. The prototype changed 28 lines in intake.js and 77 in build.js. That prototype was not kept. In this round I re-ran the base side on `main` at `0b1abad`, which has not moved: the five checksums printed exactly as the REGRESSION scenario states, and the two count scenarios printed `roles=0 clerk=0 untitled=18` and `changes=0 bare=6`, as verification.md states.

## Root cause

The two scripts were written to route tickets, and their display text was never designed for a reader. The clerk helper (`clerk()` in both scripts) receives only an action name, so its label cannot name a ticket. In build.js the helper is called for both the parent and its sub-tickets, so it cannot even tell which ticket an action is for. The scripts keep only the `state` field from the parent's `ticket show --json` reply. intake.js:128 and build.js:200 keep the state and drop the title, and `buildOne` (build.js:126-128) does the same for each sub-ticket. `transition()` (intake.js:117, build.js:116) returns the store's reply without printing anything, so no state change is narrated unless the caller happens to log.

## Out of scope

- The GitHub issue number on the start line is cut. No request carries one in a header, and a `#NN` in a title is not reliable. A request header surfaced through `ticket show --json` would be a store CLI change and can be filed on its own.
- The workflow card's name and description. They come from the fixed `meta` literal (intake.js:1-8, build.js:1-9), which the Workflow tool reads before the script runs.
- Every store command the scripts send, its order, and the routing on each STATUS, join decision and refusal. The REGRESSION scenario fixes them byte for byte.
- The store CLI (`factory/cli.py`), the prompts, the agent definitions and the test suite.
- `README.md`, `docs/design.md` and `docs/changelog.md`. The design doc does not describe labels or narrator lines. The README describes a behaviour only after it has run on a real ticket ("Maintaining this page"), and it does not quote label text today.

## Open questions

none

## Decisions

- The GitHub issue part is cut. Its sources are missing or wrong: no request has an `issue:` header, and one of the two `#NN` titles names another issue. Rejected: parsing `#NN` from the title, which would show #36 for a ticket whose issue is #38. Also rejected: adding the request header to `ticket show --json`, a store CLI change the operator's ask ("a 1-liner snippet besides just identifiers") does not need.
- The short title is the ticket title with whitespace runs collapsed to one space. A title of 60 characters or fewer is shown whole. A longer one is cut at the last space within its first 61 characters (index 60 or earlier), so at most 60 characters are kept. Trailing spaces and `,` `;` `:` `·` `—` `-` are then dropped, and `…` is added. A title with no such space is cut at 60 characters. Rejected: a fixed cut mid-word, which leaves fragments such as "ticke…".
- A ticket's tag is `<id> · <short title>`, joined by a middle dot (U+00B7). It is the bare id when the title is not known yet or is empty.
- Every clerk row reads `clerk <tag>: <action>`. That includes the two calls made before the title is known (`config` and the parent's `ticket show`) and each sub-ticket's first `ticket show`; their tag is the bare id. Rejected: the triage note's assumption that those calls keep their current labels. A uniform form still tells the operator which ticket the run is for.
- A state-change line is printed by the transition helper, the script function that asks the store to move a ticket to a new state, and only when the store accepted the move. A refused move is followed by the line the script already prints when it parks the ticket, that is, stops it for a human.
- The existing narrator lines keep their wording. Each now begins with the tag of the ticket it is about, followed by `: `. build.js's ` (<sub-ticket>)` after a run id is dropped, because the tag now names it.
- Acceptance runs the scripts under node with the stand-in clerk, as the scripts' existing acceptance scenarios do. The request asked for a stub-mode run instead: a run inside the Workflow tool in which each role agent copies a prepared fixture file as its output instead of calling a model. That needs the Claude Code runtime and cannot be a shell command, so it is Operator step 1.

## Risk

Blast radius: display text only. Labels and narrator lines never reach a shell or the store. A title containing quotes or backticks therefore cannot change a command. A REGRESSION scenario checks that every store command is byte-identical on five paths, including a park.

Protected path touched: `factory/workflows/intake.js` and `factory/workflows/build.js`, under the harness path `factory/**`. The request names both files as the change. No other protected path is touched.

The change reaches running tickets only when the operator moves the runtime, the pinned checkout of the harness that runs tickets, and accepts it with `--accept-harness`. Merging into `main` does not change the running code.

The Workflow tool resumes a run by replaying the longest unchanged prefix of its agent calls. I could not confirm whether a label is part of that match. If it is, a run started on the old scripts and resumed on the new ones replays nothing and starts live from its first call. That is safe, because both scripts start from the state the store holds.

Long labels may be cut off on a phone screen. The tag puts the id first and caps the title at 61 characters, so the id and the start of the title stay visible.

## Operator steps

These run after the runtime, the pinned checkout at `~/dev/spec-factory-harness` that runs tickets, has moved to a revision containing this change and been accepted with `--accept-harness`. Below, `$RUNTIME` is that checkout's absolute path.

1. Run the intake script in stub mode on a throwaway ticket store. Stub mode means each role agent copies a prepared fixture file as its output instead of calling a model. A throwaway store keeps the run out of the live store. In a Claude Code session, create the store and one ticket:

   ```
   T=$(mktemp -d)
   FACTORY_STATE=$T/store $RUNTIME/bin/factory init
   printf '# Demo of the workflow view\n\nDo x.\n' > $T/req.md
   FACTORY_STATE=$T/store $RUNTIME/bin/factory ticket new --file $T/req.md
   ```

   Then call the Workflow tool with `scriptPath` set to `$RUNTIME/factory/workflows/intake.js` and args `{ticket: "T-0001", repo: "$RUNTIME", instance: "$RUNTIME/.factory", state: "$T/store", stubs: "$RUNTIME/tests/factory/fixtures/stubs/accept-approve", inlineRoles: true}`, with each `$` value written out as an absolute path. Confirm that the progress display shows the start line `T-0001 · Demo of the workflow view · ready-for-triage`, at least one `→` state-change line, and role and clerk rows that carry `T-0001 · Demo of the workflow view`.
2. On the next real run, open the run in the Claude Code mobile app. Confirm that narrator lines appear there. If they do not, the rows alone still carry the title, and a follow-up ticket should say so.

=== design.md
## Proposed change

Both scripts get the same small helper. The Workflow tool runs a script as one function body with no imports, so the helper is copied into each script, as `clerk()` already is.

A. Title helper (both scripts). Add, next to `stubCount`:
- `TITLES`, an object mapping a ticket id to its short title;
- `shortTitle(t)`, the rule in proposal.md Decisions: collapse whitespace, keep ≤ 60 whole, else cut at the last space at or before index 60 (`lastIndexOf(' ', 60)`; at 60 when there is none), strip trailing `[\s,;:·—-]+`, append `…` (U+2026);
- `tag(id)`, which returns `` `${id} · ${TITLES[id]}` `` (U+00B7) when `TITLES[id]` is non-empty, else `id`.

Fill `TITLES[TICKET] = shortTitle(show.title)` right after the parent's `ticket show --json` (intake.js:128, build.js:200). In build.js `buildOne`, set `TITLES[st] = shortTitle(show.title)` right after `if (!show.ok) return`.

B. Start line (both scripts). Right after A's parent fill, print `log(TITLES[TICKET] ? `${TICKET} · ${TITLES[TICKET]} · ${state}` : `${TICKET} · ${state}`)`. It must come before any phase starts, so that it is the first narrator line.

C. Labels.
- Role rows: `` `${role} ${tag(TICKET)}` `` and `` `${role} (stub) ${tag(TICKET)}` `` in intake.js. Use `tag(ticket)` in build.js.
- Clerk rows: the label becomes `` `clerk ${tag(ticket)}: ${label}` ``. In intake.js the ticket is always `TICKET`. In build.js, give `clerk()` a fourth parameter `ticket = TICKET`. Pass the sub-ticket (`ticket` in `runRole`, `park` and `transition`; `st` in `buildOne`) on every call that acts on one, including the stub-script call at build.js:102. Calls on the parent (`config`, `ticket show`, `ready-implementers`, `spec tasks`, `plan add`, `subticket add`, `parent-check`, `archive`) keep the default.
- Action text: drop the ticket id now carried by the tag: `park ${ticket}` → `park`, `run start ${role} ${ticket}` → `run start ${role}`, `ticket show ${st}` → `ticket show`, `ticket head ${st}` → `ticket head`, `results show ${st}` → `results show`, `join ${st}…` → `join…`, `merge ${st}` → `merge`. build.js's transition label `${ticket} -> ${to}` → `transition -> ${to}`, as intake.js has it. Every other action text stays as it is.

D. Narrator lines.
- `transition()` (both scripts) awaits the clerk reply. When `res.ok`, it prints `` `${tag(ticket)}: → ${to}` `` (U+2192; `TICKET` in intake.js), then returns the reply unchanged. Callers are not edited. Awaiting inside `transition()` changes no command order: every caller already awaits its result before the next clerk call.
- Each existing `log()` call that names a ticket starts with `` `${tag(<that ticket>)}: ` `` and keeps the rest of its text:
  - park: `<tag>: parked: <reason>`;
  - a tripwire park: `<tag>: parked: <fin.parked>`;
  - a role's result: `<tag>: <role> <runId>: <status>` plus intake's escalation count, with build.js's ` (<ticket>)` dropped;
  - join: `<tag>: join: <decision> (<reason>)`;
  - merge: `<tag>: merged: <main_after>`;
  - spec approved, sub-tickets created, sub-tickets parked or waiting, resuming, and reuse lines: tagged with the parent.

E. Nothing else. Add no new clerk call, branch or reordering of calls, so the command order stays the same; the REGRESSION scenario checks it. Make no change to the CLI, prompts, agents, tests, README, design doc or changelog.

## Tests to change

none. No test under `tests/factory/` runs the workflow scripts or reads their labels. `tests/factory/test_shepherd.py:9-11` says they cannot run under pytest.

=== specs/workflow-view/spec.md
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


=== verification.md
## Acceptance

- The intake run opens with the ticket, its short title and its state → NEW; today it prints `triage run-0009-x: ACCEPT`, because the first narrator line comes after triage and carries no title.
- A ticket with no title opens with its bare id and keeps bare-id labels → NEW; today it prints `label: triage T-0001`, then `log: triage run-0009-x: REJECT`, with no start line and no `→ closed` line.
- A long title is cut at a word boundary and loses its trailing comma → NEW; today it prints `triage run-0009-x: NEEDS-HUMAN`, then `T-0001 parked: NEEDS-HUMAN from triage`.
- A short title is shown whole → NEW; today it prints only `triage run-0009-x: REJECT`.
- Every intake row after the ticket is read carries its short title → NEW; today it prints `roles=0 clerk=0 untitled=18` (re-run this round on `0b1abad`).
- Build rows carry the sub-ticket's own title, and the parent's rows the parent's → NEW; today it prints `start=0 roles=0 sub_clerk=0 parent_clerk=0 untitled=31`.
- Each intake state change gets a narrator line → NEW; today it prints `transitions=0 bare=4`.
- Build state changes and the merge are narrated under the right ticket → NEW; today it prints `changes=0 bare=6` (re-run this round on `0b1abad`).
- The clerk commands are byte-identical on five paths → REGRESSION; prints the same five lines on this checkout (re-run this round on `0b1abad`) and must after the change.
- Only the two workflow scripts change → NEW; today it prints nothing, because `main...HEAD` is empty on `main`. On the PR it fences the change to the two scripts: no CLI, test, prompt or document change.

Not restated here: the acceptance scenarios already in force for these scripts (park reasons, checker selection, the dispatcher marker) keep applying unchanged. In round 1 I ran them against a prototype of this change, and they printed the same output as on this checkout.

## Responses

- [BLOCKING] 6, unglossed terms in Evidence, Decisions and Operator steps: FIXED. Evidence now says "the acceptance scenarios already in force for the build and intake scripts", and describes the stand-in clerk as one that "returns canned store replies instead of running commands". "The GIVEN block" became "the first block of the first acceptance scenario". Decisions glosses stub mode at its first use: "a run inside the Workflow tool in which each role agent copies a prepared fixture file as its output instead of calling a model". Operator steps glosses stub mode, the throwaway store and the runtime again, since a reader may start there. The Decisions bullet on state-change lines now glosses the transition helper and "park".
- [SHOULD-FIX] 6, Operator step 1 gave no way to run it: FIXED. The step now gives the store setup commands and the full Workflow call, with `scriptPath` and args `{ticket, repo, instance, state, stubs, inlineRoles: true}`, and the exact start line and row text to look for. I ran the setup commands on this checkout with a scratch `FACTORY_STATE`: `init` exited 0, `ticket new` printed `{"ok": true, "id": "T-0001", "title": "Demo", "state": "ready-for-triage"}`, and `git status --short` was unchanged. The `stubs` and `inlineRoles` args are those documented at `factory/workflows/intake.js:9-17`.
- [SHOULD-FIX] 4, part E contradicted part D on `await`: FIXED. E now reads "Add no new clerk call, branch or reordering of calls, so the command order stays the same". D adds why the await inside `transition()` changes no order: every caller already awaits it (intake.js:136-172 and build.js:143-269, all eleven call sites).
- [NIT] 1, "character 60" read as 1-based: FIXED. Decisions and the requirement sentence now say "the last space within its first 61 characters (index 60 or earlier), so at most 60 characters are kept". design.md A keeps `lastIndexOf(' ', 60)`, which is the same rule.

STATUS: READY-FOR-CRITIC
CONFIDENCE: high, the base-side outputs re-ran unchanged on `0b1abad` and the Operator step 1 setup ran clean; the round 1 prototype was not kept, so the PR-side THENs rest on round 1's run and the critic's reproduction of the short-title rule
ESCALATIONS: none
