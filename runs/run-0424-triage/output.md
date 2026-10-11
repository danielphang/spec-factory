Type: feature. It is reported as a bug, but the harness behaves as decided and documented. The operator's answer (option A) changes that decision.

Title: factory drive: let a drive on one ticket start while another ticket has a run in flight, and refuse a second drive on the same ticket

Summary:
`factory drive` runs one ticket's intake or build from a shell by starting its role runs. A role run is one AI agent, a headless `claude` process, working one step of the ticket. Today the live-store fence refuses the drive while any ticket in the store has a run in flight. The live-store fence is the harness check that refuses unmarked writes to the store during a run. So the operator cannot start a drive on a second ticket without prefixing `FACTORY_DISPATCH=1`, the marker that lets one command through the fence. The operator chose option A:
- `drive` is exempt from the fence's in-flight check. A caller inside the store's `runs/` or `worktrees/` is still refused.
- A new same-ticket guard makes `drive T` refuse, with exit 2 and nothing written, in two cases: T or any of its sub-tickets has a run in flight, or `drive/T.yaml` names a live driver process with no `ended`. A dead pid does not block. The guard applies whether or not the caller carries the marker.
The current-truth requirement `live-store-guard` is amended to name the exemption. The README driver step that tells the operator to prefix the marker is removed, and the README says why.

Evidence:
- From the request (found by the Driver session on Nanobot, 2026-10-10, harness `4bfedc7`, runtime `66bd872`):
  - At 20:33Z, `factory drive T-0036 --phase intake` and `factory drive T-0035 --phase build --parallel 1` started together, and both ran.
  - The T-0036 drive was stopped with SIGTERM while its spec writer ran. That run was recorded KILLED, as designed.
  - Re-running `factory drive T-0036 --phase intake` was refused with `role runs may not write the live store (.../.factory/store; in flight: run-0418-implementer); use a throwaway FACTORY_STATE`. run-0418 is the T-0035 implementer, a run on a different ticket.
- Checked on this checkout (`main` at `ba09ba7`):
  - `factory/cli.py:1976-1977`: `main()` calls `fence()` for every command not in `READ_ONLY`, and `drive` is not in that set.
  - `factory/cli.py:1949-1964`: `fence()` refuses any caller under `runs/` or `worktrees/`. Without `FACTORY_DISPATCH=1`, it also refuses while `_in_flight()` lists a run of any ticket.
  - `factory/drive.py:605`: `drive()` sets `FACTORY_DISPATCH=1` only after `main()` has run the fence. This confirms the cause the requester gives.
  - `factory/drive.py:617-618`: the driver's status file `drive/<ticket>.yaml` records `pid`, `started` and `ended: None`. Those are the facts the new guard reads.
  - `factory/cli.py:207-212`: `run_start` already refuses a second run of most roles on a ticket that has one in flight. It does not stop a second drive on a ticket with no run in flight at that moment. Once the drive carries the marker, the fence stops nothing either.
- The decision this overturns: `.factory/store/decisions.md:168` (2026-10-10, T-0040, the ticket that built `factory drive`): "`factory drive` is a write command like any other, so the fence and the lock apply when it starts ... Rejected: exempting `drive` from the fence". The operator's answer names this line as overturned.
- What changes in the documents:
  - Current truth `.factory/store/openspec/specs/live-store-guard/spec.md:5-7` lists the commands exempt from the in-flight refusal. `drive` is not among them.
  - `README.md:737-740` is driver step 2: "If any run is in flight on the target, put `FACTORY_DISPATCH=1` in front of the command". This is the step to remove.
- Operator answer, 2026-10-11: option A, priority p1, and a standing decision. Issue #89 (retiring the Workflow scripts) and any later runner command follow it: the dispatcher is exempt from the in-flight fence and carries its own same-ticket guard.
- Duplicates: none. This ticket is issue #86 (`dev/issues.md:90`). Issue #53 is related: a stopped workflow leaves its run in flight, and #53 asks to record each run's owner. Issue #89 (`dev/issues.md:93`) is gated on this one.
- Reference harness: the request names no Nanobot-side commit and offers a workaround "until then". No as-built fix is assumed, and I did not look for one in `~/dev/nanobot-upstream`.

Capabilities: live-store-guard, build-dispatch, harness-docs

Assumptions:
- Accepted by the operator (Answer 1): sub-tickets count for the guard; the guard applies with or without the marker; a refusal exits 2 and writes nothing; a dead pid does not block.
- (inference) The command that starts a drive and is still refused inside `runs/` or `worktrees/` uses the same check and refusal text the fence uses today. The request and the answer do not ask to change that refusal.
- (inference) `README.md:905-909`, the "Live-store fence" bullet, also needs a line saying `factory drive` is exempt from the in-flight check, so the README does not contradict the new requirement. The answer names only the driver step.
- (inference) The suite cases the requester proposed are the behaviour to test: a drive on T2 starts while T1 has a run in flight; a drive on T1 is refused while T1 or a T1 sub-ticket has a run in flight; a drive started from inside `runs/` is refused. The answer adds the live-driver-pid case and the dead-pid case.
- (inference) The decision log gets a new line recording that T-0040's rejection at `decisions.md:168` is overturned, as the spec writer's usual decision record.

Question for human / Missing info / Reason: none. The operator's answer settles the product question this triage asked.

STATUS: ACCEPT
CONFIDENCE: high. The cause is confirmed in code at `cli.py:1976` and `drive.py:605`, and the operator's answer settles the design question.
ESCALATIONS: none
