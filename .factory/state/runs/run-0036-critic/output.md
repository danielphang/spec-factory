Critic, round 1 (spec v2; v0/v1 went NEEDS-HUMAN, no earlier critic run).

What I checked myself:
- `~/dev/spec-factory` `main` is at `b4d0f90`; `git diff --stat 4cd8d12 HEAD -- docs specs prompts README.md plans` is empty, so "today" = `4cd8d12` still holds.
- Every OLD anchor in parts A–L (22 strings) matches exactly once on `main` (`grep -c -F`).
- I applied parts A–L with my own script to a scratch clone at `4cd8d12`, re-copied the two prompts per part G, and committed: `4 files changed, 93 insertions(+), 26 deletions(-)` (doc 58, writer prompt 27, planner prompt 8, build spec 26), `git diff --check` clean. I ran all 20 Acceptance commands on the clone before and after. Before: 1 prints nothing, 2 prints the `:Problem;…` string, 3–9 print `0`, 10 `CONTIGUOUS LAST-IS-OTHER`, 11 `0 0 1`, 12 `6`, 13–19 empty, 20 clean. After: the four parts; the mapped string; `6`; clean + `4`; clean + `3`; `10`; `3`; `2`; `2`; `CONTIGUOUS LAST-IS-SPEC-STORE`; `5 2 0`; `6`; 13–19 empty; 20 clean. Identical to the spec's quoted results.
- OpenSpec quotes: fetched `docs/concepts.md` and `docs/customization.md` from `raw.githubusercontent.com/Fission-AI/OpenSpec/main`; lines 46, 393–397, 547–549 and `customization.md:184` contain the quoted text.
- `grep -rniE openspec docs specs plans prompts README.md | wc -l` → `0`; same for `~/dev/nanobot-upstream/factory` → `0`.
- Operator answers read from `intake/state/requests/T-0008.md` (`## Answer 1`, `## Answer 2`); the spec's A1/A3/A4/A5 and the four defaults match them.

Findings:

[BLOCKING] 5, 6 — Part C (routing-table Receives) together with part K ("`run compose` and its `input_sources` do not change")
Problem: The design doc will say the spec writer and critic receive current truth, but the build spec's compose lists, which are what delivers a role's input, are left unchanged, so the built harness never gives either role current truth and the FORMAT's "reuse a current-truth capability" / "MODIFIED and REMOVED name a requirement in current truth" cannot be followed.
Evidence: `specs/build-harness.md` part B, `factory run compose`: "writes `runs/<run_id>/input.md` from exactly the sources `factory/compose.py` declares … the 'with input =' lists in H"; H intake.js step 2: writer input = "ticket + request (+ round ≥ 2 …)", critic input = "spec vN (+ round ≥ 2 …)", which today mirror the Receives cells part C edits; doc Harness: "composing each role's input from *only* its declared sources"; piece 3: "only its declared inputs". Part A's last sentence ("The spec writer and the critic read current truth (routing table)") has no mechanism behind it once K says compose does not change. The `openspec/` tree lives on `tickets` (Q2), which the roles' read-only clone of `main` does not contain.
Suggested fix: In part K, also edit H's intake.js step 2 so the writer's and the critic's "with input =" lists include current truth (every `openspec/specs/<capability>/spec.md` present, recorded in `input_sources:`), and state that item 42 still holds because `openspec/specs/` is empty in case `accept-approve` (fresh `factory init`); add a check for the new compose text to Acceptance 11.

[SHOULD-FIX] 1, 5 — Part I, first paragraph: "Spec text `specs/<ID>/v<N>.md` (every version the writer returns, verbatim)"
Problem: "verbatim" contradicts the build spec and the as-built harness, which store the writer's output with its STATUS/CONFIDENCE/ESCALATIONS trailer stripped, and the spec is silent on whether the split (part I) and `tasks.md` (part I, `factory spec tasks`; item 88 "equal to the planner run's `output.md`") carry a trailer.
Evidence: Build-spec item 42 (kept verbatim by Acceptance 17): the critic's input, composed from `specs/T-0001/v1.md` alone, "contains neither the triage output nor the writer's `CONFIDENCE:` line", so `v1.md` has no trailer. Reference harness `factory/cli.py` `_text_from` (used by `spec add --from-run` and `plan add`) returns `status.strip_trailer(output.md)`.
Suggested fix: Replace "verbatim" with "trailer stripped, as `spec add` stores it", and define `tasks.md` the same way (the planner run's output with its trailer stripped) in part I and item 88.

[NIT] 4 — Part A, paragraph after the table: "The Author column follows the operator's table, with one addition."
Problem: Two cells differ from the request's table, not one: `design.md` drops "/ Planner" and `verification.md` adds the spec writer; the first is undeclared.
Evidence: `issues/08_openspec_schema.md` table rows `design.md` → "Spec writer / Planner", `verification.md` → "Critic, Verifier".
Suggested fix: Say both deviations in that sentence (the planner's only artifact is `tasks.md`).

[NIT] 6 — Part J, `approve-spec`: "exit 2 with nothing written when a part is malformed"
Problem: "Malformed" is defined only for an unknown `=== <path>` (part I); a delta part with no `## ADDED|MODIFIED|REMOVED Requirements` heading, a block without a `### Requirement:` name, or a scenario with no label in `verification.md` is left to the implementer.
Evidence: Parts I and J text; the archive step (J, step 2) needs named requirement blocks to apply MODIFIED/REMOVED.
Suggested fix: One clause in I listing what a well-formed part is (the path rule, a delta heading per part, a named requirement per block, one `## Acceptance` label per scenario name), and J's "malformed" points to it.

[NIT] 6 — Part D, the unchanged RULES above FORMAT: "give the check as an inline script in the Acceptance line itself"
Problem: After the change there is no "Acceptance line" holding a command; the command is the scenario's WHEN line, so the writer prompt carries a stale phrase.
Evidence: `docs/spec-factory.md` §2 RULES (lines 19–26 of the writer block) vs. the new FORMAT.
Suggested fix: Either change that phrase to "in the scenario's WHEN line itself" (and let Acceptance 2–4 cover the re-copy) or say in the spec that the stale wording is accepted.

Rubric items with no finding: 2 (all NEW items fail today for the stated reason and pass after; 12 holds on both; 4/5/13 catch a hand-edited prompt; 2 catches a misplaced section), 3 (one PR, ~120 lines, out-of-scope list sensible, Tests to change none is correct for a documents repo), T-0009 overlap claim checked (it names B's `run start` bullet and build-spec part I; this spec edits neither).

Out-of-scope observations:
- The reference harness already stores the planner's output as `plans/<ID>.md` via `factory plan add` (ticket key `plan:`, seen in `intake/state/tickets/T-0008.yaml`), which the build spec does not mention (`grep -F 'plans/' specs/build-harness.md` → nothing). `factory spec tasks` (part I) would be a second copy of the same text. Build-spec/reference drift, not this ticket's defect; whoever builds the spec store should reuse one of them.
- The spec-approval row of the Human gates table does not name the new `## Decisions` lines among what the human approves; Answer 2 Q3 says they are approved at the gate. The whole pinned version is what the gate approves, so this is wording, not behaviour.

Prior findings: none (round 1).

STATUS: REVISE
CONFIDENCE: high — every anchor and all 20 commands reproduced on my own clone; the BLOCKING finding rests on quoted build-spec text (part B compose, H input lists) that the spec leaves unchanged.
ESCALATIONS: none
