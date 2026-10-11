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
`/Users/dphang/dev/spec-factory/.factory/store/runs/run-0424-triage/output.md`

## Running code
Run every test, script or prototype through this wrapper, which gives it a fresh temporary HOME so it cannot write the operator's real home directory: `([ -z "${VIRTUAL_ENV:-}" ] || PATH=$(printf %s "$PATH" | tr : '\n' | grep -vxF "$VIRTUAL_ENV/bin" | paste -sd: -); unset VIRTUAL_ENV PYTHONHOME; export HOME="$(cd "$(mktemp -d)" && pwd -P)"; <command>)`. Put your command in place of <command>. This includes every test or check command the briefing above gives. A throwaway HOME does not stop a write to an absolute path: never run anything that could write a protected path outside the repository.

## Scratch directory
Put every file you make for your own use in this run under `/Users/dphang/dev/spec-factory/.factory/store/runs/run-0424-triage/scratch`: no other run uses it. The harness clears it when the ticket moves on, and keeps it while the ticket is parked.

## Request (raw, with any answers appended)

---
title: "factory drive: a second drive is refused while any other ticket has a run in flight"
---

Found by the Driver on Nanobot, 2026-10-10, at harness `4bfedc7` (runtime `66bd872`).

## What happened

- 20:33Z: `factory drive T-0036 --phase intake` and `factory drive T-0035 --phase build --parallel 1` started together, and both ran (run-0417 triage, run-0418 implementer).
- The T-0036 drive was stopped with SIGTERM while its spec writer was running (run-0419 recorded KILLED, as designed).
- Re-running `factory drive T-0036 --phase intake` was refused: `role runs may not write the live store (.../.factory/store; in flight: run-0418-implementer); use a throwaway FACTORY_STATE`.

So a second drive on a different ticket starts only if no run is in flight anywhere in the store. That breaks "workflows on different tickets may run in parallel".

## Cause

`main()` in `factory/cli.py` applies `fence()` to every command not in `READ_ONLY`, including `drive`. `drive()` sets `FACTORY_DISPATCH=1` only after that check passed. The drive is the dispatcher, so the in-flight part of the fence should not apply to it.

The fence also happens to be the only thing that stops two drives on the same ticket. `drive.py` has no same-ticket guard of its own.

## Fix

- `drive` skips the fence's in-flight check. It keeps the check for a caller inside `runs/` or `worktrees/`, so a role still cannot start a drive.
- Add a same-ticket guard: `drive T` refuses when T or any of its sub-tickets has a run in flight, or when `drive/T.yaml` names a live pid with no `ended`.
- Suite cases:
  - a drive on T2 starts while T1 has a run in flight;
  - a drive on T1 is refused while T1 or a T1 sub-ticket has a run in flight;
  - a drive started from inside `runs/` is refused.

Workaround until then: prefix `FACTORY_DISPATCH=1` on a drive for a ticket with no run in flight, never on the same ticket.



## Answer 1

Operator answer, 2026-10-11: option A.

- Exempt `drive` from the in-flight part of the live-store fence. A caller inside `runs/` or `worktrees/` is still refused.
- Add a same-ticket guard. `drive T` refuses, with exit 2 and nothing written, while T or any of its sub-tickets has a run in flight, or while `drive/T.yaml` names a live driver process with no `ended`. A dead pid does not block. The guard applies whether or not the caller carries `FACTORY_DISPATCH=1`.
- This overturns T-0040's rejection of exempting `drive` (decisions.md:168). Amend current-truth `live-store-guard` to name the exemption. Remove the README driver step that tells the operator to prefix the marker, and say why.
- Your assumptions are accepted as stated: sub-tickets count, the guard is independent of the marker, exit 2 with no write, and a dead pid does not block. Priority p1.

This is a standing decision. #89 (retiring the Workflow scripts) and any later runner command follow it: the dispatcher is exempt from the in-flight fence, and it carries its own same-ticket guard.

## Capability index: every capability in current truth

Name the capabilities this request touches on your `Capabilities:` line. The spec writer receives those in full and this index for the rest.

- build-dispatch, 64 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/build-dispatch/spec.md`: A park reason carries the failing command's error; The build runs only the checkers a commit still needs; The workflows' clerk commands carry the dispatcher marker; An implementer starts only when each sibling-added test it may change came from a merged sibling; The build parks a harness-blocked sub-ticket as BLOCKED, so a ruling returns it; The build asks the whole-spec step before it runs the planner; A role run that leaves no output is re-dispatched once, then parks as EMPTY-OUTPUT; A role run that writes its output runs once and routes on its STATUS; The build counts only the current plan's sub-tickets; A parent's final check and close count only the current plan's sub-tickets; The build parks a merge the gate blocked, with the gate's reason; A sub-ticket whose spec drifted parks before its first implementer run; Changes that leave a sub-ticket's spec intact do not park it; The driver takes a ticket through intake on the intake script's route; The driver takes an approved ticket through the build on the build script's route; Each role run is one headless claude process with its role's prompt, model and tool limits; A role process's reply is recorded with its run; The checkers run at once, and sub-tickets run concurrently up to a limit; The driver reports each step on one line and in a status file; A stopped driver ends its role processes and resumes from the stored state; The driver marks its own store calls, never its role processes, and passes a configured effort; The Workflow scripts keep working beside the driver
- gate-commands, 9 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/gate-commands/spec.md`: A gate command may declare its paths and is skipped for a sub-ticket that touches none of them; A skipped command is recorded on the gate result, and the merge still needs that result to pass; The implementer is given every gate command; A malformed gate entry refuses every build role's run start
- harness-docs, 62 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-docs/spec.md`: The documents record the change; The documents record the live-store guard; The documents describe the store branch; The planner labels checks per sub-ticket and may list tests an earlier sibling added; The spec writer lists the tests a decision overturns, and the critic checks for one left off; The preamble and the code reviewer accept a checked sibling entry; Role runs receive the new rules; The documents record the sibling-tests check; The documents record the declared-path rule; The documents record the small-change lane; Every role is told to wait for its own commands; The code reviewer judges the diff and leaves the suite and the gate to the verifier; The documents record the empty-output route; The spec writer and the critic carry the turn-economy rules; Spec writer and critic runs receive the turn-economy rules; Nothing else in the two prompts changes; The documents record the turn-economy change; The documents record the critic revert; The documents record the capability index; The documents describe the whole decision log for the spec writer, critic and planner; The documents record superseded plans; The prompts tell the reviewer what the gate checks and the spec writer how to declare; The documents record the protected-path rule at merge; The implementer, verifier, code reviewer, planner and triage carry the reading rules; The reading rules are the only change to the role prompts; Runs of the five roles receive the reading rules; The documents record the reading rules for the five roles; The critic's rubric asks about cross-ticket dependencies; The documents record spec amendment, spec drift and the cross-ticket check; The documents record the environment sync and the dropped virtual environment; The documents describe the driver; The documents record the sibling-merge exception and the start-failure ruling
- harness-suite, 2 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/harness-suite/spec.md`: The harness suite runs mid-edit without loosening the lock
- human-resolution, 21 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/human-resolution/spec.md`: A ruling returns a BLOCKED sub-ticket to its implementer; Existing ruling routes are unchanged; A re-plan returns a fully merged parent to its planner; A redispatch sets aside only rows that did not pass; Accepting the refused paths returns the sub-ticket to its checks, which then merge; A ruling on a merge gate's refusal sends the sub-ticket back to its implementer; A ruling on a reviewer's escalation returns the sub-ticket to its checks; A ruling returns a sub-ticket whose implementer run failed to start
- live-store-guard, 13 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/live-store-guard/spec.md`: Unmarked writes to a live store are refused while a role run is in flight there; Writes from inside a store's run directories or code checkouts are refused, marked or not; Reads, marked commands from outside the store, throwaway stores and idle stores stay open; The marker does not lift the harness lock
- merge-gate, 9 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/merge-gate/spec.md`: A store commit does not hold back a merge; A commit to the integration branch still holds back a merge; The merge gate refuses a changed protected path the pinned spec does not declare; A declared or unprotected path merges with no further approval
- role-escalations, 5 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-escalations/spec.md`: The implementer and verifier leave declared protected paths out of ESCALATIONS; Every role still escalates an undeclared protected path, and the code reviewer still lists declared ones
- role-inputs, 15 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/role-inputs/spec.md`: The spec writer and critic receive in full only the capabilities their ticket names or their spec cites, and a capability index for the rest; A ticket whose triage output names no capabilities receives today's inputs; Triage receives the capability index and is asked to name the capabilities a request touches; The spec writer, critic and planner receive the whole decision log, whatever capabilities their ticket names; The critic sees approved changes not yet archived
- run-environment, 10 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/run-environment/spec.md`: The running-code wrapper drops an inherited virtual environment; Each build checkout is synced before its role starts; A failed sync stops the run before it starts; Without environment_sync, run start and the input are unchanged
- spec-amendment, 12 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/spec-amendment/spec.md`: A human amends a pinned spec whose intent is unchanged; Later runs receive the amended spec, and the record names what changed; Archive writes the amended version into current truth; An amendment that changes intent is refused with a restart note; An amendment that cannot be applied is refused and writes nothing
- store-setup, 19 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/store-setup/spec.md`: Run records are exempt from whitespace checks; No half instance, and a missing briefing refuses; Relative environment paths resolve from the caller's directory; A new instance's store is a checkout of its own branch; init refuses when more than one remote carries the store branch; init refuses to run from inside the store checkout; init refuses a store path the integration branch has tracked; store migrate moves a tracked store onto its branch and keeps every record; store migrate refuses while the store is in use or uncommitted; A checkout of an older commit leaves a moved store untouched
- sub-ticket-planning, 16 kB, `/Users/dphang/dev/spec-factory/.factory/store/openspec/specs/sub-ticket-planning/spec.md`: A later plan's sub-tickets continue the parent's numbering; A spec that needs one sub-ticket becomes that sub-ticket without a planner run; The whole-spec step refuses where a planner run would; A plan made from a later approved version supersedes the earlier plan's unmerged sub-tickets; A new plan may not depend on a sub-ticket it supersedes; The planner is told which sub-tickets its plan will supersede

## Your previous Triage output (the question you asked is answered above)

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
