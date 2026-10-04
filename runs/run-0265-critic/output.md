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

STATUS: APPROVE
CONFIDENCE: high; the three round-1 findings are fixed in the text and the new cite and the T-0026 facts were verified on this checkout, and nothing outside proposal.md changed.
ESCALATIONS: none
