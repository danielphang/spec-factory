## Acceptance

- An amendment re-pins the change and keeps the plan's tasks → NEW; today `spec amend` is not a command (`invalid choice: 'amend'`), so it prints `exit=2 "approved_version": 1 pinned=0 tasks=1 first=merged`
- A later implementer run receives the amended spec, and the record lists what changed → NEW; today no record or event exists and the implementer gets v1: `changed=0 merged=0 reason=0 logged=0`, then `amended=0 old=1 run_version=1`
- Archive after an amendment writes the amended scenario and decision → NEW; today archive writes v1: `archive=0 hello=0 hi=1 decision=0`
- An amendment after archive is refused → NEW; today the amend attempts fail in argparse with no JSON, and archive writes v1: `late=0 changes=archive hello=0`
- A malformed amendment, a sub-ticket target and a two-line reason are refused and write nothing → NEW; today each attempt fails in argparse with no JSON refusal: `malformed=0 subticket=0 reason=0 "approved_version": 1 v2=0 records=0`
- An amendment is refused while a sub-ticket's run is in flight, naming the run → NEW; today it exits 2 from argparse without naming the run: `exit=2 names_run=0 "approved_version": 1 v2=0 pinned_old=1 records=0`
- The critic's input lists approved changes not yet archived, other than its own → NEW; today the section does not exist: `listed=0 self=0 decision=0 requirement=0`, then `after_archive: heading=0 listed=0`
- A critic run's system prompt carries the cross-ticket rule → NEW; today the critic prompt has no such rule: `rule=0`
- The runtime critic prompt stays a copy of the documented one → REGRESSION
- The changelog records the amendment change in one contiguous entry → NEW; today no entry names `spec amend`: `CONTIGUOUS`, `0`, `0`
- The design doc and build spec name the amend command and the critic's new input → NEW; today `amend=0 row=0 build=0`
- README lists the amend command under Where a human decides → NEW; today `amend=0`
- The amendment change adds no whitespace errors → REGRESSION

## Responses

- [BLOCKING] Decisions, "park" not glossed → FIXED. Problem's glossary paragraph now says what a parked ticket is ("the pipeline stops it and hands it to a human") and what BLOCKED is (an implementer that cannot go on parks its sub-ticket with that status). Decisions bullet 1 restates the gloss where it rejects `resolve --amend-spec`, and gives the real reason with a line cite: each `resolve` mode that sends a ticket back into the pipeline acts only on a stopped ticket, parked or waiting on its requester (`factory/cli.py:735-811`), while an amendment may be needed for a ticket that is `planned` and not stopped. While re-reading as the gate operator I also glossed four more terms used in Decisions without a gloss: "spec store", "planner" with its `tasks.md`, "in flight" and `spec-v<n>.yaml`.
- [SHOULD-FIX] Risk leaves out T-0026 → FIXED. Risk now says "two today, T-0025 and T-0026". The overlap list has a T-0026 line. I read its change folder on `main` at `0b1abad`. T-0026 is at `ready-for-planner`, approved at v2, and changes only display text in `factory/workflows/intake.js` and `factory/workflows/build.js`. Its design part E says "Make no change to the CLI, prompts, agents, tests, README, design doc or changelog." No scenario here runs the workflow scripts, so each scenario holds whichever ticket merges first. The T-0025 line now gives its current state, `planned`.
- [NIT] "store" and "target" not glossed → FIXED. Problem now says the store is "the directory where the factory keeps tickets, spec versions and agent run records". Evidence now says the Nanobot target is "a second repository the factory works on, with its own store". Each gloss is its own sentence rather than a parenthetical, as writing.md rule 3 asks.

No scenario, requirement, design part or acceptance label changed in this round; only proposal.md and this section did. `main` is still at `0b1abad`, the same commit the critic checked, and no harness file has changed since. I re-ran two checks through the HOME wrapper: `bin/factory spec amend T-0001 --file x --reason r` on a throwaway store still prints `factory spec: error: argument sub: invalid choice: 'amend' (choose from add, tasks)`, and the REGRESSION prompt-copy check still prints `copies=same`.

## Critic rounds

round 1 · spec v1 · run-0259-critic · REVISE

Spec critic, round 1, T-0027 v1 (`specs/T-0027/v1.md`).

Findings:

[BLOCKING] 6 Decisions, first bullet (and third bullet)
Problem: The first Decisions bullet says an amendment "is not tied to a park", and the third says "parked BLOCKED", but no human-facing section glosses "park", a ticket state specific to this system, so the gate operator reading Decisions first would have to infer what the command is being contrasted with.
Evidence: Read Problem, Evidence and Decisions as the rubric's operator. Problem glosses gate, pin, change folder, sub-ticket, archive, current truth and ruling; "park" appears first in Decisions bullet 1 with no gloss anywhere in the spec. The rubric makes an unglossed system term in the first paragraph of a human-facing section BLOCKING even when context suggests it. The fix is one clause; nothing else in the spec needs to move.
Suggested fix: In the first bullet, write "not tied to a park (a ticket the pipeline has stopped and handed to a human)", or add "park" to the Problem's glossary paragraph.

[SHOULD-FIX] 1 Risk, blast radius and overlap list
Problem: Risk says the critic's new section would list "one today, T-0025", and the overlap list checks only T-0025 and T-0022, but a second approved change not yet archived exists today, T-0026, so both the count and the cross-ticket check the spec applies to itself are incomplete.
Evidence: `ls .factory/state/openspec/changes/` on `main` at `0b1abad` prints `T-0025 T-0026 archive`; `.factory/state/tickets/T-0026.yaml` has `status: ready-for-planner` and `approved_version: 2`; `grep -c T-0026 .factory/state/specs/T-0027/v1.md` prints `0`. Part B as designed would list T-0026 (not closed, not the reviewed ticket). T-0026 edits the workflow view, so a real conflict is unlikely, but the spec claims it ran its own new rule and the rule missed a ticket; an implementer or operator comparing the claim to the store would see the gap.
Suggested fix: Say "two today, T-0025 and T-0026" and add a T-0026 line to the overlap list stating what it touches and that no scenario here depends on it.

[NIT] 6 Problem, first paragraph; Evidence, first paragraph
Problem: "store files" (Problem) and "Nanobot target" (Evidence) are system terms used without a gloss; a new reader can mostly work them out, so I do not block on them.
Evidence: Neither "store" (the factory's state directory) nor "target" (a repository the factory works on, with its own store) is glossed before use.
Suggested fix: "a hand edit of the files in the factory's state store" and "the Nanobot target (a second repository the factory runs on, with its own store)".

Spot-checks done (all on `~/dev/spec-factory` `main` at `0b1abad`, clean harness tree):
- Cited paths and symbols: `factory/cli.py:350` `_add_spec_version` (writes `v<n>.md`, the `specs/<id>.md` copy, logs `spec.added`), `:669` status refusal in `approve_spec`, `:919` `spec_tasks`; `factory/specstore.py:290` `pin` (rmtree at 296), `:336` `archive`, `delta_ops_of_change`, `split_parts`, `DELTA_RE`, `SCEN_RE`, `lines_outside_fences`, `_heading`, `is_active`, `change_dir`, `validate`, `applies` all exist; `factory/compose.py:145-155` critic branch, `:157` planner, `:172` implementer/reviewer/verifier read `pt["spec"]["approved_version"]`; `docs/design.md:88` contains "work from the delta the human approved", `:102`, `:104`, `:113` routing row, `:418` rubric item 5; `dev/build-harness.spec.md:314` `--amend-spec`; `docs/prompts/03-spec-critic.md:18`; `README.md:313` "## Where a human decides", `:352` "## What is built and what is not"; `.factory/state/approvals/T-0012/amendment-1.md` exists; `.factory/answers/operator-decisions-2026-10-04.md:7` has the #44 approval. The validator's text `has no NEW/REGRESSION label` is at `specstore.py:213`. T-0022 is `ready-for-spec-writer`, so "not yet specced" is accurate.
- Acceptance, run through the HOME wrapper with `TMPDIR` set to this run's scratch directory, fixture written as given: "An amendment re-pins the change" prints `exit=2 "approved_version": 1 pinned=0 tasks=1 first=merged`; "A later implementer run receives the amended spec" prints `changed=0 merged=0 reason=0 logged=0` then `amended=0 old=1 run_version=1`; "The critic's input lists approved changes" prints `listed=0 self=0 decision=0 requirement=0` then `after_archive: heading=0 listed=0`; "A critic run's system prompt carries the cross-ticket rule" prints `rule=0`; "The design doc and build spec name the amend command" prints `amend=0 row=0 build=0`; the changelog check prints `CONTIGUOUS` then `0`. Each matches the failure verification.md states. `diff <(sed 's/{2}/2/' docs/prompts/03-spec-critic.md) factory/prompts/critic.md` is empty today, so the REGRESSION item holds.
- Testability: the checks would fail against a stub. `pinned=1 tasks=1` needs both the re-pin and the `tasks.md` carry-over; `merged=1` distinguishes listing only the merged sub-ticket from listing both; `run_version=2` requires the sub-ticket's own spec record to move, since `run start` reads `t["spec"]["version"]` (`cli.py:217`); the refusal scenarios check `v2=0 records=0 pinned_old=1`, so a partial write fails them.
- Scope and decisions: parts A to E serve the two approved parts of #44 and fit one PR; protected paths `factory/**` and `docs/prompts/**` are declared under Risk; `resolve --amend-spec` rejection, the in-flight refusal, the non-closed filter and the missing `spec-v<n>.yaml` are all stated as decisions, none silent. Consistent with design.md:104 (amended version reaches implementer and checkers) and with T-0023/T-0024 decisions in `decisions.md`.

Out-of-scope observations:
- Design D does not touch `docs/design.md:104`, whose "In-flight siblings keep the spec version they received" stays true under the in-flight refusal; no change needed, noted for the implementer.

round 2 · spec v2 · run-0265-critic · APPROVE

Spec critic, round 2, T-0027 v2 (`specs/T-0027/v2.md`).

Scope of this round, per the convergence rule: whether the three round-1 findings are resolved, and the text that changed. I confirmed the writer's claim that only `proposal.md` and the new `## Responses` block changed: `diff` of v1 and v2 with the `proposal.md` section removed from both shows only the eight added Responses lines in `verification.md`. No scenario, requirement, design part or acceptance label moved, so round 1's acceptance spot-checks and testability analysis stand. `main` is still at `0b1abad` with a clean harness tree.

Prior findings:

[BLOCKING] 6 Decisions, first and third bullets ("park" unglossed) → RESOLVED.
Evidence: v2's Problem glossary paragraph now reads "A ticket is parked when the pipeline stops it and hands it to a human; an implementer that cannot go on parks its sub-ticket with the status BLOCKED." Decisions bullet 1 no longer says "not tied to a park"; it gives the real reason with a cite, and the cite holds: `factory/cli.py:735-811` is the body of `resolve`. `--answer` accepts `waiting-requester` or a `NEEDS-HUMAN` park (lines 736-741), `--ruling`, `--to spec-gate`, `--redispatch` and `--replan` each refuse unless `st == "parked"` (lines 748, 763, 773, 796), and `--close` ends the ticket (805-808). So "each `resolve` mode that sends a ticket back into the pipeline acts only on a ticket the pipeline has stopped" is accurate, and a `planned` parent is indeed outside every `resolve` route. The writer also glossed "spec store", "planner" with `tasks.md`, "in flight" and `spec-v<n>.yaml` in the same paragraph; read as the gate operator, Decisions now has no term of art that the Problem has not introduced.

[SHOULD-FIX] 1 Risk, blast radius and overlap list (T-0026 missing) → RESOLVED.
Evidence: Risk now says "two today, T-0025 and T-0026" and has a T-0026 line. Checked on `main` at `0b1abad`: `ls .factory/state/openspec/changes/` prints `T-0025 T-0026 archive`; `tickets/T-0026.yaml` has `status: ready-for-planner`, `approved_version: 2`; `tickets/T-0025.yaml` has `status: planned`, `approved_version: 5`, matching the updated T-0025 line. `openspec/changes/T-0026/design.md:29` says "Make no change to the CLI, prompts, agents, tests, README, design doc or changelog", and the only harness paths it names are `factory/workflows/intake.js` and `factory/workflows/build.js` (its line 33 mentions `tests/factory/test_shepherd.py` as a reference, under a "Tests to change: none"). Nothing in T-0027 touches or runs the workflow scripts, so the claim that every scenario holds under either merge order is right.

[NIT] 6 Problem and Evidence ("store", "target" unglossed) → RESOLVED.
Evidence: Problem now says "the factory's state store, the directory where the factory keeps tickets, spec versions and agent run records"; Evidence says "The Nanobot target is a second repository the factory works on, with its own store." Each is its own sentence, per writing.md rule 3.

New findings on changed text:

[NIT] 1 Risk, overlap list, T-0022 line
Problem: "T-0022 (issue #40) is not yet specced" is true at the committed `0b1abad` but already stale in the working store, where T-0022 has a v1 spec draft and sits at `ready-for-critic`.
Evidence: `git status` shows `.factory/state/tickets/T-0022.yaml` modified and `.factory/state/specs/T-0022/v1.md` untracked, so the move happened after the writer read the store and is not yet committed. The point the line makes still holds: T-0022 has no approved version (`approved_version: null`) and no change folder, so part B would not list it and the two tickets still edit different lines of rubric items 1 and 5. Not worth a round; the implementer's merge-catch-up handles any prompt-line collision.
Suggested fix: none required; if the writer touches Risk again, "not yet approved" is the durable wording.

Spot-checks this round: `factory/cli.py:735-811` (new cite, read in full); `.factory/state/openspec/changes/T-0026/design.md:29,33`; `tickets/T-0025.yaml`, `T-0026.yaml`, `T-0022.yaml`; `specs/T-0027/v1.md` against `v2.md`. Acceptance commands were not re-run because no scenario line changed; round 1 ran six of them on this same commit and each printed the failure `verification.md` states.

Why I would bet on this spec producing a correct PR: the design parts are precise down to check order and record format, every NEW scenario was shown to fail today for the stated reason and checks for partial writes (`v2=0 records=0 pinned_old=1`), the two product decisions the operator pre-approved (#44 parts A and B) are the only ones made, and the one remaining uncertainty, T-0025's text conflicts in `cli.py` and the four documents, is named under Risk with its resolution route.

Out-of-scope observations:
- Unchanged from round 1: design D does not touch `docs/design.md:104`, whose "In-flight siblings keep the spec version they received" stays true under the in-flight refusal.
