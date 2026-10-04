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
`/Users/dphang/dev/spec-factory/intake/state/runs/run-0033-spec_writer/output.md`

## Ticket (Triage output)

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

## Request (raw)

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


## Answer 2

Answers to the Spec writer's Open questions 1–4. Each taken as the recommended default under the operator's standing take-the-recommendation rule; the operator can overturn any of them at the spec gate (question 2 is flagged there as the one most worth a second look).

1. (A3) No runtime dependency on the `openspec` CLI. Archive and the gate's apply check are the harness's own code; the tree stays readable by OpenSpec tooling, which is an optional manual check, never a gate.
2. The `openspec/` tree lives in the ticket store on the `tickets` branch, as part B says. Writer and critic receive it through the routing table (part C).
3. Decision-log lines come from a new `## Decisions` section in `proposal.md`, written by the spec writer and approved at the spec gate; archive appends them verbatim.
4. An archive refusal reuses the existing parent-park resolution (amend the spec and re-plan, or close).

Finish from your saved draft (spec v1) with these four taken; no part changes. Go to READY-FOR-CRITIC.
