## Context for this run (composed by the harness, not part of the request)

Repository: `spec-factory`, the design repo at `~/dev/spec-factory` (branch `main`). It holds
documents, not code: `docs/spec-factory.md` (the design document, source of truth),
`specs/build-harness.md` (the spec for building the harness), `plans/` (the Planner's
decompositions; `plans/P0-intake-skeleton.md` is the walking skeleton), and `prompts/`
(each file a verbatim copy of one prompt block in the design doc; it changes only by
re-copying that block). Your shell may start in another directory: use absolute paths, or
`cd ~/dev/spec-factory && <cmd>`.

The REFERENCE implementation is the Nanobot-side harness at `~/dev/nanobot-upstream/factory/`
(branch `feat/lionbot-v3`, built from `plans/P0-intake-skeleton.md`). Read it only to observe
what a fix does today; never write there, and never copy its test names, line numbers or
commit SHAs into a spec. Never read or write `~/.nanobot/` (live credentials).

Acceptance commands must be runnable as written from `~/dev/spec-factory` (grep, sed, diff,
`git diff --check` against the documents). A change to the design doc keeps its own
conventions: the Changelog section at its end, `specs/build-harness.md` consistent with the
new text, and any `prompts/` file whose block changed re-copied from it.

The request is an issue draft, written from a real pipeline run: where in the documents,
what happened (the evidence), why it matters, a proposed fix, and the Nanobot-side commit
where a harness fix already exists. The evidence is the requirement; the proposed fix is the
requester's suggestion, not a requirement. Verify the as-built fix in the reference harness
before relying on it; a NEW criterion that already passes on this checkout proves nothing.

Output: write your complete output, in your role's required format and ending with the
STATUS / CONFIDENCE / ESCALATIONS trailer, to the file named under "Output file" below. That
is the only file you may create or modify. Then return the same text as your final message.
## Output file
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0028-triage/output.md`

## Request (raw, with any answers appended)

---
title: Adopt OpenSpec's storage model and lifecycle as a forked schema; keep the factory's roles, verification and decision log
labels: design-doc, format, proposal
---
**Where:** design doc §2 Spec writer FORMAT, §4 Planner OUTPUT, the routing table's parent-close row; `specs/build-harness.md` parts B (store layout) and K (export).

**Finding (operator question, 2026-10-01):** the factory's spec format (Problem / Evidence / Root cause / Proposed change / Acceptance / Tests to change / Out of scope / Open questions / Risk) is a change-shaped document. It has no current-truth layer: after a ticket ships, nothing in the store says what the capability does now. OpenSpec (Fission-AI) has exactly that layer and nothing the factory has: no roles, no critic rounds, no runnable NEW/REGRESSION acceptance, no verifier, no commit-bound gate.

**OpenSpec facts, from its docs** (README, docs/concepts.md, docs/customization.md, read 2026-10-01):
- Specs "are the source of truth — they describe how your system currently behaves"; requirements are `### Requirement:` + SHALL/MUST, scenarios are `#### Scenario:` + WHEN/THEN.
- A change is a folder: `proposal.md`, optional `design.md`, `specs/` deltas (`## ADDED|MODIFIED|REMOVED Requirements`), `tasks.md`. Archive applies the deltas to `openspec/specs/` and keeps the change folder intact under `changes/archive/` as history.
- Artifacts are a schema (a dependency graph) a project forks and extends: `openspec schema fork <built-in> <name>`; custom artifact types and templates are supported; `openspec/config.yaml` carries shared context and per-artifact rules.

**Proposal: an "and", not a switch.** Fork the default schema into `spec-factory` and map the factory onto it:

| OpenSpec artifact | Factory content | Author |
|---|---|---|
| `openspec/specs/<capability>/spec.md` (current truth) | requirement + scenario grammar; each scenario carries its runnable check | archive step only |
| `changes/<id>/proposal.md` | Problem, Evidence, Root cause, Out of scope, Risk, Open questions | Spec writer |
| `changes/<id>/design.md` | the "how": seams, fork lines, Tests to change | Spec writer / Planner |
| `changes/<id>/specs/<capability>/spec.md` (delta) | ADDED/MODIFIED/REMOVED requirements with WHEN/THEN scenarios = the Acceptance items | Spec writer; Critic reviews |
| `changes/<id>/tasks.md` | the Planner's sub-tickets and coverage map | Planner |
| `changes/<id>/verification.md` (factory-specific artifact) | NEW/REGRESSION labels, critic rounds, verifier results per head | Critic, Verifier |
| repo-level `decisions.md` | one line per decision with change id, appended at archive | archive step; replaces the port's ROADMAP register for new work |

Lifecycle additions: the human spec gate pins the delta; parent close becomes OpenSpec archive (apply deltas, move the folder, append decisions). Routing table, round limits, gates and harness pieces 1–12 are unchanged.

**What this costs:** a FORMAT rewrite for the writer and planner prompts, one archive step, and a one-time migration of the P0 pilot specs (T-0001, T-0003) into the new shape. What it buys: a current-truth layer the lionbot port never had, deltas that make "what changed" mechanical, and an OpenSpec-compatible tree other tooling can read.

**Open to the human:** whether `verification.md` is an artifact or lives inside the delta's scenarios; whether `decisions.md` is per repo or per capability.


## Answer 1

Answer to Triage's layout question. Taken by default under the operator's standing take-the-recommendation rule (the operator confirmed adoption itself directly, 2026-10-01); reversible at the spec gate.

**(a) As the request's table draws it.** `changes/<id>/verification.md` is its own factory artifact (NEW/REGRESSION labels, critic rounds, verifier results per head), so round-to-round churn stays out of the delta that archive applies. `decisions.md` is one file per repo, appended at archive.

Also settled for the spec writer:
- A1 confirmed: migrating green's pilot specs (SPEC-21, SPEC-27) and replacing green's ROADMAP register with `decisions.md` are Nanobot-side follow-ups, outside this ticket. This ticket covers the design doc, `specs/build-harness.md`, re-copied `prompts/` files and the Changelog.
- A4 confirmed: the already-approved specs T-0001..T-0007 in this store do not migrate.
- A5: place T-0005's `## Operator steps` in the new artifact mapping; do not drop it.
- A3 stays an Open question for the writer to answer with a recommendation.

## Your previous Triage output (the question you asked is answered above)

Type: feature

Title: Adopt OpenSpec's storage model and lifecycle as a forked `spec-factory` schema (current-truth specs, change folders with deltas, archive at parent close), keeping the factory's roles, runnable verification and decision log

Summary: The requester wants the factory's spec format to gain a current-truth layer. Today a spec (Problem / Evidence / Root cause / Proposed change / Acceptance / Tests to change / Out of scope / Open questions / Risk) only describes a change. Once a ticket ships, nothing in the store says what the capability does now. They propose forking OpenSpec's default schema into a `spec-factory` schema. Each change becomes a folder: `proposal.md`, `design.md`, delta `specs/` whose WHEN/THEN scenarios are the Acceptance items, `tasks.md` from the Planner, and a factory-only `verification.md`. Parent close becomes OpenSpec's archive step: it applies the deltas to `openspec/specs/`, moves the folder to `changes/archive/` and appends to a `decisions.md`. Roles, routing, round limits, gates and harness pieces 1–12 otherwise stay as they are. This is an "and", not a switch.

Evidence:
- Request: `issues/08_openspec_schema.md`. `intake/state/requests/T-0008.md` matches it byte for byte (`diff` gave no output).
- The locations it names all exist on this checkout:
  - `docs/spec-factory.md` §2 Spec writer (line 244), whose FORMAT block is at lines 286–296.
  - §4 Planner (line 358), whose OUTPUT is at line 381.
  - The routing table's parent-close row, line 106: "...VERIFIED closes the parent; FAILED or SPEC-DEFECT parks the parent in the human queue".
  - `specs/build-harness.md` §B "Ticket store" (line 163) and §K "Human surface and approval records" (line 304). Export goes to `knowledge_vault/sanitized_specs/<ID>.md`.
- `grep -rniE 'openspec|current truth|decisions\.md|archive' docs specs plans prompts README.md` finds nothing. The design doc has no current-truth layer and no archive step today, which confirms the finding.
- Requester quote: "Open to the human: whether `verification.md` is an artifact or lives inside the delta's scenarios; whether `decisions.md` is per repo or per capability."
- Requester quote on cost: "a FORMAT rewrite for the writer and planner prompts, one archive step, and a one-time migration of the P0 pilot specs (T-0001, T-0003)".
- The adoption decision already exists:
  - `intake/answers/T-0008-adoption.md` (commit 4dd9f88) records "Operator decision (2026-10-01...): adopt."
  - That answer is not appended to this run's input. I read it from the store.
  - It settles whether to adopt. It does not settle the two open items above.
- The facts about OpenSpec come from the requester (README, docs/concepts.md, docs/customization.md, read 2026-10-01). I did not check them: no fetch was made. `which openspec` returned "openspec not found" on this machine.
- No Nanobot-side harness fix exists for this request. `grep -rli openspec ~/dev/nanobot-upstream/factory` finds nothing. The only Nanobot-side mention is a "Proposed, awaiting the operator" entry in green's `knowledge_vault/specs/ROADMAP.md` (lines 720–723).
- Duplicate search: no duplicate among T-0001..T-0007 in this store. Two tickets overlap but are not duplicates:
  - T-0005 adds an optional `## Operator steps` section to the same Spec writer FORMAT.
  - T-0007 edits the design doc's Harness section.
  - Both are `ready-for-planner`. Commit f79b7b9 queued T-0008 after T-0006/T-0007.

Assumptions (my inferences, not stated by the requester):
- A1 (green migration out of scope here): in this request, "P0 pilot specs (T-0001, T-0003)" means green's store, not this one:
  - Green's `knowledge_vault/spec_factory/tickets/T-0001.yaml` is "SPEC-21: Session Health Monitoring".
  - Green's T-0003 is "SPEC-27: Skill System Consolidation".
  - In this store, T-0001 and T-0003 are issue drafts 01 and 03.
  - Green is a protected, read-only path for this repo, and `intake/README.md` §Scope hands Nanobot-side follow-ups to the nanobot sessions.
  - So the migration, and swapping green's ROADMAP register for `decisions.md`, are follow-ups outside this ticket. This ticket covers the design doc, `specs/build-harness.md`, re-copied `prompts/` files and the Changelog.
- A2 (parent-close row): "Routing table ... unchanged" means the STATUS routes stay the same. Only the action on the parent-close row changes, from "VERIFIED closes the parent" to "VERIFIED archives, then closes". The requester's own lifecycle text implies this.
- A3 (CLI dependency): the request does not say whether the harness runs the `openspec` CLI (fork, archive) at runtime or only follows its tree layout and implements archive itself. `openspec` is not installed here. I leave this to the spec writer as an Open question and do not decide it.
- A4 (specs already approved): the approved specs for T-0001..T-0007 in this store are in the current format. The request does not say whether they migrate. I assume they do not, because the request names only the green pilot specs.
- A5 (T-0005 overlap): T-0005's `## Operator steps` section has to land somewhere in the new artifact mapping. The spec writer should place it, and should not drop it.

Question for human: The request leaves two design calls to you (adoption itself is already answered "adopt"). How should verification records and the decision log be laid out?
- (a) As the request's table draws it. `changes/<id>/verification.md` is its own factory artifact, holding NEW/REGRESSION labels, critic rounds and verifier results per head. `decisions.md` is one file per repo, appended at archive.
  - Triage's lean, offered as a suggestion only. Critic rounds and per-head verifier results change from round to round. Keeping them out of the delta keeps that churn out of what archive applies to current truth. The deltas also stay plain OpenSpec.
- (b) Verification inline. Each delta scenario carries its runnable check and its NEW/REGRESSION label, with no `verification.md`. Critic rounds and verifier results stay in the ticket store's run records. `decisions.md` is one file per repo.
- (c) `verification.md` as its own artifact, as in (a), but `decisions.md` is per capability (`openspec/specs/<capability>/decisions.md`). A cross-cutting change then appends to each capability it touches.

Priority (suggestion only): medium. It changes the FORMAT that every later spec uses, so it is cheaper to land before more tickets are written in the old format.

Out-of-scope observations:
- Green's ROADMAP line 720 says the proposal keeps "this decision log". The request says a repo-level `decisions.md` "replaces the port's ROADMAP register for new work". Settling that belongs to the nanobot side once this ticket is decided.

STATUS: NEEDS-HUMAN
CONFIDENCE: medium. The intent is clear and every location is confirmed. I did not verify the OpenSpec facts, and the green-migration scope (A1) is my inference.
ESCALATIONS: Part of the requested work (migrating green's T-0001/T-0003 pilot specs and replacing green's ROADMAP register) is in `~/dev/nanobot-upstream`, which is read-only for this repo. I have scoped it out as a Nanobot-side follow-up (A1); confirm this, or re-scope.
