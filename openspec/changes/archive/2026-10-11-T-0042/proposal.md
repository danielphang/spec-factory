## Problem

An operator who drives two tickets at once cannot start, or restart, the second drive while the first has an agent at work. Working around this by hand removes the only check that stops two drives of the same ticket, and a second drive of the same ticket damages it.

Some terms. The factory moves each request through its steps as a ticket. Each step is a role run: one AI agent, a headless Claude process, doing one job on one ticket, such as writing its spec. A run is "in flight" from the moment it is started until its result is recorded. `factory drive TICKET` takes one ticket through its steps by starting its role runs one after another. It is the dispatcher, the one process meant to write the ticket store (the records of every ticket, run and result) while runs are working. To stop a role's own tools, such as its test suite, from changing those records by accident, the harness has a live-store fence. While any run of any ticket is in flight, the fence refuses every write command that lacks the marker `FACTORY_DISPATCH=1`. The dispatcher puts that marker on its own commands. The fence covers only the instance's own store, the one its configuration names. A throwaway store, one named by the environment variable `FACTORY_STATE`, such as a test's, is never fenced.

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

