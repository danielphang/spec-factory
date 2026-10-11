## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds the
design and the harness that runs it:
- `docs/design.md`, the design document and the source of truth, with its changelog in
  `docs/changelog.md`;
- `docs/prompts/`, each file a verbatim copy of one prompt block in the design doc; it changes only
  by re-copying that block;
- `dev/`, the working documents for building the factory itself: `dev/build-harness.spec.md` (the
  spec for building the harness), `dev/build-harness.plan.md` (the Planner's decomposition of it),
  `dev/P0-intake-skeleton.md` (the walking skeleton) and `dev/issues.md` (this repo's issue index);
- the harness, as code in this repo: `factory/` (the package, its role prompts and its workflow
  scripts), `bin/factory` (the entry point), `agents/` (the agent definition templates) and
  `tests/factory/` (its suite). Install with `uv sync --frozen`; test with
  `uv run --frozen pytest -q -p no:cacheprovider tests/factory`;
- `.factory/`, this repo's own instance of the factory: `instance.yaml`, this briefing,
  `harness.lock`, closed records (`answers/`, `green-pilot/`) and the live store, `store/`.
  The store is a checkout of its own branch, `factory-store`; the operator commits it there, so a
  store commit never moves `main`.

Two checkouts. Tickets are built and merged in the dev checkout, `~/dev/spec-factory` on `main`.
The factory runs from the runtime checkout, `~/dev/spec-factory-harness`, a detached worktree of
this repo at the harness revision `.factory/harness.lock` has accepted. A merge into `main` never
changes the running code; only the upgrade step moves the runtime, after which the instance
refuses its store until `--accept-harness`. Your shell may start in another directory: use
absolute paths, or `cd ~/dev/spec-factory && <cmd>`.

The Nanobot fork at `~/dev/nanobot-upstream` (branch `feat/lionbot-v3.5`) is instance A: a target
with only `.factory/`, run from the same runtime by its own Driver session. This repo's harness was
imported from its retired `feat/lionbot-v3` branch. Read it only to observe what a fix does there; never write there, and never copy its test names,
line numbers or commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents, the harness suite). A change to the design doc keeps its
own conventions: its changelog entry in `docs/changelog.md`, `dev/build-harness.spec.md`
consistent with the new text, and any `docs/prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. For
every role but the implementer that is the only file you may create or modify. The implementer
also changes files in its own worktree and commits there, and nowhere else. Then return the same
text as your final message.

This repo's current-state page is the top-level `README.md`. A change to a command, state, stop or
path updates it in the same ticket; read its "Maintaining this page" section before editing it.

Who reads what the roles write here: the operator at the spec gate, and a technical reader new to this project reading the README or a PR description. Gloss every term specific to the factory at first use (docs/writing.md).
## Output file
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0429-reviewer/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0429-reviewer/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Where you work
Worktree: `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0429-reviewer/wt` (branch `factory/T-0042.1`, base `98dd74c2ec5165f70bf7f08d9ed38d808ade01e4`, head `8f9c2a96193e4aef8207f6dfd750c334e78f43a5`). There is no remote: commit on the branch; the PR is the branch plus the description you return. The verifier runs the gate commands on this head; you do not run them.

## Sub-ticket T-0042.1

T-0042.1 / factory drive: let a drive on one ticket start while another ticket has a run in flight, and refuse a second drive on the same ticket
Depends on: none
Parallel-safe: yes

Parent: T-0042, approved spec v2. This sub-ticket is the whole of it; read it in full. The planner was skipped: one sub-ticket: no NEEDS-SPLIT, no seam heading, no earlier planner run.

Scope: every lettered part of the parent's Proposed change.
Acceptance: every scenario of the parent spec, with the label its verification.md gives it:
- Unmarked writes from inside the target are refused while a run is in flight, init included
- The refusal names the throwaway store and not the marker
- A harness acceptance is refused while a run is in flight
- An unmarked drive starts beside another ticket's run, is refused from a run's directory, and marks only its own store calls
- A drive of a ticket with its own run in flight is refused, marked or not, and writes nothing
- A drive of a parent whose sub-ticket has a run in flight is refused and writes nothing
- A recorded live driver blocks a second drive, and an ended or dead one does not
- The documents describe the driver's exemption and its same-ticket guard
Tests to change: the parent's list.
Protected paths: the parent's Risk list.

## Parent spec (v2, pinned). Its Evidence and Responses sections are left out; the full spec is `/Users/dphang/dev/spec-factory/.factory/store/specs/T-0042/v2.md`

=== proposal.md
## Problem

An operator who drives two tickets at once cannot start, or restart, the second drive while the first has an agent at work. Working around this by hand removes the only check that stops two drives of the same ticket, and a second drive of the same ticket damages it.

Some terms. The factory moves each request through its steps as a ticket. Each step is a role run: one AI agent, a headless Claude process, doing one job on one ticket, such as writing its spec. A run is "in flight" from the moment it is started until its result is recorded. `factory drive TICKET` takes one ticket through its steps by starting its role runs one after another. It is the dispatcher, the one process meant to write the ticket store (the records of every ticket, run and result) while runs are working. To stop a role's own tools, such as its test suite, from changing those records by accident, the harness has a live-store fence. While any run of any ticket is in flight, the fence refuses every write command that lacks the marker `FACTORY_DISPATCH=1`. The dispatcher puts that marker on its own commands. The fence covers only the instance's own store, the one its configuration names. A throwaway store, one named by the environment variable `FACTORY_STATE`, such as a test's, is never fenced.

`factory drive` meets that fence when it starts, before it has set its marker. So while ticket A has a run in flight, the fence refuses an unmarked `factory drive B`, and its message names A's run. The documented workaround is to type the marker in front of the command. The fence was also the only thing that stopped a second drive of the same ticket. With the marker, a second drive of a ticket whose run is in flight goes ahead. It then fails to start that ticket's next run and parks the ticket, setting it aside for a human, as reproduced under Evidence.

The operator has decided how to fix this, and the decision stands for every later runner command (option A). `factory drive` is exempt from the fence's in-flight check. It is still refused when started from inside the directories where roles work. It gets its own same-ticket guard: it refuses to start on a ticket that it, or one of its sub-tickets, has a run in flight, or that another live driver process is driving. This affects the operator, and any runner session (an AI session that operates the factory for the operator), driving more than one ticket of a target in parallel.

## Root cause

- `factory/cli.py` `main()`, lines 1976-1977, applies `fence()` to `drive` with the in-flight rule. `factory/drive.py` `drive()` sets its marker only afterwards, at line 605.
- `factory/drive.py` has no same-ticket guard. The fence's in-flight rule was the only thing that stopped two drives of one ticket, and only on an own store, and only for an unmarked start.

## Out of scope

- The fence for every command other than `drive`: its read-only list, its location rule, its refusal text and the harness lock check are unchanged.
- The Workflow scripts (`factory/workflows/intake.js`, `build.js`). Retiring them is issue #89, which follows this ticket's standing decision.
- Recording which process owns a run in flight (issue #53). A run left in flight by a SIGKILLed driver still blocks a drive of its ticket until the operator finishes it, as documented today.
- A lock that closes the window between two drives of the same ticket started in the same instant. The guard is checked once, before the status file is written. Cut: the reported case was two different tickets started together, and the window is a few store reads long.
- Checking that a live pid really is a `factory drive` process, for instance with `ps`. Cut: see Decisions.
- Any change to the driver's routing, role processes, status-file keys or stop handling.

## Open questions

none

## Decisions

- `factory drive` skips the fence's in-flight rule and keeps its location rule, which refuses a caller under the own store's `runs/` or `worktrees/`, marked or not. This is the operator's answer of 2026-10-11 (option A). It overturns T-0040's 2026-10-10 rejection of exempting `drive`. It is standing for every later runner command: the dispatcher is exempt from the in-flight rule and carries its own same-ticket guard.
- `factory drive` given `--accept-harness` is fenced in full, in-flight rule included, because an acceptance rewrites the harness lock. This keeps the standing 2026-10-04 T-0024 rule that any command given `--accept-harness` is a write.
- The same-ticket guard refuses `drive T`, with exit 2 and nothing written, in two cases. The first is when T or any of its sub-tickets has a run in flight. The second is when `drive/T.yaml` exists, has no `ended` value, and its `pid` is a live process. These are the operator's terms of 2026-10-11.
- The guard runs whether or not the caller carries the marker, and on any store, a throwaway store included. Rejected: applying it only on an own store, as the fence is. The guard protects a ticket's records from two drivers, which matters on any store.
- The guard runs inside the `drive` command, after the fence and the harness lock and before the driver sets its marker or writes its status file. A missing ticket skips the guard, so the existing "no such ticket" result is unchanged.
- A pid counts as live when signal 0 reaches it, or is refused for permission. A missing, non-integer or dead pid does not block. A dead pid not blocking is the operator's term.
- Rejected: checking that a live pid is a `factory drive` process. That would add a platform-dependent process query for a rare case, a pid reused after a SIGKILLed driver. The refusal names the pid and the status file instead, and README tells the operator to delete that file when the pid is not a driver.
- The refusals read `<T> has runs in flight on it or its sub-tickets: <run ids>; drive it again once they finish` and `<T> is already being driven by pid <n> (<status file>); stop that driver or wait for it to end`. Neither names the marker, as the standing 2026-10-04 T-0024 decision requires of the fence's refusal.
- README's driver step that told the operator to type the marker is removed. In its place README says why the driver needs no marker, and what it refuses instead. This is the operator's direction of 2026-10-11.

## Risk

Blast radius: the start of `factory drive` on every instance that runs this harness, once the instance accepts it. A defect in the exemption could let a role run started from inside a run's directory begin a drive. The location rule, kept and tested in scenario "An unmarked drive starts beside another ticket's run, is refused from a run's directory, and marks only its own store calls", covers that. A defect in the guard could block every drive of a ticket. The refusal names the run ids or the pid, and README gives the way out of each.

Protected paths: `factory/cli.py`, `factory/drive.py`

## Operator steps

none

=== design.md
## Proposed change

A. Exempt `drive` from the fence's in-flight rule (`factory/cli.py`).
   - Give `fence(inst, cfg, root)` a keyword `in_flight: bool = True`. When it is false, return after the location check (`runs/`, `worktrees/`) and before the marker and `_in_flight()` checks. Update its docstring.
   - In `main()`, call `fence(inst, cfg, root, in_flight=a.cmd != "drive" or bool(a.accept_harness))`. The other call, in `init` (`cli.py:1428`), is unchanged.

B. The same-ticket guard (`factory/drive.py`).
   - Add `_same_ticket_guard(root, tid)`, called first in `drive()`, before `os.environ["FACTORY_DISPATCH"] = "1"`.
   - It returns at once when `tickets/<tid>.yaml` does not exist.
   - It collects `in_flight` from the ticket and from `store.subtickets_of(root, tid)`, as `spec_amend` does at `cli.py:606-609`. If any run is listed, it raises `store.Refused` with the first text under Decisions.
   - It reads `drive/<tid>.yaml` when the file exists. If `ended` is absent or null and `pid` is a live process, it raises `store.Refused` with the second text.
   - Liveness: `os.kill(pid, 0)`. `ProcessLookupError` means dead and `PermissionError` means live. A pid that is not a positive integer means not live.
   - `main()` already turns `Refused` into exit 2 with `{"ok": false, "error": ...}` as the last stdout line, and nothing has been written at that point.
   - Update the module docstring and `drive()`'s docstring to say the driver is exempt from the in-flight rule and guards its ticket.

C. Suite tests in a new file, `tests/factory/test_drive_guard.py`. Use the stand-in `claude` pattern of `tests/factory/test_drive.py`, and an own-store target where the fence matters, as `tests/factory/test_live_store_guard.py` builds one. Cases:
   - an unmarked drive of T2 starts and finishes while T1 has a run in flight on the own store;
   - a drive of T1 is refused with exit 2, marked or not, while T1 has a run in flight, and the store is unchanged;
   - a drive of a parent is refused while one of its sub-tickets has a run in flight;
   - a drive is refused while `drive/T.yaml` names a live pid with no `ended`;
   - a drive is not refused for a dead pid, or for a live pid whose `ended` is set;
   - a drive started from under the store's `runs/` or `worktrees/` is refused, marked or not;
   - a drive given `--accept-harness` is refused while a run is in flight.

D. Documents.
   - `README.md` "Driving a ticket from a shell with `factory drive`": delete step 2 and renumber the rest. Add a paragraph that says:
     - the driver needs no `FACTORY_DISPATCH=1`, even while other tickets' runs are in flight;
     - why: it is the dispatcher, so the live-store fence exempts it from its in-flight check;
     - it refuses, with exit 2 and nothing written, to start on the same ticket while that ticket or one of its sub-tickets has a run in flight, or while `drive/<ticket>.yaml` shows another driver of it still running;
     - from inside the store's `runs/` or `worktrees/` it is refused like any write;
     - a driver killed without a chance to stop, by SIGKILL, leaves its runs in flight, and they are cleared as "Where a human decides" says;
     - if the refusal names a pid that is not a driver, delete that status file.
   - `README.md` "Live-store fence" bullet: say `factory drive` is exempt from the in-flight check and guards its own ticket instead.
   - `README.md` "Where a human decides", after the list of read-only commands: one sentence that `factory drive` is exempt and needs no marker. Keep the paragraph's first line as it is, because current truth's "README tells the operator how to write during a run, first thing under Where a human decides" checks it.
   - `README.md`: the `drive/<ticket>.yaml` row of the store's file table says the driver also reads the file to refuse a second driver of that ticket. Bump the date in the status header.
   - `docs/design.md:64`: replace "`factory drive` meets the fence and the lock like any write when it starts; once past them, it sets the marker" with text saying that `factory drive` is exempt from the in-flight rule, keeps the location rule and the lock, and is fenced in full when given `--accept-harness`. The text also states the same-ticket guard, saying "same ticket" in those words, and keeps the existing sentences on the marker and role processes.
   - `dev/build-harness.spec.md`, the `**`factory drive`**` paragraph (line 295): add one sentence that it is exempt from the fence's in-flight rule when it starts, keeps the location rule, and refuses to start on the same ticket as a run in flight or a live driver.
   - `docs/changelog.md`: entry 69, in the "After issue #N (date), where ...:" form of entries 66-68. It names issue #86, the exemption, the guard, the overturned T-0040 rejection, and the rejected alternatives under Decisions.
   - No file under `docs/prompts/` or `factory/prompts/` changes.

## Tests to change

none. No suite test pins the old behaviour (Evidence). The one current-truth scenario that does, build-dispatch's "The driver marks its own store calls, never its roles', and passes a configured effort", is restated below as a MODIFIED requirement.

=== specs/live-store-guard/spec.md
## MODIFIED Requirements

### Requirement: Unmarked writes to a live store are refused while a role run is in flight there
While any run is in flight on an instance's own store, every `factory` command on that store except `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail`, `paths` and `drive`, none of them given `--accept-harness`, MUST be refused with exit 2, writing nothing to the store, the instance or the repository, unless its environment has `FACTORY_DISPATCH=1`; the refusal SHALL name a throwaway `FACTORY_STATE` and SHALL NOT name the marker.

#### Scenario: Unmarked writes from inside the target are refused while a run is in flight, init included
Run every command in this change from the repository root of the checkout under test, after `uv sync --frozen`, with `node` on `PATH`. Each WHEN runs in a subshell.
- GIVEN the three fixture files written by the block below, run once at column 0 as shown (every later scenario of this change that names them reuses them)

```sh
cat > ${TMPDIR:-/tmp}/t0024-inflight.sh <<'EOF'
# Sourced from the repo root: a scratch target whose own store has one triage run in flight; the
# shell is left in a subdirectory of that target outside its store, as a role's shell may be.
# $S is the target's own store and $W the run's scratch directory inside it.
T=$(cd "$(mktemp -d)" && pwd -P); B=$PWD/bin/factory
git init -q -b main $T/tgt && git -C $T/tgt -c user.email=f@x -c user.name=f commit -q --allow-empty -m init
cd $T/tgt && $B init --repo-name demo >/dev/null 2>&1
S=$($B paths | tail -1 | sed -n 's/.*"state": "\([^"]*\)".*/\1/p')
printf '# F\n\nDo x.\n' > $T/req.md && printf '# G\n\nDo y.\n' > $T/req2.md && $B ticket new --file $T/req.md >/dev/null
R=$($B run start --role triage --ticket T-0001 | tail -1 | sed -n 's/.*"run_id": "\([^"]*\)".*/\1/p')
W=$S/runs/$R/scratch
mkdir -p sub/scratch && cd sub/scratch
snap() { find $T/tgt/.factory $T/tgt/.claude -type f -exec cksum {} + 2>/dev/null | sort | cksum; }
EOF
cat > ${TMPDIR:-/tmp}/t0024-count.mjs <<'EOF'
// node t0024-count.mjs <workflow.js>: runs one workflow script with a stub clerk that answers every
// command {"ok": true}; prints whether any clerk command was sent and how many lack the marker.
import { readFileSync } from 'node:fs'
const src = readFileSync(process.argv[2], 'utf8').replace(/^export const meta/m, 'const meta')
let n = 0, unmarked = 0
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (!m) return 'STATUS: X\nCONFIDENCE: high\nESCALATIONS: none\n'
  n++
  if (!/(^|\s)FACTORY_DISPATCH=1\s/.test(m[1].split('bin/factory')[0])) unmarked++
  const out = / config$/.test(m[1]) ? { ok: true, models: {}, max_rounds: { spec: 2, pr: 2 }, state_dir: '/tmp/s' } : { ok: true, state: 'ready-for-triage' }
  return { stdout: JSON.stringify(out), exit: 0, stderr: '' }
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
await fn({ ticket: 'T-0001', repo: '/r' }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(`${n > 0 ? 'sent' : 'none-sent'} unmarked=${unmarked}`)
EOF
cat > ${TMPDIR:-/tmp}/t0024-e2e.mjs <<'EOF'
// node t0024-e2e.mjs <instance dir>, from the checkout under test: runs factory/workflows/intake.js
// on ticket T-0001 of that instance's own store. Each clerk command runs for real (sh -c, from this
// checkout, environment unchanged); each role writes the stub output "STATUS: REJECT". Prints the
// state the workflow returns.
import { readFileSync, writeFileSync } from 'node:fs'
import { spawnSync } from 'node:child_process'
const src = readFileSync('factory/workflows/intake.js', 'utf8').replace(/^export const meta/m, 'const meta')
const agent = async (prompt) => {
  const m = prompt.match(/and nothing else:\n\n([\s\S]*?)\n\nReport/)
  if (m) {
    const cp = spawnSync('sh', ['-c', m[1]], { cwd: process.cwd(), encoding: 'utf8' })
    return { stdout: cp.stdout, exit: cp.status, stderr: cp.stderr }
  }
  const o = prompt.match(/Write your complete output to (\S+) and return/)
  const text = 'STATUS: REJECT\nCONFIDENCE: high, stub\nESCALATIONS: none\n'
  writeFileSync(o[1], text)
  return text
}
const fn = new (async () => {}).constructor('args', 'agent', 'log', 'phase', 'parallel', src)
const res = await fn({ ticket: 'T-0001', repo: process.cwd(), instance: process.argv[2], inlineRoles: true }, agent, () => {}, () => {}, async (fs) => Promise.all(fs.map(f => f())))
console.log(res.state)
EOF
```

- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && rm -rf $T/tgt/.claude $S/openspec $S/decisions.md && S0=$(snap); $B init --repo-name x >/dev/null 2>&1; i=$?; $B ticket new --file $T/req2.md >/dev/null 2>&1; n=$?; $B ticket transition T-0001 --to closed --by t >/dev/null 2>&1; t=$?; $B decision add T-0001 x >/dev/null 2>&1; d=$?; echo "init=$i new=$n transition=$t decision=$d store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) agents=$([ -e $T/tgt/.claude ] && echo written || echo none)")`
- THEN it prints exactly `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`

#### Scenario: The refusal names the throwaway store and not the marker
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && E=$($B decision add T-0001 x 2>&1 >/dev/null); J=$($B decision add T-0001 x 2>/dev/null | tail -1); cd $W && E2=$(FACTORY_DISPATCH=1 $B decision add T-0001 x 2>&1 >/dev/null); echo "rule=$(echo "$E" | grep -c 'role runs may not write the live store') state=$(echo "$E" | grep -c FACTORY_STATE) marker=$(echo "$E$J$E2" | grep -c FACTORY_DISPATCH) json=$(echo "$J" | grep -c '"ok": false') inside=$(echo "$E2" | grep -c 'role runs may not write the live store')")`
- THEN it prints exactly `rule=1 state=1 marker=0 json=1 inside=1`

#### Scenario: A harness acceptance is refused while a run is in flight
Needs the GIVEN block of "Unmarked writes from inside the target are refused while a run is in flight, init included" run once.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && A=$(cat $T/tgt/.factory/harness.lock) && S0=$(snap); $B --accept-harness $A ticket show T-0001 >/dev/null 2>&1; echo "accept=$? store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `accept=2 store=unchanged`
=== specs/build-dispatch/spec.md
## MODIFIED Requirements

### Requirement: The driver marks its own store calls, never its role processes, and passes a configured effort
`factory drive` MUST start unmarked while a run of another ticket is in flight on the target's own store. It MUST be refused from inside that store's `runs/` or `worktrees/`, marked or not, and refused while a run is in flight when given `--accept-harness`. Once started, its store calls SHALL carry the dispatcher marker, its role processes SHALL NOT, and a role with a level under `effort:` in `instance.yaml` SHALL get `--effort <level>`.

#### Scenario: An unmarked drive starts beside another ticket's run, is refused from a run's directory, and marks only its own store calls
Needs the GIVEN blocks of "Unmarked writes from inside the target are refused while a run is in flight, init included" (live-store-guard) and "The driver takes the intake fixtures through the same routes as the intake script" run once. T-0001's triage run stays in flight throughout; T-0002 is driven.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && FACTORY_DISPATCH=1 $B ticket new --file $T/req2.md >/dev/null && printf 'effort:\n  triage: low\n' >> $T/tgt/.factory/instance.yaml && export T40_LOG=$T/claude.log T40_PLAYS='{"triage": [{"write": "REJECT"}]}' PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH && : > $T40_LOG && cd $W && $B drive T-0002 --phase intake >/dev/null 2>&1; iu=$?; FACTORY_DISPATCH=1 $B drive T-0002 --phase intake >/dev/null 2>&1; im=$?; cd $T/tgt && $B --accept-harness $(cat $T/tgt/.factory/harness.lock) drive T-0002 --phase intake >/dev/null 2>&1; ac=$?; $B drive T-0002 --phase intake >/dev/null 2>&1; u=$?; echo "inside_unmarked=$iu inside_marked=$im accept=$ac unmarked=$u $($B ticket show T-0002 | sed -n 's/^status: //p') calls=$(grep -c . $T40_LOG) effort=$(grep -c '"--effort","low"' $T40_LOG) dispatch=$(grep -c '"dispatch":null' $T40_LOG)")`
- THEN it prints exactly `inside_unmarked=2 inside_marked=2 accept=2 unmarked=0 closed calls=1 effort=1 dispatch=1`

## ADDED Requirements

### Requirement: A drive refuses to start on a ticket that is already being worked
`factory drive T` MUST be refused with exit 2, writing nothing to the store and starting no role process, while T or any of its sub-tickets has a run in flight, or while the store's `drive/T.yaml` has no `ended` value and names in `pid` a live process, whether or not the caller has `FACTORY_DISPATCH=1` and on any store. The refusal SHALL name the runs in flight or the pid, and SHALL NOT name the marker. A status file whose `pid` is dead, or whose `ended` is set, SHALL NOT block a drive.

#### Scenario: A drive of a ticket with its own run in flight is refused, marked or not, and writes nothing
Needs the GIVEN blocks of "Unmarked writes from inside the target are refused while a run is in flight, init included" (live-store-guard) and "The driver takes the intake fixtures through the same routes as the intake script" run once. T-0001's triage run is in flight on the target's own store.
- WHEN `(. ${TMPDIR:-/tmp}/t0024-inflight.sh && S0=$(snap); cd $T/tgt && export T40_LOG=$T/claude.log T40_PLAYS='{"triage": [{"write": "ACCEPT"}]}' PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH && : > $T40_LOG; $B drive T-0001 >$T/o 2>$T/e; u=$?; FACTORY_DISPATCH=1 $B drive T-0001 >$T/o2 2>$T/e2; m=$?; echo "unmarked=$u marked=$m named=$(grep -l run-0001-triage $T/e $T/e2 | grep -c .) marker=$(cat $T/e $T/e2 $T/o $T/o2 | grep -c FACTORY_DISPATCH) json=$(tail -1 $T/o2 | grep -c '"ok": false') calls=$(grep -c . $T40_LOG) store=$([ "$(snap)" = "$S0" ] && echo unchanged || echo changed) $($B ticket show T-0001 | sed -n 's/^status: //p')")`
- THEN it prints exactly `unmarked=2 marked=2 named=2 marker=0 json=1 calls=0 store=unchanged ready-for-triage`

#### Scenario: A drive of a parent whose sub-ticket has a run in flight is refused and writes nothing
Needs the GIVEN blocks of "A test file a merged sibling added may be listed, and a mention outside Tests to change is ignored" and "The driver takes the intake fixtures through the same routes as the intake script" run once. T-0001.2's implementer run is in flight on a throwaway store; its parent T-0001 has none.
- WHEN `(E=tests/test_interim.py; . ${TMPDIR:-/tmp}/t0022-sib.sh && bin/factory run start --role implementer --ticket T-0001.2 >/dev/null 2>&1 && export T40_LOG=$T22/claude.log PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH && : > $T40_LOG && S0=$(find $FACTORY_STATE -type f -exec cksum {} + | sort | cksum); bin/factory drive T-0001 --phase build >/dev/null 2>$T22/e; x=$?; echo "exit=$x named=$(grep -c 'run-0001-implementer' $T22/e) calls=$(grep -c . $T40_LOG) store=$([ "$(find $FACTORY_STATE -type f -exec cksum {} + | sort | cksum)" = "$S0" ] && echo unchanged || echo changed)")`
- THEN it prints exactly `exit=2 named=1 calls=0 store=unchanged`

#### Scenario: A recorded live driver blocks a second drive, and an ended or dead one does not
Needs the GIVEN block of "The driver takes the intake fixtures through the same routes as the intake script" run once. On a throwaway store, T-0001's status file names a live process with no `ended`, T-0002's names the same live process with `ended` set, and T-0003's names a process that has exited.
- WHEN `(T=$(cd "$(mktemp -d)" && pwd -P); export FACTORY_STATE=$T/store T40_LOG=$T/claude.log T40_PLAYS='{"triage": [{"write": "REJECT"}]}' PATH=${TMPDIR:-/tmp}/t0040-bin:$PATH; : > $T40_LOG; for i in 1 2 3; do printf '# Fixture %s\n\nThe bot should do thing %s.\n' $i $i > $T/req$i.md && bin/factory ticket new --file $T/req$i.md >/dev/null; done; sleep 60 >/dev/null 2>&1 & L=$!; sh -c 'exit 0' & G=$!; wait $G; mkdir -p $FACTORY_STATE/drive; printf 'ticket: T-0001\npid: %s\nended: null\n' $L > $FACTORY_STATE/drive/T-0001.yaml; printf 'ticket: T-0002\npid: %s\nended: {ok: true}\n' $L > $FACTORY_STATE/drive/T-0002.yaml; printf 'ticket: T-0003\npid: %s\nended: null\n' $G > $FACTORY_STATE/drive/T-0003.yaml; S0=$(cksum < $FACTORY_STATE/drive/T-0001.yaml); bin/factory drive T-0001 >/dev/null 2>$T/e; a=$?; bin/factory drive T-0002 >/dev/null 2>&1; b=$?; bin/factory drive T-0003 >/dev/null 2>&1; c=$?; kill $L; echo "live=$a pid=$(grep -cE "pid $L([^0-9]|$)" $T/e) file=$([ "$(cksum < $FACTORY_STATE/drive/T-0001.yaml)" = "$S0" ] && echo unchanged || echo changed) $(bin/factory ticket show T-0001 | sed -n 's/^status: //p') ended=$b $(bin/factory ticket show T-0002 | sed -n 's/^status: //p') dead=$c $(bin/factory ticket show T-0003 | sed -n 's/^status: //p') calls=$(grep -c . $T40_LOG)")`
- THEN it prints exactly `live=2 pid=1 file=unchanged ready-for-triage ended=0 closed dead=0 closed calls=2`

=== specs/harness-docs/spec.md
## ADDED Requirements

### Requirement: The documents record the driver's exemption and its same-ticket guard
`docs/changelog.md` SHALL gain one entry naming issue #86 as its last numbered entry, numbered without a gap. README's `factory drive` how-to SHALL no longer tell the operator to put the marker in front of the command, and SHALL say that the driver is exempt and what it refuses on the same ticket. README's "Live-store fence" bullet and the opening of "Where a human decides" SHALL say the driver is exempt. `docs/design.md`'s fence paragraph and `dev/build-harness.spec.md`'s driver paragraph SHALL state the exemption and the same-ticket guard, and the design doc SHALL no longer say the driver meets the fence like any write. The change MUST add no whitespace errors.

#### Scenario: The documents describe the driver's exemption and its same-ticket guard
- WHEN `(y() { [ "$1" -gt 0 ] && echo yes || echo no; }; c() { tr '\n' ' ' | tr -s ' ' | grep -ci -- "$1"; }; r=README.md; D=$(sed -n '/^### Driving a ticket from a shell with `factory drive`/,/^Each role process/p' $r); F=$(sed -n '/^- \*\*Live-store fence\.\*\*/,/^- \*\*Sibling tests check/p' $r); H=$(sed -n '/^## Where a human decides/,/^```/p' $r); G=$(grep '^\*\*Only the dispatcher writes a live store during a run\.\*\*' docs/design.md); P=$(grep '^\*\*`factory drive`\*\*' dev/build-harness.spec.md); echo "changelog=$(awk '/^[0-9]+\. /{n++; if (index($0, n ". ") != 1) bad=1} END{print (bad ? "GAPPED" : "CONTIGUOUS")}' docs/changelog.md) last=$(y $(grep '^[0-9]*\. ' docs/changelog.md | tail -1 | grep -c '#86')) step=$(echo "$D" | c 'put `FACTORY_DISPATCH=1` in front of the command') drive=$(y $(echo "$D" | c exempt)),$(y $(echo "$D" | c 'same ticket')) fence=$(y $(echo "$F" | c exempt)) human=$(y $(echo "$H" | c exempt)) design=$(y $(echo "$G" | c exempt)),$(y $(echo "$G" | c 'same ticket')),$(echo "$G" | c 'like any write when it starts') buildspec=$(y $(echo "$P" | c exempt)),$(y $(echo "$P" | c 'same ticket')) whitespace=$(git diff --check main...HEAD >/dev/null && echo clean || echo dirty)")`
- THEN it prints exactly `changelog=CONTIGUOUS last=yes step=0 drive=yes,yes fence=yes human=yes design=yes,yes,0 buildspec=yes,yes whitespace=clean`

=== verification.md
## Acceptance

Run every command from the repository root of the checkout under test, after `uv sync --frozen`, with `git` and `node` on `PATH`. Each WHEN runs in a subshell, through the briefing's wrapper.

- Unmarked writes from inside the target are refused while a run is in flight, init included → REGRESSION
- The refusal names the throwaway store and not the marker → REGRESSION
- A harness acceptance is refused while a run is in flight → REGRESSION
- An unmarked drive starts beside another ticket's run, is refused from a run's directory, and marks only its own store calls → NEW. Today it prints `inside_unmarked=2 inside_marked=2 accept=2 unmarked=2 ready-for-triage calls=0 effort=0 dispatch=0`: the fence refuses the unmarked drive of T-0002 because T-0001 has a run in flight.
- A drive of a ticket with its own run in flight is refused, marked or not, and writes nothing → NEW. Today it prints `unmarked=2 marked=0 named=1 marker=0 json=0 calls=0 store=changed parked`: the marked drive goes ahead and parks T-0001.
- A drive of a parent whose sub-ticket has a run in flight is refused and writes nothing → NEW. Today it prints `exit=0 named=0 calls=0 store=changed`: the drive starts and writes its status file and records.
- A recorded live driver blocks a second drive, and an ended or dead one does not → NEW. Today it prints `live=0 pid=0 file=changed closed ended=0 closed dead=0 closed calls=3`: the drive of T-0001 ignores the live driver, overwrites its status file and closes the ticket.
- The documents describe the driver's exemption and its same-ticket guard → NEW. Today it prints `changelog=CONTIGUOUS last=no step=1 drive=no,no fence=no human=no design=no,no,1 buildspec=no,no whitespace=clean`.

## Out-of-scope observations

- `tests/factory/test_drive_build.py::test_build_step_lines_and_the_status_file_name_the_subticket_in_flight` failed once in a full serial suite run on the prototype (`seen` held fewer than four running entries), then passed in three reruns. It samples the status file every 50 ms while two checkers each sleep 2 s, so a slow moment can miss the four-entry window. It may be flaky on a loaded machine, independent of this change.
- README's driver section still says "The driver is tested, and has not yet run a real ticket", but the report shows it driving T-0035 and T-0036 on the Nanobot instance on 2026-10-10. Updating that claim is the README's own maintenance rule and is not part of this ticket's intent.

## PR description (the implementer's output)

Sub-ticket: T-0042.1, branch `factory/T-0042.1`, commit `8f9c2a9` on base `98dd74c` (worktree `/Users/dphang/dev/spec-factory/.factory/store/worktrees/T-0042.1`). Parent: T-0042, approved spec v2.

## What changed

An operator can now start `factory drive` on one ticket while another ticket has a run in flight, with no marker typed. A second drive of a ticket that is already being worked is refused. Some terms: a run is "in flight" from `run start` until its result is recorded. The live-store fence is the harness check that refuses writes to an instance's own store while any run is in flight, unless the command carries the dispatcher marker `FACTORY_DISPATCH=1`. `factory drive` is the dispatcher, the one process meant to write the store while runs work.

- **A, the exemption (`factory/cli.py`).** `fence()` gains a keyword-only `in_flight: bool = True`. When it is false, `fence()` returns after the location rule, which refuses a caller under the own store's `runs/` or `worktrees/`, and before the marker and in-flight checks. `main()` now passes `in_flight=a.cmd != "drive" or bool(a.accept_harness)`. So `drive` keeps the location rule and the harness lock, and a `drive` given `--accept-harness` is fenced in full. Callers of `fence`, from `grep -rn "fence(" factory tests bin`: `cli.py:1428`, which is `init`, unchanged, and `cli.py:1981`, which is `main()`. The fix goes in `main()` because the exemption depends on the command, and only `main()` knows the command.
- **B, the same-ticket guard (`factory/drive.py`).** `_same_ticket_guard(root, tid)` is the first call in `drive()`. It runs before the marker is set and before the status file is written. It runs whether or not the caller has the marker, and on any store, a throwaway store included. A missing ticket passes, so the existing "no such ticket" result is unchanged. The guard refuses in two cases:
  - The ticket or one of its sub-tickets has runs in flight. It collects `in_flight` the way `spec_amend` does (`cli.py:606-607`) and raises `store.Refused("<T> has runs in flight on it or its sub-tickets: <ids>; drive it again once they finish")`.
  - `drive/<T>.yaml` has `ended` absent or null, and its `pid` is live. It raises `store.Refused("<T> is already being driven by pid <n> (<path>); stop that driver or wait for it to end")`.

  `_live(pid)` sends signal 0 with `os.kill(pid, 0)`. `ProcessLookupError` counts as dead. `PermissionError` counts as live. A pid that is not a positive integer counts as not live, and so does a bool. One addition goes beyond the spec: `OverflowError`, raised for a pid past the platform's range, also counts as dead, where it would otherwise exit 1. `main()` already turns `Refused` into exit 2 with `{"ok": false, "error": ...}`. The module docstring and `drive()`'s docstring now describe the exemption and the guard.
- **C, tests.** One new file, `tests/factory/test_drive_guard.py`, with 16 cases. They reuse `test_drive.STANDIN` (the stand-in `claude`), `test_drive.Store`, `test_drive_build.BuildStore`, and the own-store `target` fixture and helpers from `test_live_store_guard`.
- **D, documents.**
  - `README.md`, in "Driving a ticket from a shell with `factory drive`": step 2, which told the operator to type the marker, is deleted, and the steps are renumbered 1-4. A new paragraph covers what the spec lists: no marker needed, why, the same-ticket refusals, the location rule, SIGKILL leaving runs in flight, and deleting a status file whose pid is not a driver.
  - `README.md`, other sections:
    - The "Live-store fence" bullet now says `drive` is exempt and guards its own ticket.
    - "Where a human decides" gains one sentence after the read-only list, and its first line is unchanged.
    - The `drive/<ticket>.yaml` row of the file table now says the next drive reads the file.
    - The status date moves to 2026-10-11.
  - `docs/design.md:64`: the "meets the fence and the lock like any write when it starts" clause is replaced with the exemption, the location rule and lock, full fencing under `--accept-harness`, and the "same ticket" guard. The sentences on the marker and the role processes are kept.
  - `dev/build-harness.spec.md:295`: one sentence added.
  - `docs/changelog.md`: entry 69 for issue #86. It names the exemption, the guard, the overturned T-0040 decision (entry 67) and the three rejected alternatives.
  - No file under `docs/prompts/` or `factory/prompts/` changed.

## Acceptance results

Every command ran from the worktree through the briefing's wrapper, with `TMPDIR` set to this run's scratch directory (`scratch/tmp`), after writing the GIVEN fixtures there. The fixtures came from current truth: live-store-guard lines 13-67, which are identical to the spec's block (`diff` empty), and build-dispatch lines 53-100 and 277-414. Raw output is in `scratch/before.txt` and `scratch/after.txt`.

NEW, before the change (base `98dd74c`). Each line matches the verification.md "Today it prints" line exactly:
- An unmarked drive starts beside another ticket's run… → `inside_unmarked=2 inside_marked=2 accept=2 unmarked=2 ready-for-triage calls=0 effort=0 dispatch=0`
- A drive of a ticket with its own run in flight is refused… → `unmarked=2 marked=0 named=1 marker=0 json=0 calls=0 store=changed parked`
- A drive of a parent whose sub-ticket has a run in flight… → `exit=0 named=0 calls=0 store=changed`
- A recorded live driver blocks a second drive… → `live=0 pid=0 file=changed closed ended=0 closed dead=0 closed calls=3`
- The documents describe the driver's exemption… → `changelog=CONTIGUOUS last=no step=1 drive=no,no fence=no human=no design=no,no,1 buildspec=no,no whitespace=clean`

NEW, after the change (`8f9c2a9`). Each line equals its THEN line exactly:
- `inside_unmarked=2 inside_marked=2 accept=2 unmarked=0 closed calls=1 effort=1 dispatch=1`: the unmarked drive of T-0002 ran to `closed` beside T-0001's run. It was refused from the run's directory, marked or not, and refused with `--accept-harness`.
- `unmarked=2 marked=2 named=2 marker=0 json=1 calls=0 store=unchanged ready-for-triage`: both drives of T-0001 were refused, naming its run. Nothing was written and no role started.
- `exit=2 named=1 calls=0 store=unchanged`: the parent drive was refused, naming the sub-ticket's implementer run.
- `live=2 pid=1 file=unchanged ready-for-triage ended=0 closed dead=0 closed calls=2`: the live recorded driver blocked the drive. The ended record and the dead record did not.
- `changelog=CONTIGUOUS last=yes step=0 drive=yes,yes fence=yes human=yes design=yes,yes,0 buildspec=yes,yes whitespace=clean`

REGRESSION, after only. Each line equals its THEN line:
- Unmarked writes from inside the target are refused… → `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`
- The refusal names the throwaway store and not the marker → `rule=1 state=1 marker=0 json=1 inside=1`
- A harness acceptance is refused while a run is in flight → `accept=2 store=unchanged`

Gates, each run exactly as written from the worktree on `8f9c2a9`:
- `git diff --check main...HEAD` exited 0, so the change adds no whitespace errors.
- `uv run --frozen pytest -q -p no:cacheprovider tests/factory` printed `546 passed in 363.07s`. The timing test that the spec's Out-of-scope observations call possibly flaky passed in this run.

## Tests added/changed

- Added `tests/factory/test_drive_guard.py`, a new file with 16 cases:
  - an unmarked drive of T-0002 finishes (`closed`) beside T-0001's in-flight run on an own store, and T-0001's run stays in flight;
  - a drive given `--accept-harness` is refused by the full fence while a run is in flight;
  - a drive from under `runs/` or `worktrees/` is refused, marked or not (4 cases);
  - a drive of a ticket with its own run in flight is refused, marked or not, with an unchanged tree and no role call (2 cases);
  - a drive of a parent whose sub-ticket has an implementer run in flight is refused;
  - a live recorded driver blocks a drive (2 cases): the test process's own pid, and pid 1, which exercises the `PermissionError` branch for a non-root user;
  - a status file whose pid is dead, `ended` set, `"abc"`, `0` or `2**70` does not block (5 cases).
- With `factory/` stashed, on the base code, the file ran `6 failed, 10 passed`. The 6 failures are the exemption case and the guard's refusal cases. The 10 that already passed pin behaviour that must not change: the location rule, the `--accept-harness` fence, and the records that must not block.
- No existing test changed. The spec's Tests to change says none.

## Known gaps and uncertainties

- Markers added with the `factory:` prefix (coding standard rule 3): none.
- A status file holding valid YAML that is not a mapping would make the guard raise `AttributeError`, so the drive exits 1 rather than exit 2. The driver itself always writes a mapping. I did not add handling, because the spec does not cover it.
- Guarding against two drives of the same ticket started in the same instant is out of scope by the spec's decision. The guard is checked once.
- Checking that a live pid really is a `factory drive` process is rejected in the spec. A pid reused after a SIGKILLed driver blocks the drive until the operator deletes the status file, as README now says.
- Test design choices:
  - The "dead pid" case spawns a process inside the test and waits for it. If the OS reused that pid within milliseconds, the case would fail spuriously. This is unlikely, and I have not seen it.
  - The pid-1 case assumes pid 1 exists, which holds on macOS and Linux.
  - The `target` fixture is imported from `test_live_store_guard` with `# noqa: F401`. No other test in the repo imports a fixture across modules yet. I chose it over copying the fixture.
- README's "Ground truth only" rule says a behaviour appears above "Where this can go" only after it has run on a real ticket. The driver section already sits there, and the spec directs these edits. The new guard has run only in tests and scenarios, not on a real ticket.
- `_same_ticket_guard` builds the status-file path `root / "drive" / f"{tid}.yaml"` itself rather than reusing `Driver.status_path`. The guard has to run before a `Driver` is constructed, so this is one repeated expression.

## Out-of-scope observations

- README's driver section still says "The driver is tested, and has not yet run a real ticket". The spec notes the driver has since run T-0035 and T-0036 on the Nanobot instance. I left that sentence unchanged, as the spec says.

STATUS: READY-FOR-REVIEW
CONFIDENCE: high. Every acceptance command printed its THEN line exactly, both gates passed on the commit, and the new tests failed on the base code for the expected reasons.
ESCALATIONS: none. The protected paths `factory/cli.py` and `factory/drive.py` are declared in the spec's Risk section, and the change does only what Proposed change A and B describe.

## Diff `98dd74c2ec5165f70bf7f08d9ed38d808ade01e4...8f9c2a96193e4aef8207f6dfd750c334e78f43a5`

diff --git a/README.md b/README.md
index 5fe487d..6221404 100644
--- a/README.md
+++ b/README.md
@@ -6,7 +6,7 @@ table, and human gates. This page is the system as it runs today; install and us
 
 | | |
 |---|---|
-| **Status** | Current state as of 2026-10-10. Intake works end to end. Build works, in local-only mode. |
+| **Status** | Current state as of 2026-10-11. Intake works end to end. Build works, in local-only mode. |
 | **Reader** | Technical, seeing this project for the first time. Terms specific to this system are defined in "Terms used on this page" or at first use. |
 | **Scope** | What runs now. The intended design and its reasoning are in `docs/design.md`; where the two disagree, this page is right about what runs and the design is amended. |
 | **Internal references** | Ticket ids, issue numbers and who did what are in "Related work and history" near the end. |
@@ -465,7 +465,7 @@ The store's path is `state_dir` in `instance.yaml`. `factory init` creates a new
 | `.claude/agents/factory-*.md` | integration | `factory init`, when they are missing | the operator, if the target keeps them | durable |
 | Store records: requests, tickets, specs, plans, runs, results, approvals, current truth, changes, decisions, log | `factory-store` | the harness, through the workflows' clerk or `factory drive`, and the operator's commands | the operator, with `git -C <store> commit`; the harness commits the store once, the first commit `store migrate` makes | durable |
 | `runs/*/scratch/`, `runs/*/wt/`, `worktrees/` | none; git ignores them | `run start` | never | scratch until the ticket moves on (kept while parked); checker checkouts until `run cleanup`; implementer checkouts until the merge |
-| `drive/<ticket>.yaml` | none; git ignores it | `factory drive` | never | a live view of one driver process, rewritten at each step; kept until the next drive of that ticket |
+| `drive/<ticket>.yaml` | none; git ignores it | `factory drive` | never | a live view of one driver process, rewritten at each step; read by the next drive of that ticket, which refuses to start while it shows a live driver; kept until that next drive |
 | Sub-ticket branches, `factory/<T>.<k>` | their own | the implementer's commits | the implementer | kept after the merge |
 | Merges of sub-tickets | integration | `merge` | the harness | durable |
 
@@ -734,23 +734,30 @@ has, the Workflow tool remains the tested route.
    goes through intake. A ticket in `ready-for-planner`, `planned` or `ready-for-parent-verify` goes
    through the build. From any other state it prints "nothing to dispatch from this state" and ends.
    Like the intake script, it stops at the spec gate: after you approve the spec, run it again.
-2. If any run is in flight on the target, put `FACTORY_DISPATCH=1` in front of the command, as for
-   any store write during a run ("Where a human decides"). Without it the live-store fence refuses
-   the command with exit 2. Once started, the driver marks its own store calls. Its role processes
-   never carry the marker.
-3. `--parallel N` sets how many sub-tickets build at once; the default is 2. A commit's reviewer
+2. `--parallel N` sets how many sub-tickets build at once; the default is 2. A commit's reviewer
    and verifier always run at the same time. Use `--parallel 1` if role processes running at once
    conflict.
-4. Read the progress. It prints one line per step, such as
+3. Read the progress. It prints one line per step, such as
    `T-0032.1 "Add the flag": start implementer run-0120-implementer`. Each line names the ticket or
    sub-ticket the step concerns, with its title. The last line is the result as one JSON object:
    what the matching script returns, with `"ok": true` added. The store's `drive/<ticket>.yaml`
    shows the same while it runs: the role processes still running, the last step line, and the
    result under `ended` once it stops. Git ignores that file.
-5. To stop it, press Ctrl-C or send SIGTERM. It ends its role processes, records their runs as
+4. To stop it, press Ctrl-C or send SIGTERM. It ends its role processes, records their runs as
    `KILLED`, parks nothing, and exits with 128 plus the signal number. Run the same command again to
    resume from the stored state.
 
+The driver needs no `FACTORY_DISPATCH=1`, even while runs of other tickets are in flight on the
+target. It is the dispatcher, the one process meant to write the store while runs work, so the
+live-store fence ("Where a human decides") exempts it from its in-flight check. Once started, it
+marks its own store calls. Its role processes never carry the marker. In place of that check, it
+guards the ticket it drives. It refuses to start on the same ticket, with exit 2 and nothing
+written, while that ticket or one of its sub-tickets has a run in flight. It also refuses while
+`drive/<ticket>.yaml` shows another driver of that ticket still running. From inside the store's
+`runs/` or `worktrees/` it is refused like any write, marker or not. A driver killed by SIGKILL has
+no chance to stop, so its runs stay in flight; clear them as "Where a human decides" says. If the
+refusal names a pid that is not a driver, delete that status file and drive again.
+
 Each role process's reply is kept as `reply.json` in its run directory. Its session id, cost in
 dollars, turn count and token usage are recorded under `claude:` in the run's `meta.yaml`. To give a
 role an effort level, add an `effort:` map to `.factory/instance.yaml`, such as
@@ -825,7 +832,9 @@ runs from the same runtime. Each target's runner then accepts the new revision b
 A run is in flight from `run start` until `run finish` records its result. While any run on a
 target is in flight, the harness refuses every write to that target's store that lacks this
 marker. A write is any command except `ticket show`, `ticket join`, `results show`, `config`,
-`status parse`, `log tail` and `paths`; a command given `--accept-harness` is always a write. The
+`status parse`, `log tail` and `paths`; a command given `--accept-harness` is always a write.
+`factory drive` is exempt from this check and needs no marker, because it is the dispatcher; it
+guards its own ticket instead ("Driving a ticket from a shell with `factory drive`"). The
 workflow scripts already put the marker on their own commands. Put it in front of one command at
 a time:
 
@@ -904,9 +913,11 @@ path above is relative to the store.
   for the operator and the run goes on. Neither prints a file's contents. It is tested, and has not
   yet fired on a real ticket.
 - **Live-store fence.** While a run is in flight on a target, a write to its store without the
-  `FACTORY_DISPATCH=1` marker is refused. The workflow scripts and `factory drive` mark their own
-  commands, the driver's role processes are never marked, and the
-  operator marks one command at a time ("Where a human decides"). A write run from inside the
+  `FACTORY_DISPATCH=1` marker is refused. The workflow scripts mark their own commands, and the
+  operator marks one command at a time ("Where a human decides"). `factory drive` is exempt from
+  this in-flight check, because it is the dispatcher. It guards its own ticket instead: it refuses
+  to start on a ticket that has a run in flight or another live driver. Once started, it marks its
+  own store calls, and its role processes are never marked. A write run from inside the
   store's `runs/` or `worktrees/` is refused even with the marker. The fence stops a role's tools,
   such as its test suite, from changing the live records by accident; it is not isolation. It has
   fired on a real target: a run left in flight by a stopped workflow blocked writes until the
diff --git a/dev/build-harness.spec.md b/dev/build-harness.spec.md
index c85b85a..f226933 100644
--- a/dev/build-harness.spec.md
+++ b/dev/build-harness.spec.md
@@ -292,7 +292,7 @@ Common step `runRole(role, ticket, head)` in both scripts: clerk `factory run st
 
 Resumption after a human decision: the `/factory` skill re-runs `build.js` for the parent; the clerk's `ready-implementers` returns the sub-ticket the human moved to `ready-for-implementer` (`resolve --ruling`, `--redispatch`), and `buildOne` starts from the state the store holds (round from the store; for `--redispatch` after a checker kill, only the missing checker runs: `ready-checkers ST` lists roles without a row on the current head; a `--ruling` on BLOCKED re-runs the implementer at the same round with the ruling in its input, K).
 
-**`factory drive`** (`factory/drive.py`) does the same routing outside the Workflow tool. It ports both scripts from `// --- start`, `build.js` with its `buildOne`, branch for branch, with the same commands, transitions, round limits and park reasons, so a ticket it drives leaves the records the scripts leave. In place of the clerk it calls `factory.cli.main` in its own process, one call at a time, so every guard, the fence and the harness lock run as for `bin/factory`. Each role runs as one `claude -p` process from the run's directory; its reply is kept as `runs/<run_id>/reply.json` and recorded by `run finish --reply`. A head's two checkers run at once, ready sub-tickets build at once up to `--parallel N`, and the driver stops at the spec gate. Its permissions are in R6 and I.4.
+**`factory drive`** (`factory/drive.py`) does the same routing outside the Workflow tool. It ports both scripts from `// --- start`, `build.js` with its `buildOne`, branch for branch, with the same commands, transitions, round limits and park reasons, so a ticket it drives leaves the records the scripts leave. In place of the clerk it calls `factory.cli.main` in its own process, one call at a time, so every guard, the fence and the harness lock run as for `bin/factory`. When it starts it is exempt from the fence's in-flight rule, keeps the location rule, and refuses to start on the same ticket as a run in flight, on that ticket or a sub-ticket, or as a live driver. Each role runs as one `claude -p` process from the run's directory; its reply is kept as `runs/<run_id>/reply.json` and recorded by `run finish --reply`. A head's two checkers run at once, ready sub-tickets build at once up to `--parallel N`, and the driver stops at the spec gate. Its permissions are in R6 and I.4.
 
 ### I. Isolated run per role (piece 3) — worktree v0
 
diff --git a/docs/changelog.md b/docs/changelog.md
index 82aeb12..7cf9e63 100644
--- a/docs/changelog.md
+++ b/docs/changelog.md
@@ -70,5 +70,6 @@ Six review rounds ran on this doc, using the reviewer prompt in the appendix. Ro
 66. After issue #51 (2026-10-04), where every build role lost its first attempt to a broken Python environment: a role's shell inherited the virtual environment activated in the session that launched the factory, which on this machine belongs to another repository's checkout, and each fresh build checkout had no `.venv`, so a `uv run --no-sync` check failed on its first import until the implementer, then the reviewer, then the verifier each installed the environment themselves. The running-code wrapper, around every role command and every gate command, now first removes the exact `$VIRTUAL_ENV/bin` entry from `PATH` and unsets `VIRTUAL_ENV` and `PYTHONHOME`, then sets the fresh HOME and the `run_env` exports as before. An instance may name one shell command, `environment_sync`, in `instance.yaml`. `run start` runs it through that wrapper in the run's checkout, the implementer's worktree at every dispatch and each checker's checkout, including the parent-close verifier's, after the environment files are copied and before the role starts. On success the run's `meta.yaml` records the command and the role's input ends its "Where you work" section with a line saying the environment is already synced and should not be synced again unless the change alters the files it is built from. A failed sync refuses the run start with exit 2 and one line naming the exit code and the run's `environment-sync.log`, which holds the command and its full output; no run is recorded or put in flight, and a checker's checkout is removed while the implementer's worktree is kept. Without the key nothing runs and the input is as before. Rejected: unsetting only the two variables, which leaves the environment's `python` first on `PATH`; an opt-in way to unset variables through `run_env`, which would leave the deactivation off by default; syncing only when the implementer's worktree is first created, because the environment files and a conflict run's merge can change the lock file at a later dispatch; and quoting the command or its output in the refusal, because the build workflow expands backticks and `$` in a park reason.
 67. After issue #65 (2026-10-05), where the dispatcher, a Workflow-tool script that can run no command and read no file, sent every store read and write through a clerk agent: the requester counted 2,236 clerk agents and 4,476 calls over 97 runs, 143M of 866M workflow context tokens (17%), and the clerk was most of the wait between steps. On 2026-10-09 the clerk also returned a correct `run finish` reply pretty-printed across lines, so T-0027.2's build parked as `harness-bug: run finish reviewer:` although the reviewer's run had succeeded. `factory drive TICKET [--phase intake|build] [--parallel N] [--prompt-mode append|replace]` (`factory/drive.py`) now does the scripts' job as an ordinary Python process. It ports both scripts branch for branch, with the same routes, round limits, refusals and park reasons, and stops at the spec gate. It calls the store CLI's entry point in its own process, one call at a time, so it has no clerk and every guard, the fence and the lock run as for `bin/factory`. It marks its own store calls with `FACTORY_DISPATCH=1` once started and never its role processes. Each role runs as one `claude -p` process from its run directory, with `--output-format json`, `--permission-mode auto`, the role's prompt file, model and an optional `--effort` from a new `effort:` map in `instance.yaml`, and `--tools`/`--allowedTools` lists whose `Edit` rules cover only the run's output file, its scratch directory and the temporary directory, plus the implementer's worktree. The reply is kept as `reply.json`, and `run finish --reply` records its session id, cost, turns and usage under `claude:` in `meta.yaml`. Progress is one line per step naming the ticket or sub-ticket and its title, and a status file, `drive/<ticket>.yaml`, which the store's `.gitignore` excludes. SIGINT or SIGTERM ends the role processes, records their runs `KILLED`, parks nothing, and a second run resumes. Absorbed: #22 (per-role effort), #28 (the operator's latest chat message reaching every role agent as overriding its task), #47 (a title beside every ticket id in progress output) and #24 part A (the checkers' tool limits). The workflow scripts stay unchanged until the driver has taken a real ticket through each half; retiring them and the clerk is a later ticket. Rejected: `dontAsk`, which removes the permission classifier while roles have no operating-system isolation (#37); the build spec's "nor `dontAsk`" stays. Rejected: a `bin/factory` subprocess per store call, and calling store functions below the CLI's entry point, which would skip the fence and the lock.
 68. After issue #85 (2026-10-10), where the spec drift check parked two sub-tickets of the driver ticket T-0040 for their own siblings' merges, and the second park had no command to clear it: the test rule walked every first-parent commit on the integration branch since the spec was written, so the `--no-ff` merge of T-0040.1, which changed `factory/cli.py` and added `tests/factory/test_drive.py`, parked T-0040.2, and the merges of T-0040.1 and T-0040.2 parked T-0040.3. The Workflow script recorded T-0040.3's drift refusal as `harness-bug: run start implementer: …`, which `resolve --ruling` refused, so the operator edited the stored park reason by hand before the ruling. The test rule now skips a first-parent commit that is the recorded merge (`main_after`) of a merged sub-ticket of the same parent, from any of its plans; every other commit and merge still counts. `resolve --ruling F` now also accepts a `harness-bug: run start implementer:` park from `ready-for-implementer`, which means the harness failed to start an implementer run: F becomes the next ruling and the sub-ticket returns to its implementer at the same round, as for BLOCKED, and the ruling on file keeps the drift check from running again. Any other harness-bug park, such as a failed `run compose` or a checker's failed run start, is still refused, and the refusal text names the new case. Rejected: skipping only the current plan's siblings, since an earlier plan's merged sub-ticket is also the parent's own work; skipping merge commits in general; widening `--redispatch`, which re-runs the checkers and would meet the same drift refusal with no ruling on file; accepting every harness-bug park from `ready-for-implementer`, since a failed `run compose` leaves its run in flight.
+69. After issue #86 (2026-10-11), where an operator driving two tickets of the Nanobot target at once could not restart one drive while the other had a run in flight: `factory drive` met the live-store fence when it started, before it set its marker, so a re-run of the T-0036 drive was refused, naming an implementer run of T-0035. Typing the marker in front of the command got past the fence, but the fence's in-flight rule was also the only thing that stopped a second drive of the same ticket, and a marked second drive of a ticket with a run in flight parked that ticket. `factory drive` is now exempt from the fence's in-flight rule: it starts unmarked beside other tickets' runs. It keeps the location rule, so it is refused from inside the own store's `runs/` or `worktrees/`, marked or not. It keeps the harness lock, and given `--accept-harness` it is fenced in full, because an acceptance rewrites the lock. In place of the in-flight rule it has a same-ticket guard, checked before it sets its marker or writes its status file, whether or not the caller is marked and on any store, a throwaway store included. It refuses with exit 2, writing nothing, while the ticket or one of its sub-tickets has a run in flight, naming the runs. It also refuses while `drive/<ticket>.yaml` has no `ended` and its `pid` is live, meaning signal 0 reaches it or is refused for permission, naming the pid and the file. A dead, missing or non-integer pid does not block, and neither refusal names the marker. README's driver how-to no longer tells the operator to type the marker. This overturns T-0040's decision of 2026-10-10 (entry 67) that the driver is a write like any other, and its rejection of exempting it; the operator made the exemption standing for every later runner command. Rejected: applying the guard only on an own store, as the fence is, since two drivers damage a ticket's records on any store; checking with a process query that a live pid is a `factory drive` process, a platform-dependent query for the rare pid reused after a SIGKILLed driver, so the refusal names the pid and README says to delete the status file when it is not a driver; and a lock against two drives of the same ticket started in the same instant, since the reported case was two different tickets and the window is a few store reads long.
 
 Declined: a dedicated merge agent (merging is gate config plus human gates, not a judgment call).
diff --git a/docs/design.md b/docs/design.md
index 7b0cbd0..c8ceede 100644
--- a/docs/design.md
+++ b/docs/design.md
@@ -61,7 +61,7 @@ The prompts say what each role does. The harness enforces the wiring rules: fres
 
 **Spec drift.** Between the writing of a spec and the build of one of its sub-tickets, other tickets merge, and a sibling that the sub-ticket's checks rely on may not have merged yet. The harness checks for this before the implementer spends a run on it. Every spec version the store keeps, from `spec add`, a gate edit or `spec amend`, records the integration branch's head when it was stored, as `integration_head` in `specs/<ticket id>/v<n>.yaml`; the value is null when the target repo or branch does not resolve. Before a sub-ticket's implementer run, `run start` checks for drift, ahead of the sibling-tests check. It checks only while the sub-ticket has no finished implementer run and no ruling on file. Two rules find drift. The sibling rule: the sub-ticket's Acceptance field names, by id or by plan label as a whole token, a sibling of the current plan that has not merged and that the sub-ticket does not depend on, directly or through other siblings. Nothing makes such a sibling merge first. The test rule counts from the head recorded with the parent's approved version. It is skipped when that version has no record, because it was stored before the record existed, or when the head is null or not a commit in the target repo. For each first-parent commit on the integration branch since that head that changed a file the version's design part names, each test file the commit changed is a finding, unless the design's `## Tests to change` or the sub-ticket's "Tests to change" lists it. A first-parent commit that is the recorded merge (`main_after`) of a merged sub-ticket of the same parent, from any of its plans, is not counted, because the plan expects its siblings' changes. Every other commit and merge still counts. Named files are the design part's backticked paths that exist at the integration branch's head, other than test files and `.md` documents, which nearly every ticket edits. A test file's name starts with `test_`, ends `_test.<ext>`, or contains `.test.`. The test rule approximates "a test pins behaviour the spec changes". Measured on two stores' history, it would have caught 9 of 10 known breaks, and it parks about half of all sub-tickets. On drift, `run start` refuses with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness: spec drift:` and names each finding. The build parks the sub-ticket with that error as the reason. The human amends the spec (`factory spec amend`, Spec store below), rules, or both; `resolve --ruling` returns the sub-ticket to its implementer, and the ruling on file stops the check from repeating.
 
-**Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. `factory drive` meets the fence and the lock like any write when it starts; once past them, it sets the marker in its own environment, so its own store calls are marked whether or not it was started marked. It removes the marker from the environment of every role process it starts, so a role's commands are never marked. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
+**Only the dispatcher writes a live store during a run.** The store CLI fences an instance's own store; a throwaway store (`FACTORY_STATE` naming another) is never fenced. The fence applies to every command except the read-only ones: `ticket show`, `ticket join`, `results show`, `config`, `status parse`, `log tail` and `paths`. A command given `--accept-harness` is always fenced, because it rewrites the lock. The location rule is checked first: a write run from inside the own store's `runs/` or `worktrees/`, where roles do their work, is refused, with or without `FACTORY_DISPATCH=1` and with or without a run in flight. Then the in-flight rule: while any run is in flight on any ticket of the store, a write is refused unless its environment carries `FACTORY_DISPATCH=1`. Both workflow scripts put that marker in front of every clerk command. `factory drive` is the dispatcher, so it is exempt from the in-flight rule: it starts unmarked while runs of other tickets are in flight. It keeps the location rule and the lock, and given `--accept-harness` it is fenced in full, in-flight rule included. In place of the in-flight rule it has a same-ticket guard: it refuses to start on the same ticket, marked or not and on any store, while that ticket or one of its sub-tickets has a run in flight, or while the ticket's status file `drive/<ticket>.yaml` has no `ended` and names a live pid. Once started, it sets the marker in its own environment, so its own store calls are marked whether or not it was started marked. It removes the marker from the environment of every role process it starts, so a role's commands are never marked. The operator, or a runner session, puts it in front of one command that must write during a run, and never exports it. A refusal exits 2, writes nothing, and tells the caller to use a throwaway `FACTORY_STATE`; it never names the marker. The fence is checked before the harness lock, so a fenced command never reaches the lock and a fenced `--accept-harness` rewrites nothing. A marked command still meets the lock and its uncommitted-edit refusal unchanged. The fence guards against accidents, such as a role's test suite running `init` from its scratch directory. It is not isolation: a role that copies the marker and writes from outside the store still gets through.
 
 **Scratch directory per run.** Every run gets its own directory for temporary files, `runs/<run id>/scratch/` in the store, so runs that happen at the same time never write into one shared place and no run leaves files in a repository checkout. `run start` creates it for every role, after every guard has passed, and makes sure the store's `.gitignore` excludes `runs/*/scratch/`: an absent or empty `.gitignore` gets the harness's commented block, and an existing one keeps its own lines and gains only the lines it lacks. The composer names the directory's absolute path in a "Scratch directory" section of the run's input, directly after "Running code", and the shared preamble's SCRATCH FILES rule tells every role to put its own temporary files there and nowhere else, taking precedence over any other instruction to use a session scratchpad. When a ticket's status changes to anything other than `parked`, the harness removes the scratch directory of each finished run of that ticket; runs still in flight, other tickets' runs and every path outside `runs/*/scratch` are left alone. A park keeps the files because a human who answers a parked ticket may need to see what the run built; they are removed once the human sends the ticket on or closes it. So a role that wants a later reader to see what a prototype showed puts that in its output, since the directory is gone by the time the ticket's next role reads it.
 
diff --git a/factory/cli.py b/factory/cli.py
index 05d09e8..4dc4000 100644
--- a/factory/cli.py
+++ b/factory/cli.py
@@ -1946,9 +1946,11 @@ def _in_flight(root: Path) -> list[str]:
             for rid in store.read_yaml(p).get("in_flight") or []]
 
 
-def fence(inst: Path, cfg: dict, root: Path) -> None:
+def fence(inst: Path, cfg: dict, root: Path, *, in_flight: bool = True) -> None:
     """Refuse a write to the instance's own store from inside its runs/ or worktrees/ (marker or
-    not), or while a run is in flight there unless FACTORY_DISPATCH=1. Accidents, not isolation."""
+    not), or while a run is in flight there unless FACTORY_DISPATCH=1. Accidents, not isolation.
+    With in_flight=False only the location rule applies: `factory drive` is the dispatcher, exempt
+    from the in-flight rule, and guards its own ticket instead (drive._same_ticket_guard)."""
     if not instance.is_own_store(inst, cfg, root):
         return
     own, cwd = instance.own_state_root(inst, cfg), instance.caller_cwd()
@@ -1956,7 +1958,7 @@ def fence(inst: Path, cfg: dict, root: Path) -> None:
         if cwd.is_relative_to(own / sub):
             raise Refused(f"role runs may not write the live store ({own}; called from inside its {sub}/); "
                           "use a throwaway FACTORY_STATE")
-    if os.environ.get("FACTORY_DISPATCH") == "1":
+    if not in_flight or os.environ.get("FACTORY_DISPATCH") == "1":
         return
     runs = _in_flight(root)
     if runs:
@@ -1974,7 +1976,9 @@ def main(argv: list[str] | None = None) -> int:
         cfg = instance.load_config(inst)
         root = store.state_root(cfg)
         if (a.cmd, getattr(a, "sub", None)) not in READ_ONLY or a.accept_harness:
-            fence(inst, cfg, root)  # before the lock, so a fenced --accept-harness rewrites nothing
+            # before the lock, so a fenced --accept-harness rewrites nothing; drive keeps only the
+            # location rule unless it accepts a harness
+            fence(inst, cfg, root, in_flight=a.cmd != "drive" or bool(a.accept_harness))
         instance.guard(inst, cfg, root, a.accept_harness)  # the harness lock (design C.2-C.4)
         a.fn(a, root, cfg)
         return 0
diff --git a/factory/drive.py b/factory/drive.py
index cd08f8d..74392cc 100644
--- a/factory/drive.py
+++ b/factory/drive.py
@@ -17,6 +17,12 @@ sub-ticket's steps name the sub-ticket), then the result as one JSON object. The
 `drive/<ticket>.yaml` is a live view of this process (git ignores it). SIGINT or SIGTERM ends the
 role processes, records their runs KILLED and parks nothing: running `factory drive` again
 resumes from the stored state.
+
+The driver is the dispatcher, so the live-store fence exempts it from its in-flight rule: it starts
+with no FACTORY_DISPATCH=1 while other tickets' runs are in flight, and is still refused from inside
+the store's runs/ or worktrees/, or while a run is in flight when given --accept-harness. In place
+of that rule it guards its own ticket: it refuses to start on a ticket that it or one of its
+sub-tickets has a run in flight, or that the status file shows another live driver of (T-0042).
 """
 from __future__ import annotations
 
@@ -598,10 +604,43 @@ def _spec_round(tr: dict, rnd: int) -> int:
     return spec if isinstance(spec, int) and not isinstance(spec, bool) else rnd
 
 
+def _live(pid) -> bool:
+    """A positive integer pid that signal 0 reaches, or is refused permission to reach."""
+    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
+        return False
+    try:
+        os.kill(pid, 0)
+    except (ProcessLookupError, OverflowError):  # no such process; or past the platform's pid range
+        return False
+    except PermissionError:  # alive, owned by another user
+        return True
+    return True
+
+
+def _same_ticket_guard(root: Path, tid: str) -> None:
+    """Refuse a drive of a ticket already being worked: a run in flight on it or a sub-ticket, or a
+    status file with no `ended` whose pid is live. A missing ticket passes, for drive() to report."""
+    if not store.ticket_path(root, tid).exists():
+        return
+    t = store.load_ticket(root, tid)
+    runs = [r for x in (t, *store.subtickets_of(root, tid)) for r in x.get("in_flight") or []]
+    if runs:
+        raise store.Refused(f"{tid} has runs in flight on it or its sub-tickets: {', '.join(runs)}; "
+                            "drive it again once they finish")
+    path = root / "drive" / f"{tid}.yaml"
+    st = (store.read_yaml(path) or {}) if path.exists() else {}
+    if st.get("ended") is None and _live(st.get("pid")):
+        raise store.Refused(f"{tid} is already being driven by pid {st['pid']} ({path}); "
+                            "stop that driver or wait for it to end")
+
+
 def drive(a, root: Path, cfg: dict) -> None:
-    """`factory drive`, after main() has run the instance refusal, the fence and the harness lock.
-    From here on the driver's own store calls carry the dispatcher marker; its role processes never
-    inherit it."""
+    """`factory drive`, after main() has run the instance refusal, the fence's location rule (the
+    driver is exempt from its in-flight rule unless given --accept-harness) and the harness lock.
+    It first refuses a ticket already being worked (_same_ticket_guard), marked or not, on any
+    store. From there on the driver's own store calls carry the dispatcher marker; its role
+    processes never inherit it."""
+    _same_ticket_guard(root, a.ticket)
     os.environ["FACTORY_DISPATCH"] = "1"
     d = Driver(a, root, cfg)
     conf = call("config")
diff --git a/tests/factory/test_drive_guard.py b/tests/factory/test_drive_guard.py
new file mode 100644
index 0000000..a1cad36
--- /dev/null
+++ b/tests/factory/test_drive_guard.py
@@ -0,0 +1,157 @@
+"""`factory drive` and the live-store fence (T-0042): the driver is the dispatcher, so the fence
+exempts it from its in-flight rule; it keeps the location rule, is fenced in full when given
+`--accept-harness`, and guards its own ticket instead.
+
+The same-ticket guard refuses `drive T`, exit 2 and nothing written, marked or not and on any store,
+while T or one of its sub-tickets has a run in flight, or while `drive/T.yaml` has no `ended` and
+names a live pid in `pid`.
+
+Black-box through the CLI. Own-store cases use test_live_store_guard's scratch target; throwaway
+store cases use test_drive's and test_drive_build's stores. Each puts test_drive's stand-in `claude`
+first on PATH and counts its calls.
+"""
+from __future__ import annotations
+
+import json
+import os
+import subprocess
+import sys
+from pathlib import Path
+
+import pytest
+
+from .test_drive import STANDIN, Store
+from .test_drive_build import BuildStore
+from .test_instance import cli, js, tree
+from .test_live_store_guard import (  # noqa: F401  (target is a fixture)
+    assert_refused,
+    request,
+    snapshot,
+    start_triage,
+    state,
+    target,
+)
+
+REJECT = {"triage": [{"write": "REJECT"}]}
+
+
+class StandIn:
+    """test_drive's stand-in `claude` in tmp_path/bin, and the environment that puts it on PATH."""
+
+    def __init__(self, tmp_path: Path):
+        bindir = tmp_path / "bin"
+        bindir.mkdir()
+        (bindir / "claude").write_text(STANDIN.format(python=sys.executable))
+        (bindir / "claude").chmod(0o755)
+        self.log = tmp_path / "claude.log"
+        self.env = {"PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}", "STANDIN_LOG": str(self.log)}
+
+    def drive(self, cwd: Path, *argv: str, plays: dict | None = None, **extra: str):
+        return cli(cwd, *argv, **self.env, STANDIN_PLAYS=json.dumps(plays or {}), **extra)
+
+    def calls(self) -> list[dict]:
+        return [json.loads(ln) for ln in self.log.read_text().splitlines()] if self.log.exists() else []
+
+
+def guard_refused(cp, error: str) -> None:
+    assert cp.returncode == 2, (cp.returncode, cp.stdout, cp.stderr)
+    assert cp.stderr.strip() == error
+    assert js(cp) == {"ok": False, "error": error}
+    assert "FACTORY_DISPATCH" not in cp.stdout + cp.stderr
+
+
+# ----- the exemption --------------------------------------------------------------------------
+
+def test_an_unmarked_drive_starts_and_finishes_beside_another_tickets_run(target, tmp_path):
+    rid = start_triage(target)
+    assert cli(target, "ticket", "new", "--file", request(tmp_path), FACTORY_DISPATCH="1").returncode == 0
+    c = StandIn(tmp_path)
+    cp = c.drive(target, "drive", "T-0002", "--phase", "intake", plays=REJECT)
+    assert cp.returncode == 0, cp.stderr
+    assert js(cp)["state"] == "closed"
+    assert js(cli(target, "ticket", "show", "T-0001", "--json"))["in_flight"] == [rid]
+    calls = c.calls()
+    assert len(calls) == 1 and calls[0]["dispatch"] is None
+    assert Path(calls[0]["cwd"]).name.endswith("-triage") and Path(calls[0]["cwd"]).name != rid
+
+
+def test_a_drive_given_accept_harness_is_refused_while_a_run_is_in_flight(target, tmp_path):
+    rid = start_triage(target)
+    assert cli(target, "ticket", "new", "--file", request(tmp_path), FACTORY_DISPATCH="1").returncode == 0
+    lock = (target / ".factory" / "harness.lock").read_text().strip()
+    c = StandIn(tmp_path)
+    before = snapshot(target)
+    assert_refused(c.drive(target, "--accept-harness", lock, "drive", "T-0002", plays=REJECT), f"in flight: {rid}")
+    assert snapshot(target) == before and c.calls() == []
+
+
+@pytest.mark.parametrize("marker", [{}, {"FACTORY_DISPATCH": "1"}], ids=["unmarked", "marked"])
+@pytest.mark.parametrize("where", ["runs", "worktrees"])
+def test_a_drive_from_inside_the_store_is_refused(target, tmp_path, where, marker):
+    rid = start_triage(target)
+    assert cli(target, "ticket", "new", "--file", request(tmp_path), FACTORY_DISPATCH="1").returncode == 0
+    assert cli(target, "run", "finish", rid, "--status-override", "KILLED", FACTORY_DISPATCH="1").returncode == 0
+    cwd = state(target) / "runs" / rid / "scratch" if where == "runs" else state(target) / "worktrees" / "T-0002"
+    cwd.mkdir(parents=True, exist_ok=True)
+    c = StandIn(tmp_path)
+    before = snapshot(target)
+    assert_refused(c.drive(cwd, "drive", "T-0002", plays=REJECT, **marker), f"called from inside its {where}/")
+    assert snapshot(target) == before and c.calls() == []
+
+
+# ----- the same-ticket guard ------------------------------------------------------------------
+
+@pytest.mark.parametrize("marker", [{}, {"FACTORY_DISPATCH": "1"}], ids=["unmarked", "marked"])
+def test_a_drive_of_a_ticket_with_its_own_run_in_flight_is_refused(target, tmp_path, marker):
+    rid = start_triage(target)
+    c = StandIn(tmp_path)
+    before = snapshot(target)
+    cp = c.drive(target, "drive", "T-0001", plays={"triage": [{"write": "ACCEPT"}]}, **marker)
+    guard_refused(cp, f"T-0001 has runs in flight on it or its sub-tickets: {rid}; drive it again once they finish")
+    assert snapshot(target) == before and c.calls() == []
+
+
+def test_a_drive_of_a_parent_whose_subticket_has_a_run_in_flight_is_refused(tmp_path):
+    s = BuildStore(tmp_path)
+    plan = tmp_path / "plan.md"
+    plan.write_text("ST-1 / One\nDepends on: none\nParallel-safe: yes\n")
+    s.ok("subticket", "add", "T-0001", "--file", str(plan))
+    s.ok("ticket", "transition", "T-0001", "--to", "planned", "--by", "t")
+    rid = s.ok("run", "start", "--role", "implementer", "--ticket", "T-0001.1")["run_id"]
+    before = tree(s.root)
+    cp = s.cli("drive", "T-0001", "--phase", "build", plays={"implementer": [{"write": "READY-FOR-REVIEW"}]})
+    guard_refused(cp, f"T-0001 has runs in flight on it or its sub-tickets: {rid}; drive it again once they finish")
+    assert tree(s.root) == before and s.calls() == []
+
+
+def write_status(s: Store, pid, ended=None) -> Path:
+    p = s.root / "drive" / "T-0001.yaml"
+    p.parent.mkdir(parents=True, exist_ok=True)
+    p.write_text(f"ticket: T-0001\npid: {pid}\nended: {json.dumps(ended)}\n")
+    return p
+
+
+@pytest.mark.parametrize("pid", [os.getpid(), 1], ids=["own-user", "other-user-or-root"])
+def test_a_recorded_live_driver_blocks_a_second_drive(tmp_path, pid):
+    s = Store(tmp_path)
+    p = write_status(s, pid)
+    before = tree(s.root)
+    cp, _ = s.drive(REJECT)
+    guard_refused(cp, f"T-0001 is already being driven by pid {pid} ({p}); stop that driver or wait for it to end")
+    assert tree(s.root) == before and s.calls() == []
+
+
+def dead_pid() -> int:
+    p = subprocess.Popen([sys.executable, "-c", "pass"])
+    p.wait()
+    return p.pid
+
+
+@pytest.mark.parametrize("pid,ended", [("dead", None), (os.getpid(), {"ok": True}), ("abc", None), (0, None),
+                                       (2**70, None)], ids=["dead", "ended", "not-a-pid", "zero", "out-of-range"])
+def test_an_ended_dead_or_unusable_driver_record_does_not_block(tmp_path, pid, ended):
+    s = Store(tmp_path)
+    write_status(s, dead_pid() if pid == "dead" else pid, ended)
+    cp, res = s.drive(REJECT)
+    assert cp.returncode == 0, cp.stderr
+    assert res["state"] == "closed" and len(s.calls()) == 1
