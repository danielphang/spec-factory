## Problem

Once the operator approves a spec at the spec gate, nothing in the factory can change it, even after it turns out to be wrong. The spec gate is the one human sign-off on a design before code is written. The spec's acceptance scenarios are the runnable checks the code must pass. They can become impossible to pass when another approved ticket merges first and changes behaviour they rely on. The code is then correct, and the check is wrong. The operator has two workarounds today. One is a hand edit of the files in the factory's state store, the directory where the factory keeps tickets, spec versions and agent run records. No command is behind that edit. The other is a written instruction that never reaches the repository's record of what the system does.

Some terms used below. At the gate the harness pins the spec: it freezes the approved version and writes it out as the ticket's change folder. Every later agent reads that pinned version. A store that keeps change folders and current truth has a spec store; a store set up without one skips both. A ticket is built as sub-tickets, each merged on its own. The planner is the agent that splits a ticket into sub-tickets, and it leaves its task list, `tasks.md`, in the change folder. When the last sub-ticket has merged and a final check passes, archive writes the change folder's scenarios into current truth. Current truth is the repository's description of how the system behaves now, and later specs are written against it. A run is in flight while an agent is working on a ticket. A ticket is parked when the pipeline stops it and hands it to a human; an implementer that cannot go on parks its sub-ticket with the status BLOCKED. A ruling is a human's written instruction, filed with the ticket, that the harness hands to later agent runs.

Two things go wrong:

- **No way to amend.** The only command that writes a spec version works only while the ticket waits at the gate. A ruling can tell the builders to change a scenario's setup, so the build goes on. But archive still copies the unamended scenario into current truth, where anyone who re-runs it sees it fail.
- **Nobody checks for the conflict.** These breaks are foreseeable. When the second spec reached the gate, the first ticket was already approved and its decision was on file. The critic, the agent that grades a spec before the operator sees it, was not asked to look at other approved tickets. Its input does not list them.

This ticket adds a human-only command that amends a pinned spec, and a critic check, with the input that check needs.

## Evidence

Two incidents, both read in the stores:

- **Nanobot target, 2026-10-04.** The Nanobot target is a second repository the factory works on, with its own store. Ticket T-0002 (its spec 20) merged and made WhatsApp groups fail closed when no policy store exists. Two pinned scenarios of T-0008 (its spec 05, typing indicators) create no policy store, so they cannot pass. T-0008.1's implementer reported itself blocked (run-0166). The workaround is a ruling: `~/dev/nanobot-upstream/.factory/state/approvals/T-0008.1/ruling-1.md` and `.../T-0008/ruling-1.md` both exist. Each says "Test setup only. No behaviour change, and no change to any THEN" and seeds a `policies.json`. The requester expects the same in two more tickets. When T-0002 was approved, T-0008's spec could have been checked against it. Nothing did.
- **This repository, 2026-10-03.** `.factory/state/approvals/T-0012/amendment-1.md` records that the operator "Applied in place to `specs/T-0012/v3.md` (the pinned version every checker reads)". No command made that edit.

Today's behaviour, on a scratch store (the GIVEN fixture of the first scenario below; ticket T-0001 pinned at v1, its one scenario running `echo hi`; v2 changes it to `echo hello`):

- `bin/factory spec amend T-0001 --file v2.md --reason ...` prints `factory spec: error: argument sub: invalid choice: 'amend' (choose from add, tasks)` and exits 2. No command can write a new version after the gate.
- With T-0001 split into two sub-tickets, an implementer run on T-0001.2 receives v1: its input has `echo hi` once and `echo hello` zero times. A ruling would be the only way to tell it otherwise.
- `bin/factory archive T-0001` then writes v1's scenario into current truth: `hello=0 hi=1`. That is the harm the ruling workaround leaves behind.
- A critic run on a second ticket, T-0002, gets no list of other approved tickets. Its input headings are the briefing, the spec under review and its own parts, and nothing names T-0001 (`t1=0`). Its system prompt has no rule on this (`rule=0`).

The design already allows amending. `docs/design.md:102` says "the human amends the spec and re-plans". Line 104 says "The human may amend the sub-ticket or the pinned spec first; the amended version is what the implementer and checkers receive." The build spec, `dev/build-harness.spec.md:314`, specifies a `resolve --amend-spec FILE` flag that was never built.

The operator approved both parts as one ticket, pre-approved at the gate: `.factory/answers/operator-decisions-2026-10-04.md` says "#44: approve parts A (spec amend, human-only, logged) and B (critic cross-ticket check) as one ticket, pre-approved."

The fix was prototyped in a clone of `main` at `0b1abad` in this run's scratch directory. Every scenario below printed its THEN line there. On an unmodified clone, every scenario labelled NEW printed the failure stated in verification.md. The full harness suite on the prototype: `1 failed, 264 passed`. The one failure was the test that keeps the design doc's critic block equal to `docs/prompts/03-spec-critic.md`, because the prototype had not edited the design doc yet. After that edit, the test passed (`5 passed`).

## Root cause

- `factory/cli.py:653-688` `approve_spec` is the only path that sets `spec.approved_version` and calls `specstore.pin`, and it refuses unless the ticket is `awaiting-spec-gate` (`cli.py:669-670`). `_add_spec_version` (`cli.py:350`) writes a version but pins nothing.
- `factory/compose.py:172` and `:188`/`:206` hand implementer, reviewer and verifier runs `specs/<parent>/v<approved_version>.md`, and the planner gets `v<approved_version>` too (`compose.py:157`). So moving `approved_version` is enough to reach every later run. Nothing moves it.
- `factory/specstore.py:290-303` `pin` deletes and rewrites the whole change folder (`shutil.rmtree(d)`, line 296). That would drop the planner's `tasks.md`, which `spec tasks` (`cli.py:919`) writes there.
- `factory/specstore.py:336` `archive` applies the deltas in the change folder, so only a re-pin changes what reaches current truth.
- `factory/compose.py:145-155`, the critic branch, adds the spec, current truth, the decision log and rulings, and nothing about other tickets. The critic's rubric item 5 (`docs/design.md:418`, `docs/prompts/03-spec-critic.md:18`, `factory/prompts/critic.md:18`) says only "doesn't conflict with open tickets".

## Out of scope

- How a ticket moves after an amendment. Today's routes stay as they are: `resolve --ruling` on a BLOCKED sub-ticket, `ticket transition` back to `ready-for-parent-verify`, `resolve --replan`.
- Amending a sub-ticket's own text (`specs/<id>/subticket.md`).
- Giving the spec writer the list of approved changes not yet archived. Only the critic gets it here.
- Handing the amendment record itself to role runs. They receive the amended spec.
- Re-checking merged sub-tickets against the amended scenarios. The final check on the merged result does that, as today.
- Replacing the Nanobot target's existing rulings with amendments. That is the operator's call on that target.
- The gate's `approve-spec`, `--edit` and `resolve` behaviour, and `archive`'s refusals: unchanged.
- The tests that a decision overturns within one ticket. That is the queued ticket T-0022 (issue #40, part C).

## Open questions

none

## Decisions

- The command is `factory spec amend <parent> --file <F> --reason "<one line>"`, run by a human. Rejected: the build spec's unbuilt `resolve --amend-spec`. Each `resolve` mode that sends a ticket back into the pipeline acts only on a ticket the pipeline has stopped and handed to a human: a parked one, or for `--answer` one waiting on its requester (`factory/cli.py:735-811`). Its other mode, `--close`, ends the ticket. An amendment needed after another ticket merges may come while the ticket is not stopped, for example while it is `planned` with sub-tickets still waiting.
- An amendment changes no ticket state. The operator resumes the ticket with the routes that exist: `resolve --ruling` on a BLOCKED sub-ticket, `ticket transition` to `ready-for-parent-verify`, or `resolve --replan`. Rejected: an amendment that also moves the ticket, which would duplicate those routes.
- `spec amend` refuses while any run is in flight on the parent or one of its sub-tickets. A parked or waiting sub-ticket does not block it. Rejected: refusing while any sub-ticket is unmerged, which would block the motivating case of a sub-ticket parked BLOCKED on a scenario it cannot pass. This is a standing decision.
- Human-only means that no workflow script and no role prompt names the command. A role run on the parent or a sub-ticket is in flight while it runs, so the in-flight refusal stops it. There is no identity check, because the harness runs under one identity.
- `spec amend` refuses, with exit 2 and nothing written: a sub-ticket; a ticket with no approved version; a ticket at `awaiting-spec-gate`, where `approve-spec --edit` is the route; a closed ticket; a reason that is not one non-blank line; and, when the store has a spec store, a ticket whose change folder is gone because it was archived. An amended version must pass the gate's own checks: well-formed, and its deltas apply to current truth.
- The re-pin keeps the planner's `tasks.md` in the change folder. The rest of the folder is rewritten as the gate writes it, `## Critic rounds` included.
- Each sub-ticket that is neither merged nor closed has its spec record moved to the new version, so later runs record the version they received. Merged and closed sub-tickets keep theirs.
- The record is `approvals/<parent>/amendment-<n>.md`, numbered after any amendment file already there. It holds who, when, the reason, the old and new version, a `- changed: <name>`, `- added: <name>` or `- removed: <name>` line per scenario that differs, a `- <id> / <title>: merged` line per sub-ticket merged before the amendment, and the unified diff. The log gets a `spec.amended` event. No `spec-v<n>.yaml`, the file the gate writes to record an approval, is written. The amendment record is that version's approval record.
- The critic's input gains a section, "Approved changes not yet archived". It lists each change folder whose ticket is not closed, other than the reviewed ticket's own. Each entry gives the ticket id, title, state, folder path, the requirements its deltas add, modify or remove, and its Decisions lines. The section reads `none` when there are none, and is left out when the store has no spec store. Rejected: a prompt rule with no input, because the critic cannot find another target's store. Rejected: whole proposals, which would multiply the critic's input.
- The cross-ticket rule extends the critic's rubric item 5 (Consistent). A scenario whose setup would not hold under one of the two merge orders is a BLOCKING finding that names the other ticket and its decision. This is a standing decision.

## Risk

Blast radius: one new command, which touches only the ticket it names and its sub-tickets' spec records. Every critic run on a store that has a spec store gets one more input section: one entry per approved ticket not yet archived (two today, T-0025 and T-0026). The critic prompt gains four lines in rubric item 5. No routing, state, gate or archive behaviour changes.

Protected paths this change touches:
- harness (`factory/**`): `factory/cli.py`, `factory/specstore.py`, `factory/compose.py`, `factory/prompts/critic.md`;
- generated (`docs/prompts/**`): `docs/prompts/03-spec-critic.md`, re-copied from the design doc's critic block.

It also edits `docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md` and `README.md`, and adds one new test file under `tests/factory/`.

Overlap with other open tickets, checked under this ticket's own new rule:
- T-0025 (the store moves to its own branch) is approved, now `planned`, and not yet archived. It edits `factory/cli.py` (`init`), `README.md`, `docs/design.md`, `docs/changelog.md` and the build spec, so text conflicts are likely and a merge-catch-up run resolves them. Its decisions keep a throwaway store a plain directory, which is what this spec's fixture uses. The document checks below find this ticket's changelog entry by content, not as the last entry, so they hold whichever ticket merges first.
- T-0026 (the workflow view shows a short title beside each ticket id) is approved at v2, `ready-for-planner`, and not yet archived. It changes only display text in `factory/workflows/intake.js` and `factory/workflows/build.js`; its design part E makes no change to the CLI, prompts, tests, README, design doc or changelog. This ticket does not touch the workflow scripts, and no scenario here runs them or reads their output, so every scenario holds whichever of the two merges first.
- T-0022 (issue #40) is not yet specced. Its part C adds a check under critic rubric item 1. This ticket edits item 5, so the two edits touch different lines of the same three copies.

## Operator steps

none
