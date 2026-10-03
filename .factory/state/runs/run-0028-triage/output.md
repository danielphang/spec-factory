Type: feature

Title: Adopt OpenSpec's storage model and lifecycle as a forked `spec-factory` schema (current-truth specs, change folders with deltas plus a factory `verification.md`, archive at parent close, repo-level `decisions.md`), keeping the factory's roles, runnable verification and gates

Summary: The requester wants the factory's spec format to gain a current-truth layer. Today a spec only describes a change, so once a ticket ships nothing in the store says what the capability does now. Fork OpenSpec's default schema into a `spec-factory` schema and map the factory onto it, as the request's table draws it:
- current-truth `openspec/specs/<capability>/spec.md`, written only by the archive step;
- a change folder with `proposal.md`, `design.md`, delta `specs/` whose WHEN/THEN scenarios are the Acceptance items, and the Planner's `tasks.md`;
- a factory-only `changes/<id>/verification.md` for NEW/REGRESSION labels, critic rounds and per-head verifier results;
- one repo-level `decisions.md`, appended at archive.

The human spec gate pins the delta. Parent close becomes archive: apply the deltas, move the folder to `changes/archive/`, append to `decisions.md`. Roles, round limits, gates and harness pieces 1–12 otherwise stay the same. The ticket covers the design doc (§2 Spec writer FORMAT, §4 Planner OUTPUT, the routing table's parent-close row, the Changelog), `specs/build-harness.md` parts B and K, and re-copying every `prompts/` file whose block changes.

Evidence:
- Request: `issues/08_openspec_schema.md`. The operator's answers are `intake/answers/T-0008-adoption.md` ("adopt", commit 4dd9f88) and `intake/answers/T-0008-2.md` (layout (a), commit 9c0367c). `T-0008-2.md` has the same text as "Answer 1" in this run's input.
- I re-checked these locations on this checkout today:
  - `docs/spec-factory.md` `## 2. Spec writer` is at line 244, and its FORMAT block is at lines 286–296.
  - `## 4. Planner / decomposer` is at line 358, with its OUTPUT block at about lines 381–393.
  - The parent-close text is in the Merge gate row at line 106: "VERIFIED closes the parent; FAILED or SPEC-DEFECT parks the parent in the human queue".
  - `## Changelog` is at line 605.
  - `specs/build-harness.md` has `### B. Ticket store (piece 1), requests, change proposal (piece 5)` at line 163 and `### K. Human surface and approval records (piece 9)` at line 304.
  - The prompt copies `prompts/02-spec-writer.md` and `prompts/04-planner.md` exist.
- `grep -rniE 'openspec' docs specs plans prompts README.md` found nothing. No current-truth layer or archive step exists yet, which confirms the finding.
- The operator's settled scope, quoted from Answer 1:
  - "(a) As the request's table draws it. `changes/<id>/verification.md` is its own factory artifact ... `decisions.md` is one file per repo, appended at archive."
  - A1: migrating green's pilot specs and replacing green's ROADMAP register are Nanobot-side follow-ups.
  - A4: approved specs T-0001..T-0007 in this store do not migrate.
  - A5: place T-0005's `## Operator steps` in the new mapping.
  - A3: stays an Open question for the writer.
- Requester's cost statement: "a FORMAT rewrite for the writer and planner prompts, one archive step, and a one-time migration of the P0 pilot specs". Per A1, that migration is outside this ticket.
- No Nanobot-side harness fix exists to verify against. My previous run found no match for `grep -rli openspec ~/dev/nanobot-upstream/factory`. All acceptance for this ticket will be NEW, checked against the documents.
- The OpenSpec facts (artifact names, `### Requirement:` / `#### Scenario:` grammar, `openspec schema fork`, `openspec/config.yaml`, archive behaviour) come from the requester's reading of OpenSpec's docs on 2026-10-01. I did not fetch those docs, and `openspec` is not installed on this machine.

Assumptions (my inferences, not stated by the requester):
- A2 (parent-close row): the STATUS routes stay the same. Only the action changes, so VERIFIED archives the change and then closes the parent. The archive step may be described in the design doc and spec without the harness calling the `openspec` CLI; that is A3, left open for the writer.
- A5 ordering: T-0005 (`ready-for-planner`) has not yet landed `## Operator steps` in the design doc. `grep -n 'Operator steps' docs/spec-factory.md` finds nothing today. The spec writer must place it in the mapping either way. The spec's Risk section should name the merge order against T-0005 and T-0007 (`ready-for-planner`, which edits the Harness section).
- Prompt scope: the requester names the writer and planner prompts. If the new FORMAT changes text that the critic or verifier blocks (`prompts/03-spec-critic.md`, `prompts/07-verifier.md`) rely on, those blocks need consistent edits and re-copies. That is for the spec writer to determine and declare; I am not adding it as a requirement.
- The spec writer should treat the OpenSpec artifact grammar as the requester's claim. Either cite the OpenSpec docs, or mark the grammar as the factory's own definition in the forked schema.

Reason: The operator answered the open design call (layout (a)) and confirmed scope (A1, A4, A5). Intent is clear and no product decision remains. A3 (runtime CLI dependency) is a design detail delegated to the spec writer as an Open question.

Priority (suggestion only): medium. It changes the FORMAT every later spec uses, so landing it before more tickets are written in the old shape is cheaper.

Out-of-scope observations:
- Green's ROADMAP (lines 720–723 in my previous run) still says "Proposed, awaiting the operator". Updating it, migrating SPEC-21/SPEC-27, and replacing green's ROADMAP register with `decisions.md` are Nanobot-side follow-ups (A1).

STATUS: ACCEPT
CONFIDENCE: medium. Every location and the operator's answers are confirmed on this checkout. The OpenSpec grammar and CLI facts are unverified requester claims, and the merge order with T-0005/T-0007 is unresolved.
ESCALATIONS: none. The read-only green scope from my previous run is resolved by the operator's A1 confirmation.
