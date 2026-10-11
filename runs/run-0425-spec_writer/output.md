=== proposal.md
## Problem

An operator who drives two tickets at once cannot start, or restart, the second drive while the first has an agent at work. Working around this by hand removes the only check that stops two drives of the same ticket, and a second drive of the same ticket damages it.

Some terms. The factory moves each request through its steps as a ticket. Each step is a role run: one AI agent, a headless Claude process, doing one job on one ticket, such as writing its spec. A run is "in flight" from the moment it is started until its result is recorded. `factory drive TICKET` takes one ticket through its steps by starting its role runs one after another. It is the dispatcher, the one process meant to write the ticket store (the records of every ticket, run and result) while runs are working. To stop a role's own tools, such as its test suite, from changing those records by accident, the harness has a live-store fence. While any run of any ticket is in flight, the fence refuses every write command that lacks the marker `FACTORY_DISPATCH=1`. The dispatcher puts that marker on its own commands.

`factory drive` meets that fence when it starts, before it has set its marker. So while ticket A has a run in flight, the fence refuses an unmarked `factory drive B`, and its message names A's run. The documented workaround is to type the marker in front of the command. The fence was also the only thing that stopped a second drive of the same ticket. With the marker, a second drive of a ticket whose run is in flight goes ahead. It then fails to start that ticket's next run and parks the ticket, setting it aside for a human, as reproduced under Evidence.

The operator has decided how to fix this, and the decision stands for every later runner command (option A). `factory drive` is exempt from the fence's in-flight check. It is still refused when started from inside the directories where roles work. It gets its own same-ticket guard: it refuses to start on a ticket that it, or one of its sub-tickets, has a run in flight, or that another live driver process is driving. This affects the operator, and any runner session (an AI session that operates the factory for the operator), driving more than one ticket of a target in parallel.

## Evidence

Reported by the session that runs the factory on the Nanobot fork, 2026-10-10, at harness `4bfedc7`. At 20:33Z, `factory drive T-0036 --phase intake` and `factory drive T-0035 --phase build --parallel 1` started together, and both ran. The T-0036 drive was stopped with SIGTERM while its spec writer ran, and that run was recorded KILLED, as designed. Re-running the T-0036 drive was refused with `role runs may not write the live store (.../.factory/store; in flight: run-0418-implementer); use a throwaway FACTORY_STATE`. `run-0418-implementer` is a run of T-0035, a different ticket.

Reproduced on this checkout (`main` at `ba09ba7`), each command run through the briefing's wrapper with `TMPDIR` set to this run's scratch directory, after writing the fixture files from the GIVEN blocks named in the scenarios below:

- The five NEW scenarios of this change, run on base, printed:
  - `inside_unmarked=2 inside_marked=2 accept=2 unmarked=2 ready-for-triage calls=0 effort=0 dispatch=0`. An unmarked drive of T-0002 is refused (`unmarked=2`) only because T-0001 has a run in flight, so T-0002 never moves (`ready-for-triage`, `calls=0`: no role process started). The refusal's text, captured separately, is `role runs may not write the live store (<tmp>/tgt/.factory/state; in flight: run-0001-triage); use a throwaway FACTORY_STATE`, the same message as the report.
  - `unmarked=2 marked=0 named=1 marker=0 json=0 calls=0 store=changed parked`. A marked drive of T-0001, whose own triage run is in flight, is not refused (`marked=0`). It writes the store and leaves T-0001 `parked`: its run start was refused because a run was already in flight, and the driver parked the ticket for that.
  - `exit=0 named=0 calls=0 store=changed`. A drive of a parent whose sub-ticket has an implementer run in flight starts and writes the store. On a throwaway store the fence never applies, so nothing stops it.
  - `live=0 pid=0 file=changed closed ended=0 closed dead=0 closed calls=3`. A drive of T-0001 goes ahead while `drive/T-0001.yaml` names a live process with no `ended`. It overwrites that file (`file=changed`) and closes the ticket, so two drivers of one ticket are not told apart from one.
  - The documents check printed `changelog=CONTIGUOUS last=no step=1 drive=no,no fence=no human=no design=no,no,1 buildspec=no,no whitespace=clean`. README's driver section still tells the operator to type the marker (`step=1`), and no document names the exemption or the guard.
- A prototype of Proposed change A and B, in a scratch clone of `ba09ba7` (about 30 changed lines in `factory/cli.py` and `factory/drive.py`), printed the expected THEN line of each of the four NEW behaviour scenarios. It has no document changes, so the documents check was not run on it. The three restated live-store-guard scenarios printed their current-truth lines: `init=2 new=2 transition=2 decision=2 store=unchanged agents=none`, `rule=1 state=1 marker=0 json=1 inside=1` and `accept=2 store=unchanged`. So the fence is unchanged for every command but `drive`.
- The harness suite on that prototype: `1 failed, 529 passed`. The one failure is a timing test, which passed in three reruns of `tests/factory/test_drive_build.py tests/factory/test_drive.py tests/factory/test_live_store_guard.py` (`35 passed` each time; see Out-of-scope observations). No existing suite test pins the old behaviour. `grep` of `tests/factory/test_drive.py`, `test_drive_build.py` and `test_live_store_guard.py` finds no drive started while a run is in flight on an own store. The drive tests use a throwaway store, which the fence never covers.
- The code, at `ba09ba7`:
  - `factory/cli.py:1976-1977`: `main()` calls `fence()` for every command outside `READ_ONLY` (`cli.py:1939-1940`), and `drive` is outside it.
  - `factory/cli.py:1949-1964`: `fence()` refuses a caller under the own store's `runs/` or `worktrees/`. Then, unless `FACTORY_DISPATCH=1`, it refuses while `_in_flight()` (`cli.py:1943-1946`) lists a run of any ticket.
  - `factory/drive.py:601-619`: `drive()` sets `FACTORY_DISPATCH=1` (line 605) only after `main()` has run the fence. It writes `drive/<ticket>.yaml` with `pid`, `started` and `ended: None` (lines 617-619) and reads no existing status file first.
  - `factory/cli.py:207-212`: `run_start` refuses a second run of most roles on a ticket with a run in flight. The driver turns that refusal into a park, which is the second reproduction above.
- The decision this overturns is in `.factory/store/decisions.md`, 2026-10-10, T-0040, the ticket that built `factory drive`: "`factory drive` is a write command like any other, so the fence and the lock apply when it starts ... Rejected: exempting `drive` from the fence". The operator's answer of 2026-10-11 names it as overturned. The standing replacement is already logged as the 2026-10-11 T-0042 line.
- The documents that state the old rule:
  - `README.md:737-740`, driver step 2: "If any run is in flight on the target, put `FACTORY_DISPATCH=1` in front of the command".
  - `README.md:906-913`: the "Live-store fence" bullet.
  - `README.md:824-830`: the opening of "Where a human decides".
  - `docs/design.md:64`: "`factory drive` meets the fence and the lock like any write when it starts".
  - `.factory/store/openspec/specs/live-store-guard/spec.md:5-7`: the current-truth list of commands exempt from the in-flight refusal, without `drive`.

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

STATUS: READY-FOR-CRITIC
CONFIDENCE: high, because every NEW scenario was run on `ba09ba7` (fails as stated) and on a scratch prototype of A and B (prints its THEN line), and the operator's answer settles the design.
ESCALATIONS: none
