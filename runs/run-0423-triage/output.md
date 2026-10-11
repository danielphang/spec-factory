Type: bug (as reported). Under the recorded decisions it is a design change: the harness behaves as decided and documented.

Title: factory drive: let a drive on one ticket start while another ticket has a run in flight, and refuse a second drive on the same ticket

Summary:
`factory drive` runs one ticket's intake or build from a shell. Its only role is to start the role runs: the AI agents, each one headless `claude` process, that do the work. It is refused while any run on any ticket is in flight in the store. A run is in flight from its start until it is finished or killed. So the operator cannot start a second drive on a different ticket without the `FACTORY_DISPATCH=1` prefix. The requester wants that second drive to start unprefixed. They also want a guard against two drives on the same ticket. Today nothing in `factory drive` prevents that, and the prefix workaround removes the one check that did. Their proposed fix exempts `drive` from the in-flight part of the live-store fence, adds a same-ticket guard and adds three suite cases. The live-store fence is the harness check that refuses writes to the store while a run is in flight. The requester offers the fix as a suggestion, not a requirement.

Evidence:
- From the request (Driver on Nanobot, 2026-10-10, harness `4bfedc7`, runtime `66bd872`):
  - At 20:33Z, `factory drive T-0036 --phase intake` and `factory drive T-0035 --phase build --parallel 1` started together and both ran.
  - The T-0036 drive was stopped with SIGTERM while its spec writer ran. That run was recorded KILLED, as designed.
  - Re-running `factory drive T-0036 --phase intake` was refused with `role runs may not write the live store (.../.factory/store; in flight: run-0418-implementer); use a throwaway FACTORY_STATE`. run-0418 is the T-0035 implementer run, on a different ticket.
- Checked on this checkout (`main` at `ba09ba7`). The fence code has not changed since `4bfedc7`. The only later commits to `factory/cli.py` are T-0041.1's spec-drift fix.
  - `factory/cli.py:1976-1977`: `main()` calls `fence()` for every command not in `READ_ONLY` (`cli.py:1937-1938`), and `drive` is not in that set.
  - `factory/cli.py:1949-1964`: `fence()` refuses any caller under `runs/` or `worktrees/`. Without `FACTORY_DISPATCH=1`, it also refuses while `_in_flight()` lists any run of any ticket in the store.
  - `factory/drive.py:605`: `drive()` sets `FACTORY_DISPATCH=1` only after `main()` has run the fence. That confirms the requester's description of the cause.
  - `factory/drive.py:617-618`: the status file `drive/<ticket>.yaml` records `pid`, `started` and `ended: None`. It holds the facts the proposed pid guard would read.
- This is the decided behaviour, not a regression:
  - `.factory/store/decisions.md:168` (2026-10-10, T-0040, the ticket that built `factory drive`): "`factory drive` is a write command like any other, so the fence and the lock apply when it starts ... Rejected: exempting `drive` from the fence, which would change the current-truth requirement that every unmarked write is refused while a run is in flight."
  - `.factory/store/decisions.md:15,17` (2026-10-04, T-0024, a standing decision): while a run is in flight, a runner writes the store by prefixing one command with `FACTORY_DISPATCH=1`.
  - `README.md:736-740` documents this for the driver: "If any run is in flight on the target, put `FACTORY_DISPATCH=1` in front of the command."
  - Current truth `live-store-guard` (`.factory/store/openspec/specs/live-store-guard/spec.md:5-7`) requires that every unmarked non-read command is refused while any run is in flight, except the listed read commands. `drive` is not among them.
- The request quotes the rule "workflows on different tickets may run in parallel". I could not find that sentence in `docs/design.md`, `README.md`, `decisions.md` or current truth. I searched for "different ticket", "other ticket", "same ticket", "in parallel" and "concurrent". The nearest support is README.md:808, which records overlapping runs of different tickets in the two stores.
- The request says the fence is the only thing that stops two drives on the same ticket. That is partly right. `run_start` (`factory/cli.py:207-212`) refuses a second triage, spec writer, critic, planner or implementer run on a ticket that already has a run in flight. It also refuses a second reviewer or verifier of the same role. That check is per ticket, not per driver. Neither that check nor the fence stops a second drive on a ticket that has no run in flight at that moment. Once the drive is prefixed with the marker, the fence stops nothing.
- Duplicates: none. T-0042 is this ticket, from issue #86 in `dev/issues.md:90`. Issue #53 (`dev/issues.md:60`, not in intake) is related: a stopped workflow leaves its run in flight forever, and it asks to record each run's owner. Issue #89 (`dev/issues.md:93`) retires the Workflow scripts and is gated on this one.
- Reference harness: the request names no Nanobot-side commit, and it offers a workaround "until then", so I assume no as-built fix exists. I did not search `~/dev/nanobot-upstream` for one.

Capabilities: live-store-guard, build-dispatch, harness-docs

Assumptions:
- (inference) The same-ticket guard should also count runs in flight on the ticket's sub-tickets and a live driver recorded in `drive/<T>.yaml`, as the requester's fix says. The same rule should apply whether or not the second drive carries the marker. Otherwise the workaround would bypass it.
- (inference) A second drive refused on the same ticket should exit 2 and write nothing, like other harness refusals. The request does not say.
- (inference) "A live pid" means a process that still exists. A `drive/<T>.yaml` that names a dead pid with no `ended` would not block. That case occurs after SIGKILL or a crash.
- (suggestion, priority is a human call) p1, as `dev/issues.md:90` lists it. Issue #89 waits on it.

Question for human:
Today `factory drive` is refused while any ticket in the store has a run in flight. That was decided on purpose when the driver was built (T-0040, `decisions.md:168`). The documented way around it is to prefix the command with `FACTORY_DISPATCH=1`. This request asks to reverse that decision. Which do you want?

- A. Exempt `drive` from the in-flight check, as requested. Every caller inside `runs/` or `worktrees/` is still refused. Add a same-ticket guard: `drive T` refuses while T or a sub-ticket has a run in flight, or while `drive/T.yaml` names a live driver. This overturns T-0040's rejection and changes the current-truth `live-store-guard` requirement, which now lists the commands exempt from the in-flight refusal. The README driver step that tells you to prefix the marker goes away.
- B. Keep the fence on `drive` and the documented marker prefix. Add only the same-ticket guard, checked whether or not the drive is marked, so the prefix is safe to use. No decision is overturned. Every second drive still needs the prefix.
- C. Change nothing in code: close this as working as designed. Instead, document the risk of two drives on one ticket next to the prefix advice in README.

Is the answer a standing decision that later tickets must follow? Two later tickets would be bound by it: the retirement of the Workflow scripts (#89), and any later command a runner session uses to start work.

STATUS: NEEDS-HUMAN
CONFIDENCE: high. The cause is confirmed in code (`cli.py:1976`, `drive.py:605`), and the conflict with the recorded decision is quoted from `decisions.md:168`.
ESCALATIONS: none
