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

**Fix as implemented on the Nanobot side:** green `feat/lionbot-v3` `fffeddcf6` (factory/specstore.py; `init`, gate pinning, `spec tasks`, `archive`), `4c68ef5db` (compose: current truth), `8281f9929` (prompts), `a7ef49ef6` (intake.js). Tests `tests/factory/test_spec_store.py`.
