## Acceptance

- An intent-unchanged amendment re-pins the change and keeps the plan's tasks → NEW; today `spec amend` is not a command (`invalid choice: 'amend'`), so it prints `exit=2 "approved_version": 1 pinned=0 tasks=1 first=merged`
- A later implementer run receives the amended spec, and the record lists what changed → NEW; today no record or event exists and the implementer gets v1: `changed=0 merged=0 reason=0 logged=0`, then `amended=0 old=1 run_version=1`
- Archive after an amendment writes the amended scenario → NEW; today archive writes v1: `archive=0 hello=0 hi=1`
- An amendment declared or found to change intent is refused, naming what a restart keeps and discards → NEW; today both attempts fail in argparse with no JSON refusal: `intent=changed exit_json=0 restart=0 decision=0 merged=0 pending=0 paths=0`, then the same for `intent=unchanged`, then `"approved_version": 1 versions=1 records=0`
- An amendment after archive is refused → NEW; today the amend attempts fail in argparse with no JSON, and archive writes v1: `late=0 changes=archive hello=0`
- A malformed amendment, a sub-ticket target and a two-line reason are refused and write nothing → NEW; today each attempt fails in argparse with no JSON refusal: `malformed=0 subticket=0 reason=0 "approved_version": 1 v2=0 records=0`
- An amendment is refused while a sub-ticket's run is in flight, naming the run → NEW; today it exits 2 from argparse without naming the run: `exit=2 names_run=0 "approved_version": 1 v2=0 pinned_old=1 records=0`
- A sub-ticket whose Acceptance names an unmerged sibling it does not depend on is refused until that sibling merges → NEW; today the implementer starts at once, and the second start is refused because that run is in flight: `unmerged: blocked=0 names=0 runs=1 ready-for-implementer`, then `merged: exit=2 runs=1`
- A test changed beside a file the spec names parks the sub-ticket, and a ruling lets it start → NEW; today the implementer runs instead of parking: `park T-0001.1: EMPTY-OUTPUT from implementer`, then `greet=0 other=0 runs=2`, then `ruled: exit=2 runs=2`
- Unrelated changes, a listed test and an amendment written after the change let the implementer start → REGRESSION; guards against the drift check parking what it should not
- The critic's input lists approved changes not yet archived, other than its own → NEW; today the section does not exist: `listed=0 self=0 decision=0 requirement=0`, then `after_archive: heading=0 listed=0`
- A change sent back to the spec writer leaves the critic's list → NEW; today the section does not exist: `listed=0 self=0 decision=0 requirement=0`, then `respec: heading=0 listed=0`
- A critic run's system prompt carries the cross-ticket rule → NEW; today the critic prompt has no such rule: `rule=0`
- The runtime critic prompt stays a copy of the documented one → REGRESSION
- The changelog records the change in one contiguous entry → NEW; today no entry names `factory spec amend`: `CONTIGUOUS`, `0`, `0`
- The design doc and build spec name the amend command, its intent flag, spec drift and the critic's new input → NEW; today `amend=0 intent=0 drift=0 row=0 build=0 build_drift=0`
- README lists the amend command and the drift check → NEW; today `amend=0 intent=0 built=0`
- The change adds no whitespace errors → REGRESSION

## Responses

To the operator's change request of 2026-10-09 (`approvals/T-0027/changes-1.md`), on approved v2:
- 1, fold in issue #50 (amend declares intent) → FIXED. `--intent unchanged|changed` is required. `unchanged` is checked against the Problem, the Decisions and each requirement's statement. `changed`, or a failed check, is refused with a note on what is merged and what a restart discards, naming both restart paths. Issue #50's part B, a critic run on every amendment, is replaced by that mechanical check (Decisions). Its part C, the triggers and the amend-or-restart rule in the README, is in design part E. New scenario: "An amendment declared or found to change intent is refused, naming what a restart keeps and discards". v2's archive scenario no longer changes a Decisions line, which is now an intent change.
- 2, drift check at build start → FIXED, as design part D, with both kinds of drift the request names. One departure: drift is counted from when the approved version was written, not from when it was pinned, because T-0032.1's test arrived between the two (Evidence). The test rule is a heuristic. Its measured park rate is in Evidence and Risk, and I flag it under ESCALATIONS.
- 3, evidence → FIXED. The incidents table adds Nanobot T-0031 and this repo's T-0032.1, each checked in its store. The 15.1M-token figure is the operator's; I could not check it.
- 4, `Protected paths:` line → FIXED. Risk declares seven paths on the line the merge gate reads.
- 5, keep the critic's cross-ticket check → kept, as parts B and C. One change: the list leaves out a ticket sent back into the spec loop, as this ticket is now. Its old change folder still exists, but it is no longer an approved change. New scenario: "A change sent back to the spec writer leaves the critic's list".

## Out-of-scope observations

- After `request-changes`, the spec writer's input does not include the spec it wrote before. `compose.py` adds the previous version only when `round.spec >= 1`, and `request-changes` resets the round to 0. I read v2 from `specs/T-0027/v2.md` directly.
- In this repo's store, `openspec/changes/` still holds the folders of closed tickets T-0026 and T-0030. Part B skips closed tickets, so they do not reach the critic. Why they were not archived is not checked here.

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

round 1 · spec v3 · run-0371-critic · APPROVE

Review of T-0027 spec v3 (round 1 on v3; the input carries no earlier findings of mine).

What I checked, on `~/dev/spec-factory` at `b002c95` (tree clean apart from an untracked `.factory/answers/T-0027-changes-2026-10-09.md`, a copy of `approvals/T-0027/changes-1.md`):

- Cited paths and symbols: `factory/cli.py:843` `approve_spec`, `:859` the `awaiting-spec-gate` refusal, `:862` the `_add_spec_version` call, `:395` `_add_spec_version` (two callers, `:407` and `:862`, as part D says), `:1564` the `spec` subparser with `add` and `tasks`, `:198` `run_start`, `:213` `_check_sibling_tests`; `factory/compose.py:265` critic branch, `:291` planner, `:334/:349/:352` implementer and checkers; `factory/specstore.py:290` `pin` with `shutil.rmtree` at `:296`, `:336` `archive`; `docs/design.md:110`, `:113`, `:456`; `docs/prompts/03-spec-critic.md:21` and `factory/prompts/critic.md:21`; `dev/build-harness.spec.md:315` (`--amend-spec FILE`) and `:193`; `factory/workflows/build.js:81-83`. All exist and say what the spec says. Every helper part A, B and D names exists: `_next_n` (cli.py:839), `subtickets_of` (store.py:228), `decisions_of`, `delta_ops_of_change`, `split_parts`, `DELTA_RE`, `lines_outside_fences`, `SCEN_RE`, `_heading`, `parse_delta`, `validate`, `applies`, `is_active`, `change_dir` (specstore.py), `split_plan`, `sibling_tests`, `PLAN_FIELDS` (subtickets.py), `gitops.rev`, `compose._runs_for`. Every CLI verb the scenarios use exists with the flags used (`ticket show --json`, `ticket set`, `ticket park --reason`, `resolve --to`, `request-changes --notes`, `log tail --event`, `archive`).
- Evidence records: `approvals/T-0012/amendment-1.md:5` carries the quoted "Applied in place" sentence; `run-0304-implementer` exists here; on Nanobot `run-0166-implementer`, `run-0380-verifier`, `run-0391-implementer`, `run-0399-implementer` and both T-0008 rulings exist (read only). `tests/factory/test_gate_paths.py` was added by commit `0e99fa7` (T-0028.1). `openspec/changes/` here holds T-0026 (closed), T-0027 (self, `ready-for-critic`), T-0030 (closed), T-0031 (`planned`): part B's list would hold one entry, T-0031, as Risk says. T-0039 is `awaiting-spec-gate`.
- Acceptance commands, run as given under a throwaway HOME, with the fixture in my scratch directory: "The runtime critic prompt stays a copy" prints `copies=same`; "A critic run's system prompt carries the cross-ticket rule" prints `rule=0`; scenario 1 prints `exit=2 "approved_version": 1 pinned=0 tasks=1 first=merged`; "A later implementer run receives the amended spec" prints `changed=0 merged=0 reason=0 logged=0` then `amended=0 old=1 run_version=1`; "Archive after an amendment" prints `archive=0 hello=0 hi=1`; the sibling-rule scenario prints `unmerged: blocked=0 names=0 runs=1 ready-for-implementer` then `merged: exit=2 runs=1`. Each matches the failure verification.md states for it.
- Tests pinning old behaviour (rubric 1): I searched `tests/factory/` for a pin on the `spec` subcommand set (`invalid choice`), on the critic rubric wording or the critic prompt copies, on `_add_spec_version`'s signature, on a listing of `specs/<id>/` (where the new `v<n>.yaml` lands), and on Acceptance fields naming an unmerged non-dependency sibling. None found: the only Acceptance fields in tests (`test_subtickets.py:183`, `test_parent_close_reuse.py:15-18`) name the sub-ticket itself or no sibling, and the `t0022-sib.sh` fixture adds its spec before the target repo exists, so its versions would record a null head and the test rule skips. "Tests to change: none" holds as far as a search can tell.
- Not checked: the drift measurement (17 of 36, 29 of 43, 9 of 10), the prototype's `408 passed`, and that the three current-truth sibling-tests scenarios print the same on the prototype. These need the suite or the build and are the verifier's.

Findings

[SHOULD-FIX] 6 design.md, part A, the restart note (and Decisions, the restart-note bullet)
Problem: The note prints each merged sub-ticket as `<id> / <title> (merge <main_after, 9 chars>)`, but the scenario that exercises it marks T-0001.1 merged with `ticket set status=merged`, which records no merge commit, so the implementer has to guess what to print when `merge.main_after` is absent.
Evidence: scenario "An amendment declared or found to change intent is refused" sets `status=merged` only; `t0022-sib.sh` shows the merge record lives in `merge.main_after`, set separately. The scenario greps `T-0001.1 / First`, so any choice passes it, but the output format is unspecified for that case.
Suggested fix: Say what the note prints when a merged sub-ticket has no `merge.main_after` (for example, `(merge unrecorded)`), in design part A.

[SHOULD-FIX] 6 proposal.md, Decisions, first paragraph
Problem: "the build spec's unbuilt `resolve --amend-spec`" uses "build spec", a term of this system, which no human-facing section has glossed; the rule names this BLOCKING, but I do not block on it because the Evidence paragraph gives the file's path and says it "specifies a flag that was never built", which tells the reader what it is in all but form.
Evidence: Problem glosses ticket, role, spec, gate, pin, store, change folder, planner, archive, current truth, run, parked, BLOCKED, ruling; neither Problem nor Evidence says what the build spec is. `resolve` is glossed in the same Decisions sentence ("acts on a ticket the pipeline has stopped").
Suggested fix: Gloss it once where it first appears, in Evidence: "The build spec, the harness's own build-and-acceptance document at `dev/build-harness.spec.md`, ...".

[NIT] 4 proposal.md, Decisions, "Human-only means..."
Problem: The argument that the in-flight refusal stops a role run from amending covers only a run on the same ticket; a role run on another ticket is stopped by the live-store guard instead, which the paragraph does not say.
Evidence: current truth live-store-guard, "Unmarked writes to a live store are refused while a role run is in flight there".
Suggested fix: Add one sentence naming the live-store guard as what stops a role run on another ticket.

[NIT] 2 specs/spec-amendment, scenario "An amendment is refused while a sub-ticket's run is in flight"
Problem: `names_run` greps stderr (`2>&1 >/dev/null`) while every other refusal scenario greps the JSON on stdout; both work (cli.py:1709-1710 prints the error to both), but a reader checking the scenarios against each other will pause on it.
Evidence: `factory/cli.py:1708-1711`.
Suggested fix: Grep stdout like the others, or leave it with a word that says the refusal is printed to both.

No blocking issues. The spec is NEEDS-SPLIT with its seams named, every NEW scenario I ran fails today for the stated reason, every protected path the design touches is on the `Protected paths:` line, and the overlap with T-0031's `run_start` edit is declared.

Prior findings: none in input.

## Verifier results

49cc429424c1eb02708268bf4ecb0f251bfe8ae7 · T-0027.3 · VERIFIED · run-0385-verifier
7c21daea30f6dd1d79a3c78ad92c5d40b383522b · T-0027.2 · VERIFIED · run-0389-verifier
9a99851bd15fe781c814231bb952513d1b597438 · T-0027.1 · VERIFIED · run-0382-verifier
d085ca0b1cd5f084c4065c186c5467d6fd82b9ae · T-0027.2 · VERIFIED · run-0381-verifier
d9c8a4d40544b62dd11214a9fc41887b28c3e778 · T-0027.4 · VERIFIED · run-0392-verifier
