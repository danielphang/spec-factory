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

STATUS: REVISE
CONFIDENCE: high; every cited path and six acceptance commands were checked on this checkout, and the one BLOCKING finding is a rubric-mandated gloss with a one-clause fix.
ESCALATIONS: none
