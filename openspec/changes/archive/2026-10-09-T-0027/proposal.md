## Problem

When the factory builds two approved designs close together, the one that merges first can make the other's approved acceptance checks impossible to pass. The factory has no command to correct the approved design afterwards. It also has no check that catches the conflict before an agent has spent a build on it. The operator pays in blocked builds, hand-written instructions and repeated agent runs. On the Nanobot target, one ticket closed at 15.1M tokens across five build passes, mostly for this reason.

Some terms used below. The factory turns a request, called a ticket, into merged code through a chain of AI agents, called roles. The spec is the ticket's design. Its scenarios are the runnable checks the code must pass. The spec gate is the one human sign-off on a spec before code is written. At the gate the harness pins the spec: it freezes the approved version, and every later role reads that version. The store is the directory where the factory keeps tickets, spec versions and the records of agent runs. A pinned spec is also written out as the ticket's change folder in the store; a store set up without that layout has no spec store. The planner is the role that splits a ticket into sub-tickets, and it leaves its task list, `tasks.md`, in the change folder. Each sub-ticket is built by the implementer role on its own branch, checked by two checker roles, and merged on its own into the integration branch, the repository's main line. When every sub-ticket has merged and a final check passes, archive writes the change folder's scenarios into current truth. Current truth is the store's record of how the system behaves now; later specs are written against it. A run is in flight while a role is working on a ticket. A ticket is parked when the pipeline stops it and hands it to a human. An implementer that cannot go on parks its sub-ticket with the status BLOCKED. A ruling is a human's written instruction, filed with the ticket, that the harness hands to later role runs.

Three things are missing:

- **No way to amend.** Only the gate writes a spec version. A ruling can tell the builders to change a scenario's setup, so the build goes on, but archive still writes the unamended scenario into current truth, where it fails when anyone re-runs it. Nor does anything separate a correction (a scenario's setup, a precondition, a wording fix) from a change of what the ticket is for. A change of that kind, patched in under sub-tickets already merged for the old intent, would leave merged code that no longer matches its spec.
- **No check at the gate.** The critic is the role that grades a spec before the operator sees it. It is not asked whether a scenario depends on behaviour that another approved, unmerged ticket changes, and its input does not list those tickets.
- **No check at build start.** Between writing a spec and building a sub-ticket, other tickets merge. One may add a test that pins behaviour the spec changes. A sub-ticket's scenarios may also need a sibling sub-ticket that has not merged. Today the implementer or a checker finds out, after a run has been spent.

This ticket adds three things. The first is a human-only command that amends a pinned spec when the amendment keeps the spec's intent; it refuses a change of intent and says what a restart would keep and discard. The second is a drift check before a sub-ticket's first implementer run. The third is the critic's cross-ticket check, with the list of approved changes that check needs.

## Evidence

The incidents behind this ticket. Each is read in the store named. Nanobot is a second repository the factory works on, with its own store at `~/dev/nanobot-upstream/.factory/store`. Its tickets have their own numbers: Nanobot's T-0027 is not this ticket.

| Date | Where | What broke | What it cost |
|---|---|---|---|
| 2026-10-03 | this repo, T-0012 | A scenario could not pass as written: its whitespace check covered the store's own records. | The operator edited the pinned `specs/T-0012/v3.md` in place by hand. `.factory/store/approvals/T-0012/amendment-1.md` records "Applied in place to `specs/T-0012/v3.md` (the pinned version every checker reads)". No command made the edit. |
| 2026-10-04 | Nanobot, T-0008 (its spec 05, typing) | Nanobot T-0002 (its spec 20) merged first and made WhatsApp groups fail closed without a policy file. Two pinned scenarios of T-0008 create none, so they cannot pass. | Implementer BLOCKED (run-0166). Rulings in `approvals/T-0008.1/ruling-1.md` and `approvals/T-0008/ruling-1.md` say "Test setup only. No behaviour change, and no change to any THEN". Archive would still write the unamended scenarios. |
| 2026-10-07 | this repo, T-0032.1 | `tests/factory/test_gate_paths.py`, added by T-0028.1, asserted the opposite of the spec's part B.2. T-0032's spec was written 2026-10-04 23:23–23:57 (runs 0292 and 0294), T-0028.1 merged 2026-10-05 15:09, and T-0032 was approved 2026-10-07 05:21. | Implementer BLOCKED (run-0304), an operator ruling, one more implementer run and both checkers again. The test arrived after the spec was written but before it was pinned. |
| 2026-10-09 | Nanobot, T-0031 (its spec 34) | Three separate breaks. T-0031.4's acceptance named sibling T-0031.2 as "already merged", but T-0031.2 waited on Nanobot's T-0027 and had not merged. T-0031.2 broke 8 tests that Nanobot's T-0027 (its spec 22) added after T-0031's spec was written. T-0031.5 broke 1 test that its sibling T-0031.4 added, which checked the last lines of an output. | A verifier SPEC-DEFECT (run-0380) and a re-run of the checks; implementer BLOCKED twice (run-0391, run-0399), each with a ruling and another implementer run. The store records 13 implementer runs for 5 sub-tickets. Five of them are catch-up runs (`resolution: conflict` in their `meta.yaml`), made while Nanobot's T-0027 sub-tickets merged in between. The operator's change request gives 15.1M tokens for the ticket. I could not check that figure, which needs the workflow transcripts. |

Today's behaviour, on a scratch store and target (the GIVEN fixture of the first scenario below, run on an unmodified clone of `main` at `b002c95`):

- `bin/factory spec amend T-0001 --file x --reason r --intent unchanged` prints `factory spec: error: argument sub: invalid choice: 'amend' (choose from 'add', 'tasks')` and exits 2. No command writes a spec version after the gate.
- A later implementer run on T-0001.2 receives v1 (`amended=0 old=1 run_version=1`): only a ruling could tell it otherwise. Archive then writes v1's scenario into current truth (`hello=0 hi=1`). That is the harm the ruling workaround leaves behind.
- A sub-ticket whose acceptance names an unmerged sibling starts its implementer (`runs=1`). So does one whose spec names `src/greet.py` after a later commit changed that file and added `tests/test_greet.py`: the build runs the implementer instead of parking.
- A critic run's input lists no other approved change (`listed=0`), and its system prompt has no cross-ticket rule (`rule=0`).

How often a drift check would park, measured on both stores' history. For each sub-ticket with an implementer run, I took the integration-branch commit when its parent's approved version was added (from the store's log) as the start. The base of its first implementer run was the end. I applied part D's two rules to the commits between them. The "known incidents" are the BLOCKED and SPEC-DEFECT runs whose escalation names a test or scenario that another merge broke.

| Store | Sub-tickets | Test rule would park | Known incidents it catches | Sibling rule would park |
|---|---|---|---|---|
| this repo | 36 | 17 | 2 of 2 (T-0025.1, T-0032.1) | 2 |
| Nanobot | 43 | 29 | 7 of 8 (misses T-0022.1, whose breaking merge changed no file the spec names) | 5: T-0031.4, the real case; three T-0002 sub-tickets that did start too early, when their dependency records were empty (a bug since fixed); and T-0027.2 |

So the test rule catches nearly every known case, and it also parks about half the sub-tickets that had no problem. Decisions and Risk say what that costs.

The design already allows amending. `docs/design.md:110` says "the human amends the spec and re-plans". `docs/design.md:113` says "The human may amend the sub-ticket or the pinned spec first; the amended version is what the implementer and checkers receive." The build spec, `dev/build-harness.spec.md:315`, specifies a `resolve --amend-spec FILE` flag that was never built.

The operator approved parts A and B of issue #44 as one ticket (`.factory/answers/operator-decisions-2026-10-04.md`: "#44: approve parts A (spec amend, human-only, logged) and B (critic cross-ticket check) as one ticket, pre-approved"). On 2026-10-09 the operator sent the approved v2 back (`.factory/store/approvals/T-0027/changes-1.md`) to fold in issue #50, which asks `spec amend` to declare intent and refuse a change of intent, and to add the drift check.

I prototyped the change in a clone of `main` at `b002c95`: about 275 changed lines of harness code and prompt, plus stub documents. Every scenario below printed its THEN line there. On an unmodified clone, each scenario labelled NEW printed the failure given in verification.md. The full harness suite passed on both clones, `408 passed`. On the prototype, the three current-truth scenarios of the sibling-tests check (build-dispatch) printed the same lines as before.

## Root cause

- `factory/cli.py:843` `approve_spec` is the only command that sets `spec.approved_version` and calls `specstore.pin` (`cli.py:864`). It refuses unless the ticket is `awaiting-spec-gate` (`cli.py:859`). `_add_spec_version` (`cli.py:395`) writes a version but pins nothing. The `spec` subcommands are `add` and `tasks` (`cli.py:1564`).
- `factory/compose.py:334` hands an implementer `specs/<parent>/v<approved_version>.md`; the checkers (`compose.py:349`, `:352`) and the planner (`compose.py:291`) get the same version. So moving `approved_version` reaches every later run, and nothing moves it.
- `factory/specstore.py:290` `pin` deletes and rewrites the whole change folder (`shutil.rmtree(d)`, line 296). That would drop the planner's `tasks.md`.
- `factory/specstore.py:336` `archive` applies the deltas in the change folder, so only a re-pin changes what reaches current truth.
- `factory/cli.py:198` `run_start` checks an implementer's sub-ticket only for tests a sibling added (`_check_sibling_tests`, `cli.py:213`). No record says which integration-branch commit a spec version was written against, so no check can ask what changed since.
- `factory/compose.py:265`, the critic branch, adds the spec, current truth, the decision log and rulings, and nothing about other tickets. Rubric item 5 (`docs/design.md:456`, `docs/prompts/03-spec-critic.md:21`, `factory/prompts/critic.md:21`) says only "doesn't conflict with open tickets".

## Out of scope

- How a ticket moves after an amendment. The routes that exist stay as they are: `resolve --ruling` on a BLOCKED sub-ticket, `ticket transition` back to `ready-for-parent-verify`, `resolve --replan`.
- Amending a sub-ticket's own text (`specs/<id>/subticket.md`). T-0031.4's sibling case was in that text; a ruling handles it, as today.
- A restart command. The refusal names the existing commands; the factory never discards merged work by itself.
- Catch-up runs when two tickets' sub-tickets merge alongside each other.
- Running a sub-ticket's scenarios at build start (Decisions says why).
- Re-checking merged sub-tickets against amended scenarios. The final check on the merged result does that, as today.
- Giving the spec writer the list of approved changes not yet archived. Only the critic gets it here.
- Replacing the Nanobot target's existing rulings with amendments. That is the operator's call on that target.
- The gate's `approve-spec`, `--edit` and `resolve` behaviour, and `archive`'s refusals: unchanged.
- Tests that a decision overturns within one ticket: T-0022 (issue #40) built that check, and it is live.

## Open questions

none

## Decisions

- The command is `factory spec amend <parent> --file <F> --reason "<one line>" --intent unchanged|changed`, run by a human. Rejected: the build spec's unbuilt `resolve --amend-spec`. Each `resolve` mode acts on a ticket the pipeline has stopped, and an amendment may be needed while a ticket is `planned` and not stopped.
- `--intent` is required. With `unchanged`, the harness checks the claim: the amended version must keep the Problem section, every Decisions line, and each requirement's name, operation and statement (its text before its first scenario), whitespace aside. Scenarios, setup, Evidence, design text and Tests to change may change. Any other difference is refused as a change of intent, naming each one. `--intent changed` is always refused. Rejected: issue #50's critic run on every amendment, which needs a new route from the command to the critic; the mechanical check covers the same three things. Rejected: no flag, which lets a human make an intent change without saying so. This is a standing decision.
- A refused change of intent prints a restart note. The note lists each merged sub-ticket with its merge commit, which stays on the integration branch. It lists each unmerged one with its state and branch, which a restart discards. It names both ways to restart. The first re-specs and re-plans: `factory ticket park`, `factory resolve <id> --to spec-gate`, then `factory approve-spec <id> --edit F`, after which the new plan supersedes the unmerged sub-tickets. The second closes the ticket and re-files it: `factory resolve <id> --close` and `factory ticket new`. The factory never restarts by itself. This is a standing decision.
- An amendment changes no ticket state. The operator resumes the ticket with the routes that exist. Rejected: an amendment that also moves the ticket, which would duplicate those routes.
- `spec amend` refuses while any run is in flight on the parent or one of its sub-tickets. A parked or waiting sub-ticket does not block it. Rejected: refusing while any sub-ticket is unmerged, which would block the motivating case of a sub-ticket parked BLOCKED on a scenario it cannot pass. This is a standing decision.
- Human-only means that no workflow script and no role prompt names the command. A role run on the parent or a sub-ticket is in flight while it runs, so the in-flight refusal stops it. There is no identity check, because the harness runs under one identity.
- `spec amend` refuses, with exit 2 and nothing written, in these cases: a sub-ticket; a ticket with no approved version; a ticket at `awaiting-spec-gate`, where `approve-spec --edit` is the route; a closed ticket; a reason that is not one non-blank line; and, with a spec store, a ticket whose change folder is gone because it was archived. An amended version must pass the gate's own checks: it is well-formed, and its deltas apply to current truth.
- The re-pin keeps the planner's `tasks.md` in the change folder. The rest of the folder is rewritten as the gate writes it.
- Each sub-ticket that is neither merged nor closed has its spec record moved to the new version, so later runs record the version they received. Its `planned_from`, the version its plan was made from, does not change, so an amendment never supersedes a plan.
- The record is `approvals/<parent>/amendment-<n>.md`, numbered after any amendment file already there. It holds who, when, the reason, `Intent: unchanged`, the old and new version, and one line per scenario that differs: `- changed: <name>`, `- added: <name>` or `- removed: <name>`. It also holds a `- <id> / <title>: merged` line per sub-ticket merged before the amendment, and the unified diff. The log gets a `spec.amended` event. The amendment record is that version's approval record; no gate approval file is written.
- Every spec version records the integration branch's head when it was stored, in `specs/<id>/v<n>.yaml`; that covers `spec add`, a gate edit and `spec amend`. Drift is counted from the record of the parent's approved version. Rejected: counting from the pin, because T-0032.1's test arrived between writing and pinning. A version stored before this change has no record, so its sub-tickets get only the sibling rule.
- The drift check runs at `run start` of a sub-ticket's implementer, before the sibling-tests check. It runs only while the sub-ticket has no implementer run and no ruling on file. On drift it refuses with exit 2, writes nothing, and gives an error that starts `BLOCKED from harness: spec drift:` and names each finding. The build already parks any `BLOCKED ` refusal with it as the reason. The human then amends the spec, rules, or both, and `resolve --ruling` returns the sub-ticket; the ruling also stops the check from repeating. Rejected: a new SPEC-DRIFT park status, as issue #50 proposed, which needs a new `resolve` route.
- Sibling rule: drift when the sub-ticket's Acceptance field names, by id or by plan label, a sibling of the current plan that has not merged and that the sub-ticket does not depend on, directly or through other siblings. Nothing makes such a sibling merge first. This is a standing decision.
- Test rule: drift for each test file changed on the integration branch since the version's recorded head, by a first-parent commit that also changed a file the spec's design part names, and that neither the spec's Tests to change nor the sub-ticket's Tests to change lists. A test file's name starts with `test_`, or ends `_test.<ext>`, or contains `.test.`. Named files are the design part's backticked paths that exist at the integration head, except test files and `.md` documents, which every ticket here edits. This approximates "pins behaviour the spec changes": measured above, it catches 9 of 10 known incidents and would park about half the sub-tickets. Rejected: running each NEW scenario at build start and comparing it with the spec's "fails today" output (issue #50, part D). That output is prose, not something a program can compare. Rejected: a judge run per sub-ticket, which needs a new role and route.
- The critic's input gains a section, `## Approved changes not yet archived`. It lists each change folder whose ticket is neither closed nor back in the spec loop (`ready-for-spec-writer`, `ready-for-critic`, `awaiting-spec-gate`), other than the reviewed ticket's own. Each entry gives the ticket id, title, state, folder path, the requirements its deltas add, modify or remove, and its Decisions lines. The section reads `none` when the list is empty, and is left out when the store has no spec store. Rejected: whole proposals, which would multiply the critic's input.
- The cross-ticket rule extends the critic's rubric item 5 (Consistent). A scenario whose setup would not hold under one of the two merge orders is a BLOCKING finding that names the other ticket and its decision. This is a standing decision.

## Risk

Blast radius:
- One new human command, which touches only the ticket it names and its sub-tickets' spec records.
- Every `spec add` and gate edit writes one more small file, `specs/<id>/v<n>.yaml`.
- Every sub-ticket's first implementer run start gains the drift check. This is the main cost. Measured on history, the test rule would park 17 of 36 sub-tickets here and 29 of 43 on Nanobot, each for one human ruling or amendment, and catch 9 of the 10 known breaks before an implementer run. A park the operator judges harmless costs one ruling, which the implementer then receives.
- Every critic run on a store with a spec store gets one more input section, with one entry per approved change not yet archived. Today that is one entry here, T-0031.
- The critic prompt gains four lines in rubric item 5. No routing, state, gate or archive behaviour changes.

Overlap with other open tickets, checked under this ticket's own new rule:
- T-0031 here (role commands drop an inherited virtual environment; build checkouts run an optional `environment_sync` command) is approved, `planned`, and not yet archived. It also edits `run_start` in `factory/cli.py`, so text conflicts are likely, and a catch-up run resolves them. Its decision sets `environment_sync` on neither instance. The scenarios here start implementers with this checkout's instance configuration and never use the running-code wrapper, so they hold whichever ticket merges first.
- T-0039 (reading rules for five more roles) is at the spec gate, not approved. It edits other prompt blocks of `docs/design.md`, not the critic's.
- The documents checks below find this ticket's changelog entry by its content, not as the last entry, so they hold whichever ticket merges first.

Protected paths: `factory/cli.py`, `factory/specstore.py`, `factory/compose.py`, `factory/subtickets.py`, `factory/gitops.py`, `factory/prompts/critic.md`, `docs/prompts/03-spec-critic.md`

`factory/gitops.py` is declared for a git helper the drift check may add; the prototype did without one. The change also edits `docs/design.md`, `docs/changelog.md`, `dev/build-harness.spec.md` and `README.md`, which are not protected, and adds new test files under `tests/factory/`.

## Operator steps

none
